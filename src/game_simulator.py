from game_model.PrototypeGameModel import PrototypeGameModel
from game_engine.GameEngine import GameEngine
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
    db_conn.close()
    return home_team, away_team

def run_single_simulation(home_team_abbrev: str, away_team_abbrev:str, game_model=PrototypeGameModel(), print_debug_info=False) -> dict:
    home_team, away_team = initialize_teams_for_game_engine(home_team_abbrev, away_team_abbrev)
    game_engine = GameEngine(home_team, away_team, game_model)
    game_summary = game_engine.run_simulation()
    if print_debug_info:
        print("Number of plays:", game_summary["num_plays_in_game"])
        for play in game_summary["play_log"]:
            print(play)
            print("\n")
    return game_summary

if __name__ == "__main__":
    home_team = "ATL"
    away_team = "JAX"
    print(run_single_simulation(home_team, away_team, print_debug_info=True))