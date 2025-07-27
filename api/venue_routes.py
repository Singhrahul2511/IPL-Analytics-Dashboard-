from flask import Blueprint, jsonify, request
from services.venue_service import get_venue_fortress_stats
from .team_routes import standardize_team_name

venue_bp = Blueprint('venue_bp', __name__)

@venue_bp.route('/venue-fortress')
def venue_fortress():
    team_name = standardize_team_name(request.args.get('team'))
    stats = get_venue_fortress_stats(team_name)
    return jsonify(stats)