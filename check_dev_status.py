import pandas as pd
df = pd.read_excel('dataset/ECD Data sets.xlsx', sheet_name='Risk_Classification')
print(df['developmental_status'].value_counts())
