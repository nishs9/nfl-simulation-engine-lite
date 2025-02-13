from game_model.game_model import AbstractGameModel
from fourth_down_models.models import v1_fdm
import pandas as pd
import random

class GameModel_V1(AbstractGameModel):
    
    def __init__(self, off_weight=0.65):
        self.fourth_down_model = v1_fdm
        self.fourth_down_model_column_mapping = { 0: "run", 1: "pass",
                                                2: "punt", 3: "field_goal" }
        super().__init__(off_weight)

    def get_model_code(self) -> str:
        return "v1"

    def get_half_seconds_remaining(self, qtr: int, qtr_seconds_remaining: int) -> int:
        if qtr == 1 or qtr == 3:
            return qtr_seconds_remaining + 900
        else:
            return qtr_seconds_remaining

    def handle_4th_down(self, game_state: dict) -> str:
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
        posteam_stats = posteam.get_stats()

        defteam = game_state["defense_team"]
        defteam_stats = defteam.get_stats()

        time_elapsed = random.randint(15,40)

        play_type = None
        if (game_state["down"] == 4):
            # For 4th downs, use our random forest model to determine the play call
            play_type = self.handle_4th_down(game_state)
        else:
            # If not 4th down, run normal simulation logic
            play_type = random.choices(['run', 'pass'], [posteam_stats.run_rate, posteam_stats.pass_rate])[0]

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
            fg_success_rate = posteam_stats.field_goal_success_rate
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

        # Handle normal play calls (run or pass)
        off_yards_per_play = None
        def_yards_per_play = None
        if (play_type == "run"):
            off_yards_per_play = posteam.sample_offensive_rushing_play()
            def_yards_per_play = defteam.sample_defensive_rushing_play()
        else:
            off_yards_per_play = posteam.sample_offensive_passing_play()
            def_yards_per_play = defteam.sample_defensive_passing_play()
        
        weighted_yards_per_play = self.get_weighted_average(off_yards_per_play, def_yards_per_play)

        if (play_type == "pass"):
            off_pass_cmp_rate = posteam_stats.pass_completion_rate / 100
            def_pass_cmp_rate = defteam_stats.pass_completion_rate_allowed / 100
            weighted_pass_cmp_rate = self.get_weighted_average(off_pass_cmp_rate, def_pass_cmp_rate)
            pass_completed = random.choices([True, False], [weighted_pass_cmp_rate, 1 - weighted_pass_cmp_rate])[0]
            if (not pass_completed):
               weighted_yards_per_play = 0 

        off_turnover_rate = posteam_stats.turnover_rate
        def_turnover_rate = defteam_stats.forced_turnover_rate
        weighted_turnover_rate = (0.45) * (self.get_weighted_average(off_turnover_rate, def_turnover_rate))
        turnover_on_play = random.choices([True, False], [weighted_turnover_rate, 1 - weighted_turnover_rate])[0]

        if (not turnover_on_play):
            yards_gained = weighted_yards_per_play
        else:
            yards_gained = 0

        off_sack_rate = posteam_stats.sacks_allowed_rate
        def_sack_rate = defteam_stats.sacks_made_rate
        weighted_sack_rate = self.get_weighted_average(off_sack_rate, def_sack_rate)
        sack_on_play = random.choices([True, False], [weighted_sack_rate, 1 - weighted_sack_rate])[0]

        if (sack_on_play and play_type == "pass"):
            off_yards_lost_per_sack = posteam_stats.sack_yards_allowed
            def_yards_inflicted_per_sack = defteam_stats.sack_yards_inflicted
            yards_lost_on_sack = self.get_weighted_average(off_yards_lost_per_sack, def_yards_inflicted_per_sack)
            yards_gained = yards_lost_on_sack

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