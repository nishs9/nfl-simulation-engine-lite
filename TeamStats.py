from dataclasses import dataclass

@dataclass(slots=True)
class TeamStats:
    team: str
    games_played: int

    pass_rate: float
    pass_completion_rate: float
    yards_per_completion: float
    pass_completion_rate_allowed: float
    yards_allowed_per_completion: float

    run_rate: float
    rush_yards_per_carry: float
    rush_yards_per_carry_allowed: float

    turnover_rate: float
    forced_turnover_rate: float
    
    sacks_allowed_rate: float
    sack_yards_allowed: float
    sacks_made_rate: float
    sack_yards_inflicted: float

    field_goal_success_rate: float

    off_rush_yards_per_play_mean: float
    off_rush_yards_per_play_variance: float
    def_rush_yards_per_play_mean: float
    def_rush_yards_per_play_variance: float

    off_pass_yards_per_play_mean: float
    off_pass_yards_per_play_variance: float
    def_pass_yards_per_play_mean: float
    def_pass_yards_per_play_variance: float

    off_air_yards_per_attempt: float
    def_air_yards_per_attempt: float
    off_yac_per_completion: float
    def_yac_per_completion: float