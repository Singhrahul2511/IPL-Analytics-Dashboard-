from .data_service import matches_df
import pandas as pd
def get_all_teams():
    """Returns a list of all unique team names."""
    if matches_df is None:
        return []
    return sorted(list(set(matches_df['Team1'].unique().tolist() + matches_df['Team2'].unique().tolist())))

def get_all_venues():
    """Returns a sorted list of all unique venue names."""
    if matches_df is None:
        return []
    return sorted(list(matches_df['Venue'].unique()))

def get_all_seasons():
    """Returns a sorted list of all unique seasons."""
    if matches_df is None:
        return []
    return sorted(list(matches_df['Season'].unique()))

# --- New Advanced Head-to-Head Service ---
def get_advanced_head_to_head(team1, team2, season=None, venue=None):
    """
    Performs a deep analytical dive into the head-to-head matchup between two teams,
    with optional filtering by season and venue.
    """
    if matches_df is None:
        return {'error': 'Data not loaded'}

    # 1. Core Filtering Logic
    h2h_df = matches_df[
        ((matches_df['Team1'] == team1) & (matches_df['Team2'] == team2)) |
        ((matches_df['Team1'] == team2) & (matches_df['Team2'] == team1))
    ].copy()

    if season and season != 'All':
        h2h_df = h2h_df[h2h_df['Season'] == season]
    
    if venue and venue != 'All':
        h2h_df = h2h_df[h2h_df['Venue'] == venue]

    if h2h_df.empty:
        return {'summary': {'message': 'No matches found with the selected filters.'}}

    # 2. Basic Win/Loss/Draw Calculation
    total_matches = h2h_df.shape[0]
    team1_wins = h2h_df['WinningTeam'].value_counts().get(team1, 0)
    team2_wins = h2h_df['WinningTeam'].value_counts().get(team2, 0)
    draws = total_matches - (team1_wins + team2_wins)

    summary = {
        'total_matches': int(total_matches),
        team1: int(team1_wins),
        team2: int(team2_wins),
        'draws': int(draws)
    }

    # 3. Toss vs. Match Win Correlation
    toss_winners = h2h_df[h2h_df['TossWinner'] == h2h_df['WinningTeam']]
    toss_win_match_win_percent = (len(toss_winners) / total_matches * 100) if total_matches > 0 else 0
    toss_analysis = {'toss_win_match_win_percent': round(toss_win_match_win_percent, 2)}

    # 4. Win Margin Analysis
    win_margins = {}
    for team in [team1, team2]:
        team_wins_df = h2h_df[h2h_df['WinningTeam'] == team]
        if not team_wins_df.empty:
            runs_wins = team_wins_df[team_wins_df['WonBy'] == 'Runs']
            wickets_wins = team_wins_df[team_wins_df['WonBy'] == 'Wickets']
            win_margins[team] = {
                'avg_run_margin': round(runs_wins['Margin'].mean(), 2) if not runs_wins.empty else 0,
                'max_run_margin': int(runs_wins['Margin'].max()) if not runs_wins.empty else 0,
                'big_run_wins (>50)': int((runs_wins['Margin'] > 50).sum()),
                'avg_wicket_margin': round(wickets_wins['Margin'].mean(), 2) if not wickets_wins.empty else 0,
                'max_wicket_margin': int(wickets_wins['Margin'].max()) if not wickets_wins.empty else 0,
                'big_wicket_wins (>7)': int((wickets_wins['Margin'] > 7).sum())
            }
        else:
            win_margins[team] = {}

    # 5. Winning Streak Analysis
    h2h_df = h2h_df.sort_values(by='Date').dropna(subset=['WinningTeam'])
    streaks = {team1: 0, team2: 0, 'current_streak_team': None, 'current_streak_count': 0}
    max_streaks = {team1: 0, team2: 0}

    if not h2h_df.empty:
        for winner in h2h_df['WinningTeam']:
            if streaks['current_streak_team'] == winner:
                streaks['current_streak_count'] += 1
            else:
                streaks['current_streak_team'] = winner
                streaks['current_streak_count'] = 1
            
            if streaks['current_streak_count'] > max_streaks.get(winner, 0):
                max_streaks[winner] = streaks['current_streak_count']
    
    # --- Combine all analytics into a single response ---
    return {
        'summary': summary,
        'toss_analysis': toss_analysis,
        'win_margins': win_margins,
        'streaks': max_streaks
    }
