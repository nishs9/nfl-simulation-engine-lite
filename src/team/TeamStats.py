from dataclasses import dataclass

@dataclass(slots=True)
class TeamStats:
    team: str = None
    games_played: int = 0

    pass_rate: float = 0
    pass_completion_rate: float = 0
    yards_per_completion: float = 0
    pass_completion_rate_allowed: float = 0
    yards_allowed_per_completion: float = 0

    run_rate: float = 0
    rush_yards_per_carry: float = 0
    rush_yards_per_carry_allowed: float = 0

    turnover_rate: float = 0
    forced_turnover_rate: float = 0
    
    sacks_allowed_rate: float = 0
    sack_yards_allowed: float = 0
    sacks_made_rate: float = 0
    sack_yards_inflicted: float = 0

    field_goal_success_rate: float = 0

    off_rush_yards_per_play_mean: float = 0
    off_rush_yards_per_play_variance: float = 0
    def_rush_yards_per_play_mean: float = 0
    def_rush_yards_per_play_variance: float = 0

    off_pass_yards_per_play_mean: float = 0
    off_pass_yards_per_play_variance: float = 0
    def_pass_yards_per_play_mean: float = 0
    def_pass_yards_per_play_variance: float = 0

    off_air_yards_per_attempt: float = 0
    def_air_yards_per_attempt: float = 0
    off_yac_per_completion: float = 0
    def_yac_per_completion: float = 0