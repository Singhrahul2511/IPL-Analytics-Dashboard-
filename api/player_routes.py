from flask import Blueprint, jsonify, request
from services.player_service import get_batsman_summary, get_bowler_summary, get_player_runs_per_season, standardize_player_name
from flask import Blueprint, jsonify, request
from services.player_service import (
    standardize_player_name, 
    get_player_vs_player_stats, 
    get_performance_by_phase
)

player_bp = Blueprint('player_bp', __name__)

@player_bp.route('/head-to-head')
def head_to_head():
    batsman_raw = request.args.get('batsman')
    bowler_raw = request.args.get('bowler')
    
    batsman = standardize_player_name(batsman_raw)
    bowler = standardize_player_name(bowler_raw)
    
    stats = get_player_vs_player_stats(batsman, bowler)
    return jsonify({
        'corrected_batsman': batsman,
        'corrected_bowler': bowler,
        'stats': stats
    })

@player_bp.route('/phase-analysis')

def phase_analysis():
    player_raw = request.args.get('player')
    role = request.args.get('role')
    
    player = standardize_player_name(player_raw)
    stats = get_performance_by_phase(player, role)
    
    return jsonify({
        'corrected_player': player,
        'role': role,
        'stats': stats
    })

@player_bp.route('/player-stats')
def player_stats():
    player_name_raw = request.args.get('player')
    role = request.args.get('role', 'batsman') # Default to batsman
    
    player_name = standardize_player_name(player_name_raw)
    
    if role == 'batsman':
        summary = get_batsman_summary(player_name)
    else:
        summary = get_bowler_summary(player_name)
        
    return jsonify({
        'corrected_name': player_name,
        'summary': summary
    })

@player_bp.route('/player-runs-per-season')
def player_runs_chart():
    player_name_raw = request.args.get('player')
    player_name = standardize_player_name(player_name_raw)
    chart_data = get_player_runs_per_season(player_name)
    return jsonify(chart_data)

@player_bp.route('/player-head-to-head')
def player_head_to_head():
    """Handles Player vs Player head-to-head analysis."""
    batsman_raw = request.args.get('batsman')
    bowler_raw = request.args.get('bowler')
    
    # Standardize names to handle variations
    batsman = standardize_player_name(batsman_raw)
    bowler = standardize_player_name(bowler_raw)
    
    # Call the correct service function from player_service
    stats = get_player_vs_player_stats(batsman, bowler)
    
    return jsonify({
        'corrected_batsman': batsman,
        'corrected_bowler': bowler,
        'stats': stats
    })