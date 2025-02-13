import pandas as pd

def generate_team_passing_stats_summary(team: str, df: pd.DataFrame) -> dict:
    passing_df = df[(df["play_type"] == "pass") & (df["posteam"] == team)]
    passing_df["agg_pass_yards"] = passing_df["yards_gained"].cumsum()
    team_pass_stats_df = passing_df[["game_time_elapsed", "agg_pass_yards"]]
    return team_pass_stats_df.to_dict(orient="records")

def generate_team_rushing_stats_summary(team: str, df: pd.DataFrame) -> dict:
    rushing_df = df[(df["play_type"] == "run") & (df["posteam"] == team)]
    rushing_df["agg_rush_yards"] = rushing_df["yards_gained"].cumsum()
    team_rush_stats_df = rushing_df[["game_time_elapsed", "agg_rush_yards"]]
    return team_rush_stats_df.to_dict(orient="records")

def generate_team_scoring_summary(team: str, df: pd.DataFrame) -> dict:
    posteam_df = df[df["posteam"] == team]
    team_scoring_df = posteam_df[["game_time_elapsed", "posteam_score"]]
    return team_scoring_df.to_dict(orient="records")