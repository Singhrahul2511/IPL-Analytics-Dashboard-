from flask import Blueprint, jsonify, request
from services.model_service import predict_win_probability
from .team_routes import standardize_team_name

predictor_bp = Blueprint('predictor_bp', __name__)

@predictor_bp.route('/predict')
def predict():
    team1 = standardize_team_name(request.args.get('team1'))
    team2 = standardize_team_name(request.args.get('team2'))
    venue = request.args.get('venue')
    toss_winner = standardize_team_name(request.args.get('toss_winner'))
    toss_decision = request.args.get('toss_decision')

    # --- FIX APPLIED HERE ---
    # The dictionary keys MUST EXACTLY match the column names used for training the model.
    prediction_data = {
        'Team1': team1,
        'Team2': team2,
        'Venue': venue,
        'TossWinner': toss_winner,
        'TossDecision': toss_decision
    }
    
    result = predict_win_probability(prediction_data)
    return jsonify(result)