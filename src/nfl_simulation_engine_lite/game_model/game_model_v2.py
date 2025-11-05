from nfl_simulation_engine_lite.game_model.game_model import AbstractGameModel
from nfl_simulation_engine_lite.team.team import Team
from nfl_simulation_engine_lite.team.team_rates import TeamRates
from nfl_simulation_engine_lite.fourth_down_models.models import v2a_fdm
from math import exp
import random
import pandas as pd
import numpy as np

rpi_params = {
    "gamma" : 0.06,
    "multiplier_floor": 0.80,
    "multiplier_ceiling": 1.20,
    "hfa_const": 0.08
}

class GameModel_V2(AbstractGameModel):
    def __init__(self, off_weight=0.525, rpi_enabled=True):
        self.strength_data = None
        self.fourth_down_model = v2a_fdm
        self.fourth_down_model_column_mapping = { 0: "goforit", 1: "field_goal", 2: "punt" }
        super().__init__(off_weight)

    def init_team_strength_data(self, rpi_enabled: bool) -> dict:
        if rpi_enabled:
            home_z_score = self.get_home_team().get_rpi_data()["rpi_z_score"]
            away_z_score = self.get_away_team().get_rpi_data()["rpi_z_score"]
            z_diff = home_z_score - away_z_score + rpi_params["hfa_const"]
            home_multiplier = np.clip(exp(rpi_params["gamma"] * z_diff), rpi_params["multiplier_floor"], rpi_params["multiplier_ceiling"])
            away_multipler = np.clip(exp(-1 * rpi_params["gamma"] * z_diff), rpi_params["multiplier_floor"], rpi_params["multiplier_ceiling"])

            self.strength_data = {
                "z_diff": z_diff,
                "home_multiplier": home_multiplier,
                "away_multiplier": away_multipler,
            }
        else:
            self.strength_data = {
                "home_multiplier": 1.0,
                "away_multiplier": 1.0,
            }

    def get_model_code(self) -> str:
        return "v2"

    def get_half_seconds_remaining(self, qtr: int, qtr_seconds_remaining: int) -> int:
        if qtr == 1 or qtr == 3:
            return qtr_seconds_remaining + 900
        else:
            return qtr_seconds_remaining

    def handle_4th_down(self, game_state:dict):
        posteam = game_state["possession_team"].name
        defteam = game_state["defense_team"].name
        fourth_down_data = {
            "game_seconds_remaining": game_state["game_seconds_remaining"],
            "half_seconds_remaining": self.get_half_seconds_remaining(game_state["quarter"], game_state["quarter_seconds_remaining"]),
            "ydstogo": game_state["distance"],
            "yardline_100": game_state["yardline"],
            "score_differential": game_state["score"][posteam] - game_state["score"][defteam]    
        }
        prediction = self.fourth_down_model.predict(pd.DataFrame([fourth_down_data]))
        return self.fourth_down_model_column_mapping[prediction[0]]

    def resolve_play(self, game_state: dict) -> dict:
        posteam = game_state["possession_team"]
        defteam = game_state["defense_team"]

        distance_category = "short" if game_state["distance"] < 4 else "medium" if game_state["distance"] < 7 else "long"
        redzone = 1 if game_state["yardline"] <= 20 else 0
        situational_condition = (game_state["down"], game_state["distance"], game_state["yardline"], distance_category, redzone)

        time_elapsed = random.randint(15,40)

        play_type = None
        if (game_state["down"] == 4):
            play_type = self.handle_4th_down(game_state)
        else:
            # for non-4th down scenarios or 4th downs that we are trying to convert
            # get the the type of play to be called: run or pass
            play_type = self.get_conditional_play_type(posteam.get_team_rates(), situational_condition)

        # Handle 4th down scenarios for punts and field goals
        if game_state["down"] == 4 and play_type == "punt":
            return {
                "play_type": "punt", 
                "field_goal_made": None,
                "yards_gained": 40,
                "time_elapsed": time_elapsed, 
                "quarter": game_state["quarter"],
                "quarter_seconds_remaining": game_state["quarter_seconds_remaining"],
                "turnover": False,
                "touchdown": False,
                "posteam": posteam.name
            }
        elif game_state["down"] == 4 and play_type == "field_goal":
            fg_success_rate = self.get_field_goal_success_rate(posteam)
            return {
                "play_type": "field_goal", 
                "field_goal_made": random.choices([True, False], [fg_success_rate, 1 - fg_success_rate])[0],
                "yards_gained": 0,
                "time_elapsed": time_elapsed,
                "quarter": game_state["quarter"],
                "quarter_seconds_remaining": game_state["quarter_seconds_remaining"],  
                "turnover": False,
                "touchdown": False,
                "posteam": posteam.name
            }

        off_yards_per_play = self.get_off_yards_per_play(posteam, play_type, situational_condition)
        def_yards_per_play = self.get_def_yards_per_play(defteam, play_type, situational_condition)
        
        yards_gained = self.get_weighted_average(off_yards_per_play, def_yards_per_play)

        # Log NaN values in calculations
        if pd.isna(yards_gained):
            print(f"yards_gained is NaN: off_yards_per_play={off_yards_per_play}, def_yards_per_play={def_yards_per_play}, situational_condition={situational_condition}")

        if play_type == "pass":
            off_sack_rate = self.get_off_sack_rate(posteam, situational_condition)
            def_sack_rate = self.get_def_sack_rate(defteam, situational_condition)
            weighted_sack_rate = self.get_weighted_average(off_sack_rate, def_sack_rate)
            sack = random.choices([True, False], [weighted_sack_rate, 1 - weighted_sack_rate])[0]
            if (sack):
                off_yards_lost_per_sack = self.get_sack_yards_allowed(posteam, situational_condition)
                def_yards_inflicted_per_sack = self.get_sack_yards_inflicted(defteam, situational_condition)
                weighted_yards_gained = self.get_weighted_average(off_yards_lost_per_sack, def_yards_inflicted_per_sack)
                yards_gained = -weighted_yards_gained

            off_pass_cmp_rate = self.get_off_pass_cmp_rate(posteam, situational_condition)
            def_pass_cmp_rate = self.get_def_pass_cmp_rate(defteam, situational_condition)
            weighted_pass_cmp_rate = self.get_weighted_average(off_pass_cmp_rate, def_pass_cmp_rate)
            pass_completed = random.choices([True, False], [weighted_pass_cmp_rate, 1 - weighted_pass_cmp_rate])[0]
            if (not pass_completed):
                yards_gained = 0

        off_turnover_rate = self.get_off_turnover_rate(posteam, situational_condition)
        def_turnover_rate = self.get_def_turnover_rate(defteam, situational_condition)
        weighted_turnover_rate = self.get_weighted_average(off_turnover_rate, def_turnover_rate)
        turnover_on_play = random.choices([True, False], [weighted_turnover_rate, 1 - weighted_turnover_rate])[0]
        if (turnover_on_play):
            yards_gained = 0
        
        return {
            "play_type": play_type, 
            "field_goal_made": None,
            "yards_gained": yards_gained,
            "time_elapsed": time_elapsed,
            "quarter": game_state["quarter"],
            "quarter_seconds_remaining": game_state["quarter_seconds_remaining"],
            "turnover": turnover_on_play,
            "touchdown": False, # This will be updated after the play is processed in update_game_state
            "posteam": posteam.name
        }

    def get_conditional_play_type(self, team_rates: TeamRates, situation: tuple[int, int, int, int, int]) -> str:
        # Based on the game situation, determine what play type will be called next
        down, __, __, distance_category, redzone = situation
        team_rates_data = team_rates.get_data_for_situation(down, distance_category, redzone)
        run_prob = team_rates_data.run_rate
        pass_prob = team_rates_data.pass_rate 
        return np.random.choice(["run", "pass"], p=[run_prob, pass_prob])

    def _bias_off_value(self, value: float, team: str) -> float:
        if team == self.home_team.name:
            return value * self.strength_data["home_multiplier"]
        else:
            return value * self.strength_data["away_multiplier"]

    def _bias_def_value(self, value: float, team: str) -> float:
        if team == self.home_team.name:
            return value / self.strength_data["home_multiplier"]
        else:
            return value / self.strength_data["away_multiplier"]

    def get_off_yards_per_play(self, posteam: Team, play_type: str, situation: tuple[int, int, int]) -> float:
        down, __, __, distance_category, redzone = situation
        team_rates = self.home_team.get_team_rates() if posteam == self.home_team else self.away_team.get_team_rates()
        team_rates_data = team_rates.get_data_for_situation(down, distance_category, redzone)
        fallback_team_rates_data = team_rates.get_data_for_situation(None, None, None)

        raw_off_yards_per_play = 0
        if play_type == "pass":
            raw_off_yards_per_play = team_rates_data.yards_per_completion if pd.notna(team_rates_data.yards_per_completion) else fallback_team_rates_data.yards_per_completion
        else:
            raw_off_yards_per_play = team_rates_data.rush_yards_per_carry if pd.notna(team_rates_data.rush_yards_per_carry) else fallback_team_rates_data.rush_yards_per_carry

        return self._bias_off_value(raw_off_yards_per_play, posteam)

    def get_def_yards_per_play(self, defteam: Team, play_type: str, situation: tuple[int, int, int]) -> float:
        down, __, __, distance_category, redzone = situation
        team_rates = self.home_team.get_team_rates() if defteam == self.home_team else self.away_team.get_team_rates()
        team_rates_data = team_rates.get_data_for_situation(down, distance_category, redzone)
        fallback_team_rates_data = team_rates.get_data_for_situation(None, None, None)

        raw_def_yards_per_play = 0
        if play_type == "pass":
            raw_def_yards_per_play = team_rates_data.yards_allowed_per_completion if pd.notna(team_rates_data.yards_allowed_per_completion) else fallback_team_rates_data.yards_allowed_per_completion
        else:
            raw_def_yards_per_play = team_rates_data.rush_yards_per_carry_allowed if pd.notna(team_rates_data.rush_yards_per_carry_allowed) else fallback_team_rates_data.rush_yards_per_carry_allowed

        return self._bias_def_value(raw_def_yards_per_play, defteam)


    def get_off_sack_rate(self, posteam: Team, situation: tuple[int, int, int]) -> float:
        down, __, __, distance_category, redzone = situation
        team_rates = self.home_team.get_team_rates() if posteam == self.home_team else self.away_team.get_team_rates()
        team_rates_data = team_rates.get_data_for_situation(down, distance_category, redzone)
        fallback_team_rates_data = team_rates.get_data_for_situation(None, None, None)

        return team_rates_data.sacks_allowed_rate if pd.notna(team_rates_data.sacks_allowed_rate) else fallback_team_rates_data.sacks_allowed_rate

    def get_def_sack_rate(self, defteam: Team, situation: tuple[int, int, int]) -> float:
        down, __, __, distance_category, redzone = situation
        team_rates = self.home_team.get_team_rates() if defteam == self.home_team else self.away_team.get_team_rates()
        team_rates_data = team_rates.get_data_for_situation(down, distance_category, redzone)
        fallback_team_rates_data = team_rates.get_data_for_situation(None, None, None)

        return team_rates_data.sacks_made_rate if pd.notna(team_rates_data.sacks_made_rate) else fallback_team_rates_data.sacks_made_rate

    def get_sack_yards_allowed(self, posteam: Team, situation: tuple[int, int, int]) -> float:
        down, __, __, distance_category, redzone = situation
        team_rates = self.home_team.get_team_rates() if posteam == self.home_team else self.away_team.get_team_rates()
        team_rates_data = team_rates.get_data_for_situation(down, distance_category, redzone)
        fallback_team_rates_data = team_rates.get_data_for_situation(None, None, None)

        return team_rates_data.sack_yards_allowed if pd.notna(team_rates_data.sack_yards_allowed) else fallback_team_rates_data.sack_yards_allowed

    def get_sack_yards_inflicted(self, defteam: Team, situation: tuple[int, int, int]) -> float:
        down, __, __, distance_category, redzone = situation
        team_rates = self.home_team.get_team_rates() if defteam == self.home_team else self.away_team.get_team_rates()
        team_rates_data = team_rates.get_data_for_situation(down, distance_category, redzone)
        fallback_team_rates_data = team_rates.get_data_for_situation(None, None, None)

        return team_rates_data.sack_yards_inflicted if pd.notna(team_rates_data.sack_yards_inflicted) else fallback_team_rates_data.sack_yards_inflicted

    def get_off_pass_cmp_rate(self, posteam: Team, situation: tuple[int, int, int]) -> float:
        down, __, __, distance_category, redzone = situation
        team_rates = self.home_team.get_team_rates() if posteam == self.home_team else self.away_team.get_team_rates()
        team_rates_data = team_rates.get_data_for_situation(down, distance_category, redzone)
        fallback_team_rates_data = team_rates.get_data_for_situation(None, None, None)

        raw_off_pass_cmp_rate = team_rates_data.pass_completion_rate if pd.notna(team_rates_data.pass_completion_rate) else fallback_team_rates_data.pass_completion_rate
        return self._bias_off_value(raw_off_pass_cmp_rate, posteam)

    def get_def_pass_cmp_rate(self, defteam: Team, situation: tuple[int, int, int]) -> float:
        down, __, __, distance_category, redzone = situation
        team_rates = self.home_team.get_team_rates() if defteam == self.home_team else self.away_team.get_team_rates()
        team_rates_data = team_rates.get_data_for_situation(down, distance_category, redzone)
        fallback_team_rates_data = team_rates.get_data_for_situation(None, None, None)

        raw_def_pass_cmp_rate = team_rates_data.pass_completion_rate_allowed if pd.notna(team_rates_data.pass_completion_rate_allowed) else fallback_team_rates_data.pass_completion_rate_allowed
        return self._bias_def_value(raw_def_pass_cmp_rate, defteam)

    def get_off_turnover_rate(self, posteam: Team, situation: tuple[int, int, int]) -> float:
        down, __, __, distance_category, redzone = situation
        team_rates = self.home_team.get_team_rates() if posteam == self.home_team else self.away_team.get_team_rates()
        team_rates_data = team_rates.get_data_for_situation(down, distance_category, redzone)
        fallback_team_rates_data = team_rates.get_data_for_situation(None, None, None)

        return team_rates_data.turnover_rate if pd.notna(team_rates_data.turnover_rate) else fallback_team_rates_data.turnover_rate

    def get_def_turnover_rate(self, defteam: Team, situation: tuple[int, int, int]) -> float:
        down, __, __, distance_category, redzone = situation
        team_rates = self.home_team.get_team_rates() if defteam == self.home_team else self.away_team.get_team_rates()
        team_rates_data = team_rates.get_data_for_situation(down, distance_category, redzone)
        fallback_team_rates_data = team_rates.get_data_for_situation(None, None, None)

        return team_rates_data.forced_turnover_rate if pd.notna(team_rates_data.forced_turnover_rate) else fallback_team_rates_data.forced_turnover_rate

    def get_field_goal_success_rate(self, posteam: Team) -> float:
        team_rates = self.home_team.get_team_rates() if posteam == self.home_team else self.away_team.get_team_rates()
        team_rates_data = team_rates.get_data_for_situation(None, None, None)
        return team_rates_data.field_goal_success_rate if pd.notna(team_rates_data.field_goal_success_rate) else 0.75