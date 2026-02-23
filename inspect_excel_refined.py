import pandas as pd
import numpy as np

excel_path = r'c:\Users\S Sameer\Desktop\autism - Copy\dataset\ECD Data sets.xlsx'

try:
    # 1. Look at Neuro_Behavioral (likely source of risk labels)
    print("--- Sheet: Neuro_Behavioral ---")
    df_nb = pd.read_excel(excel_path, sheet_name='Neuro_Behavioral')
    print(df_nb[['child_id', 'autism_risk', 'adhd_risk', 'behavior_risk']].head(5))
    
    # 2. Look at Developmental_Assessment (source of DQ scores)
    print("\n--- Sheet: Developmental_Assessment ---")
    df_da = pd.read_excel(excel_path, sheet_name='Developmental_Assessment')
    dq_cols = ['gross_motor_dq', 'fine_motor_dq', 'language_dq', 'cognitive_dq', 'socio_emotional_dq', 'composite_dq']
    print(df_da[['child_id', 'assessment_cycle'] + dq_cols].head(5))
    
    # 3. Merge and check correlation
    print("\n--- Correlation Analysis (Merged) ---")
    df_merged = pd.merge(df_da, df_nb, on=['child_id', 'assessment_cycle'], how='inner')
    
    if 'autism_risk' in df_merged.columns:
        corr = df_merged[['autism_risk'] + dq_cols].corr()['autism_risk']
        print("\nCorrelation with autism_risk:")
        print(corr)
        
        print("\nMeans by autism_risk:")
        print(df_merged.groupby('autism_risk')[dq_cols].mean())
    else:
        print("Required columns for correlation not found in merged data.")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
