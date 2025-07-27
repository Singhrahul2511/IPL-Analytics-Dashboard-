import pickle
import pandas as pd
import os

# --- Load Model ---
model_path = 'model/win_predictor.pkl'
model = None

if os.path.exists(model_path):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
else:
    print("Warning: Model file 'win_predictor.pkl' not found.")

def predict_win_probability(data):
    """
    Predicts win probability using the loaded model.
    'data' is a dictionary with keys: 'Team1', 'Team2', etc.
    """
    if model is None:
        return {'error': 'Model not loaded'}

    input_df = pd.DataFrame([data])
    
    probabilities = model.predict_proba(input_df)[0]
    
    # --- FIX APPLIED HERE ---
    # The keys to get the team names from the 'data' dictionary must match
    # what the API sent: 'Team1' and 'Team2' (with capital letters).
    return {
        data['Team1']: round(probabilities[0] * 100, 2),
        data['Team2']: round(probabilities[1] * 100, 2)
    }