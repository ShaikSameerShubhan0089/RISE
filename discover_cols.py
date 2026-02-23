import pandas as pd

excel_path = r'c:\Users\S Sameer\Desktop\autism - Copy\dataset\ECD Data sets.xlsx'

try:
    xl = pd.ExcelFile(excel_path)
    for sheet in xl.sheet_names:
        df = pd.read_excel(excel_path, sheet_name=sheet, nrows=0)
        print(f"Sheet: {sheet}")
        print(f"Columns: {df.columns.tolist()}\n")

except Exception as e:
    print(f"Error: {e}")
