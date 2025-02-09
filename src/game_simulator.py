from game_model.PrototypeGameModel import PrototypeGameModel
from game_engine.GameEngine import GameEngine
from team.Team import Team
from time import time
from tqdm import tqdm
import team.TeamFactory as TeamFactory
import random
import pandas as pd
import math
import os
import warnings
import csv
import requests
import sqlite3

warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

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

def run_multiple_simulations(home_team_abbrev: str, away_team_abbrev: str, num_simulations: int, game_model=PrototypeGameModel()):
    home_team, away_team = initialize_teams_for_game_engine(home_team_abbrev, away_team_abbrev)
    
    home_wins = 0
    i = 0
    print(f"Running {num_simulations} simulations of {home_team.name} vs. {away_team.name}.")
    with tqdm(total=num_simulations) as pbar:
        while i < num_simulations:
            game_engine = GameEngine(home_team, away_team, game_model)
            game_summary = game_engine.run_simulation()
            final_score = game_summary["final_score"]
            if final_score[home_team.name] > final_score[away_team.name]:
                home_wins += 1
            i += 1
            pbar.update(1)
    
    print(f"{home_team.name} wins {round(100 * (home_wins/num_simulations), 2)} percent of the time.")

def generate_simulation_stats_summary(home_team: Team, away_team: Team, home_wins: int, 
                                      num_simulations: int, home_team_stats_df_list: list[pd.DataFrame], 
                                      away_team_stats_df_list: list[pd.DataFrame]) -> dict:
    
    home_team_sim_stats_df = pd.concat(home_team_stats_df_list)
    away_team_sim_stats_df = pd.concat(away_team_stats_df_list)
    combined_sim_stats_df = pd.concat([home_team_sim_stats_df, away_team_sim_stats_df])
    
    home_team_sim_stats_df.to_csv(f"../simulation_logs/{home_team.name}_sim_stats.csv", index=True)
    away_team_sim_stats_df.to_csv(f"../simulation_logs/{away_team.name}_sim_stats.csv", index=True)
    combined_sim_stats_df.to_csv(f"../simulation_logs/{home_team.name}_{away_team.name}_sim_stats.csv", index=True)

    # Load the data
    home_team_df = pd.read_csv(f"../simulation_logs/{home_team.name}_sim_stats.csv")
    away_team_df = pd.read_csv(f"../simulation_logs/{away_team.name}_sim_stats.csv")

    stats_columns = ["team","score","run_rate","pass_rate","pass_cmp_rate",
                    "pass_yards","passing_tds","sacks_allowed","pass_yards_per_play",
                    "rushing_attempts","rushing_yards","rushing_tds","rush_yards_per_play",
                    "total_turnovers","fg_pct"]

    home_team_sim_stats_dict = {
                "team": home_team_df["team"].iloc[0],
                "score": round(home_team_df["score"].mean(), 2),
                "run_rate": round(home_team_df["run_rate"].mean(), 2),
                "pass_rate": round(home_team_df["pass_rate"].mean(), 2),
                "pass_cmp_rate": round(home_team_df["pass_cmp_rate"].mean(), 2),
                "pass_yards": round(home_team_df["pass_yards"].mean(), 2),
                "passing_tds": round(home_team_df["passing_tds"].mean(), 2),
                "sacks_allowed": round(home_team_df["sacks_allowed"].mean(), 2),
                "pass_yards_per_play": round(home_team_df["pass_yards_per_play"].mean(), 2),
                "rushing_attempts": round(home_team_df["rushing_attempts"].mean(), 2),
                "rushing_yards": round(home_team_df["rushing_yards"].mean(), 2),
                "rushing_tds": round(home_team_df["rushing_tds"].mean(), 2),
                "rush_yards_per_play": round(home_team_df["rush_yards_per_play"].mean(), 2),
                "total_turnovers": round(home_team_df["total_turnovers"].mean(), 2),
                "fg_pct": round(home_team_df["fg_pct"].mean(), 2),
            }

    away_team_sim_stats_dict = {
                "team": away_team_df["team"].iloc[0],
                "score": round(away_team_df["score"].mean(), 2),
                "run_rate": round(away_team_df["run_rate"].mean(), 2),
                "pass_rate": round(away_team_df["pass_rate"].mean(), 2),
                "pass_cmp_rate": round(away_team_df["pass_cmp_rate"].mean(), 2),
                "pass_yards": round(away_team_df["pass_yards"].mean(), 2),
                "passing_tds": round(away_team_df["passing_tds"].mean(), 2),
                "sacks_allowed": round(away_team_df["sacks_allowed"].mean(), 2),
                "pass_yards_per_play": round(away_team_df["pass_yards_per_play"].mean(), 2),
                "rushing_attempts": round(away_team_df["rushing_attempts"].mean(), 2),
                "rushing_yards": round(away_team_df["rushing_yards"].mean(), 2),
                "rushing_tds": round(away_team_df["rushing_tds"].mean(), 2),
                "rush_yards_per_play": round(away_team_df["rush_yards_per_play"].mean(), 2),
                "total_turnovers": round(away_team_df["total_turnovers"].mean(), 2),
                "fg_pct": round(away_team_df["fg_pct"].mean(), 2),
            }

    home_team_sim_stats_df = pd.DataFrame(home_team_sim_stats_dict, index=[0], columns=stats_columns)
    away_team_sim_stats_df = pd.DataFrame(away_team_sim_stats_dict, index=[0], columns=stats_columns)

    stats_csv_path = "../simulation_logs/total_sim_stats.csv"

    total_sim_stats_df = pd.concat([home_team_sim_stats_df, away_team_sim_stats_df])
    total_sim_stats_df.to_csv(stats_csv_path, index=False)
    total_sim_stats_dict = total_sim_stats_df.reset_index().to_dict(orient="records")
    #print(total_sim_stats_dict)

    home_score = home_team_sim_stats_dict["score"]
    away_score = away_team_sim_stats_dict["score"]
    average_score_diff = home_score - away_score
    home_win_pct = round(100 * (home_wins/num_simulations), 2)
    #result_string = f"{home_team.name} wins {home_win_pct} percent of the time."
    result_string = f"Average score difference: {round(average_score_diff, 2)}"
    result_string += f"\nAverage total score: {round(home_score+away_score, 2)}"
    print(result_string)

    return {
        "result_string": result_string,
        "home_win_pct": home_win_pct,
        "total_sim_stats": total_sim_stats_dict,
        "average_score_diff": average_score_diff
    }

def run_multiple_simulations_with_statistics(home_team_abbrev: str, away_team_abbrev: str, num_simulations: int, game_model=PrototypeGameModel()) -> dict:
    home_team, away_team = initialize_teams_for_game_engine(home_team_abbrev, away_team_abbrev)

    home_wins = 0
    i = 0
    print(f"Running {num_simulations} simulations of {home_team.name} vs. {away_team.name}.")

    home_team_stats_df_list= []
    away_team_stats_df_list = []

    with tqdm(total=num_simulations) as pbar:
        while i < num_simulations:
            game_engine = GameEngine(home_team, away_team, game_model)
            game_summary = game_engine.run_simulation()
            final_score = game_summary["final_score"]
            if final_score[home_team.name] > final_score[away_team.name]:
                home_wins += 1
            home_team_stats_df_list.append(pd.DataFrame([game_summary[home_team.name]]))
            away_team_stats_df_list.append(pd.DataFrame([game_summary[away_team.name]]))
            i += 1
            pbar.update(1)

    return generate_simulation_stats_summary(home_team, away_team, home_wins, num_simulations, home_team_stats_df_list, away_team_stats_df_list)

if __name__ == "__main__":
    home_team = "BUF"
    away_team = "PHI"
    num_simulations = 2500
    ## ADD SIMULATION INVOCATION BELOW ##
    # single_simulation_result = run_single_simulation(home_team, away_team)
    # print(single_simulation_result)
    exec_start = time()
    run_multiple_simulations_with_statistics(home_team, away_team, num_simulations)
    exec_end = time()
    print(f"\nExecution time: {exec_end - exec_start} seconds.")