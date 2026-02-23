import pickle
import pandas as pd
import numpy as np

model_path = 'ml/models/saved/autism_risk_classifier_v1.pkl'
with open(model_path, 'rb') as f:
    data = pickle.load(f)

model = data['model']
calibrated = data['calibrated_model']
scaler = data['scaler']

from ml.models.autism_risk_classifier import AutismRiskClassifier

classifier = AutismRiskClassifier.load_model(model_path)

# Load engineered data (using the saved one)
df = pd.read_csv('ml/data/engineered_features.csv')
sample = df.sample(100)
X, y = classifier.prepare_data(sample)

X_scaled = classifier.scaler.transform(X)
raw_probs = classifier.model.predict_proba(X_scaled)[:, 1]
cal_probs = classifier.calibrated_model.predict_proba(X_scaled)[:, 1]

print("--- RAW PROBABILITIES ---")
print(pd.Series(raw_probs).describe())
print("\n--- CALIBRATED PROBABILITIES ---")
print(pd.Series(cal_probs).describe())

print("\nRisk class count in sample:", y.sum())
