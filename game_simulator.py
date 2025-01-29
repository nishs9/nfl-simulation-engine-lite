import random
import pandas as pd
import math
import os
import warnings
import csv
import requests
import sqlite3

def initialize_teams_for_game_engine(home_team_abbrev: str, away_team_abbrev: str) -> tuple:
    db_conn = sqlite3.connect("nfl_stats.db")
    
    home_team_stats_df = pd.read_sql(f"SELECT * FROM sim_engine_team_stats_2024 WHERE team = '{home_team_abbrev}'", db_conn)
    home_team_stats = home_team_stats_df.iloc[0].to_dict()

    away_team_stats_df = pd.read_sql(f"SELECT * FROM sim_engine_team_stats_2024 WHERE team = '{away_team_abbrev}'", db_conn)
    away_team_stats = away_team_stats_df.iloc[0].to_dict()
    
    for key in home_team_stats.keys():
        print(key)
    

if __name__ == "__main__":
    print("Running game simulator orchestrator")
    initialize_teams_for_game_engine("DAL", "PHI")