from game_model.PrototypeGameModel import PrototypeGameModel
from team.Team import Team
import pandas as pd

class GameEngine:
    def __init__(self, home_team: Team, away_team: Team, game_model=PrototypeGameModel()):
        self.home_team = home_team
        self.away_team = away_team
        self.initialize_game_state()
        self.game_model = game_model
        home_team.setup_stat_distributions(game_model.get_model_code())
        away_team.setup_stat_distributions(game_model.get_model_code())

    def _initialize_game_state(self) -> dict:
        return {
            "quarter": 1,
            "game_seconds_remaining": 3600,
            "quarter_seconds_remaining": 900, 
            "possession_team": self.home_team, 
            "defense_team": self.away_team,
            "yardline": 75, 
            "down": 1,
            "distance": 10,
            "score": {self.home_team.name: 0, self.away_team.name: 0},
            "play_log": [],
        }