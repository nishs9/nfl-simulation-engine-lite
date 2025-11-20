import pandas as pd
import numpy as np

def smoothed_win_pct(wins: int, games: int, alpha: float = 0.5, beta: float = 0.5) -> float:
    return (wins + alpha) / (games + alpha + beta)

def compute_rpi_from_schedule(schedule_df: pd.DataFrame) -> pd.DataFrame:
    # ---- Expand schedule into team-centric view ----
    home_df = schedule_df[['season', 'week', 'home_team', 'away_team', 'home_score', 'away_score']]
    home_df = home_df.rename(columns={
        'home_team': 'team', 'away_team': 'opp',
        'home_score': 'team_score', 'away_score': 'opp_score'
    })
    home_df['is_home'] = 1

    away_df = schedule_df[['season', 'week', 'home_team', 'away_team', 'home_score', 'away_score']]
    away_df = away_df.rename(columns={
        'away_team': 'team', 'home_team': 'opp',
        'away_score': 'team_score', 'home_score': 'opp_score'
    })
    away_df['is_home'] = 0

    games_df = pd.concat([home_df, away_df], ignore_index=True)
    games_df['win'] = (games_df['team_score'] > games_df['opp_score']).astype(int)

    teams = games_df['team'].unique()
    results = []

    # ---- Compute base WP for each team ----
    team_wp = {}
    for team in teams:
        t_games = games_df[games_df['team'] == team]
        wp = smoothed_win_pct(t_games['win'].sum(), len(t_games))
        team_wp[team] = wp

    # ---- Compute OWP (opponent win%) for each team ----
    team_owp = {}
    for team in teams:
        opps = games_df.loc[games_df['team'] == team, 'opp'].unique()
        opp_wp_values = []
        for opp in opps:
            opp_games = games_df[(games_df['team'] == opp) & (games_df['opp'] != team)]
            if len(opp_games) > 0:
                opp_wp = smoothed_win_pct(opp_games['win'].sum(), len(opp_games))
                opp_wp_values.append(opp_wp)
        owp = None
        if len(opp_wp_values) == 0:
            print(f"No OWP values found for team {team}")
            owp = 0.5
        else:
            owp = np.mean(opp_wp_values)
        team_owp[team] = owp

    # ---- Compute OOWP (opp of opp win%) ----
    team_oowp = {}
    for team in teams:
        opps = games_df.loc[games_df['team'] == team, 'opp'].unique()
        owp_vals = [team_owp.get(o, 0.5) for o in opps]
        oowp = None
        if len(owp_vals) == 0:
            print(f"No OWP values found for team {team}")
            oowp = 0.5
        else:
            oowp = np.mean(owp_vals)
        team_oowp[team] = oowp

    # ---- Final RPI formula ----
    for team in teams:
        rpi = 0.25 * team_wp[team] + 0.50 * team_owp[team] + 0.25 * team_oowp[team]
        games_played = len(games_df[games_df['team'] == team])
        results.append({
            'team': team,
            'games_played': games_played,
            'win_pct': team_wp[team],
            'opp_win_pct': team_owp[team],
            'opp_opp_win_pct': team_oowp[team],
            'rpi': rpi
        })

    df = pd.DataFrame(results)
    df['rpi_z_score'] = (df['rpi'] - df['rpi'].mean()) / df['rpi'].std(ddof=0)
    return df