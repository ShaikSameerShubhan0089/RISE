import pandas as pd

excel_path = r'c:\Users\S Sameer\Desktop\autism - Copy\dataset\ECD Data sets.xlsx'
xl = pd.ExcelFile(excel_path)

for sheet in xl.sheet_names:
    df = pd.read_excel(excel_path, sheet_name=sheet, nrows=0)
    dq_cols = [c for c in df.columns if 'DQ' in str(c)]
    if dq_cols:
        print(f"Sheet: {sheet}")
        print(f"DQ Columns: {dq_cols}")
