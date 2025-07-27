from flask import Blueprint, jsonify, request
from services.team_service import get_all_teams, get_all_seasons, get_all_venues, get_advanced_head_to_head
# ... (keep standardize_team_name if you have it)
from services.data_service import team_aliases
from difflib import get_close_matches

team_bp = Blueprint('team_bp', __name__)

def standardize_team_name(name):
    name_lower = name.strip().lower()
    if name_lower in team_aliases:
        return team_aliases[name_lower]
    
    official_teams = get_all_teams()
    match = get_close_matches(name.title(), official_teams, n=1, cutoff=0.6)
    return match[0] if match else name

@team_bp.route('/teams')
def teams():
    return jsonify(get_all_teams())

@team_bp.route('/venues')
def venues():
    return jsonify(get_all_venues())

@team_bp.route('/seasons')
def seasons():
    return jsonify(get_all_seasons())
    
# --- New Advanced Head-to-Head Endpoint ---
@team_bp.route('/team-head-to-head')
def head_to_head():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    season_str = request.args.get('season') # Season might be a string like "2008" or "All"
    venue = request.args.get('venue')

    # Convert season to int if it's a numeric string, otherwise pass as is
    season = int(season_str) if season_str and season_str.isdigit() else season_str

    stats = get_advanced_head_to_head(team1, team2, season, venue)
    return jsonify(stats)