import numpy as np
from difflib import get_close_matches
from .data_service import deliveries_df, matches_df, player_names, team_aliases

def standardize_player_name(name):
    """Finds the closest matching official player name."""
    name_lower = name.strip().lower()
    # Direct match check first for performance
    if name_lower in [p.lower() for p in player_names]:
        return [p for p in player_names if p.lower() == name_lower][0]
    
    match = get_close_matches(name_lower, [p.lower() for p in player_names], n=1, cutoff=0.6)
    if match:
        # Find original casing
        return [p for p in player_names if p.lower() == match[0]][0]
    return name # Return original if no good match

#batsman summary
def get_batsman_summary(player_name):
    """Generates a comprehensive summary of a batsman's performance."""
    if deliveries_df is None or matches_df is None:
        return {}
    
    player_df = deliveries_df[deliveries_df['batter'] == player_name]
    if player_df.empty:
        return {}

    # --- Basic Stats ---
    runs = int(player_df['batsman_run'].sum())
    balls_faced = player_df[~player_df['extra_type'].isin(['wides'])].shape[0]
    
    # --- Innings & Dismissals ---
    innings = int(player_df['ID'].nunique())
    dismissals = player_df[player_df['player_out'] == player_name].shape[0]
    not_out = innings - dismissals

    # --- Averages & Strike Rate ---
    avg = (runs / dismissals) if dismissals > 0 else float('inf')
    strike_rate = (runs / balls_faced * 100) if balls_faced > 0 else 0.0

    # --- Scores & Milestones ---
    # Group by match to calculate runs per innings
    innings_scores = player_df.groupby('ID')['batsman_run'].sum()
    
    fifties = int(innings_scores[(innings_scores >= 50) & (innings_scores < 100)].count())
    hundreds = int(innings_scores[innings_scores >= 100].count())
    highest_score = int(innings_scores.max()) if not innings_scores.empty else 0
    
    # --- Awards ---
    # Man of the Match awards are in the matches_df
    mom_awards = int(matches_df[matches_df['Player_of_Match'] == player_name].shape[0])

    # --- Final Dictionary ---
    return {
        "Innings": innings,
        "Total Runs": runs,
        "Dismissals": dismissals,
        "Not Out": not_out,
        "Average": f"{avg:.2f}",
        "Strike Rate": f"{strike_rate:.2f}",
        "Fifties": fifties,
        "Hundreds": hundreds,
        "Highest Score": highest_score,
        "Fours": int(player_df[player_df['batsman_run'] == 4].shape[0]),
        "Sixes": int(player_df[player_df['batsman_run'] == 6].shape[0]),
        "Man of the Match": mom_awards,
    }

#boller summary
def get_bowler_summary(player_name):
    """Generates a comprehensive summary of a bowler's performance."""
    if deliveries_df is None or matches_df is None:
        return {}
    
    player_df = deliveries_df[deliveries_df['bowler'] == player_name].copy()
    if player_df.empty:
        return {}

    # --- Accurately calculate runs conceded by the bowler ---
    # This excludes byes and legbyes, which aren't charged to the bowler.
    player_df['bowler_run'] = player_df['total_run'] - player_df['extras_run']
    player_df.loc[player_df['extra_type'].isin(['byes', 'legbyes']), 'bowler_run'] = 0

    # --- Basic Stats ---
    innings = int(player_df['ID'].nunique())
    runs_conceded = int(player_df['bowler_run'].sum())
    balls_bowled = player_df[~player_df['extra_type'].isin(['wides', 'noballs'])].shape[0]
    overs_bowled = f"{(balls_bowled // 6)}.{balls_bowled % 6}"
    
    # --- Wickets & Averages ---
    wickets = int(player_df[player_df['isWicketDelivery'] == 1].shape[0])
    economy = (runs_conceded / (balls_bowled / 6)) if balls_bowled > 0 else 0.0
    average = (runs_conceded / wickets) if wickets > 0 else float('inf')
    strike_rate = (balls_bowled / wickets) if wickets > 0 else float('inf')
    
    # --- Milestones & Best Performance ---
    # Group by match to calculate wickets per innings
    innings_stats = player_df.groupby('ID').agg(
        wickets_taken=('isWicketDelivery', 'sum'),
        runs_given=('bowler_run', 'sum')
    )
    
    three_wickets = int(innings_stats[innings_stats['wickets_taken'] >= 3].count()['wickets_taken'])
    five_wickets = int(innings_stats[innings_stats['wickets_taken'] >= 5].count()['wickets_taken'])
    
    # Calculate best bowling figures
    if not innings_stats.empty:
        best_figures_row = innings_stats.sort_values(by=['wickets_taken', 'runs_given'], ascending=[False, True]).iloc[0]
        best_figures = f"{int(best_figures_row['wickets_taken'])}/{int(best_figures_row['runs_given'])}"
    else:
        best_figures = "N/A"

    # --- Awards ---
    mom_awards = int(matches_df[matches_df['Player_of_Match'] == player_name].shape[0])

    # --- Final Dictionary ---
    return {
        "Innings": innings,
        "Overs Bowled": overs_bowled,
        "Wickets": wickets,
        "Runs Conceded": runs_conceded,
        "Average": f"{average:.2f}",
        "Economy": f"{economy:.2f}",
        "Strike Rate": f"{strike_rate:.2f}",
        "3+ Wicket Hauls": three_wickets,
        "5+ Wicket Hauls": five_wickets,
        "Best Figures": best_figures,
        "Man of the Match": mom_awards,
    }


def get_player_runs_per_season(player_name):
    """Calculates a player's runs season by season."""
    if deliveries_df is None or matches_df is None: return {}

    player_df = deliveries_df[deliveries_df['batter'] == player_name]
    # Merge with matches to get Season info
    merged_df = player_df.merge(matches_df[['ID', 'Season']], on='ID')
    
    seasonal_runs = merged_df.groupby('Season')['batsman_run'].sum().sort_index()

    return {
        'seasons': seasonal_runs.index.astype(str).tolist(),
        'runs': seasonal_runs.values.tolist()
    }


def get_player_vs_player_stats(batsman, bowler):
    """Calculates head-to-head stats for a batsman against a bowler."""
    if deliveries_df is None: return {}
    
    h2h_df = deliveries_df[(deliveries_df['batter'] == batsman) & (deliveries_df['bowler'] == bowler)]
    if h2h_df.empty:
        return {"runs_scored": 0, "dismissals": 0, "strike_rate": 0.0}

    runs = int(h2h_df['batsman_run'].sum())
    balls = h2h_df[~h2h_df['extra_type'].isin(['wides'])].shape[0]
    dismissals = int(h2h_df[h2h_df['player_out'] == batsman].shape[0])
    strike_rate = (runs / balls * 100) if balls > 0 else 0.0

    return {
        "runs_scored": runs,
        "balls_faced": balls,
        "dismissals": dismissals,
        "strike_rate": f"{strike_rate:.2f}"
    }

def get_performance_by_phase(player_name, role):
    """Analyzes player performance across different match phases."""
    if deliveries_df is None: return {}

    phases = {
        'Powerplay': (deliveries_df['overs'] >= 0) & (deliveries_df['overs'] < 6),
        'Middle': (deliveries_df['overs'] >= 6) & (deliveries_df['overs'] < 15),
        'Death': (deliveries_df['overs'] >= 15) & (deliveries_df['overs'] < 20)
    }

    results = {}
    if role == 'batsman':
        df = deliveries_df[deliveries_df['batter'] == player_name]
        for phase, condition in phases.items():
            phase_df = df[condition]
            runs = int(phase_df['batsman_run'].sum())
            balls = phase_df[~phase_df['extra_type'].isin(['wides'])].shape[0]
            strike_rate = (runs / balls * 100) if balls > 0 else 0
            results[phase] = {'runs': runs, 'strike_rate': round(strike_rate, 2)}
    else: # bowler
        df = deliveries_df[deliveries_df['bowler'] == player_name]
        for phase, condition in phases.items():
            phase_df = df[condition]
            runs = int(phase_df['total_run'].sum())
            wickets = int(phase_df['isWicketDelivery'].sum())
            balls = phase_df[~phase_df['extra_type'].isin(['wides', 'noballs'])].shape[0]
            economy = (runs / (balls / 6)) if balls > 0 else 0
            results[phase] = {'wickets': wickets, 'economy': round(economy, 2)}
            
    return results