from game_model.GameModel import GameModel
import random

class PrototypeGameModel(GameModel):

    def __init__(self, off_weight=0.55):
        super().__init__(off_weight=off_weight)

    def get_model_code(self) -> str:
        return "proto"
    
    def resolve_play(self, game_state: dict) -> dict:
        posteam = game_state["possession_team"]
        posteam_stats = posteam.get_stats()

        defteam = game_state["defense_team"]
        defteam_stats = defteam.get_stats()

        time_elapsed = random.randint(15,40)

        # Handle 4th down scenarios
        if game_state["down"] == 4 and game_state["yardline"] > 55:
            return {
                "play_type": "punt", 
                "field_goal_made": None,
                "yards_gained": 40,
                "time_elapsed": time_elapsed, 
                "quarter": game_state["quarter"],
                "quarter_seconds_remaining": game_state["quarter_seconds_remaining"],
                "turnover": False,
                "touchdown": False,
                "posteam": posteam.name
            }
        elif game_state["down"] == 4 and game_state["yardline"] <= 45:
            fg_success_rate = posteam.get_stat("field_goal_success_rate")
            return {
                "play_type": "field_goal", 
                "field_goal_made": random.choices([True, False], [fg_success_rate, 1 - fg_success_rate])[0],
                "yards_gained": 0,
                "time_elapsed": time_elapsed,
                "quarter": game_state["quarter"],
                "quarter_seconds_remaining": game_state["quarter_seconds_remaining"],  
                "turnover": False,
                "touchdown": False,
                "posteam": posteam.name
            }
        
        # If not 4th down, run normal simulation logic
        play_type = random.choices(['run', 'pass'], [posteam_stats.run_rate, posteam_stats.pass_rate])[0]

        off_yards_per_play = None
        def_yards_per_play = None
        if (play_type == "run"):
            off_yards_per_play = posteam_stats.rush_yards_per_carry
            def_yards_per_play = defteam_stats.rush_yards_per_carry_allowed
        else:
            off_yards_per_play = posteam_stats.yards_per_completion
            def_yards_per_play = defteam_stats.yards_allowed_per_completion
        
        weighted_yards_per_play = self.get_weighted_average(off_yards_per_play, def_yards_per_play)

        if (play_type == "pass"):
            off_pass_cmp_rate = posteam_stats.pass_completion_rate / 100
            def_pass_cmp_rate = defteam_stats.pass_completion_rate_allowed / 100
            weighted_pass_cmp_rate = self.get_weighted_average(off_pass_cmp_rate, def_pass_cmp_rate)
            pass_completed = random.choices([True, False], [weighted_pass_cmp_rate, 1 - weighted_pass_cmp_rate])[0]
            if (not pass_completed):
               weighted_yards_per_play = 0 

        off_turnover_rate = posteam_stats.turnover_rate
        def_turnover_rate = defteam_stats.forced_turnover_rate
        weighted_turnover_rate = self.get_weighted_average(off_turnover_rate, def_turnover_rate)
        turnover_on_play = random.choices([True, False], [weighted_turnover_rate, 1 - weighted_turnover_rate])[0]

        if (not turnover_on_play):
            yards_gained = weighted_yards_per_play
        else:
            yards_gained = 0

        off_sack_rate = posteam_stats.sacks_allowed_rate
        def_sack_rate = defteam_stats.sacks_made_rate
        weighted_sack_rate = self.get_weighted_average(off_sack_rate, def_sack_rate)
        sack_on_play = random.choices([True, False], [weighted_sack_rate, 1 - weighted_sack_rate])[0]

        if (sack_on_play and play_type == "pass"):
            off_yards_lost_per_sack = posteam_stats.sack_yards_allowed
            def_yards_inflicted_per_sack = defteam_stats.sack_yards_inflicted
            yards_lost_on_sack = self.get_weighted_average(off_yards_lost_per_sack, def_yards_inflicted_per_sack)
            yards_gained = yards_lost_on_sack

        return {
            "play_type": play_type, 
            "field_goal_made": None,
            "yards_gained": yards_gained,
            "time_elapsed": time_elapsed,
            "quarter": game_state["quarter"],
            "quarter_seconds_remaining": game_state["quarter_seconds_remaining"],
            "turnover": turnover_on_play,
            "touchdown": False, # This will be updated after the play is processed in update_game_state
            "posteam": posteam.name
        }

    