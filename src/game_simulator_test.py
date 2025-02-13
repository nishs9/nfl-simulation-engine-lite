import pytest
import random
from typing import Tuple
from game_engine.game_engine import GameEngine
from game_model.prototype_game_model import PrototypeGameModel
from game_model.game_model_v1 import GameModel_V1
from game_model.game_model_v1a import GameModel_V1a
from game_model.game_model_v1b import GameModel_V1b
from team.team import Team

teams = ["ARI","ATL","BAL","BUF","CAR","CHI","CIN","CLE","DAL",
        "DEN","DET","GB","HOU","IND","JAX","KC","LA","LAC",
        "LV","MIA","MIN","NE","NO","NYG","NYJ","PHI","PIT",
        "SEA","SF","TB","TEN","WAS"]

def test_game_engine_initialization():
    home_team_abbrev, away_team_abbrev = get_random_teams()
    home_team, away_team = init_teams_for_test(home_team_abbrev, away_team_abbrev)
    
    game_engine = GameEngine(home_team, away_team)

    assert game_engine.home_team.name == home_team_abbrev
    assert game_engine.away_team.name == away_team_abbrev
    assert game_engine.game_state is not None
    assert game_engine.game_model is not None

def test_game_state_initialization():
    home_team_abbrev, away_team_abbrev = get_random_teams()
    home_team, away_team = init_teams_for_test(home_team_abbrev, away_team_abbrev)
    
    game_engine = GameEngine(home_team, away_team)

    assert game_engine.game_state["quarter"] == 1
    assert game_engine.game_state["game_seconds_remaining"] == 3600
    assert game_engine.game_state["quarter_seconds_remaining"] == 900
    assert game_engine.game_state["possession_team"] == home_team
    assert game_engine.game_state["defense_team"] == away_team
    assert game_engine.game_state["yardline"] == 75
    assert game_engine.game_state["down"] == 1
    assert game_engine.game_state["distance"] == 10
    assert game_engine.game_state["score"][home_team.name] == 0
    assert game_engine.game_state["score"][away_team.name] == 0
    assert game_engine.game_state["play_log"] == []

def test_turnover_simulation():
    home_team_abbrev, away_team_abbrev = get_random_teams()
    home_team, away_team = init_teams_for_test(home_team_abbrev, away_team_abbrev)

    expected_yardline = 34
    expected_down = 1
    expected_distance = 10
    expected_posteam = away_team.name
    expected_defteam = home_team.name

    # Create an initial mock game state
    mock_game_state = {
        "quarter": 1,
        "game_seconds_remaining": 3600,
        "quarter_seconds_remaining": 900, 
        "possession_team": home_team, 
        "defense_team": away_team,
        "yardline": 100-expected_yardline, 
        "down": 2,
        "distance": 5,
        "score": {home_team.name: 0, away_team.name: 0},
        "play_log": [],
    }

    game_engine = GameEngine(home_team, away_team)
    game_engine.game_state = mock_game_state
    game_engine.simulate_turnover()

    assert game_engine.game_state["yardline"] == expected_yardline
    assert game_engine.game_state["down"] == expected_down
    assert game_engine.game_state["distance"] == expected_distance
    assert game_engine.game_state["possession_team"].name == expected_posteam
    assert game_engine.game_state["defense_team"].name == expected_defteam

def test_punt_simulation():
    home_team_abbrev, away_team_abbrev = get_random_teams()
    home_team, away_team = init_teams_for_test(home_team_abbrev, away_team_abbrev)

    expected_yardline = 60
    expected_down = 1
    expected_distance = 10
    expected_posteam = away_team.name
    expected_defteam = home_team.name

    mock_play_result = { "yards_gained" : 0 }

    # Create an initial mock game state
    mock_game_state = {
        "quarter": 1,
        "game_seconds_remaining": 3600,
        "quarter_seconds_remaining": 900, 
        "possession_team": home_team, 
        "defense_team": away_team,
        "yardline": 100 - expected_yardline, 
        "down": 2,
        "distance": 5,
        "score": {home_team.name: 0, away_team.name: 0},
        "play_log": [],
    }

    game_engine = GameEngine(home_team, away_team)
    game_engine.game_state = mock_game_state
    game_engine.simulate_punt(mock_play_result)

    assert game_engine.game_state["yardline"] == expected_yardline
    assert game_engine.game_state["down"] == expected_down
    assert game_engine.game_state["distance"] == expected_distance
    assert game_engine.game_state["possession_team"].name == expected_posteam
    assert game_engine.game_state["defense_team"].name == expected_defteam

def test_single_game_simulation_with_prototype_model():
    try:
        home_team_abbrev, away_team_abbrev = get_random_teams()
        home_team, away_team = init_teams_for_test(home_team_abbrev, away_team_abbrev)
        game_engine = GameEngine(home_team, away_team, game_model=PrototypeGameModel())
        game_summary = game_engine.run_simulation(test_mode=True)

        # Verify that the team objects are being instantiated only with necessary
        # attributes for the prototype model
        assert home_team.off_passing_distribution is None
        assert home_team.off_rushing_distribution is None
        assert home_team.def_passing_distribution is None
        assert home_team.def_rushing_distribution is None
        assert home_team.enhanced_off_passing_dist is None
        assert home_team.enhanced_def_passing_dist is None

        assert away_team.off_passing_distribution is None
        assert away_team.off_rushing_distribution is None
        assert away_team.def_passing_distribution is None
        assert away_team.def_rushing_distribution is None
        assert away_team.enhanced_off_passing_dist is None
        assert away_team.enhanced_def_passing_dist is None

        assert game_engine.game_state is not None
        assert game_engine.game_state["quarter"] == 4
        assert game_engine.game_state["game_seconds_remaining"] <= 0
        assert game_engine.game_state["quarter_seconds_remaining"] <= 0

        assert game_summary is not None
        assert game_summary["final_score"][home_team.name] >= 0
        assert game_summary["final_score"][away_team.name] >= 0
        assert game_summary["num_plays_in_game"] > 0
        assert len(game_summary["play_log"]) == game_summary["num_plays_in_game"]
    except Exception as e:
        pytest.fail("Single game simulation failed due to an unexpected exception: " + str(e))

def test_single_game_simulation_with_V1_model():
    try:
        home_team_abbrev, away_team_abbrev = get_random_teams()
        home_team, away_team = init_teams_for_test(home_team_abbrev, away_team_abbrev)
        game_engine = GameEngine(home_team, away_team, game_model=GameModel_V1())
        game_summary = game_engine.run_simulation(test_mode=True)

        # Verify that the team objects are being instantiated only with necessary
        # attributes for the V1 model
        assert home_team.off_passing_distribution is not None
        assert home_team.off_passing_distribution.rvs() >= 0

        assert home_team.off_rushing_distribution is not None
        assert home_team.off_rushing_distribution.rvs() >= 0

        assert home_team.def_passing_distribution is not None
        assert home_team.def_passing_distribution.rvs() >= 0

        assert home_team.def_rushing_distribution is not None
        assert home_team.def_rushing_distribution.rvs() >= 0

        assert home_team.enhanced_off_passing_dist is None
        assert home_team.enhanced_def_passing_dist is None

        assert away_team.off_passing_distribution is not None
        assert away_team.off_passing_distribution.rvs() >= 0

        assert away_team.off_rushing_distribution is not None
        assert away_team.off_rushing_distribution.rvs() >= 0

        assert away_team.def_passing_distribution is not None
        assert away_team.def_passing_distribution.rvs() >= 0

        assert away_team.def_rushing_distribution is not None
        assert away_team.def_rushing_distribution.rvs() >= 0

        assert away_team.enhanced_off_passing_dist is None
        assert away_team.enhanced_def_passing_dist is None

        assert game_engine.game_state is not None
        assert game_engine.game_state["quarter"] == 4
        assert game_engine.game_state["game_seconds_remaining"] <= 0
        assert game_engine.game_state["quarter_seconds_remaining"] <= 0

        assert game_summary is not None
        assert game_summary["final_score"][home_team.name] >= 0
        assert game_summary["final_score"][away_team.name] >= 0
        assert game_summary["num_plays_in_game"] > 0
        assert len(game_summary["play_log"]) == game_summary["num_plays_in_game"]
    except Exception as e:
        pytest.fail("Single game simulation failed due to an unexpected exception: " + str(e))

def test_single_game_simulation_with_V1a_model():
    try:
        home_team_abbrev, away_team_abbrev = get_random_teams()
        home_team, away_team = init_teams_for_test(home_team_abbrev, away_team_abbrev)
        game_engine = GameEngine(home_team, away_team, game_model=GameModel_V1a())
        game_summary = game_engine.run_simulation(test_mode=True)

        # Verify that the team objects are being instantiated only with necessary
        # attributes for the V1a model
        assert home_team.off_passing_distribution is not None
        assert home_team.off_passing_distribution.rvs() >= 0

        assert home_team.off_rushing_distribution is not None
        assert home_team.off_rushing_distribution.rvs() >= 0

        assert home_team.def_passing_distribution is not None
        assert home_team.def_passing_distribution.rvs() >= 0

        assert home_team.def_rushing_distribution is not None
        assert home_team.def_rushing_distribution.rvs() >= 0

        assert home_team.enhanced_off_passing_dist is None
        assert home_team.enhanced_def_passing_dist is None

        assert away_team.off_passing_distribution is not None
        assert away_team.off_passing_distribution.rvs() >= 0

        assert away_team.off_rushing_distribution is not None
        assert away_team.off_rushing_distribution.rvs() >= 0

        assert away_team.def_passing_distribution is not None
        assert away_team.def_passing_distribution.rvs() >= 0

        assert away_team.def_rushing_distribution is not None
        assert away_team.def_rushing_distribution.rvs() >= 0

        assert away_team.enhanced_off_passing_dist is None
        assert away_team.enhanced_def_passing_dist is None

        assert game_engine.game_state is not None
        assert game_engine.game_state["quarter"] == 4
        assert game_engine.game_state["game_seconds_remaining"] <= 0
        assert game_engine.game_state["quarter_seconds_remaining"] <= 0

        assert game_summary is not None
        assert game_summary["final_score"][home_team.name] >= 0
        assert game_summary["final_score"][away_team.name] >= 0
        assert game_summary["num_plays_in_game"] > 0
        assert len(game_summary["play_log"]) == game_summary["num_plays_in_game"]
    except Exception as e:
        pytest.fail("Single game simulation failed due to an unexpected exception: " + str(e))

def test_single_game_simulation_with_V1b_model():
    try:
        home_team_abbrev, away_team_abbrev = get_random_teams()
        home_team, away_team = init_teams_for_test(home_team_abbrev, away_team_abbrev)
        game_engine = GameEngine(home_team, away_team, game_model=GameModel_V1b())
        game_summary = game_engine.run_simulation(test_mode=True)

        # Verify that the team objects are being instantiated only with necessary
        # attributes for the v1b model
        assert home_team.off_passing_distribution is None
        assert home_team.def_passing_distribution is None

        assert home_team.off_rushing_distribution is not None
        assert home_team.off_rushing_distribution.rvs() >= 0

        assert home_team.def_rushing_distribution is not None
        assert home_team.def_rushing_distribution.rvs() >= 0

        assert home_team.enhanced_off_passing_dist is not None
        assert home_team.enhanced_off_passing_dist.rvs() >= 0
        
        assert home_team.enhanced_def_passing_dist is not None
        assert home_team.enhanced_def_passing_dist.rvs() >= 0

        assert away_team.off_passing_distribution is None
        assert away_team.def_passing_distribution is None

        assert away_team.off_rushing_distribution is not None
        assert away_team.off_rushing_distribution.rvs() >= 0

        assert away_team.def_rushing_distribution is not None
        assert away_team.def_rushing_distribution.rvs() >= 0

        assert away_team.enhanced_off_passing_dist is not None
        assert away_team.enhanced_off_passing_dist.rvs() >= 0
        
        assert away_team.enhanced_def_passing_dist is not None
        assert away_team.enhanced_def_passing_dist.rvs() >= 0

        assert game_engine.game_state is not None
        assert game_engine.game_state["quarter"] == 4
        assert game_engine.game_state["game_seconds_remaining"] <= 0
        assert game_engine.game_state["quarter_seconds_remaining"] <= 0

        assert game_summary is not None
        assert game_summary["final_score"][home_team.name] >= 0
        assert game_summary["final_score"][away_team.name] >= 0
        assert game_summary["num_plays_in_game"] > 0
        assert len(game_summary["play_log"]) == game_summary["num_plays_in_game"]
    except Exception as e:
        pytest.fail("Single game simulation failed due to an unexpected exception: " + str(e))

###########################################################################################
# Helper functions
def get_random_teams() -> Tuple[str, str]:
    home_team_idx = random.randint(0, len(teams)-1)
    away_team_idx = random.randint(0, len(teams)-1)

    home_team_abbrev = teams[home_team_idx]
    away_team_abbrev = teams[away_team_idx]
    return home_team_abbrev, away_team_abbrev

def init_teams_for_test(home_team_abbrev: str, away_team_abbrev: str) -> Tuple[object, object]:
    home_team_stats = {
        "team": home_team_abbrev,
        "games_played": 16,
        "pass_completion_rate": 0.65,
        "yards_per_completion": 12.5,
        "rush_yards_per_carry": 4.5,
        "scoring_efficiency": 0.35,
        "turnover_rate": 0.1,
        "forced_turnover_rate": 0.15,
        "redzone_efficiency": 0.75,
        "run_rate": 0.45,
        "pass_rate": 0.55,
        "sacks_allowed_rate": 0.05,
        "sacks_made_rate": 0.1,
        "sack_yards_allowed": 5.0,
        "sack_yards_inflicted": 7.5,
        "field_goal_success_rate": 0.85,
        "pass_completion_rate_allowed": 0.6,
        "yards_allowed_per_completion": 11.5,
        "rush_yards_per_carry_allowed": 4.0,
        "off_pass_yards_per_play_mean": 10.5,
        "off_pass_yards_per_play_variance": 80.2,
        "off_rush_yards_per_play_mean": 5.5,
        "off_rush_yards_per_play_variance": 40.2,
        "def_pass_yards_per_play_mean": 11.5,
        "def_pass_yards_per_play_variance": 90.2,
        "def_rush_yards_per_play_mean": 4.5,
        "def_rush_yards_per_play_variance": 50.2,
        "off_air_yards_per_attempt":8.9,
        "def_air_yards_per_attempt":9.1,
        "off_yac_per_completion":4.5,
        "def_yac_per_completion":4.3
    }

    away_team_stats = home_team_stats = {
        "team": away_team_abbrev,
        "games_played": 16,
        "pass_completion_rate": 0.59,
        "yards_per_completion": 10.5,
        "rush_yards_per_carry": 6.5,
        "scoring_efficiency": 0.35,
        "turnover_rate": 0.02,
        "forced_turnover_rate": 0.17,
        "redzone_efficiency": 0.87,
        "run_rate": 0.40,
        "pass_rate": 0.60,
        "sacks_allowed_rate": 0.06,
        "sacks_made_rate": 0.07,
        "sack_yards_allowed": 5.0,
        "sack_yards_inflicted": 7.5,
        "field_goal_success_rate": 0.85,
        "pass_completion_rate_allowed": 0.6,
        "yards_allowed_per_completion": 11.5,
        "rush_yards_per_carry_allowed": 4.0,
        "off_pass_yards_per_play_mean": 15.5,
        "off_pass_yards_per_play_variance": 86.2,
        "off_rush_yards_per_play_mean": 4.5,
        "off_rush_yards_per_play_variance": 43.2,
        "def_pass_yards_per_play_mean": 13.5,
        "def_pass_yards_per_play_variance": 81.21,
        "def_rush_yards_per_play_mean": 5.5,
        "def_rush_yards_per_play_variance": 59.78,
        "off_air_yards_per_attempt":10.2,
        "def_air_yards_per_attempt":8.3,
        "off_yac_per_completion":3.5,
        "def_yac_per_completion":5.8
    }

    home_team = Team(home_team_abbrev, home_team_stats)
    away_team = Team(away_team_abbrev, away_team_stats)

    return home_team, away_team