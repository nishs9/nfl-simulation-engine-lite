from abc import ABC, abstractmethod
from functools import lru_cache

class AbstractGameModel(ABC):

    def __init__(self, off_weight=0.55):
        self.off_weight = off_weight
        self.def_weight = 1 - off_weight

    @abstractmethod
    def resolve_play(self, game_state: dict) -> dict:
        pass

    @lru_cache(maxsize=1000)
    def get_weighted_average(self, off_stat: float, def_stat: float) -> float:
        return (off_stat * self.off_weight) + (def_stat * self.def_weight)