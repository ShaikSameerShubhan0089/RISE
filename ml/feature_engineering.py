"""
Feature Engineering for RISE
Risk Identification System for Early Detection
Implements clinical indices and longitudinal change metrics
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional


class FeatureEngineer:
    """
    Implements clinical feature engineering as per CDSS specifications:
    1. Social Communication Impairment Index (SCII)
    2. Neurodevelopmental Severity Index (NSI)
    3. Environmental Risk Modifier (ERM)
    4. Delay Burden Score (DBS)
    5. Longitudinal Change Metrics
    """
    
    def __init__(self):
        # Weights for SCII (empirically determined, can be tuned)
        self.scii_weights = {
            'lc_weight': 0.4,  # Language communication
            'se_weight': 0.45,  # Socio-emotional
            'behavior_weight': 0.15  # Behavior score
        }
        
        # Weights for ERM
        self.erm_weights = {
            'caregiver_engagement': 0.35,
            'language_exposure': 0.30,
            'nutrition_score': 0.20,
            'parent_child_interaction': 0.15
        }
    
    def compute_scii(self, row: pd.Series) -> float:
        """
        Social Communication Impairment Index (SCII)
        Higher values indicate greater social-communication impairment
        
        Formula: w1*(100-LC_DQ) + w2*(100-SE_DQ) + w3*behavior_score
        Normalized to 0-100 scale
        """
        lc_inverse = 100 - row['language_dq']
        se_inverse = 100 - row['socio_emotional_dq']
        behavior = row['behavior_score']
        
        scii = (
            self.scii_weights['lc_weight'] * lc_inverse +
            self.scii_weights['se_weight'] * se_inverse +
            self.scii_weights['behavior_weight'] * behavior
        )
        
        return round(scii, 2)
    
    def compute_nsi(self, row: pd.Series) -> float:
        """
        Neurodevelopmental Severity Index (NSI)
        Higher values indicate greater developmental severity
        
        Formula: 1 - (Composite_DQ / 100)
        Range: 0-1 (0 = no severity, 1 = maximum severity)
        """
        nsi = 1 - (row['composite_dq'] / 100)
        return round(nsi, 4)
    
    def compute_erm(self, row: pd.Series) -> float:
        """
        Environmental Risk Modifier (ERM)
        Higher values indicate better environmental support (protective factor)
        
        Weighted combination of environmental factors
        Range: 0-100
        """
        erm = (
            self.erm_weights['caregiver_engagement'] * row['caregiver_engagement_score'] +
            self.erm_weights['language_exposure'] * row['language_exposure_score'] +
            self.erm_weights['nutrition_score'] * row['nutrition_score'] +
            self.erm_weights['parent_child_interaction'] * row['parent_child_interaction_score']
        )
        
        return round(erm, 2)
    
    def compute_dbs(self, row: pd.Series) -> float:
        """
        Delay Burden Score (DBS)
        Proportion of developmental domains with delays
        
        Formula: delayed_domains / total_domains
        Range: 0-1 (0 = no delays, 1 = all domains delayed)
        """
        total_domains = 5  # GM, FM, LC, COG, SE
        dbs = row['delayed_domains'] / total_domains
        return round(dbs, 2)
    
    def compute_longitudinal_features(self, 
                                     current: pd.Series, 
                                     previous: Optional[pd.Series]) -> Dict[str, float]:
        """
        Compute longitudinal change metrics (deltas)
        
        Returns dict with:
        - dq_delta: Change in composite DQ
        - behavior_delta: Change in behavior score
        - socio_emotional_delta: Change in SE_DQ
        - environmental_delta: Change in ERM
        - delay_delta: Change in number of delays
        - nutrition_delta: Change in nutrition score
        - days_since_last: Days between assessments
        """
        if previous is None:
            # First assessment - no changes
            return {
                'dq_delta': 0.0,
                'behavior_delta': 0.0,
                'socio_emotional_delta': 0.0,
                'environmental_delta': 0.0,
                'delay_delta': 0,
                'nutrition_delta': 0.0,
                'days_since_last_assessment': 0
            }
        
        # Calculate deltas
        dq_delta = current['composite_dq'] - previous['composite_dq']
        behavior_delta = current['behavior_score'] - previous['behavior_score']
        se_delta = current['socio_emotional_dq'] - previous['socio_emotional_dq']
        delay_delta = current['delayed_domains'] - previous['delayed_domains']
        nutrition_delta = current['nutrition_score'] - previous['nutrition_score']
        
        # Environmental delta (using ERM)
        current_erm = self.compute_erm(current)
        previous_erm = self.compute_erm(previous)
        env_delta = current_erm - previous_erm
        
        # Time delta (if dates available)
        days_since = 180  # Default 6 months
        
        return {
            'dq_delta': round(dq_delta, 2),
            'behavior_delta': round(behavior_delta, 2),
            'socio_emotional_delta': round(se_delta, 2),
            'environmental_delta': round(env_delta, 2),
            'delay_delta': int(delay_delta),
            'nutrition_delta': round(nutrition_delta, 2),
            'days_since_last_assessment': days_since
        }
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all feature engineering to the dataset
        
        Args:
            df: DataFrame with raw assessment data
            
        Returns:
            DataFrame with additional engineered features
        """
        df = df.copy()
        
        # Compute clinical indices for all rows
        df['scii'] = df.apply(self.compute_scii, axis=1)
        df['nsi'] = df.apply(self.compute_nsi, axis=1)
        df['erm'] = df.apply(self.compute_erm, axis=1)
        df['dbs'] = df.apply(self.compute_dbs, axis=1)
        
        # Compute longitudinal features
        longitudinal_features = []
        
        for child_id in df['child_id'].unique():
            child_assessments = df[df['child_id'] == child_id].sort_values('assessment_cycle')
            
            previous_assessment = None
            for idx, current_assessment in child_assessments.iterrows():
                long_features = self.compute_longitudinal_features(
                    current_assessment, 
                    previous_assessment
                )
                long_features['assessment_idx'] = idx
                longitudinal_features.append(long_features)
                
                previous_assessment = current_assessment
        
        # Merge longitudinal features
        long_df = pd.DataFrame(longitudinal_features)
        long_df = long_df.set_index('assessment_idx')
        
        df = df.join(long_df)
        
        return df
    
    def get_ml_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract only the features needed for ML model training
        
        Returns:
            DataFrame with feature columns only (excluding target)
        """
        feature_cols = [
            # DQ Scores
            'gross_motor_dq', 'fine_motor_dq', 'language_dq', 
            'cognitive_dq', 'socio_emotional_dq', 'composite_dq',
            
            # Delays
            'gross_motor_delay', 'fine_motor_delay', 'language_delay',
            'cognitive_delay', 'socio_emotional_delay', 'delayed_domains',
            
            # Neuro-behavioral
            'adhd_risk', 'behavior_risk', 'attention_score', 'behavior_score',
            
            # Nutrition
            'stunting', 'wasting', 'anemia', 'nutrition_score',
            
            # Environmental
            'caregiver_engagement_score', 'language_exposure_score',
            'parent_child_interaction_score', 'stimulation_score',
            
            # Demographics
            'age_months', 'gender',
            
            # Engineered features
            'scii', 'nsi', 'erm', 'dbs',
            
            # Longitudinal (for escalation model)
            'dq_delta', 'behavior_delta', 'socio_emotional_delta',
            'environmental_delta', 'delay_delta', 'nutrition_delta',
            'days_since_last_assessment'
        ]
        
        return df[feature_cols]


def validate_data(df: pd.DataFrame) -> Dict[str, any]:
    """
    Validate assessment data quality
    
    Returns:
        Dictionary with validation results
    """
    validation = {
        'total_records': len(df),
        'missing_values': df.isnull().sum().to_dict(),
        'invalid_dq_scores': 0,
        'invalid_age': 0,
        'warnings': []
    }
    
    # Check DQ score ranges
    dq_cols = ['gross_motor_dq', 'fine_motor_dq', 'language_dq', 
               'cognitive_dq', 'socio_emotional_dq', 'composite_dq']
    
    for col in dq_cols:
        if col in df.columns:
            invalid = ((df[col] < 0) | (df[col] > 100)).sum()
            if invalid > 0:
                validation['invalid_dq_scores'] += invalid
                validation['warnings'].append(f"{col}: {invalid} values out of range [0, 100]")
    
    # Check age ranges
    if 'age_months' in df.columns:
        invalid_age = ((df['age_months'] < 0) | (df['age_months'] > 72)).sum()
        if invalid_age > 0:
            validation['invalid_age'] = invalid_age
            validation['warnings'].append(f"age_months: {invalid_age} values out of range [0, 72]")
    
    return validation


if __name__ == '__main__':
    # Test feature engineering
    print("Testing Feature Engineering...")
    
    # Load synthetic data
    df = pd.read_csv('ml/data/synthetic_assessments.csv')
    
    # Apply feature engineering
    engineer = FeatureEngineer()
    df_engineered = engineer.engineer_features(df)
    
    print("\n✓ Feature engineering complete")
    print(f"Original features: {len(df.columns)}")
    print(f"Engineered features: {len(df_engineered.columns)}")
    
    # Display sample
    print("\nSample engineered features:")
    print(df_engineered[['child_id', 'assessment_cycle', 'scii', 'nsi', 'erm', 'dbs', 
                          'dq_delta', 'autism_risk']].head(10))
    
    # Validate data
    validation = validate_data(df_engineered)
    print(f"\n✓ Validation complete")
    print(f"Total records: {validation['total_records']}")
    if validation['warnings']:
        print(f"Warnings: {len(validation['warnings'])}")
        for warning in validation['warnings'][:5]:
            print(f"  - {warning}")
