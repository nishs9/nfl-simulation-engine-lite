from nfl_simulation_engine_lite.game_model.game_model_v2 import GameModel_V2
from nfl_simulation_engine_lite.team.team import Team
import pandas as pd

class GameModel_V2b(GameModel_V2):
    def __init__(self, off_weight=0.525, rpi_enabled=True):
        super().__init__(off_weight=off_weight, rpi_enabled=rpi_enabled)

    def get_model_code(self) -> str:
        return "v2b"