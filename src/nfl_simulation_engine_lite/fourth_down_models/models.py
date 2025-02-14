import joblib
import os

v1_model_path = os.path.join(os.path.dirname(__file__), "v1_4th_down_playcall_model.pkl")
v2_model_path = os.path.join(os.path.dirname(__file__), "v2_4th_down_playcall_model.pkl")
v2a_model_path = os.path.join(os.path.dirname(__file__), "v2a_4th_down_playcall_model.pkl")

v1_fdm = joblib.load(v1_model_path)
v2_fdm = joblib.load(v2_model_path)
v2a_fdm = joblib.load(v2a_model_path)