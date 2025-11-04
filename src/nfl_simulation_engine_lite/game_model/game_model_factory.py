from nfl_simulation_engine_lite.game_model.game_model import AbstractGameModel
from nfl_simulation_engine_lite.game_model.prototype_game_model import PrototypeGameModel
from nfl_simulation_engine_lite.game_model.game_model_v1 import GameModel_V1
from nfl_simulation_engine_lite.game_model.game_model_v1a import GameModel_V1a
from nfl_simulation_engine_lite.game_model.game_model_v1b import GameModel_V1b
from nfl_simulation_engine_lite.game_model.game_model_v2 import GameModel_V2

def initialize_new_game_model_instance(model_code:str) -> AbstractGameModel:
    if model_code == "v1":
        return GameModel_V1()
    elif model_code == "v1a":
        return GameModel_V1a()
    elif model_code == "v1b":
        return GameModel_V1b()
    elif model_code == "v2":
        return GameModel_V2()
    else:
        return PrototypeGameModel()