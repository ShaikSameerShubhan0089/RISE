import pandas as pd
import numpy as np

# Load dataset
try:
    df = pd.read_csv('ml/data/engineered_features.csv')
except Exception as e:
    print(f"Error loading dataset: {e}")
    exit()

# Identify features of interest
dq_features = [
    'gross_motor_dq', 'fine_motor_dq', 'language_dq', 
    'cognitive_dq', 'socio_emotional_dq', 'composite_dq'
]

risk_features = [
    'adhd_risk_score', 'behavior_risk_score'
]

env_features = [
    'caregiver_engagement_score', 'stimulation_score', 'language_exposure_score'
]

all_features = dq_features + risk_features + env_features
available_features = [f for f in all_features if f in df.columns]

# Target determination
target_col = None
if 'risk_tier' in df.columns:
    target_col = 'risk_tier'
elif 'autism_risk' in df.columns:
    df['risk_tier'] = df['autism_risk'].map({1: 'High', 0: 'Low/No'})
    target_col = 'risk_tier'

if target_col:
    # Ensure standard order if strings
    # We'll use the unique values sorted or a custom sort if we can guess it
    unique_tiers = df[target_col].unique()
    
    # Calculate stats
    stats = df.groupby(target_col)[available_features].mean().round(1)
    
    print("=== DATASET SUMMARY ===")
    print(f"Total Records: {len(df)}")
    print(f"Tiers Found: {unique_tiers}")
    print("\n=== FEATURE MEANS BY TIER ===")
    print(stats.to_string())
    
    print("\n=== REPRESENTATIVE EXAMPLES ===")
    for tier in sorted(unique_tiers):
        print(f"\n--- {tier} Risk Representative ---")
        example = df[df[target_col] == tier].head(1)
        if not example.empty:
            print(example[available_features].transpose())
else:
    print("Could not identify a risk target column.")
    print(f"Columns: {df.columns.tolist()[:20]}...")
