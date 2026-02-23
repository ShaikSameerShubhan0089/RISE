import pandas as pd
df = pd.read_excel('dataset/ECD Data sets.xlsx', sheet_name='Risk_Classification')
print(df.head(20))
print(df['autism_risk'].value_counts())
