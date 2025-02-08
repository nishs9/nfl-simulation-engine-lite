from game_model.PrototypeGameModel import PrototypeGameModel
import team.TeamFactory as TeamFactory
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
    home_team = TeamFactory.initialize_team(home_team_abbrev, db_conn)
    away_team = TeamFactory.initialize_team(away_team_abbrev, db_conn) 
    print(home_team.get_stats())
    db_conn.close()
    return (home_team, away_team)

if __name__ == "__main__":
    print("Running game simulator orchestrator")
    initialize_teams_for_game_engine("DAL", "PHI")