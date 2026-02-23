import pandas as pd
import os

file_path = r'C:\Users\S Sameer\Desktop\autism - Copy\dataset\ECD Data sets.xlsx'

if not os.path.exists(file_path):
    print(f"Error: {file_path} not found")
    exit(1)

try:
    # Read all sheets
    excel_data = pd.read_excel(file_path, sheet_name=None)
    
    print(f"Total Sheets: {len(excel_data)}")
    print("="*60)
    
    for sheet_name, df in excel_data.items():
        print(f"\nSheet: {sheet_name}")
        print(f"Shape: {df.shape}")
        print("-" * 30)
        print("Columns:")
        for col in df.columns:
            null_count = df[col].isnull().sum()
            dtype = df[col].dtype
            print(f"  - {col} ({dtype}): {null_count} nulls")
        
        print("\nFirst 5 rows:")
        print(df.head())
        print("="*60)

except Exception as e:
    print(f"Error: {e}")
