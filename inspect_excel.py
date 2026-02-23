import pandas as pd

excel_path = r'c:\Users\S Sameer\Desktop\autism - Copy\dataset\ECD Data sets.xlsx'

# List all sheets
try:
    xl = pd.ExcelFile(excel_path)
    print(f"Sheets: {xl.sheet_names}")
    
    for sheet in xl.sheet_names:
        print(f"\n--- Analysis for Sheet: {sheet} ---")
        df = pd.read_excel(excel_path, sheet_name=sheet)
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        
        # Check for DQ and Risk columns
        dq_cols = [c for c in df.columns if 'DQ' in str(c) or 'score' in str(c).lower()]
        risk_cols = [c for c in df.columns if 'risk' in str(c).lower() or 'autism' in str(c).lower()]
        
        if dq_cols and risk_cols:
            print(f"DQ columns found: {dq_cols}")
            print(f"Risk columns found: {risk_cols}")
            
            # Group by first risk column
            target = risk_cols[0]
            try:
                summary = df.groupby(target)[dq_cols].mean()
                print("\nAverages by Risk:")
                print(summary)
            except Exception as e:
                print(f"Stat error: {e}")
        else:
            print("Could not find DQ or Risk columns in this sheet.")

except Exception as e:
    print(f"Error: {e}")
