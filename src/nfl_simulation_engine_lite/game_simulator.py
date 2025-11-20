from concurrent.futures import ProcessPoolExecutor, as_completed
from nfl_simulation_engine_lite.db.db_conn import get_db_conn
from nfl_simulation_engine_lite.game_model.game_model_factory import initialize_new_game_model_instance
from nfl_simulation_engine_lite.game_model.game_model import AbstractGameModel
from nfl_simulation_engine_lite.game_model.prototype_game_model import PrototypeGameModel
from nfl_simulation_engine_lite.game_engine.game_engine import GameEngine
from nfl_simulation_engine_lite.team.team import Team
from time import time
from tqdm import tqdm
import math
import os
import pandas as pd
import random
import nfl_simulation_engine_lite.team.team_factory as TeamFactory
import nfl_simulation_engine_lite.utils.play_log_util as plu
import warnings
import requests
import re
import csv

warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

def initialize_teams_for_game_engine(home_team_abbrev: str, away_team_abbrev: str) -> tuple:
    db_conn = get_db_conn() 
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

def run_multiple_simulations(home_team_abbrev: str, away_team_abbrev: str, num_simulations: int, game_model=PrototypeGameModel()) -> None:
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

def parse_simulation_result(score_diff: float, home_team: str, away_team: str) -> str:
    if score_diff > 0:
        return f"{home_team} wins by {round(score_diff, 2)}"
    elif score_diff < 0:
        return f"{away_team} wins by {round(score_diff * -1, 2)}"
    else:
        return f"{home_team} and {away_team} tie"

def read_matchup_column(file_path):
    matchups = []
    try:
        with open(file_path, mode='r') as input_file:
            for line in input_file:
                line = line.strip()
                teams = line.split(" v ") 
                if len(teams) != 2:
                    raise ValueError("Invalid matchup format. Must be 'TEAM_A v TEAM_B'.")
                matchups.append((teams[0], teams[1])) 
    except ValueError as ve:
        print(f"ValueError: {ve}")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return matchups

def extract_team_abbrev(team_string):
    match = re.match(r'(\S+)\s\S+\s(\S+)', team_string)
    if match:
        return match.groups()
    else:
        print("The following game string is in an invalid format:")
        print(team_string)

def generate_weekly_prediction_input_file(week: int) -> None:
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?week={week}"
    response = requests.get(url)
    data = response.json()
    matchup_records = []
    for game in data['events']:
        print(f"Processing game: {game['shortName']}")
        team_abbrevs = extract_team_abbrev(game['shortName'])
        home_team_abbrev = team_abbrevs[1]
        if home_team_abbrev == 'LAR':
            home_team_abbrev = 'LA'
        away_team_abbrev = team_abbrevs[0]
        if away_team_abbrev == 'LAR':
            away_team_abbrev = 'LA'
        game_date = game['date']
        matchup_record = {
            "home_team_abbrev": home_team_abbrev,
            "away_team_abbrev": away_team_abbrev,
            "game_date": game_date
        }
        matchup_records.append(matchup_record)
    
    game_df = pd.DataFrame(matchup_records)
    game_df.sort_values(by='game_date', inplace=True)
    game_df.reset_index(drop=True, inplace=True)

    with open(f'input_week_{week}.txt', 'w') as input_file:
        for __, row in game_df.iterrows():
            home_team_abbrev = row['home_team_abbrev']
            away_team_abbrev = row['away_team_abbrev']
            input_file.write(f"{away_team_abbrev} v {home_team_abbrev}\n")
    print(f"Weekly prediction input file has been generated for week {week}.")

def fetch_scores_for_week(week: int) -> None:
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?week={week}"
    response = requests.get(url)
    data = response.json()
    score_records = []
    for game in data['events']:
        game_state = game['status']['type']['state']
        if game_state != 'post':
            # Only process completed games
            continue
        print(f"Processing game: {game['shortName']}")
        team_abbrevs = extract_team_abbrev(game['shortName'])
        home_team_abbrev = team_abbrevs[1]
        if home_team_abbrev == 'LAR':
            home_team_abbrev = 'LA'
        away_team_abbrev = team_abbrevs[0]
        if away_team_abbrev == 'LAR':
            away_team_abbrev = 'LA'
        game_date = game['date']
        home_score = game['competitions'][0]['competitors'][0]['score']
        away_score = game['competitions'][0]['competitors'][1]['score']
        print(f"Home team: {home_team_abbrev} {home_score}, Away team: {away_team_abbrev} {away_score}")
        score_record = {
            "home_team_abbrev": home_team_abbrev,
            "away_team_abbrev": away_team_abbrev,
            "game_date": game_date,
            "home_score": home_score,
            "away_score": away_score
        }
        score_records.append(score_record)
    score_df = pd.DataFrame(score_records)
    score_df.sort_values(by='game_date', inplace=True)
    score_df.reset_index(drop=True, inplace=True)
    with open(f'scores_{week}.txt', 'w') as scores_file:
        for __, row in score_df.iterrows():
            home_team_abbrev = row['home_team_abbrev']
            away_team_abbrev = row['away_team_abbrev']
            home_score = int(row['home_score'])
            away_score = int(row['away_score'])
            if home_score > away_score:
                score_diff = home_score - away_score
                scores_file.write(f"{home_team_abbrev} wins by {score_diff}\n")
            elif home_score < away_score:
                score_diff = away_score - home_score
                scores_file.write(f"{away_team_abbrev} wins by {score_diff}\n")
            else:
                scores_file.write(f"{home_team_abbrev} and {away_team_abbrev} tie\n")
    print(f"Scores for week {week} have been written to 'test_scores.txt'.")

def run_weekly_predictions(week: int, num_simulations=3000, num_workers=None):
    prediction_run_start = time()
    matchups = read_matchup_column(f"input_week_{week}.txt")
    game_models = [
        PrototypeGameModel(), initialize_new_game_model_instance("v1"), 
        initialize_new_game_model_instance("v1a"), initialize_new_game_model_instance("v1b"),
        initialize_new_game_model_instance("v2"), initialize_new_game_model_instance("v2a"),
        initialize_new_game_model_instance("v2b")
    ]
    prediction_results = {key: [] for key in matchups}
    for game_model in game_models:
        for matchup in matchups:
            away_team = matchup[0].strip()
            home_team = matchup[1].strip()
            print(f"Running simulations for {away_team} at {home_team} with {game_model.get_model_code()}")
            result = run_multiple_simulations_multi_threaded(home_team, away_team, num_simulations, game_model, num_workers=num_workers)
            prediction_results[matchup].append(parse_simulation_result(result["average_score_diff"], home_team, away_team))
            prediction_results[matchup].append(matchup[1] + " WP%: " + str(result["home_win_pct"]))

    with open("weekly_predictions_enhanced.csv", "w", newline='') as output_file:
        csv_fieldnames = ["Matchup", "Prototype", "Prototype_WP", "V1", "V1_WP", "V1a", "V1a_WP", "V1b", "V1b_WP", "V2", "V2_WP", "V2a", "V2a_WP", "V2b", "V2b_WP"]
        writer = csv.DictWriter(output_file, fieldnames=csv_fieldnames)
        writer.writeheader()
        for matchup in matchups:
            writer.writerow({
                "Matchup": f"{matchup[0]} v {matchup[1]}",
                "V2b_WP": prediction_results[matchup][13],
                "V2b": prediction_results[matchup][12],
                "V2a_WP": prediction_results[matchup][11],
                "V2a": prediction_results[matchup][10],
                "V2_WP": prediction_results[matchup][9],
                "V2": prediction_results[matchup][8],
                "V1b_WP": prediction_results[matchup][7],
                "V1b": prediction_results[matchup][6],
                "V1a_WP": prediction_results[matchup][5],
                "V1a": prediction_results[matchup][4],
                "V1_WP": prediction_results[matchup][3],
                "V1": prediction_results[matchup][2],
                "Prototype_WP": prediction_results[matchup][1],
                "Prototype": prediction_results[matchup][0]
            })

    with open("weekly_predictions.csv", "w", newline='') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=["Matchup", "Prototype", "V1", "V1a", "V1b", "V2", "V2a", "V2b"])
        writer.writeheader()
        for matchup in matchups:
            writer.writerow({
                "Matchup": f"{matchup[0]} v {matchup[1]}",
                "V2b": prediction_results[matchup][12],
                "V2a": prediction_results[matchup][10],
                "V2": prediction_results[matchup][8],
                "V1b": prediction_results[matchup][6],
                "V1a": prediction_results[matchup][4],
                "V1": prediction_results[matchup][2],
                "Prototype": prediction_results[matchup][0]
            })
    prediction_run_end = time()
    prediction_run_time = prediction_run_end - prediction_run_start
    print(f"Prediction run time: {prediction_run_time} seconds.")
    print("Weekly predictions have been written to 'weekly_predictions.csv'.")

def generate_simulation_stats_summary(home_team: Team, away_team: Team, home_wins: int, 
                                      num_simulations: int, home_team_stats_df_list: list[pd.DataFrame], 
                                      away_team_stats_df_list: list[pd.DataFrame], debug_mode=True) -> dict:
    
    home_team_sim_stats_df = pd.concat(home_team_stats_df_list)
    away_team_sim_stats_df = pd.concat(away_team_stats_df_list)
    combined_sim_stats_df = pd.concat([home_team_sim_stats_df, away_team_sim_stats_df])
    
    if debug_mode:
        home_team_sim_stats_df.to_csv(f"../simulation_logs/{home_team.name}_sim_stats.csv", index=True)
        away_team_sim_stats_df.to_csv(f"../simulation_logs/{away_team.name}_sim_stats.csv", index=True)
        combined_sim_stats_df.to_csv(f"../simulation_logs/{home_team.name}_{away_team.name}_sim_stats.csv", index=True)

    home_team_df = home_team_sim_stats_df
    away_team_df = away_team_sim_stats_df

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

    total_sim_stats_df = pd.concat([home_team_sim_stats_df, away_team_sim_stats_df])
    if debug_mode:
        stats_csv_path = "../simulation_logs/total_sim_stats.csv"
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

def run_multiple_simulations_with_statistics(home_team_abbrev: str, away_team_abbrev: str, num_simulations: int, game_model=PrototypeGameModel(), debug_mode=True) -> dict:
    home_team, away_team = initialize_teams_for_game_engine(home_team_abbrev, away_team_abbrev)

    home_wins = 0
    i = 0
    print(f"Running {num_simulations} simulations of {away_team.name} at {home_team.name}.")

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

    return generate_simulation_stats_summary(home_team, away_team, home_wins, num_simulations, home_team_stats_df_list, away_team_stats_df_list, debug_mode=debug_mode)

def run_simulation_chunk(home_team: Team, away_team: Team, game_model: AbstractGameModel, start_index: int, num_simulations_for_chunk: int) -> list:
    chunk_results = []
    for i in range(num_simulations_for_chunk):
        game_engine = GameEngine(home_team, away_team, game_model)
        game_summary = game_engine.run_simulation()
        chunk_results.append((start_index + i, game_summary))
    return chunk_results

def run_multiple_simulations_multi_threaded(home_team_abbrev: str, away_team_abbrev: str, num_simulations: int, game_model=PrototypeGameModel(), num_workers=None, debug_mode=True) -> dict:
    home_team, away_team = initialize_teams_for_game_engine(home_team_abbrev, away_team_abbrev)
    print(f"Running {num_simulations} simulations of {away_team.name} at {home_team.name}.")

    ## The default number of workers is half the number of CPU cores
    number_of_workers = min(num_simulations, os.cpu_count() // 2)
    if num_workers:
        number_of_workers = num_workers
    chunk_size = math.ceil(num_simulations / number_of_workers)

    print(f"Using a chunk size of {chunk_size} and {number_of_workers} workers...\n")

    futures = []
    with ProcessPoolExecutor(max_workers=number_of_workers) as executor:
        start_index = 0
        for _ in range(number_of_workers):
            sim_count_for_curr_chunk = min(chunk_size, num_simulations - start_index)
            if sim_count_for_curr_chunk <= 0:
                break
            futures.append(executor.submit(
                run_simulation_chunk,
                home_team,
                away_team,
                game_model,
                start_index,
                sim_count_for_curr_chunk
            ))
            start_index += sim_count_for_curr_chunk
        
        all_results = []
        print(f"Running {num_simulations} simulations over {number_of_workers} chunks...")
        with tqdm(total=number_of_workers) as pbar:
            for future in as_completed(futures):
                chunk_results = future.result()
                all_results.extend(chunk_results)
                pbar.update(1)

    home_wins = 0
    home_team_stats_df_list = []
    away_team_stats_df_list = []
    
    # Randomly choose a game to be featured in detail on the frontend
    featured_game_index = random.randint(0, len(all_results) - 1)
    featured_play_log = None

    for i, game_summary in all_results:
        final_score = game_summary["final_score"]
        if i == featured_game_index:
            featured_play_log = pd.DataFrame(game_summary["play_log"])
            featured_play_log["game_time_elapsed"] = (featured_play_log["game_seconds_remaining"] - 3600) * -1
            if debug_mode:
                featured_play_log.to_csv("logs/featured_game.csv", index=True)
        if final_score[home_team.name] > final_score[away_team.name]:
            home_wins += 1
        home_team_stats_df_list.append(pd.DataFrame(game_summary[home_team_abbrev], index=[i]))
        away_team_stats_df_list.append(pd.DataFrame(game_summary[away_team_abbrev], index=[i]))

    sim_result = generate_simulation_stats_summary(home_team, away_team, home_wins, num_simulations, home_team_stats_df_list, away_team_stats_df_list, debug_mode=debug_mode)
    sim_result["featured_game_home_pass_data"] = plu.generate_team_passing_stats_summary(home_team_abbrev, featured_play_log)
    sim_result["featured_game_away_pass_data"] = plu.generate_team_passing_stats_summary(away_team_abbrev, featured_play_log)
    sim_result["featured_game_home_rush_data"] = plu.generate_team_rushing_stats_summary(home_team_abbrev, featured_play_log)
    sim_result["featured_game_away_rush_data"] = plu.generate_team_rushing_stats_summary(away_team_abbrev, featured_play_log)
    sim_result["featured_game_home_scoring_data"] = plu.generate_team_scoring_summary(home_team_abbrev, featured_play_log)
    sim_result["featured_game_away_scoring_data"] = plu.generate_team_scoring_summary(away_team_abbrev, featured_play_log)
    return sim_result

if __name__ == "__main__":
    home_team = "IND"
    away_team = "ATL"
    num_simulations = 150
    ## ADD SIMULATION INVOCATION BELOW ##
    # single_simulation_result = run_single_simulation(home_team, away_team)
    # print(single_simulation_result)
    # exec_start = time()
    # run_multiple_simulations_with_statistics(home_team, away_team, num_simulations, game_model=PrototypeGameModel())
    # exec_end = time()
    # print(f"\nExecution time: {exec_end - exec_start} seconds.\n")

    # exec_start = time()
    # run_multiple_simulations_with_statistics(home_team, away_team, num_simulations, game_model=initialize_new_game_model_instance("v1"))
    # exec_end = time()
    # print(f"\nExecution time: {exec_end - exec_start} seconds.")

    # exec_start = time()
    # run_multiple_simulations_with_statistics(home_team, away_team, num_simulations, game_model=initialize_new_game_model_instance("v1a"))
    # exec_end = time()
    # print(f"\nExecution time: {exec_end - exec_start} seconds.")

    # exec_start = time()
    # run_multiple_simulations_multi_threaded(home_team, away_team, num_simulations, game_model=initialize_new_game_model_instance("v1b"), num_workers=2)
    # exec_end = time()
    # print(f"\nExecution time: {exec_end - exec_start} seconds.")

    # run_multiple_simulations_multi_threaded(home_team, away_team, num_simulations, game_model=initialize_new_game_model_instance("v1b"), num_workers=3)
    # run_multiple_simulations_multi_threaded(home_team, away_team, num_simulations, game_model=initialize_new_game_model_instance("v1b"), num_workers=3)
    exec_start = time()
    # fetch_scores_for_week(11)
    generate_weekly_prediction_input_file(12)
    run_weekly_predictions(week=12, num_simulations=4500, num_workers=4)
    #run_multiple_simulations_multi_threaded(home_team, away_team, num_simulations, game_model=initialize_new_game_model_instance("v2b"), num_workers=3)
    #run_multiple_simulations_multi_threaded(home_team, away_team, num_simulations, game_model=initialize_new_game_model_instance("v2"), num_workers=3)
    exec_end = time()
    print(f"\nExecution time: {exec_end - exec_start} seconds.")