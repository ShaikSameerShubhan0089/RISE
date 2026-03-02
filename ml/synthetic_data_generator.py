"""
Synthetic Data Generator for RISE
Risk Identification System for Early Detection
Generates realistic developmental assessment data for ML model training and testing
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

class SyntheticDataGenerator:
    """Generate synthetic ECD assessment data with realistic correlations"""
    
    def __init__(self):
        self.risk_profiles = {
            'low': {
                'dq_mean': 88, 'dq_std': 8,
                'behavior_mean': 20, 'behavior_std': 10,
                'nutrition_mean': 90, 'nutrition_std': 8,
                'caregiver_mean': 88, 'caregiver_std': 8,
                'autism_prob': 0.05
            },
            'moderate': {
                'dq_mean': 72, 'dq_std': 10,
                'behavior_mean': 45, 'behavior_std': 15,
                'nutrition_mean': 75, 'nutrition_std': 12,
                'caregiver_mean': 72, 'caregiver_std': 12,
                'autism_prob': 0.25
            },
            'high': {
                'dq_mean': 58, 'dq_std': 12,
                'behavior_mean': 75, 'behavior_std': 15,
                'nutrition_mean': 65, 'nutrition_std': 15,
                'caregiver_mean': 60, 'caregiver_std': 15,
                'autism_prob': 0.75
            }
        }
    
    def generate_dataset(self, n_children=500, n_cycles_range=(1, 3)):
        """
        Generate synthetic dataset with multiple assessment cycles
        
        Args:
            n_children: Number of unique children
            n_cycles_range: Tuple of (min, max) assessment cycles per child
            
        Returns:
            DataFrame with all assessments
        """
        all_assessments = []
        
        for child_id in range(1, n_children + 1):
            # Assign initial risk profile (weighted towards low/moderate)
            initial_risk = np.random.choice(
                ['low', 'moderate', 'high'],
                p=[0.5, 0.35, 0.15]
            )
            
            n_cycles = random.randint(*n_cycles_range)
            
            for cycle in range(1, n_cycles + 1):
                assessment = self._generate_assessment(
                    child_id, cycle, initial_risk
                )
                all_assessments.append(assessment)
                
                # Risk may evolve over cycles
                if cycle < n_cycles:
                    initial_risk = self._evolve_risk(initial_risk, assessment)
        
        df = pd.DataFrame(all_assessments)
        return df
    
    def _generate_assessment(self, child_id, cycle, risk_profile):
        """Generate a single assessment based on risk profile"""
        profile = self.risk_profiles[risk_profile]
        
        # Age (months) - increases with cycles
        base_age = random.randint(18, 36)
        age_months = base_age + (cycle - 1) * 6
        
        # Generate correlated DQ scores
        composite_dq = np.clip(
            np.random.normal(profile['dq_mean'], profile['dq_std']),
            30, 100
        )
        
        # Individual domain DQs (correlated with composite)
        dq_noise = 8
        gm_dq = np.clip(composite_dq + np.random.normal(0, dq_noise), 30, 100)
        fm_dq = np.clip(composite_dq + np.random.normal(0, dq_noise), 30, 100)
        lc_dq = np.clip(composite_dq + np.random.normal(-5, dq_noise), 30, 100)  # Language slightly lower for autism risk
        cog_dq = np.clip(composite_dq + np.random.normal(0, dq_noise), 30, 100)
        
        # Socio-emotional DQ - strongly correlated with autism risk
        if risk_profile == 'high':
            se_dq = np.clip(composite_dq - np.random.uniform(10, 25), 30, 100)
        else:
            se_dq = np.clip(composite_dq + np.random.normal(0, dq_noise), 30, 100)
        
        # Recalculate composite as average
        composite_dq = np.mean([gm_dq, fm_dq, lc_dq, cog_dq, se_dq])
        
        # Delays (DQ < 70 indicates delay)
        gm_delay = gm_dq < 70
        fm_delay = fm_dq < 70
        lc_delay = lc_dq < 70
        cog_delay = cog_dq < 70
        se_delay = se_dq < 70
        delayed_domains = sum([gm_delay, fm_delay, lc_delay, cog_delay, se_delay])
        
        # Behavior score (higher = more concerning)
        behavior_score = np.clip(
            np.random.normal(profile['behavior_mean'], profile['behavior_std']),
            0, 100
        )
        
        # Autism screen flag
        autism_screen_flag = (
            np.random.random() < profile['autism_prob']
        ) or (se_dq < 60 and behavior_score > 70)
        
        # ADHD and behavior risk
        adhd_risk = behavior_score > 60 and np.random.random() < 0.3
        behavior_risk = behavior_score > 70
        
        # Attention score (inverse of behavior score)
        attention_score = np.clip(100 - behavior_score + np.random.normal(0, 10), 0, 100)
        
        # Nutrition
        nutrition_score = np.clip(
            np.random.normal(profile['nutrition_mean'], profile['nutrition_std']),
            0, 100
        )
        stunting = nutrition_score < 65 and np.random.random() < 0.3
        wasting = nutrition_score < 60 and np.random.random() < 0.25
        anemia = nutrition_score < 70 and np.random.random() < 0.35
        
        # Environmental/Caregiving
        caregiver_engagement = np.clip(
            np.random.normal(profile['caregiver_mean'], profile['caregiver_std']),
            0, 100
        )
        language_exposure = np.clip(
            caregiver_engagement + np.random.normal(0, 8),
            0, 100
        )
        parent_child_interaction = np.clip(
            caregiver_engagement + np.random.normal(0, 8),
            0, 100
        )
        stimulation_score = np.clip(
            caregiver_engagement + np.random.normal(0, 10),
            0, 100
        )
        
        # Ground truth autism risk
        # Binary: 0 = Low/Moderate, 1 = High
        autism_risk = 1 if (
            se_dq < 65 or
            (behavior_score > 75 and lc_dq < 65) or
            delayed_domains >= 4 or
            (autism_screen_flag and se_dq < 70)
        ) else 0
        
        return {
            'child_id': child_id,
            'assessment_cycle': cycle,
            'age_months': age_months,
            'gross_motor_dq': round(gm_dq, 2),
            'fine_motor_dq': round(fm_dq, 2),
            'language_dq': round(lc_dq, 2),
            'cognitive_dq': round(cog_dq, 2),
            'socio_emotional_dq': round(se_dq, 2),
            'composite_dq': round(composite_dq, 2),
            'gross_motor_delay': gm_delay,
            'fine_motor_delay': fm_delay,
            'language_delay': lc_delay,
            'cognitive_delay': cog_delay,
            'socio_emotional_delay': se_delay,
            'delayed_domains': delayed_domains,
            'autism_screen_flag': autism_screen_flag,
            'adhd_risk': adhd_risk,
            'behavior_risk': behavior_risk,
            'attention_score': round(attention_score, 2),
            'behavior_score': round(behavior_score, 2),
            'stunting': stunting,
            'wasting': wasting,
            'anemia': anemia,
            'nutrition_score': round(nutrition_score, 2),
            'stimulation_score': round(stimulation_score, 2),
            'caregiver_engagement_score': round(caregiver_engagement, 2),
            'language_exposure_score': round(language_exposure, 2),
            'parent_child_interaction_score': round(parent_child_interaction, 2),
            'autism_risk': autism_risk,
            'gender': random.choice(['Male', 'Female']),
        }
    
    def _evolve_risk(self, current_risk, previous_assessment):
        """Evolve risk level based on previous assessment (for longitudinal data)"""
        # Most children remain stable
        if np.random.random() < 0.7:
            return current_risk
        
        # Some deteriorate or improve
        if current_risk == 'low':
            return np.random.choice(['low', 'moderate'], p=[0.8, 0.2])
        elif current_risk == 'moderate':
            return np.random.choice(['low', 'moderate', 'high'], p=[0.2, 0.6, 0.2])
        else:  # high
            return np.random.choice(['moderate', 'high'], p=[0.3, 0.7])


def generate_training_data(output_path='ml/data/synthetic_assessments.csv', n_children=1000):
    """Generate and save synthetic training data"""
    generator = SyntheticDataGenerator()
    df = generator.generate_dataset(n_children=n_children, n_cycles_range=(1, 4))
    
    df.to_csv(output_path, index=False)
    
    print(f"✓ Generated {len(df)} assessments for {n_children} children")
    print(f"✓ Saved to: {output_path}")
    print(f"\nRisk Distribution:")
    print(df['autism_risk'].value_counts())
    print(f"\nLow/Moderate (0): {(df['autism_risk'] == 0).sum()} ({(df['autism_risk'] == 0).mean()*100:.1f}%)")
    print(f"High (1): {(df['autism_risk'] == 1).sum()} ({(df['autism_risk'] == 1).mean()*100:.1f}%)")
    
    return df


if __name__ == '__main__':
    # Generate training data
    df = generate_training_data(n_children=1000)
    
    # Display sample
    print("\nSample assessments:")
    print(df.head(10)[['child_id', 'assessment_cycle', 'composite_dq', 'socio_emotional_dq', 
                        'behavior_score', 'delayed_domains', 'autism_risk']])
