import pandas as pd # Import the pandas library
from .data_service import matches_df

def get_venue_fortress_stats(team_name):
    """Calculates a team's win percentage at each venue."""
    if matches_df is None:
        return {}
    
    # Filter for matches involving the team
    team_matches = matches_df[(matches_df['Team1'] == team_name) | (matches_df['Team2'] == team_name)]
    
    if team_matches.empty:
        return {}

    # Calculate total matches and wins per venue
    venue_stats = team_matches.groupby('Venue').apply(
        lambda x: pd.Series({
            'matches_played': x.shape[0],
            'wins': x[x['WinningTeam'] == team_name].shape[0]
        })
    ).reset_index()

    # Calculate win percentage
    venue_stats['win_percentage'] = (venue_stats['wins'] / venue_stats['matches_played'] * 100).round(2)
    
    # Sort by win percentage and filter for venues with at least 5 matches
    venue_stats = venue_stats[venue_stats['matches_played'] >= 5].sort_values(by='win_percentage', ascending=False)
    
    return {
        'venues': venue_stats['Venue'].tolist(),
        'win_percentages': venue_stats['win_percentage'].tolist()
    }