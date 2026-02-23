import pandas as pd
import sys

def inspect_sheet():
    try:
        excel_path = 'dataset/ECD Data sets.xlsx'
        print(f"Loading {excel_path}...")
        
        # Load Developmental_Assessment with header=0
        df = pd.read_excel(excel_path, sheet_name='Developmental_Assessment', header=0)
        
        print("\n" + "="*50)
        print("Developmental_Assessment (header=0)")
        print("="*50)
        print(f"Shape: {df.shape}")
        print("\nColumns (first 20):")
        print(df.columns.tolist()[:20])
        
        print("\nFirst 3 rows:")
        print(df.head(3))
        
        # Check first column for variable names
        print("\nVariable Names in First Column:")
        print(df.iloc[:, 0].head(20).tolist())
        
        # Check for child_id candidates
        print("\nPotential Child ID columns (in header):")
        child_ids = [c for c in df.columns if 'AP_ECD' in str(c)]
        print(f"Found {len(child_ids)} child IDs in columns: {child_ids[:5]}...")
                
        # Inspect ALL sheets
        xl = pd.ExcelFile(excel_path)
        print(f"\nSheet Names: {xl.sheet_names}")
        
        for sheet in xl.sheet_names:
            print(f"\n{'='*30}")
            print(f"Sheet: {sheet}")
            try:
                # Read first few rows to check headers
                d = pd.read_excel(excel_path, sheet_name=sheet, nrows=5)
                print(f"Columns: {d.columns.tolist()}")
            except Exception as e:
                print(f"Error reading sheet: {e}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_sheet()
