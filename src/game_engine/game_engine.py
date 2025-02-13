from game_model.prototype_game_model import PrototypeGameModel
from team.Team import Team
import pandas as pd

class GameEngine:
    def __init__(self, home_team: Team, away_team: Team, game_model=PrototypeGameModel()):
        self.home_team = home_team
        self.away_team = away_team
        self.game_state = self.initialize_game_state()
        self.initialize_game_state()
        self.game_model = game_model
        home_team.setup_stat_distributions(game_model.get_model_code())
        away_team.setup_stat_distributions(game_model.get_model_code())

    def initialize_game_state(self) -> dict:
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
    
    def simulate_play(self) -> dict:
        play_result = self.game_model.resolve_play(self.game_state)
        play_result["game_seconds_remaining"] = self.game_state["game_seconds_remaining"]
        play_result["yardline"] = self.game_state["yardline"]
        play_result["down"] = self.game_state["down"]
        play_result["distance"] = self.game_state["distance"]
        play_result["score"] = self.game_state["score"].copy()
        play_result["posteam_score"] = self.game_state["score"][self.game_state["possession_team"].name]
        return play_result
    
    def update_game_state(self, play_result: dict) -> bool:
        # Update game state based on play result
        # Update yardline, down, distance, score, time remaining, etc.
        # Append play result to play log
        self.game_state["quarter_seconds_remaining"] -= play_result["time_elapsed"]
        self.game_state["game_seconds_remaining"] -= play_result["time_elapsed"]

        if (play_result["turnover"]):
            self.simulate_turnover()
        elif (play_result["play_type"] == "punt"):
            self.simulate_punt(play_result)
        elif (play_result["play_type"] == "field_goal"):
            self.simulate_field_goal(play_result)
        else:
            self.game_state["yardline"] -= play_result["yards_gained"]

            if (play_result["yards_gained"] >= self.game_state["distance"]): # Gained a first down
                self.game_state["down"] = 1
                self.game_state["distance"] = 10
            elif (play_result["yards_gained"] < self.game_state["distance"] and self.game_state["down"] == 4): # Turnover on downs
                self.switch_possession()
            else:
                self.game_state["down"] += 1
                self.game_state["distance"] -= play_result["yards_gained"]

            if (self.game_state["yardline"] <= 0): # Touchdown
                self.game_state["score"][self.game_state["possession_team"].name] += 7
                self.switch_possession()
                self.game_state["yardline"] = 75
                self.game_state["down"] = 1
                self.game_state["distance"] = 10
                play_result["touchdown"] = True
            elif (self.game_state["yardline"] > 100): # Safety
                self.game_state["score"][self.game_state["defense_team"].name] += 2
                self.switch_possession()
                self.game_state["yardline"] = 60 # Since free kicks typically don't travel as far as kickoffs
                self.game_state["down"] = 1
                self.game_state["distance"] = 10

        self.game_state["play_log"].append(play_result)

        if (self.game_state["quarter_seconds_remaining"] <= 0 and self.game_state["quarter"] not in [2, 4]):
            self.game_state["quarter"] += 1
            self.game_state["quarter_seconds_remaining"] = 900
            return False
        elif (self.game_state["quarter_seconds_remaining"] <= 0 and self.game_state["quarter"] == 2):
            self.handle_halftime()
            return False
        elif (self.game_state["quarter_seconds_remaining"] <= 0 and self.game_state["quarter"] == 4):
            self.game_state["play_log"].append(play_result)
            return True
        
    def simulate_turnover(self):
        self.switch_possession()
        self.game_state["yardline"] = 100 - self.game_state["yardline"]
        self.game_state["down"] = 1
        self.game_state["distance"] = 10

    def simulate_punt(self, play_result: dict):
        self.switch_possession()
        self.game_state["yardline"] -= play_result["yards_gained"]
        if (self.game_state["yardline"] < 0): # Handle touchbacks
            self.game_state["yardline"] = 25
        self.game_state["yardline"] = 100 - self.game_state["yardline"]
        self.game_state["down"] = 1
        self.game_state["distance"] = 10

    def simulate_field_goal(self, play_result: dict):
        if (play_result["field_goal_made"]):
            self.game_state["score"][self.game_state["possession_team"].name] += 3
        self.switch_possession()
        self.game_state["yardline"] = 75
        self.game_state["down"] = 1
        self.game_state["distance"] = 10

    def switch_possession(self):
        if (self.game_state["possession_team"] == self.home_team):
            self.game_state["possession_team"] = self.away_team
            self.game_state["defense_team"] = self.home_team
        else:
            self.game_state["possession_team"] = self.home_team
            self.game_state["defense_team"] = self.away_team
    
    def handle_halftime(self):
        self.game_state["quarter"] += 1
        self.game_state["quarter_seconds_remaining"] = 900
        self.game_state["possession_team"] = self.away_team
        self.game_state["defense_team"] = self.home_team
        self.game_state["yardline"] = 75
        self.game_state["down"] = 1
        self.game_state["distance"] = 10

    def run_simulation(self, test_mode=False) -> dict:
        while True:
            play_result = self.simulate_play()
            game_over = self.update_game_state(play_result)
            if game_over:
                break
        return self.get_game_summary(test_mode)

    def get_game_summary(self, test_mode: bool) -> dict:
        # create play log dataframe and save it to a csv file
        play_log_df = pd.DataFrame(self.game_state["play_log"])

        home_team_df = play_log_df[play_log_df["posteam"] == self.home_team.name]
        away_team_df = play_log_df[play_log_df["posteam"] == self.away_team.name]

        game_summary_dict = {
            "final_score": self.game_state["score"],
            "num_plays_in_game": len(self.game_state["play_log"]),
            "play_log": self.game_state["play_log"],
            self.home_team.name: self.generate_team_stats_summary(self.home_team.name, home_team_df),
            self.away_team.name: self.generate_team_stats_summary(self.away_team.name, away_team_df)
        }

        if (not test_mode):
            play_log_df.to_csv(f"../simulation_logs/{self.home_team.name}_{self.away_team.name}_play_log.csv", index=True)
            home_team_stats_df = pd.DataFrame([game_summary_dict[self.home_team.name]])
            away_team_stats_df = pd.DataFrame([game_summary_dict[self.away_team.name]])
            team_stats_df = pd.concat([home_team_stats_df, away_team_stats_df])
            team_stats_df.to_csv(f"../simulation_logs/{self.home_team.name}_{self.away_team.name}_team_stats.csv", index=False)

        return game_summary_dict
    
    def generate_team_stats_summary(self, team_name: str, team_df: pd.DataFrame) -> dict:
        team_run_df = team_df[team_df["play_type"] == "run"]
        team_pass_df = team_df[team_df["play_type"] == "pass"]
        team_fg_df = team_df[team_df["play_type"] == "field_goal"]
        total_plays = team_df["play_type"].count()
        total_run_plays = team_run_df["play_type"].count()
        team_rush_yards = team_run_df["yards_gained"].sum()
        team_rush_tds = team_run_df[team_run_df["touchdown"] == True]["touchdown"].count()
        total_pass_plays = team_pass_df["play_type"].count()
        team_pass_cmps = team_pass_df[team_pass_df["yards_gained"] > 0]["yards_gained"].count()
        team_pass_yards = team_pass_df["yards_gained"].sum()
        team_pass_tds = team_pass_df[team_pass_df["touchdown"] == True]["touchdown"].count()
        team_total_turnovers = team_df[team_df["turnover"] == True]["turnover"].count()
        team_total_sacks = team_pass_df[team_pass_df["yards_gained"] < 0]["yards_gained"].count()
        team_fg_attempts = team_fg_df["play_type"].count()
        team_fg_makes = team_fg_df[team_fg_df["field_goal_made"] == True]["field_goal_made"].count()

        run_rate = round(total_run_plays / total_plays, 2)
        pass_rate = round(total_pass_plays / total_plays, 2)
        pass_cmp_rate = round(team_pass_cmps / total_pass_plays, 2)
        rush_yards_per_play = round(team_rush_yards / total_run_plays, 2)
        pass_yards_per_play = round(team_pass_yards / total_pass_plays, 2)
        fg_pct = None
        if (team_fg_attempts > 0):
            fg_pct = round(100 * (team_fg_makes / team_fg_attempts), 2)

        return {
            "team": team_df["posteam"].iloc[0],
            "score": self.game_state["score"][team_name],
            "run_rate": run_rate,
            "pass_rate": pass_rate,
            "pass_cmp_rate": pass_cmp_rate,
            "pass_yards": team_pass_yards,
            "passing_tds": team_pass_tds,
            "sacks_allowed": team_total_sacks,
            "pass_yards_per_play": pass_yards_per_play,
            "rushing_attempts": total_run_plays,
            "rushing_yards": team_rush_yards,
            "rushing_tds": team_rush_tds,
            "rush_yards_per_play": rush_yards_per_play,
            "total_turnovers": team_total_turnovers,
            "fg_pct": fg_pct
        }