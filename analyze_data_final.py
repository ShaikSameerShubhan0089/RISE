import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv('ml/data/engineered_features.csv')

# Identify features
features = [
    'gross_motor_dq', 'fine_motor_dq', 'language_dq', 
    'cognitive_dq', 'socio_emotional_dq', 'composite_dq',
    'adhd_risk_score', 'behavior_risk_score',
    'caregiver_engagement_score', 'stimulation_score', 'language_exposure_score'
]

# Standardize risk tiers
if 'risk_tier' not in df.columns:
    if 'autism_risk' in df.columns:
         df['risk_tier'] = df['autism_risk'].map({1: 'High', 0: 'Low/No'})
    else:
         # Fallback to something
         df['risk_tier'] = 'Unknown'

# Filter to available features
available = [f for f in features if f in df.columns]

# Print stats row by row to avoid truncation
print("--- START ANALYSIS ---")
for tier in df['risk_tier'].unique():
    print(f"TIER: {tier}")
    subset = df[df['risk_tier'] == tier]
    means = subset[available].mean().round(2)
    for feat, val in means.items():
        print(f"  {feat}: {val}")
    print("-" * 20)
print("--- END ANALYSIS ---")
