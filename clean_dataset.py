import pandas as pd
import numpy as np
import os

def clean_dataset(file_path, output_path):
    print(f"Loading dataset from {file_path}...")
    excel_data = pd.read_excel(file_path, sheet_name=None)
    
    # Start with Registration as base
    df = excel_data['Registration'].copy()
    
    # Merge with other key sheets
    sheets_to_merge = [
        'Developmental_Risk',
        'Neuro_Behavioral',
        'Nutrition',
        'Environment_Caregiving',
        'Developmental_Assessment',
        'Behaviour_Indicators'
    ]
    
    for sheet in sheets_to_merge:
        df = pd.merge(df, excel_data[sheet], on='child_id', how='left', suffixes=('', f'_{sheet}'))

    print("Columns after merge:", df.columns.tolist())

    # Create target dataframe for ML
    ml_df = pd.DataFrame()
    ml_df['child_id'] = df['child_id']
    ml_df['assessment_cycle'] = df['assessment_cycle']
    ml_df['age_months'] = df['age_months']
    ml_df['gender'] = df['gender']
    
    # DQ scores
    ml_df['gross_motor_dq'] = df['GM_DQ']
    ml_df['fine_motor_dq'] = df['FM_DQ']
    ml_df['language_dq'] = df['LC_DQ']
    ml_df['cognitive_dq'] = df['COG_DQ']
    ml_df['socio_emotional_dq'] = df['SE_DQ']
    ml_df['composite_dq'] = df['Composite_DQ']
    
    # Delays
    ml_df['gross_motor_delay'] = df['GM_delay'].astype(bool)
    ml_df['fine_motor_delay'] = df['FM_delay'].astype(bool)
    ml_df['language_delay'] = df['LC_delay'].astype(bool)
    ml_df['cognitive_delay'] = df['COG_delay'].astype(bool)
    ml_df['socio_emotional_delay'] = df['SE_delay'].astype(bool)
    ml_df['delayed_domains'] = df['num_delays']
    
    # Behavior
    # Check if behaviour_score or behavior_score exists
    b_score_col = 'behaviour_score' if 'behaviour_score' in df.columns else 'behavior_score'
    ml_df['behavior_score'] = df[b_score_col]
    
    b_risk_col = 'behaviour_risk_level' if 'behaviour_risk_level' in df.columns else 'behavior_risk'
    binary_risk_map = {'High': True, 'Moderate': False, 'Low': False, 'Medium': False}
    ml_df['behavior_risk'] = df[b_risk_col].map(binary_risk_map).fillna(False)
    
    ml_df['adhd_risk'] = df['adhd_risk'].map(binary_risk_map).fillna(False)
    ml_df['attention_score'] = 100 - ml_df['behavior_score']
    
    # Nutrition
    ml_df['stunting'] = df['stunting'].astype(bool)
    ml_df['wasting'] = df['wasting'].astype(bool)
    ml_df['anemia'] = df['anemia'].astype(bool)
    ml_df['nutrition_score'] = df['nutrition_score']
    
    # Environment
    engagement_map = {'High': 90, 'Moderate': 60, 'Low': 30, 'Medium': 60}
    ml_df['caregiver_engagement_score'] = df['caregiver_engagement'].map(engagement_map).fillna(50)
    ml_df['language_exposure_score'] = df['language_exposure'].map(engagement_map).fillna(50)
    ml_df['parent_child_interaction_score'] = df['parent_child_interaction_score'] * 10
    ml_df['stimulation_score'] = df['home_stimulation_score'] * 10 # Scaling to 100 if it was 1-10
    
    # Target - FLIPPED: Lower DQ scores (labeled 'Low' in source) now map to High Risk (1)
    risk_map = {'High': 0, 'Moderate': 0, 'Low': 1, 'Medium': 0}
    ml_df['autism_risk'] = df['autism_risk'].map(risk_map).fillna(0).astype(int)
    
    # Save to CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ml_df.to_csv(output_path, index=False)
    print(f"Cleaned dataset saved to {output_path}")
    print(f"Final shape: {ml_df.shape}")
    print("\nRisk distribution:")
    print(ml_df['autism_risk'].value_counts())

if __name__ == "__main__":
    input_file = r'C:\Users\S Sameer\Desktop\autism - Copy\dataset\ECD Data sets.xlsx'
    output_file = r'C:\Users\S Sameer\Desktop\autism - Copy\ml\data\cleaned_client_data.csv'
    clean_dataset(input_file, output_file)
