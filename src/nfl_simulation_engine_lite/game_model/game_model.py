from abc import ABC, abstractmethod
from nfl_simulation_engine_lite.team.team import Team
from functools import lru_cache

class AbstractGameModel(ABC):

    def __init__(self, off_weight=0.55):
        self.off_weight = off_weight
        self.def_weight = 1 - off_weight
        self.home_team = None
        self.away_team = None

    @abstractmethod
    def resolve_play(self, game_state: dict) -> dict:
        pass

    @lru_cache(maxsize=1000)
    def get_weighted_average(self, off_stat: float, def_stat: float) -> float:
        return (off_stat * self.off_weight) + (def_stat * self.def_weight)

    def set_home_team(self, home_team: Team) -> None:
        self.home_team = home_team

    def get_home_team(self) -> Team:
        return self.home_team

    def set_away_team(self, away_team: Team) -> None:
        self.away_team = away_team

    def get_away_team(self) -> Team:
        return self.away_team