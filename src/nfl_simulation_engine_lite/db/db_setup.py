from nfl_simulation_engine_lite.db.constants import pbp_filter_list
import pandas as pd
import sqlite3
import argparse
import nfl_simulation_engine_lite.db.team_stats_util as tsu
import warnings

warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

def init_argparser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="This is a CLI used to populate the NFL Sim Engine Lite database")
    parser.add_argument("-l", "--local", action="store_true", help="Use local NFL play-by-play data file")
    parser.add_argument("-r", "--save_raw_pbp", action="store_true", help="Save the raw play-by-play data to CSV (testing purposes only)")
    parser.add_argument("-f", "--filter_pbp", action="store_true", help="Save the play-by-play data with only the necessary columns for sim engine calculations (testing purposes only)")  
    parsed_args = parser.parse_args()
    return parsed_args

def hydrate_db(pbp_df: pd.DataFrame, season: int, save_raw_data: bool, filter_data: bool) -> None:
    db_conn = sqlite3.connect("nfl_stats.db")

    # Filter the play-by-play data to only include necessary columns
    filtered_pbp_data = pbp_df[pbp_filter_list]

    # Optionally, save the raw play-by-play data to a CSV file
    if (save_raw_data and not filter_data):
        raw_output_file = f"data/{season}_NFL_raw.csv"
        pbp_df.to_csv(raw_output_file, index=False)
    elif (filter_data):
        filtered_output_file = f"data/{season}_NFL_filtered.csv"
        filtered_pbp_data.to_csv(filtered_output_file, index=False)

    setup_sim_engine_team_stats_table(filtered_pbp_data, db_conn)
    db_conn.close()

def alt_online_db_hydrate() -> None:
    base_url_1 = 'https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2024.csv.gz'
    base_url_2 = 'https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2025.csv.gz'
    raw_pbp_data_1 = pd.read_csv(base_url_1, compression='gzip', low_memory=False)
    raw_pbp_data_1 = raw_pbp_data_1[raw_pbp_data_1["week"] >= 17]
    raw_pbp_data_2 = pd.read_csv(base_url_2, compression='gzip', low_memory=False)
    raw_pbp_data = pd.concat([raw_pbp_data_1, raw_pbp_data_2])
    regular_season_data = raw_pbp_data[raw_pbp_data["season_type"] == "REG"]
    hydrate_db(regular_season_data, 2025, False, False)

def hydrate_db_online(season: int, save_raw_data: bool, filter_data: bool) -> None:
    base_url = 'https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_' + str(season) + '.csv.gz'
    raw_pbp_data = pd.read_csv(base_url, compression='gzip', low_memory=False)
    regular_season_data = raw_pbp_data[raw_pbp_data["season_type"] == "REG"]
    hydrate_db(regular_season_data, season, save_raw_data, filter_data)

def hydrate_db_local(season: int, save_raw_data: bool, filter_data: bool) -> None:
    try:
        raw_pbp_data = pd.read_csv(f"input/play_by_play_{season}.csv")
        hydrate_db(raw_pbp_data, season, save_raw_data, filter_data)
    except FileNotFoundError as err:
        print("Local play-by-play data file not found. Please download the data from nflverse on GitHub and put it in the data folder.")
        print(err.strerror + ": " + err.filename)
        return

def initialize_team_stats_dict(team_abbrev_list: list[str]) -> dict[str, list[any]]:
    team_stats_dict = {}
    team_stats_dict["team"] = team_abbrev_list
    team_stats_dict["games_played"] = None
    team_stats_dict["pass_completion_rate"] = None
    team_stats_dict["yards_per_completion"] = None
    team_stats_dict["rush_yards_per_carry"] = None
    team_stats_dict["turnover_rate"] = None
    team_stats_dict["forced_turnover_rate"] = None
    team_stats_dict["run_rate"] = None
    team_stats_dict["pass_rate"] = None
    team_stats_dict["sacks_allowed_rate"] = None
    team_stats_dict["sack_yards_allowed"] = None
    team_stats_dict["sacks_made_rate"] = None
    team_stats_dict["sack_yards_inflicted"] = None
    team_stats_dict["field_goal_success_rate"] = None
    team_stats_dict["pass_completion_rate_allowed"] = None
    team_stats_dict["yards_allowed_per_completion"] = None
    team_stats_dict["rush_yards_per_carry_allowed"] = None
    return team_stats_dict

def setup_sim_engine_team_stats_table(raw_pbp_df: pd.DataFrame, db_conn: sqlite3.Connection) -> None:
    team_abbrev_list = sorted(raw_pbp_df["home_team"].unique())
    team_stats_dict = initialize_team_stats_dict(team_abbrev_list)
    games_played_list = []
    pass_completion_rate_list = []
    yards_per_completion_list = []
    rush_yards_per_carry_list = []
    turnover_rate_list = []
    forced_turnover_rate_list = []
    run_rate_list = []
    pass_rate_list = []
    sacks_allowed_rate_list = []
    sack_yards_allowed_list = []
    sacks_made_rate_list = []
    sack_yards_inflicted_list = []
    fg_success_rate_list = []
    pass_completion_rate_allowed_list = []
    yards_allowed_per_completion_list = []
    rush_yards_allowed_per_carry_list = []
    off_pass_yards_per_play_mean_list = []
    off_pass_yards_per_play_variance_list = []
    def_pass_yards_per_play_mean_list = []
    def_pass_yards_per_play_variance_list = []
    off_rush_yards_per_play_mean_list = []
    off_rush_yards_per_play_variance_list = []
    def_rush_yards_per_play_mean_list = []
    def_rush_yards_per_play_variance_list = []
    off_air_yards_per_attempt_list = []
    def_air_yards_per_attempt_list = []
    off_yac_per_completion_list = []
    def_yac_per_completion_list = []
    for team in team_abbrev_list:
        curr_team_df = raw_pbp_df[(raw_pbp_df["home_team"] == team) | (raw_pbp_df["away_team"] == team)]
        curr_team_df["game_drive_composite_id"] = curr_team_df["game_id"] + "_" + curr_team_df["drive"].astype(str)

        games_played_list.append(curr_team_df["game_id"].unique().size)

        pass_completion_rate_list.append(tsu.get_completion_pct(team, curr_team_df))
        yards_per_completion_list.append(tsu.get_yards_per_completion(team, curr_team_df))

        off_air_yards_per_attempt_list.append(tsu.get_air_yards_per_attempt(team, curr_team_df))
        def_air_yards_per_attempt_list.append(tsu.get_air_yards_allowed_per_attempt(team, curr_team_df))

        off_yac_per_completion_list.append(tsu.get_yards_after_catch_per_completion(team, curr_team_df))
        def_yac_per_completion_list.append(tsu.get_yards_after_catch_allowed_per_completion(team, curr_team_df))

        rush_yards_per_carry_list.append(tsu.get_rush_yards_per_carry(team, curr_team_df))
        turnover_rate_list.append(tsu.get_turnover_rate(team, curr_team_df))
        forced_turnover_rate_list.append(tsu.get_forced_turnover_rate(team, curr_team_df))

        mean, variance = tsu.get_off_pass_yards_per_play_distribution_params(team, curr_team_df)
        off_pass_yards_per_play_mean_list.append(mean)
        off_pass_yards_per_play_variance_list.append(variance)

        mean, variance = tsu.get_def_pass_yards_per_play_distribution_params(team, curr_team_df)
        def_pass_yards_per_play_mean_list.append(mean)
        def_pass_yards_per_play_variance_list.append(variance)

        mean, variance = tsu.get_off_rush_yards_per_play_distribution_params(team, curr_team_df)
        off_rush_yards_per_play_mean_list.append(mean)
        off_rush_yards_per_play_variance_list.append(variance)

        mean, variance = tsu.get_def_rush_yards_per_play_distribution_params(team, curr_team_df)
        def_rush_yards_per_play_mean_list.append(mean)
        def_rush_yards_per_play_variance_list.append(variance)

        run_rate, pass_rate = tsu.get_run_and_pass_rates(team, curr_team_df)
        run_rate_list.append(run_rate)
        pass_rate_list.append(pass_rate)

        sacks_allowed_rate, sack_yards_allowed, sacks_made_rate, sack_yards_inflicted = tsu.get_sack_rates(team, curr_team_df)
        sacks_allowed_rate_list.append(sacks_allowed_rate)
        sack_yards_allowed_list.append(sack_yards_allowed)
        sacks_made_rate_list.append(sacks_made_rate)
        sack_yards_inflicted_list.append(sack_yards_inflicted)
        fg_success_rate_list.append(tsu.get_field_goal_success_rate(team, curr_team_df))
        pass_completion_rate_allowed_list.append(tsu.get_completion_pct_allowed(team, curr_team_df))
        yards_allowed_per_completion_list.append(tsu.get_yards_allowed_per_completion(team, curr_team_df))
        rush_yards_allowed_per_carry_list.append(tsu.get_rush_yards_allowed_per_carry(team, curr_team_df))

    team_stats_dict["games_played"] = games_played_list
    team_stats_dict["pass_completion_rate"] = pass_completion_rate_list
    team_stats_dict["yards_per_completion"] = yards_per_completion_list
    team_stats_dict["rush_yards_per_carry"] = rush_yards_per_carry_list
    team_stats_dict["turnover_rate"] = turnover_rate_list
    team_stats_dict["forced_turnover_rate"] = forced_turnover_rate_list
    team_stats_dict["run_rate"] = run_rate_list
    team_stats_dict["pass_rate"] = pass_rate_list
    team_stats_dict["sacks_allowed_rate"] = sacks_allowed_rate_list
    team_stats_dict["sacks_made_rate"] = sacks_made_rate_list
    team_stats_dict["sack_yards_allowed"] = sack_yards_allowed_list
    team_stats_dict["sack_yards_inflicted"] = sack_yards_inflicted_list
    team_stats_dict["field_goal_success_rate"] = fg_success_rate_list
    team_stats_dict["pass_completion_rate_allowed"] = pass_completion_rate_allowed_list
    team_stats_dict["yards_allowed_per_completion"] = yards_allowed_per_completion_list
    team_stats_dict["rush_yards_per_carry_allowed"] = rush_yards_allowed_per_carry_list
    team_stats_dict["off_pass_yards_per_play_mean"] = off_pass_yards_per_play_mean_list
    team_stats_dict["off_pass_yards_per_play_variance"] = off_pass_yards_per_play_variance_list
    team_stats_dict["def_pass_yards_per_play_mean"] = def_pass_yards_per_play_mean_list
    team_stats_dict["def_pass_yards_per_play_variance"] = def_pass_yards_per_play_variance_list
    team_stats_dict["off_rush_yards_per_play_mean"] = off_rush_yards_per_play_mean_list
    team_stats_dict["off_rush_yards_per_play_variance"] = off_rush_yards_per_play_variance_list
    team_stats_dict["def_rush_yards_per_play_mean"] = def_rush_yards_per_play_mean_list
    team_stats_dict["def_rush_yards_per_play_variance"] = def_rush_yards_per_play_variance_list
    team_stats_dict["off_air_yards_per_attempt"] = off_air_yards_per_attempt_list
    team_stats_dict["def_air_yards_per_attempt"] = def_air_yards_per_attempt_list
    team_stats_dict["off_yac_per_completion"] = off_yac_per_completion_list
    team_stats_dict["def_yac_per_completion"] = def_yac_per_completion_list

    team_stats_df = pd.DataFrame(team_stats_dict)
    team_stats_df.to_sql(f'sim_engine_team_stats_2024', con=db_conn, if_exists='replace', index=True)

if __name__ == "__main__":
    print("Running NFL Sim Engine Lite DB Setup Script")
    #args = init_argparser()
    alt_online_db_hydrate()
    # if args.local:
    #     hydrate_db_local(2024, args.save_raw_pbp, args.filter_pbp)
    # else:
    #     hydrate_db_online(2024, args.save_raw_pbp, args.filter_pbp)