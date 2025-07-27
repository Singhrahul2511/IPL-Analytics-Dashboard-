import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pickle
import os

print("Loading data...")
# Adjust path as needed
matches = pd.read_csv('data/IPL_Matches_2008_2022.csv')

# --- Feature Engineering ---
# 1. Simplify WinningTeam to a binary outcome (0 for Team1, 1 for Team2)
# We need to handle non-decisive matches (e.g., tied/no result)
df = matches.dropna(subset=['WinningTeam']) # Drop matches with no winner
df['outcome'] = (df['WinningTeam'] == df['Team2']).astype(int)

# 2. Select features
features = ['Team1', 'Team2', 'Venue', 'TossWinner', 'TossDecision']
X = df[features]
y = df['outcome']

print("Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- Model Pipeline ---
# Define the preprocessing steps for categorical features
# OneHotEncoder will create binary columns for each category and handle unknown values
categorical_features = ['Team1', 'Team2', 'Venue', 'TossWinner', 'TossDecision']
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

# Create the logistic regression pipeline
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(solver='liblinear'))
])

print("Training model...")
model_pipeline.fit(X_train, y_train)

# --- Evaluate and Save ---
accuracy = model_pipeline.score(X_test, y_test)
print(f"Model Accuracy: {accuracy:.4f}")

# Ensure the model directory exists
if not os.path.exists('model'):
    os.makedirs('model')

# Save the trained model pipeline
model_path = 'model/win_predictor.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(model_pipeline, f)

print(f"Model saved successfully to {model_path}")