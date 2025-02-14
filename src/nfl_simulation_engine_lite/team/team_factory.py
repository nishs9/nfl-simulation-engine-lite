from nfl_simulation_engine_lite.team.team import Team
from nfl_simulation_engine_lite.team.team_stats import TeamStats
from sqlite3 import Connection
import pandas as pd

def initialize_team(team_abbrev: str, db_conn: Connection) -> Team:
    team_stats_df = pd.read_sql(f"SELECT * FROM sim_engine_team_stats_2024 WHERE team = '{team_abbrev}'", db_conn)
    team_stats = initialize_team_stats(team_stats_df.iloc[0].to_dict())
    team = Team(team_abbrev, team_stats)
    return team

def initialize_team_stats(team_stats_dict: dict) -> TeamStats:
    team_stats = TeamStats()
    team_stats.team = team_stats_dict["team"]
    team_stats.games_played = team_stats_dict["games_played"]
    team_stats.pass_completion_rate = team_stats_dict["pass_completion_rate"]
    team_stats.yards_per_completion = team_stats_dict["yards_per_completion"]
    team_stats.rush_yards_per_carry = team_stats_dict["rush_yards_per_carry"]
    team_stats.turnover_rate = team_stats_dict["turnover_rate"]
    team_stats.forced_turnover_rate = team_stats_dict["forced_turnover_rate"]
    team_stats.run_rate = team_stats_dict["run_rate"]
    team_stats.pass_rate = team_stats_dict["pass_rate"]
    team_stats.sacks_allowed_rate = team_stats_dict["sacks_allowed_rate"]
    team_stats.sack_yards_allowed = team_stats_dict["sack_yards_allowed"]
    team_stats.sacks_made_rate = team_stats_dict["sacks_made_rate"]
    team_stats.sack_yards_inflicted = team_stats_dict["sack_yards_inflicted"]
    team_stats.field_goal_success_rate = team_stats_dict["field_goal_success_rate"]
    team_stats.pass_completion_rate_allowed = team_stats_dict["pass_completion_rate_allowed"]
    team_stats.yards_allowed_per_completion = team_stats_dict["yards_allowed_per_completion"]
    team_stats.rush_yards_per_carry_allowed = team_stats_dict["rush_yards_per_carry_allowed"]
    team_stats.off_pass_yards_per_play_mean = team_stats_dict["off_pass_yards_per_play_mean"]
    team_stats.off_pass_yards_per_play_variance = team_stats_dict["off_pass_yards_per_play_variance"]
    team_stats.off_rush_yards_per_play_mean = team_stats_dict["off_rush_yards_per_play_mean"]
    team_stats.off_rush_yards_per_play_variance = team_stats_dict["off_rush_yards_per_play_variance"]
    team_stats.def_pass_yards_per_play_mean = team_stats_dict["def_pass_yards_per_play_mean"]
    team_stats.def_pass_yards_per_play_variance = team_stats_dict["def_pass_yards_per_play_variance"]
    team_stats.def_rush_yards_per_play_mean = team_stats_dict["def_rush_yards_per_play_mean"]
    team_stats.def_rush_yards_per_play_variance = team_stats_dict["def_rush_yards_per_play_variance"]
    team_stats.off_air_yards_per_attempt = team_stats_dict["off_air_yards_per_attempt"]
    team_stats.def_air_yards_per_attempt = team_stats_dict["def_air_yards_per_attempt"]
    team_stats.off_yac_per_completion = team_stats_dict["off_yac_per_completion"]
    team_stats.def_yac_per_completion = team_stats_dict["def_yac_per_completion"]
    return team_stats