import pandas as pd
df = pd.read_csv('ml/data/cleaned_client_data.csv')
# Exclude non-numeric for corr
numeric_df = df.select_dtypes(include=['number'])
corrs = numeric_df.corr()['autism_risk'].sort_values(ascending=False)
print("Correlations with autism_risk:")
print(corrs)
