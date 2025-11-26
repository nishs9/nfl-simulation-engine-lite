from nfl_simulation_engine_lite.game_model.game_model_v2 import GameModel_V2
from nfl_simulation_engine_lite.team.team import Team
import pandas as pd

class GameModel_V2b(GameModel_V2):
    def __init__(self, off_weight=0.5, rpi_enabled=True):
        super().__init__(off_weight=off_weight, rpi_enabled=rpi_enabled)

    def get_model_code(self) -> str:
        return "v2b"

    def get_off_yards_per_play(self, posteam: Team, play_type: str, situation: tuple[int, int, int]) -> float:
        down, __, __, distance_category, redzone = situation
        team_rates = self.home_team.get_team_rates() if posteam == self.home_team else self.away_team.get_team_rates()
        team_rates_data = team_rates.get_data_for_situation(down, distance_category, redzone)
        fallback_team_rates_data = team_rates.get_data_for_situation(None, None, None)

        raw_off_yards_per_play = 0
        if play_type == "pass":
            sampled_yards_per_completion = posteam.sample_offensive_passing_play()
            if (pd.notna(team_rates_data.yards_per_completion)):
                raw_off_yards_per_play = (team_rates_data.yards_per_completion + sampled_yards_per_completion) / 2
            else:
                raw_off_yards_per_play = (sampled_yards_per_completion + fallback_team_rates_data.yards_per_completion) / 2
        else:
            sampled_rush_yards_per_carry = posteam.sample_offensive_rushing_play()
            if (pd.notna(team_rates_data.rush_yards_per_carry)):
                raw_off_yards_per_play = (team_rates_data.rush_yards_per_carry + sampled_rush_yards_per_carry) / 2
            else:
                raw_off_yards_per_play = (sampled_rush_yards_per_carry + fallback_team_rates_data.rush_yards_per_carry) / 2

        return self._bias_off_value(raw_off_yards_per_play, posteam)

    def get_def_yards_per_play(self, posteam: Team, play_type: str, situation: tuple[int, int, int]) -> float:
        down, __, __, distance_category, redzone = situation
        team_rates = self.home_team.get_team_rates() if posteam == self.home_team else self.away_team.get_team_rates()
        team_rates_data = team_rates.get_data_for_situation(down, distance_category, redzone)
        fallback_team_rates_data = team_rates.get_data_for_situation(None, None, None)

        raw_def_yards_per_play = 0
        if play_type == "pass":
            sampled_yards_allowed_per_completion = posteam.sample_defensive_passing_play()
            if (pd.notna(team_rates_data.yards_allowed_per_completion)):
                raw_def_yards_per_play = (team_rates_data.yards_allowed_per_completion + sampled_yards_allowed_per_completion) / 2
            else:
                raw_def_yards_per_play = (sampled_yards_allowed_per_completion + fallback_team_rates_data.yards_allowed_per_completion) / 2
        else:
            sampled_rush_yards_allowed_per_carry = posteam.sample_defensive_rushing_play()
            if (pd.notna(team_rates_data.rush_yards_per_carry_allowed)):
                raw_def_yards_per_play = (team_rates_data.rush_yards_per_carry_allowed + sampled_rush_yards_allowed_per_carry) / 2
            else:
                raw_def_yards_per_play = (sampled_rush_yards_allowed_per_carry + fallback_team_rates_data.rush_yards_per_carry_allowed) / 2

        return self._bias_def_value(raw_def_yards_per_play, posteam)