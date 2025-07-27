from flask import Flask, render_template
import os

from api.team_routes import team_bp
from api.player_routes import player_bp
from api.venue_routes import venue_bp
from api.predictor import predictor_bp # Import the new blueprint

from services.team_service import get_all_teams, get_all_venues

# --- App & Cache Configuration ---
app = Flask(__name__)


# --- Register Blueprints for API routes ---
app.register_blueprint(team_bp, url_prefix='/api')
app.register_blueprint(player_bp, url_prefix='/api')
app.register_blueprint(venue_bp, url_prefix='/api')
app.register_blueprint(predictor_bp, url_prefix='/api')

# --- Main Route ---
@app.route('/')
def home():
    """Renders the main dashboard page with initial data."""
    teams = get_all_teams()
    venues = get_all_venues()
    if not teams or not venues:
        return "Error: Could not load initial data.", 500
    return render_template('index.html', teams=teams, venues=venues)
@app.route('/hybridaction/<path:anything>')
def block_tracker(anything):
    return '', 204  # No Content
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)