import pandas as pd

def load_data():
    """Loads and preprocesses the IPL datasets."""
    try:
        matches = pd.read_csv('data/IPL_Matches_2008_2022.csv')
        deliveries = pd.read_csv('data/IPL_Ball_by_Ball_2008_2022.csv')
    except FileNotFoundError:
        print("Error: Dataset files not found. Make sure they are in the 'data/' directory.")
        return None, None, None # Return three Nones

    # === FIX APPLIED HERE ===
    # To determine the BowlingTeam, we first need to bring Team1 and Team2 into the deliveries DataFrame.
    # We do this by merging with the matches DataFrame on the common 'ID' column.
    deliveries = pd.merge(deliveries, matches[['ID', 'Team1', 'Team2']], on='ID', how='left')

    # Now that 'Team1' and 'Team2' are available in the deliveries DataFrame, this apply() will work.
    deliveries['BowlingTeam'] = deliveries.apply(
        lambda row: row['Team2'] if row['BattingTeam'] == row['Team1'] else row['Team1'],
        axis=1
    )
    
    # Create a list of all known player names from the merged dataframe
    player_names = list(set(
        deliveries['batter'].unique().tolist() +
        deliveries['bowler'].unique().tolist()
    ))

    return matches, deliveries, player_names

# Load data and player names once when the module is imported
matches_df, deliveries_df, player_names = load_data()

# Team name aliases for fuzzy matching
team_aliases = {
    "mi": "Mumbai Indians", "mumbai": "Mumbai Indians",
    "rcb": "Royal Challengers Bangalore", "bangalore": "Royal Challengers Bangalore",
    "csk": "Chennai Super Kings", "chennai": "Chennai Super Kings",
    "dc": "Delhi Capitals", "delhi": "Delhi Capitals", "dd": "Delhi Daredevils",
    "srh": "Sunrisers Hyderabad", "sunrisers": "Sunrisers Hyderabad",
    "kkr": "Kolkata Knight Riders", "kolkata": "Kolkata Knight Riders",
    "kxip": "Kings XI Punjab", "punjab": "Punjab Kings", "pbks": "Punjab Kings",
    "rr": "Rajasthan Royals", "rajasthan": "Rajasthan Royals",
    "gt": "Gujarat Titans", "gujarat": "Gujarat Titans",
    "lsg": "Lucknow Super Giants", "lucknow": "Lucknow Super Giants"
}