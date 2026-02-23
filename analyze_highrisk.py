#!/usr/bin/env python
import pandas as pd
import os

os.chdir(r'c:\Users\S Sameer\Desktop\autism - Copy')

df = pd.read_csv('ml/data/engineered_features.csv')

print("=" * 100)
print("HIGH RISK vs LOW RISK ANALYSIS")
print("=" * 100)

high_risk = df[df['autism_risk'] == 1]
low_risk = df[df['autism_risk'] == 0]

print(f"\nTotal records: {len(df)}")
print(f"High Risk (autism_risk=1): {len(high_risk)}")
print(f"Low Risk (autism_risk=0): {len(low_risk)}")

features_to_analyze = [
    'gross_motor_dq', 'fine_motor_dq', 'language_dq', 'cognitive_dq', 'socio_emotional_dq', 'composite_dq',
    'adhd_risk', 'behavior_risk',
    'caregiver_engagement_score', 'stimulation_score', 'language_exposure_score'
]

print("\n" + "=" * 100)
print("FEATURE STATISTICS BY RISK LEVEL")
print("=" * 100)

comparison = pd.DataFrame({
    'Feature': features_to_analyze,
    'High Risk Mean': [high_risk[f].mean() for f in features_to_analyze],
    'Low Risk Mean': [low_risk[f].mean() for f in features_to_analyze],
})

comparison['Difference'] = comparison['High Risk Mean'] - comparison['Low Risk Mean']
print(comparison.to_string(index=False))

print("\n" + "=" * 100)
print("REPRESENTATIVE HIGH RISK EXAMPLE (First 3 high risk cases)")
print("=" * 100)

high_risk_examples = high_risk[features_to_analyze].head(3)
print(high_risk_examples.to_string())

print("\n" + "=" * 100)
print("REPRESENTATIVE LOW RISK EXAMPLE (First 3 low risk cases)")
print("=" * 100)

low_risk_examples = low_risk[features_to_analyze].head(3)
print(low_risk_examples.to_string())

print("\n" + "=" * 100)
print("STATISTICAL RANGES")
print("=" * 100)

for f in features_to_analyze:
    print(f"\n{f}:")
    print(f"  High Risk - Min: {high_risk[f].min():.2f}, Max: {high_risk[f].max():.2f}, Mean: {high_risk[f].mean():.2f}")
    print(f"  Low Risk  - Min: {low_risk[f].min():.2f}, Max: {low_risk[f].max():.2f}, Mean: {low_risk[f].mean():.2f}")

print("\n" + "=" * 100)
print("FEATURE VALUES FOR TESTING HIGH RISK")
print("=" * 100)
print("\nUse these values to test HIGH RISK classification:")
print("(Using mean values from high-risk cases)\n")

test_values = {}
for f in features_to_analyze:
    test_values[f] = round(high_risk[f].mean(), 2)
    print(f"{f}: {test_values[f]}")

print("\n" + "=" * 100)
print("FEATURE VALUES FOR TESTING LOW RISK")
print("=" * 100)
print("\nUse these values to test LOW RISK classification:")
print("(Using mean values from low-risk cases)\n")

for f in features_to_analyze:
    val = round(low_risk[f].mean(), 2)
    print(f"{f}: {val}")
