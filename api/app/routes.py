from flask import Blueprint, request, jsonify
from flask_limiter.util import get_remote_address
from nfl_simulation_engine_lite.game_simulator import run_multiple_simulations_with_statistics, run_multiple_simulations_multi_threaded
from nfl_simulation_engine_lite.game_model.game_model_factory import initialize_new_game_model_instance

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'message': 'Welcome to the NFL Simulation Engine Lite API!'
    })

@api_bp.route('/run-simulations', methods=['POST'])
def run_simulation():
    payload = request.get_json()
    home_team_abbrev = payload['home_team']
    away_team_abbrev = payload['away_team']
    num_simulations = int(payload['num_simulations'])
    game_model = payload['game_model']

    if not home_team_abbrev or not away_team_abbrev:
        return jsonify({'message': 'Please provide a home and away team'}), 400
    
    if not num_simulations:
        return jsonify({'message': 'Please provide the number of simulatiion iterations to be run'}), 400

    if not game_model:
        game_model = 'proto'

    game_model_instance = initialize_new_game_model_instance(game_model)
    results = run_multiple_simulations_multi_threaded(home_team_abbrev, away_team_abbrev, num_simulations, game_model_instance, num_workers=3, debug_mode=False)
    return jsonify(results)

@api_bp.route('/run-simulation-legacy', methods=['POST'])
def run_simulation_legacy():
    payload = request.get_json()
    home_team_abbrev = payload['home_team']
    away_team_abbrev = payload['away_team']
    num_simulations = int(payload['num_simulations'])
    game_model = payload['game_model']

    if not home_team_abbrev or not away_team_abbrev:
        return jsonify({'message': 'Please provide a home and away team'}), 400
    
    if not num_simulations:
        return jsonify({'message': 'Please provide the number of simulatiion iterations to be run'}), 400

    if not game_model:
        game_model = 'proto'

    game_model_instance = initialize_new_game_model_instance(game_model)
    results = run_multiple_simulations_with_statistics(home_team_abbrev, away_team_abbrev, num_simulations, game_model_instance, debug_mode=False)
    return jsonify(results)