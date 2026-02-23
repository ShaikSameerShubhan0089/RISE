#!/usr/bin/env python
"""
Save trained ML models to pickle files for Render deployment
This script loads the models and saves them to the ml/models/saved/ directory
"""

import os
import sys
import pickle
from pathlib import Path

os.chdir(r'c:\Users\S Sameer\Desktop\autism - Copy')
sys.path.insert(0, '.')

print("=" * 80)
print("SAVING ML MODELS FOR DEPLOYMENT")
print("=" * 80)

try:
    from ml.models.autism_risk_classifier import AutismRiskClassifier
    from ml.models.risk_escalation_predictor import RiskEscalationPredictor
    import pandas as pd
    
    # Create save directory
    save_dir = Path('ml/models/saved')
    save_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n1. Loading training data for model training...")
    df = pd.read_csv('ml/data/engineered_features.csv')
    print(f"   ✓ Loaded {len(df)} records")
    
    # Split data
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        df.drop('autism_risk', axis=1),
        df['autism_risk'],
        test_size=0.2,
        random_state=42,
        stratify=df['autism_risk']
    )
    
    print(f"\n2. Training Autism Risk Classifier...")
    classifier = AutismRiskClassifier(model_version='v1.0')
    
    # Prepare data
    X_train_prepared, y_train_prepared = classifier.prepare_data(
        pd.concat([X_train, df[['autism_risk']].iloc[X_train.index]], axis=1)
    )
    
    X_test_prepared, y_test_prepared = classifier.prepare_data(
        pd.concat([X_test, df[['autism_risk']].iloc[X_test.index]], axis=1)
    )
    
    # Train
    classifier.train(X_train_prepared, y_train_prepared, 
                     X_test_prepared, y_test_prepared)
    
    # Evaluate
    metrics = classifier.evaluate(X_test_prepared, y_test_prepared)
    
    # Save Model A
    model_a_path = save_dir / 'autism_risk_classifier_v1.pkl'
    with open(model_a_path, 'wb') as f:
        pickle.dump({
            'model': classifier.model,
            'calibrated_model': classifier.calibrated_model,
            'scaler': classifier.scaler,
            'feature_names': classifier.feature_names,
            'model_version': classifier.model_version,
            'metrics': classifier.metrics,
            'risk_thresholds': classifier.risk_thresholds,
            'clinical_actions': classifier.clinical_actions
        }, f)
    print(f"   ✓ Saved Model A to {model_a_path}")
    
    print(f"\n3. Training Risk Escalation Predictor...")
    escalation = RiskEscalationPredictor(model_version='v1.0')
    
    # Filter for escalation data (rows with will_escalate column)
    df_escalation = df[df['will_escalate'].notna()].copy() if 'will_escalate' in df.columns else df.copy()
    
    if len(df_escalation) > 0:
        X_esc_train, X_esc_test, y_esc_train, y_esc_test = train_test_split(
            df_escalation.drop(['autism_risk', 'will_escalate'], axis=1, errors='ignore'),
            df_escalation['will_escalate'] if 'will_escalate' in df.columns else df['autism_risk'],
            test_size=0.2,
            random_state=42,
            stratify=df_escalation['will_escalate'] if 'will_escalate' in df.columns else df['autism_risk']
        )
        
        X_esc_train_prepared, y_esc_train_prepared = escalation.prepare_data(
            pd.concat([X_esc_train, df_escalation[['will_escalate'] if 'will_escalate' in df.columns else ['autism_risk']].iloc[X_esc_train.index]], axis=1)
        )
        
        X_esc_test_prepared, y_esc_test_prepared = escalation.prepare_data(
            pd.concat([X_esc_test, df_escalation[['will_escalate'] if 'will_escalate' in df.columns else ['autism_risk']].iloc[X_esc_test.index]], axis=1)
        )
        
        # Train
        escalation.train(X_esc_train_prepared, y_esc_train_prepared,
                        X_esc_test_prepared, y_esc_test_prepared)
        
        # Evaluate
        metrics_b = escalation.evaluate(X_esc_test_prepared, y_esc_test_prepared)
    
    # Save Model B
    model_b_path = save_dir / 'risk_escalation_predictor_v1.pkl'
    with open(model_b_path, 'wb') as f:
        pickle.dump({
            'model': escalation.model,
            'calibrated_model': escalation.calibrated_model,
            'scaler': escalation.scaler,
            'feature_names': escalation.feature_names,
            'model_version': escalation.model_version,
            'metrics': escalation.metrics
        }, f)
    print(f"   ✓ Saved Model B to {model_b_path}")
    
    print("\n" + "=" * 80)
    print("DEPLOYMENT READY!")
    print("=" * 80)
    print(f"\nModels saved to: {save_dir.absolute()}")
    print(f"Total files: {len(list(save_dir.glob('*.pkl')))}")
    print("\nNext steps:")
    print("1. Commit these files to GitHub")
    print("2. Update environment variables in Render dashboard")
    print("3. Deploy using Render dashboard or Git integration")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
