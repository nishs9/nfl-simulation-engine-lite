from constants import pbp_filter_list
import pandas as pd
import sqlite3
import argparse
import os

def init_argparser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="This is a CLI used to populate the NFL Sim Engine Lite database")
    parser.add_argument("-l", "--local", action="store_true", help="Use local NFL play-by-play data file")
    parser.add_argument("-r", "--save_raw_pbp", action="store_true", help="Save the raw play-by-play data to CSV (testing purposes only)")
    parser.add_argument("-f", "--filter_pbp", action="store_true", help="Save the play-by-play data with only the necessary columns for sim engine calculations (testing purposes only)")  
    parsed_args = parser.parse_args()
    print(parsed_args)
    return parsed_args

def init_db_conn() -> sqlite3.Connection:
    db_conn = sqlite3.connect("nfl_stats.db")
    return db_conn

def hydrate_db(pbp_df: pd.DataFrame, season: int, save_raw_data: bool, filter_data: bool) -> None:
    db_conn = init_db_conn()
    filtered_pbp_data = pbp_df[pbp_filter_list]
    if (save_raw_data and not filter_data):
        raw_output_file = f"data/{season}_NFL_raw.csv"
        pbp_df.to_csv(raw_output_file, index=False)
    elif (filter_data):
        filtered_output_file = f"data/{season}_NFL_filtered.csv"
        filtered_pbp_data.to_csv(filtered_output_file, index=False)
    db_conn.close()

def hydrate_db_online(season: int, save_raw_data: bool, filter_data: bool) -> None:
    base_url = 'https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_' + str(season) + '.csv.gz'
    raw_pbp_data = pd.read_csv(base_url, compression='gzip', low_memory=False)
    hydrate_db(raw_pbp_data, season, save_raw_data, filter_data)

def hydrate_db_local(season: int, save_raw_data: bool, filter_data: bool) -> None:
    raw_pbp_data = pd.read_csv(f"data/play_by_play_{season}.csv")
    hydrate_db(raw_pbp_data, season, save_raw_data, filter_data)

if __name__ == "__main__":
    print("Running NFL Sim Engine Lite DB Setup Script")
    args = init_argparser()
    if args.local:
        hydrate_db_local(2024, args.save_raw_pbp, args.filter_pbp)
    else:
        hydrate_db_online(2024, args.save_raw_pbp, args.filter_pbp)