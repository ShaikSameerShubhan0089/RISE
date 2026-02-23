import pandas as pd
df = pd.read_csv('ml/data/cleaned_client_data.csv')
high_risk = df[df['autism_risk'] == 1]
low_risk = df[df['autism_risk'] == 0]

print("High Risk Stats:")
print(high_risk[['socio_emotional_dq', 'language_dq', 'composite_dq', 'behavior_score', 'delayed_domains']].describe())

print("\nLow Risk Stats:")
print(low_risk[['socio_emotional_dq', 'language_dq', 'composite_dq', 'behavior_score', 'delayed_domains']].describe())
