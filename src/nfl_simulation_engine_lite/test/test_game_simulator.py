from nfl_simulation_engine_lite.db import db_conn
from nfl_simulation_engine_lite.game_engine.game_engine import GameEngine
from nfl_simulation_engine_lite.game_model.prototype_game_model import PrototypeGameModel
from nfl_simulation_engine_lite.game_model.game_model_v1 import GameModel_V1
from nfl_simulation_engine_lite.game_model.game_model_v1a import GameModel_V1a
from nfl_simulation_engine_lite.game_model.game_model_v1b import GameModel_V1b
from nfl_simulation_engine_lite.team.team import Team
from typing import Tuple
import nfl_simulation_engine_lite.team.team_factory as team_factory
import pytest
import random
import sqlite3

teams = ["ARI","ATL","BAL","BUF","CAR","CHI","CIN","CLE","DAL",
            "DEN","DET","GB","HOU","IND","JAX","KC","LA","LAC",
            "LV","MIA","MIN","NE","NO","NYG","NYJ","PHI","PIT",
            "SEA","SF","TB","TEN","WAS"]

class TestGameSimulator:
    def test_game_engine_initialization(self):
        home_team_abbrev, away_team_abbrev = self.get_random_teams()
        home_team, away_team = self.init_teams_for_test(home_team_abbrev, away_team_abbrev)
        
        game_engine = GameEngine(home_team, away_team)

        assert game_engine.home_team.name == home_team_abbrev
        assert game_engine.away_team.name == away_team_abbrev
        assert game_engine.game_state is not None
        assert game_engine.game_model is not None

    def test_game_state_initialization(self):
        home_team_abbrev, away_team_abbrev = self.get_random_teams()
        home_team, away_team = self.init_teams_for_test(home_team_abbrev, away_team_abbrev)
        
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

    def test_turnover_simulation(self):
        home_team_abbrev, away_team_abbrev = self.get_random_teams()
        home_team, away_team = self.init_teams_for_test(home_team_abbrev, away_team_abbrev)

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

    def test_punt_simulation(self):
        home_team_abbrev, away_team_abbrev = self.get_random_teams()
        home_team, away_team = self.init_teams_for_test(home_team_abbrev, away_team_abbrev)

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

    def test_single_game_simulation_with_prototype_model(self):
        try:
            home_team_abbrev, away_team_abbrev = self.get_random_teams()
            home_team, away_team = self.init_teams_for_test(home_team_abbrev, away_team_abbrev)

            game_engine = GameEngine(home_team, away_team, game_model=PrototypeGameModel())
            game_summary = game_engine.run_simulation(test_mode=True)

            # Verify that the team objects are being instantiated only with necessary
            # attributes for the prototype model
            assert home_team.off_passing_distribution is None
            assert home_team.off_rushing_distribution is None
            assert home_team.def_passing_distribution is None
            assert home_team.def_rushing_distribution is None

            assert away_team.off_passing_distribution is None
            assert away_team.off_rushing_distribution is None
            assert away_team.def_passing_distribution is None
            assert away_team.def_rushing_distribution is None

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

    def test_single_game_simulation_with_V1_model(self):
        try:
            home_team_abbrev, away_team_abbrev = self.get_random_teams()
            home_team, away_team = self.init_teams_for_test(home_team_abbrev, away_team_abbrev)
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

            assert away_team.off_passing_distribution is not None
            assert away_team.off_passing_distribution.rvs() >= 0

            assert away_team.off_rushing_distribution is not None
            assert away_team.off_rushing_distribution.rvs() >= 0

            assert away_team.def_passing_distribution is not None
            assert away_team.def_passing_distribution.rvs() >= 0

            assert away_team.def_rushing_distribution is not None
            assert away_team.def_rushing_distribution.rvs() >= 0

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

    def test_single_game_simulation_with_V1a_model(self):
        try:
            home_team_abbrev, away_team_abbrev = self.get_random_teams()
            home_team, away_team = self.init_teams_for_test(home_team_abbrev, away_team_abbrev)
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

            assert away_team.off_passing_distribution is not None
            assert away_team.off_passing_distribution.rvs() >= 0

            assert away_team.off_rushing_distribution is not None
            assert away_team.off_rushing_distribution.rvs() >= 0

            assert away_team.def_passing_distribution is not None
            assert away_team.def_passing_distribution.rvs() >= 0

            assert away_team.def_rushing_distribution is not None
            assert away_team.def_rushing_distribution.rvs() >= 0

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

    def test_single_game_simulation_with_V1b_model(self):
        try:
            home_team_abbrev, away_team_abbrev = self.get_random_teams()
            home_team, away_team = self.init_teams_for_test(home_team_abbrev, away_team_abbrev)
            game_engine = GameEngine(home_team, away_team, game_model=GameModel_V1b())
            game_summary = game_engine.run_simulation(test_mode=True)

            # Verify that the team objects are being instantiated only with necessary
            # attributes for the v1b model
            assert home_team.off_passing_distribution is None
            assert home_team.def_passing_distribution is None

            assert home_team.off_air_yards_distribution is not None
            assert home_team.off_air_yards_distribution.rvs() >= 0

            assert home_team.def_air_yards_allowed_distribution is not None
            assert home_team.def_air_yards_allowed_distribution.rvs() >= 0

            assert home_team.off_rushing_distribution is not None
            assert home_team.off_rushing_distribution.rvs() >= 0

            assert home_team.def_rushing_distribution is not None
            assert home_team.def_rushing_distribution.rvs() >= 0

            assert away_team.off_passing_distribution is None
            assert away_team.def_passing_distribution is None

            assert away_team.off_air_yards_distribution is not None
            assert away_team.off_air_yards_distribution.rvs() >= 0

            assert away_team.def_air_yards_allowed_distribution is not None
            assert away_team.def_air_yards_allowed_distribution.rvs() >= 0

            assert away_team.off_rushing_distribution is not None
            assert away_team.off_rushing_distribution.rvs() >= 0

            assert away_team.def_rushing_distribution is not None
            assert away_team.def_rushing_distribution.rvs() >= 0

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
    @staticmethod
    def get_random_teams() -> Tuple[str, str]:
        home_team_idx = random.randint(0, len(teams)-1)
        away_team_idx = random.randint(0, len(teams)-1)

        home_team_abbrev = teams[home_team_idx]
        away_team_abbrev = teams[away_team_idx]
        return home_team_abbrev, away_team_abbrev

    @staticmethod
    def init_teams_for_test(home_team_abbrev: str, away_team_abbrev: str) -> Tuple[Team, Team]:
        test_db_conn = db_conn.get_db_conn()
        home_team = team_factory.initialize_team(home_team_abbrev, test_db_conn)
        away_team = team_factory.initialize_team(away_team_abbrev, test_db_conn)
        test_db_conn.close()
        return home_team, away_team
    
    # @staticmethod
    # def get_test_db_conn() -> sqlite3.Connection:
    #     return sqlite3.connect("test_nfl_stats.db") 