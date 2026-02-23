import pandas as pd

excel_path = r'c:\Users\S Sameer\Desktop\autism - Copy\dataset\ECD Data sets.xlsx'

try:
    df_da = pd.read_excel(excel_path, sheet_name='Developmental_Assessment')
    df_nb = pd.read_excel(excel_path, sheet_name='Neuro_Behavioral')
    
    dq_cols = ['GM_DQ', 'FM_DQ', 'LC_DQ', 'COG_DQ', 'SE_DQ', 'Composite_DQ']
    
    # Merge on child_id
    # Note: If there are multiple cycles, we should merge on child_id and cycle if available
    # Let's check if assessment_cycle exists in both
    if 'assessment_cycle' in df_da.columns and 'assessment_cycle' in df_nb.columns:
        df_merged = pd.merge(df_da, df_nb, on=['child_id', 'assessment_cycle'])
    else:
        df_merged = pd.merge(df_da, df_nb, on='child_id')
        
    print(f"Merged records: {len(df_merged)}")
    
    if 'autism_risk' in df_merged.columns:
        # Standardize autism_risk to match what we might expect (0/1 or Low/High)
        print("\nUnique autism_risk values:")
        print(df_merged['autism_risk'].unique())
        
        print("\nMeans by autism_risk:")
        summary = df_merged.groupby('autism_risk')[dq_cols].mean()
        print(summary)
    else:
        print("autism_risk column not found in merged data.")

except Exception as e:
    print(f"Error: {e}")
