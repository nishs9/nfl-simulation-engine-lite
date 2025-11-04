from nfl_simulation_engine_lite.team.team_stats import TeamStats
import pandas as pd

class TeamRates:
    def __init__(self, total_team_rate_stats: pd.DataFrame):
        self.team_rate_stats = self.initialize_team_rate_stats(total_team_rate_stats)

    def initialize_team_rate_stats(self, total_team_rate_stats: pd.DataFrame) -> dict[str, TeamStats]:
        team_rate_stats = {}
        for __, row in total_team_rate_stats.iterrows():
            situation_key = f"{row['down']}_{row['distance_category']}_{row['redzone']}"
            curr_situation_stats = self.init_situation_team_stats(row.to_dict())
            team_rate_stats[situation_key] = curr_situation_stats
        return team_rate_stats

    def get_data_for_situation(self, down: int, distance_category: str, redzone: bool) -> TeamStats:
        situation_key = f"{down}_{distance_category}_{redzone}"
        if situation_key not in self.team_rate_stats:
            raise ValueError(f"Invalid situation key: {situation_key}")
        return self.team_rate_stats[situation_key]

    def init_situation_team_stats(self, team_stats_dict: dict) -> TeamStats:
        team_stats = TeamStats()
        team_stats.team = team_stats_dict["team"]
        team_stats.games_played = team_stats_dict["games_played"]
        team_stats.pass_completion_rate = team_stats_dict["pass_completion_rate"]
        team_stats.yards_per_completion = team_stats_dict["yards_per_completion"]
        team_stats.scramble_rate = team_stats_dict["scramble_rate"]
        team_stats.scramble_rate_allowed = team_stats_dict["scramble_rate_allowed"]
        team_stats.rush_yards_per_carry = team_stats_dict["rush_yards_per_carry"]
        team_stats.turnover_rate = team_stats_dict["turnover_rate"]
        team_stats.forced_turnover_rate = team_stats_dict["forced_turnover_rate"]
        team_stats.run_rate = team_stats_dict["run_rate"]
        team_stats.pass_rate = team_stats_dict["pass_rate"]
        team_stats.sacks_allowed_rate = team_stats_dict["sacks_allowed_rate"]
        team_stats.sack_yards_allowed = team_stats_dict["sack_yards_allowed"]
        team_stats.sacks_made_rate = team_stats_dict["sacks_made_rate"]
        team_stats.sack_yards_inflicted = team_stats_dict["sack_yards_inflicted"]
        team_stats.field_goal_success_rate = team_stats_dict["field_goal_success_rate"]
        team_stats.pass_completion_rate_allowed = team_stats_dict["pass_completion_rate_allowed"]
        team_stats.yards_allowed_per_completion = team_stats_dict["yards_allowed_per_completion"]
        team_stats.rush_yards_per_carry_allowed = team_stats_dict["rush_yards_per_carry_allowed"]
        team_stats.off_air_yards_per_attempt = team_stats_dict["off_air_yards_per_attempt"]
        team_stats.def_air_yards_per_attempt = team_stats_dict["def_air_yards_per_attempt"]
        team_stats.off_yac_per_completion = team_stats_dict["off_yac_per_completion"]
        team_stats.def_yac_per_completion = team_stats_dict["def_yac_per_completion"]
        return team_stats