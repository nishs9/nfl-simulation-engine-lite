from game_model.prototype_game_model import PrototypeGameModel
from game_model.game_model_v1 import GameModel_V1
from game_model.game_model_v1a import GameModel_V1a
from game_model.game_model_v1b import GameModel_V1b

def initialize_new_game_model_instance(model_code:str):
    if model_code == "v1":
        return GameModel_V1()
    elif model_code == "v1a":
        return GameModel_V1a()
    elif model_code == "v1b":
        return GameModel_V1b()
    else:
        return PrototypeGameModel()