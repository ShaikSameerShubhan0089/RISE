import pickle
import os

model_path = 'ml/models/saved/autism_risk_classifier_v1.pkl'
if os.path.exists(model_path):
    with open(model_path, 'rb') as f:
        data = pickle.load(f)
    print("--- MODEL A METRICS ---")
    for k, v in data['metrics'].items():
        print(f"{k}: {v}")
else:
    print("Model A not found")

esc_model_path = 'ml/models/saved/risk_escalation_predictor_v1.pkl'
if os.path.exists(esc_model_path):
    with open(esc_model_path, 'rb') as f:
        data = pickle.load(f)
    print("\n--- MODEL B METRICS ---")
    for k, v in data['metrics'].items():
        print(f"{k}: {v}")
else:
    print("\nModel B not found - check terminal output for longitudinal data availability.")
