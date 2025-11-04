import pandas as pd
import datetime
import nfl_simulation_engine_lite.db.team_stats_util as tsu

def initialize_team_stats_dict(team_abbrev_list: list[str], down: int, distance_category: str, redzone: bool) -> dict[str, list[any]]:
    team_stats_dict = {}
    team_stats_dict["team"] = team_abbrev_list
    team_stats_dict["down"] = down
    team_stats_dict["distance_category"] = distance_category
    team_stats_dict["redzone"] = redzone
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
    team_stats_dict["last_updated"] = None
    return team_stats_dict

def full_calculate_team_stats(df: pd.DataFrame) -> pd.DataFrame:
    return calculate_team_stats(None, None, None, df)

def calculate_team_stats(down: int, distance_category: str, redzone: bool, df: pd.DataFrame) -> pd.DataFrame:
    
    df["distance_category"] = df["ydstogo"].apply(lambda x: "short" if x < 4  else "medium" if x < 7 else "long")

    # Filter play-by-play data for the given situation
    filtered_df = df.copy()
    if down is not None and distance_category is not None and redzone is not None:
        if redzone:
            filtered_df = df[(df['down'] == down) & (df['distance_category'] == distance_category) & (df['yardline_100'] <= 20)]
        else:
            filtered_df = df[(df['down'] == down) & (df['distance_category'] == distance_category) & (df['yardline_100'] > 20)]

    team_abbrev_list = sorted(df["home_team"].unique())
    team_stats_dict = initialize_team_stats_dict(team_abbrev_list, down, distance_category, redzone)
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
    off_air_yards_per_attempt_list = []
    def_air_yards_per_attempt_list = []
    off_yac_per_completion_list = []
    def_yac_per_completion_list = []
    scramble_rate_list = []
    scramble_rate_allowed_list = []
    timestamp_list = []
    for team in team_abbrev_list:
        curr_team_df = filtered_df[(filtered_df["home_team"] == team) | (filtered_df["away_team"] == team)]
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

        scramble_rate_list.append(tsu.get_scramble_rate(team, curr_team_df))
        scramble_rate_allowed_list.append(tsu.get_scramble_rate_allowed(team, curr_team_df))

        timestamp_list.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

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
    team_stats_dict["off_air_yards_per_attempt"] = off_air_yards_per_attempt_list
    team_stats_dict["def_air_yards_per_attempt"] = def_air_yards_per_attempt_list
    team_stats_dict["off_yac_per_completion"] = off_yac_per_completion_list
    team_stats_dict["def_yac_per_completion"] = def_yac_per_completion_list
    team_stats_dict["scramble_rate"] = scramble_rate_list
    team_stats_dict["scramble_rate_allowed"] = scramble_rate_allowed_list
    team_stats_dict["last_updated"] = timestamp_list

    return pd.DataFrame(team_stats_dict)

def main():
    df = pd.read_csv("raw_data/2024_NFL.csv")
    team_df = full_calculate_team_stats(df)
    #print(team_df)
    team_df.to_csv("team_rates_2024.csv", index=False)

if __name__ == "__main__":
    main()
