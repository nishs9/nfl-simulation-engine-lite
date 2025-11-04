from scipy.stats import lognorm
from nfl_simulation_engine_lite.team.team_stats import TeamStats
from nfl_simulation_engine_lite.team.team_rates import TeamRates
import numpy as np
import pandas as pd

class Team:
    def __init__(self, name: str, stats: TeamStats, team_rates: TeamRates, rpi_data: dict = None):
        self.name = name
        self.stats = stats
        self.team_rates = team_rates
        self.rpi_data = rpi_data
        self.off_passing_distribution = None
        self.def_passing_distribution = None
        self.off_rushing_distribution = None
        self.def_rushing_distribution = None
        self.off_air_yards_distribution = None
        self.def_air_yards_allowed_distribution = None

    def setup_stat_distributions(self, game_model_str: str) -> None:
        if game_model_str == "proto" or game_model_str == "v2":
            pass
        elif game_model_str == "v1" or game_model_str == "v1a":
            self.off_passing_distribution = self.init_distribution(self.stats.off_pass_yards_per_play_mean, self.stats.off_pass_yards_per_play_variance)
            self.def_passing_distribution = self.init_distribution(self.stats.def_pass_yards_per_play_mean, self.stats.def_pass_yards_per_play_variance)

            self.off_rushing_distribution = self.init_distribution(self.stats.off_rush_yards_per_play_mean, self.stats.off_rush_yards_per_play_variance)
            self.def_rushing_distribution = self.init_distribution(self.stats.def_rush_yards_per_play_mean, self.stats.def_rush_yards_per_play_variance)
        elif game_model_str == "v1b":
            self.off_air_yards_distribution = self.init_distribution(self.stats.off_air_yards_per_attempt, self.stats.off_pass_yards_per_play_variance)
            self.def_air_yards_allowed_distribution = self.init_distribution(self.stats.def_air_yards_per_attempt, self.stats.def_pass_yards_per_play_variance)

            self.off_rushing_distribution = self.init_distribution(self.stats.off_rush_yards_per_play_mean, self.stats.off_rush_yards_per_play_variance)
            self.def_rushing_distribution = self.init_distribution(self.stats.def_rush_yards_per_play_mean, self.stats.def_rush_yards_per_play_variance)
        else:
            raise ValueError(f"Invalid game model string: {game_model_str}")
        
    def init_distribution(self, mean: float, variance: float):
        sigma = np.sqrt(np.log(1 + (variance / mean**2)))
        mu = np.log(mean) - (sigma**2) / 2
        dist = lognorm(s=sigma, scale=np.exp(mu))
        return dist
    
    def sample_offensive_passing_play(self) -> float:
        return self.off_passing_distribution.rvs()
    
    def sample_defensive_passing_play(self) -> float:
        return self.def_passing_distribution.rvs()
    
    def sample_offensive_rushing_play(self) -> float:
        return self.off_rushing_distribution.rvs()
    
    def sample_defensive_rushing_play(self) -> float:
        return self.def_rushing_distribution.rvs()
    
    def sample_offensive_air_yards(self) -> float:
        return self.off_air_yards_distribution.rvs()
    
    def sample_defensive_air_yards(self) -> float:
        return self.def_air_yards_allowed_distribution.rvs()
    
    def __str__(self) -> str:
        return f"Team object representing {self.name}"
    
    def get_name(self) -> str:
        return self.name
    
    def set_name(self, name: str) -> None:
        self.name = name

    def get_stats(self) -> TeamStats:
        return self.stats
    
    def set_stats(self, stats: TeamStats) -> None:
        self.stats = stats

    def get_rpi_data(self) -> dict:
        return self.rpi_data

    def set_rpi_data(self, rpi_data: dict) -> None:
        self.rpi_data = rpi_data

    def get_team_rates(self) -> TeamRates:
        return self.team_rates

    def set_team_rates(self, team_rates: TeamRates) -> None:
        self.team_rates = team_rates
