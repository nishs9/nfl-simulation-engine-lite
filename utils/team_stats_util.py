import pandas as pd
from scipy import stats
from scipy.stats import lognorm

def get_completion_pct(team: str, team_df: pd.DataFrame) -> float:
    pass_comp_pct_df = team_df[(team_df["posteam"] == team) & (team_df["pass_attempt"] == 1) & (team_df["sack"] == 0)]
    total_attempts = pass_comp_pct_df["pass_attempt"].sum()
    total_completions = pass_comp_pct_df["complete_pass"].sum()
    completion_pct = total_completions / total_attempts
    completion_pct = round(completion_pct * 100, 2)
    return completion_pct

def get_completion_pct_allowed(team: str, team_df: pd.DataFrame) -> float:
    pass_comp_pct_df = team_df[(team_df["defteam"] == team) & (team_df["pass_attempt"] == 1) & (team_df["sack"] == 0)]
    total_attempts = pass_comp_pct_df["pass_attempt"].sum()
    total_completions = pass_comp_pct_df["complete_pass"].sum()
    completion_pct_allowed = total_completions / total_attempts
    completion_pct_allowed = round(completion_pct_allowed * 100, 2)
    return completion_pct_allowed

def get_yards_per_completion(team: str, team_df: pd.DataFrame) -> float:
    pass_yds_per_comp_df = team_df[(team_df["posteam"] == team) & (team_df["complete_pass"] == 1)]
    total_completions = pass_yds_per_comp_df["complete_pass"].sum()
    total_pass_yds = pass_yds_per_comp_df["passing_yards"].sum()
    yards_per_completion = round(total_pass_yds / total_completions, 2)
    return yards_per_completion

def get_yards_allowed_per_completion(team: str, team_df: pd.DataFrame) -> float:
    pass_yds_per_comp_df = team_df[(team_df["defteam"] == team) & (team_df["complete_pass"] == 1)]
    total_completions = pass_yds_per_comp_df["complete_pass"].sum()
    total_pass_yds_allowed = pass_yds_per_comp_df["passing_yards"].sum()
    yards_allowed_per_completion = round(total_pass_yds_allowed / total_completions, 2)
    return yards_allowed_per_completion

def get_air_yards_per_attempt(team: str, team_df: pd.DataFrame) -> float:
    air_yards_per_attempt_df = team_df[(team_df["posteam"] == team) & (team_df["pass_attempt"] == 1) & (team_df["sack"] == 0)]
    total_pass_attempts = air_yards_per_attempt_df["pass_attempt"].sum()
    total_air_yards = air_yards_per_attempt_df["air_yards"].sum()
    air_yards_per_attempt = total_air_yards / total_pass_attempts
    return air_yards_per_attempt

def get_air_yards_allowed_per_attempt(team: str, team_df: pd.DataFrame) -> float:
    air_yards_per_attempt_df = team_df[(team_df["defteam"] == team) & (team_df["pass_attempt"] == 1) & (team_df["sack"] == 0)]
    total_pass_attempts = air_yards_per_attempt_df["pass_attempt"].sum()
    total_air_yards_allowed = air_yards_per_attempt_df["air_yards"].sum()
    air_yards_allowed_per_attempt = total_air_yards_allowed / total_pass_attempts
    return air_yards_allowed_per_attempt

def get_yards_after_catch_per_completion(team: str, team_df: pd.DataFrame) -> float:
    yac_per_comp_df = team_df[(team_df["posteam"] == team) & (team_df["complete_pass"] == 1)]
    total_yac = yac_per_comp_df["yards_after_catch"].sum()
    total_completions = yac_per_comp_df["complete_pass"].sum()
    yac_per_completion = total_yac / total_completions
    return yac_per_completion

def get_yards_after_catch_allowed_per_completion(team: str, team_df: pd.DataFrame) -> float:
    yac_per_comp_df = team_df[(team_df["defteam"] == team) & (team_df["complete_pass"] == 1)]
    total_yac = yac_per_comp_df["yards_after_catch"].sum()
    total_completions = yac_per_comp_df["complete_pass"].sum()
    yac_per_completion = total_yac / total_completions
    return yac_per_completion

def get_rush_yards_per_carry(team: str, team_df: pd.DataFrame) -> float:
    rush_yds_per_carry_df = team_df[(team_df["posteam"] == team) & (team_df["rush_attempt"] == 1)]
    total_rush_attempts = rush_yds_per_carry_df["rush_attempt"].sum()
    total_rush_yds = rush_yds_per_carry_df["rushing_yards"].sum()
    yards_per_carry = total_rush_yds / total_rush_attempts
    yards_per_carry = round(yards_per_carry, 2)
    return yards_per_carry

def get_rush_yards_allowed_per_carry(team: str, team_df: pd.DataFrame) -> float:
    rush_yds_per_carry_df = team_df[(team_df["defteam"] == team) & (team_df["rush_attempt"] == 1)]
    total_rush_attempts = rush_yds_per_carry_df["rush_attempt"].sum()
    total_rush_yds_allowed = rush_yds_per_carry_df["rushing_yards"].sum()
    yards_allowed_per_carry = total_rush_yds_allowed / total_rush_attempts
    yards_allowed_per_carry = round(yards_allowed_per_carry, 2)
    return yards_allowed_per_carry

def get_turnover_rate(team: str, team_df: pd.DataFrame) -> float:
    num_drives = team_df["game_drive_composite_id"].unique().size
    turnover_df = team_df[(team_df["posteam"] == team) & ((team_df["interception"] == 1) | (team_df["fumble_lost"] == 1))]
    total_turnovers = turnover_df["interception"].sum() + turnover_df["fumble_lost"].sum()
    turnovers_per_drive = total_turnovers / num_drives
    turnovers_per_drive = round(turnovers_per_drive, 2)
    return turnovers_per_drive

def get_forced_turnover_rate(team: str, team_df: pd.DataFrame) -> float:
    num_drives = team_df["game_drive_composite_id"].unique().size
    forced_turnover_df = team_df[(team_df["defteam"] == team) & ((team_df["interception"] == 1) | (team_df["fumble_lost"] == 1))]
    total_forced_turnovers = forced_turnover_df["interception"].sum() + forced_turnover_df["fumble_lost"].sum()
    forced_turnovers_per_drive = total_forced_turnovers / num_drives
    forced_turnovers_per_drive = round(forced_turnovers_per_drive, 2)
    return forced_turnovers_per_drive

def get_run_and_pass_rates(team: str, team_df: pd.DataFrame) -> tuple[float, float]:
    team_df = team_df[(team_df["posteam"] == team)]
    num_run_plays = team_df["rush_attempt"].sum()
    num_pass_plays = team_df["pass_attempt"].sum()
    total_plays = num_run_plays + num_pass_plays
    run_rate = round(num_run_plays / total_plays, 2)
    pass_rate = round(1 - run_rate, 2)
    return (run_rate, pass_rate)

def get_sack_rates(team: str, team_df: pd.DataFrame) -> tuple[float, float, float, float]:
    offense_team_df = team_df[(team_df["posteam"] == team)]
    num_pass_plays_run = offense_team_df["pass_attempt"].sum()
    num_sacks_allowed = offense_team_df["sack"].sum()
    sacks_allowed_rate = round(num_sacks_allowed / num_pass_plays_run, 3)

    offense_sack_df = offense_team_df[(offense_team_df["sack"] == 1)]
    num_yards_lost_to_sacks = offense_sack_df["yards_gained"].sum()
    yards_lost_per_sack = round(num_yards_lost_to_sacks / num_sacks_allowed, 2)

    defense_team_df = team_df[(team_df["defteam"] == team)]
    num_pass_plays_faced = defense_team_df["pass_attempt"].sum()
    num_sacks_made = defense_team_df["sack"].sum()
    sacks_made_rate = round(num_sacks_made / num_pass_plays_faced, 3)

    defense_sack_df = defense_team_df[(defense_team_df["sack"] == 1)]
    num_yards_inflicted_by_sacks = defense_sack_df["yards_gained"].sum()
    yards_inflicted_per_sack = round(num_yards_inflicted_by_sacks / num_sacks_made, 2)

    return (sacks_allowed_rate, yards_lost_per_sack, sacks_made_rate, yards_inflicted_per_sack)
    
def get_field_goal_success_rate(team: str, team_df: pd.DataFrame) -> float:
    field_goal_df = team_df[(team_df["posteam"] == team) & (team_df["field_goal_attempt"] == 1)]
    total_field_goal_attempts = field_goal_df["field_goal_attempt"].sum()
    total_field_goals_made = field_goal_df[field_goal_df["field_goal_result"] == "made"]["field_goal_result"].count()
    field_goal_success_rate = total_field_goals_made / total_field_goal_attempts
    field_goal_success_rate = round(field_goal_success_rate, 2)
    return field_goal_success_rate

def get_distribution(data: pd.Series, dist_name: str):
    dist = getattr(stats, dist_name)
    params = dist.fit(data)
    mean = dist.mean(*params)
    variance = dist.var(*params)
    if (mean < 0):
        # Sometimes we aren't able to fit an approximate distribution and so we just
        # use the mean and variance of the real distribution (not ideal but functional)
        mean = data.mean()
        variance = data.var()
    return (mean, variance)

def get_off_pass_yards_per_play_distribution_params(team: str, team_df: pd.DataFrame) -> tuple[float, float]:
    comp_pass_df = team_df[(team_df["posteam"] == team) & (team_df["complete_pass"] == 1)]
    comp_pass_yards = comp_pass_df["passing_yards"].dropna()
    return get_distribution(comp_pass_yards, "lognorm")

def get_def_pass_yards_per_play_distribution_params(team: str, team_df: pd.DataFrame) -> tuple[float, float]:
    comp_pass_df = team_df[(team_df["defteam"] == team) & (team_df["complete_pass"] == 1)]
    comp_pass_yards = comp_pass_df["passing_yards"].dropna()
    return get_distribution(comp_pass_yards, "lognorm")

def get_off_rush_yards_per_play_distribution_params(team: str, team_df: pd.DataFrame) -> tuple[float, float]:
    rush_df = team_df[(team_df["posteam"] == team) & (team_df["rush_attempt"] == 1)]
    rush_yards = rush_df["rushing_yards"].dropna()
    return get_distribution(rush_yards, "lognorm")

def get_def_rush_yards_per_play_distribution_params(team: str, team_df: pd.DataFrame) -> tuple[float, float]:
    rush_df = team_df[(team_df["defteam"] == team) & (team_df["rush_attempt"] == 1)]
    rush_yards = rush_df["rushing_yards"].dropna()
    return get_distribution(rush_yards, "lognorm")