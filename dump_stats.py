import pandas as pd
import json

df = pd.read_csv('ml/data/engineered_features.csv')

# Feature mapping
feature_map = {
    'gross_motor_dq': 'Gross Motor DQ',
    'fine_motor_dq': 'Fine Motor DQ',
    'language_dq': 'Language DQ',
    'cognitive_dq': 'Cognitive DQ',
    'socio_emotional_dq': 'Socio-Emotional DQ',
    'composite_dq': 'Composite DQ',
    'adhd_risk_score': 'ADHD Risk',
    'behavior_risk_score': 'Behavior Risk',
    'caregiver_engagement_score': 'Caregiver Engagement',
    'stimulation_score': 'Stimulation Score',
    'language_exposure_score': 'Language Exposure'
}

# Standardize risk tiers if missing
if 'risk_tier' not in df.columns:
    if 'autism_risk' in df.columns:
         df['risk_tier'] = df['autism_risk'].map({1: 'High', 0: 'Low/No'})
    else:
         df['risk_tier'] = 'Unknown'

available_cols = [col for col in feature_map.keys() if col in df.columns]

# Calculate averages
stats = df.groupby('risk_tier')[available_cols].mean().round(2).to_dict('index')

with open('stats_output.json', 'w') as f:
    json.dump({'stats': stats, 'columns': df.columns.tolist()}, f, indent=2)

print("Stats written to stats_output.json")
