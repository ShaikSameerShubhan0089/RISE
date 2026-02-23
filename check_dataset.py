import pandas as pd
import os

dataset_path = 'dataset/ECD Data sets.xlsx'
output_path = 'dataset_columns.txt'
if os.path.exists(dataset_path):
    xl = pd.ExcelFile(dataset_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        for s in xl.sheet_names:
            f.write(f"--- SHEET: {s} ---\n")
            df = pd.read_excel(xl, s, nrows=0)
            f.write(str(list(df.columns)) + "\n\n")
    print(f"Columns written to {output_path}")
else:
    print(f"File not found: {dataset_path}")
