"""
Complete ML Training Pipeline
Trains both autism risk classifier and escalation predictor
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from synthetic_data_generator import generate_training_data
from feature_engineering import FeatureEngineer
from models.autism_risk_classifier import AutismRiskClassifier
from models.risk_escalation_predictor import RiskEscalationPredictor

from sklearn.model_selection import train_test_split


def prepare_escalation_data(df):
    """
    Prepare data for escalation prediction
    Label: did child escalate to high risk in next cycle?
    """
    escalation_data = []
    
    for child_id in df['child_id'].unique():
        child_assessments = df[df['child_id'] == child_id].sort_values('assessment_cycle')
        
        # Need at least 2 cycles
        if len(child_assessments) < 2:
            continue
        
        for i in range(len(child_assessments) - 1):
            current = child_assessments.iloc[i]
            next_assessment = child_assessments.iloc[i + 1]
            
            # Did escalate if: current is not high risk AND next is high risk
            current_high_risk = current['autism_risk'] == 1
            next_high_risk = next_assessment['autism_risk'] == 1
            
            will_escalate = (not current_high_risk) and next_high_risk
            
            # Create row with current features + escalation label
            row = current.to_dict()
            row['will_escalate'] = int(will_escalate)
            
            escalation_data.append(row)
    
    return pd.DataFrame(escalation_data)


def train_model_pipeline(n_children=1000, test_size=0.2, save_models=True):
    """
    Complete training pipeline for both models
    """
    print("="*70)
    print("AUTISM RISK STRATIFICATION CDSS - ML TRAINING PIPELINE")
    print("="*70)
    
    # Create directories
    os.makedirs('ml/data', exist_ok=True)
    os.makedirs('ml/models/saved', exist_ok=True)
    os.makedirs('ml/evaluation', exist_ok=True)
    
    # Step 1: Load and prepare client data
    print("\n[1/6] Loading Cleaned Client Data...")
    print("-" * 70)
    data_path = 'ml/data/cleaned_client_data.csv'
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Run clean_dataset.py first.")
        # Fallback to synthetic if requested or just fail
        return None, None, None, None
    
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} records from client dataset")
    
    # Step 2: Feature engineering
    print("\n[2/6] Performing Feature Engineering...")
    print("-"*70)
    engineer = FeatureEngineer()
    df_engineered = engineer.engineer_features(df)
    
    # Save engineered data
    df_engineered.to_csv('ml/data/engineered_features.csv', index=False)
    print(f"Engineered features saved")
    print(f"  Total features: {len(df_engineered.columns)}")
    
    # Step 3: Train Autism Risk Classifier (Model A)
    print("\n[3/6] Training Autism Risk Classifier (Model A)...")
    print("-"*70)
    
    # Prepare data
    classifier = AutismRiskClassifier(model_version='v1.0')
    X, y = classifier.prepare_data(df_engineered)
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    
    # Further split train into train/val
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.15, random_state=42, stratify=y_train
    )
    
    print(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    
    # Train model
    classifier.train(X_train, y_train, X_val, y_val, 
                    hyperparameter_tuning=False)  # Set True for tuning
    
    # Step 4: Evaluate Autism Risk Classifier
    print("\n[4/6] Evaluating Autism Risk Classifier...")
    print("-"*70)
    metrics = classifier.evaluate(X_test, y_test, verbose=True)
    
    # Generate evaluation plots
    fig = classifier.plot_evaluation(X_test, y_test, 
                                     save_path='ml/evaluation/autism_risk_classifier_eval.png')
    
    # Save model
    if save_models:
        classifier.save_model('ml/models/saved/autism_risk_classifier_v1.pkl')
    
    # Step 5: Train Risk Escalation Predictor (Model B)
    print("\n[5/6] Training Risk Escalation Predictor (Model B)...")
    print("-"*70)
    
    # Prepare escalation data
    df_escalation = prepare_escalation_data(df_engineered)
    
    if len(df_escalation) > 0:
        predictor = RiskEscalationPredictor(model_version='v1.0')
        X_esc, y_esc = predictor.prepare_data(df_escalation)
        
        # Train-test split
        X_esc_train, X_esc_test, y_esc_train, y_esc_test = train_test_split(
            X_esc, y_esc, test_size=test_size, random_state=42, stratify=y_esc
        )
        
        X_esc_train, X_esc_val, y_esc_train, y_esc_val = train_test_split(
            X_esc_train, y_esc_train, test_size=0.15, random_state=42, 
            stratify=y_esc_train
        )
        
        # Train
        predictor.train(X_esc_train, y_esc_train, X_esc_val, y_esc_val)
        
        # Step 6: Evaluate Escalation Predictor
        print("\n[6/6] Evaluating Risk Escalation Predictor...")
        print("-"*70)
        esc_metrics = predictor.evaluate(X_esc_test, y_esc_test, verbose=True)
        
        # Save model
        if save_models:
            predictor.save_model('ml/models/saved/risk_escalation_predictor_v1.pkl')
    else:
        print("Not enough longitudinal data for escalation predictor")
        esc_metrics = None
    
    # Final Summary
    print("\n" + "="*70)
    print("TRAINING COMPLETE - SUMMARY")
    print("="*70)
    print("\nModel A: Autism Risk Classifier")
    print(f"  ROC-AUC:     {metrics['roc_auc']:.4f}")
    print(f"  Sensitivity: {metrics['sensitivity']:.4f}")
    print(f"  Specificity: {metrics['specificity']:.4f}")
    print(f"  F1 Score:    {metrics['f1_score']:.4f}")
    
    if esc_metrics:
        print("\nModel B: Risk Escalation Predictor")
        print(f"  ROC-AUC:     {esc_metrics['roc_auc']:.4f}")
        print(f"  Sensitivity: {esc_metrics['sensitivity']:.4f}")
        print(f"  Specificity: {esc_metrics['specificity']:.4f}")
    
    print("\n" + "="*70)
    print("Models ready for deployment!")
    print("="*70)
    
    return classifier, predictor if esc_metrics else None, metrics, esc_metrics


if __name__ == '__main__':
    # Train models
    classifier, predictor, metrics, esc_metrics = train_model_pipeline(
        n_children=1000,
        test_size=0.2,
        save_models=True
    )
    
    # Demo: Make sample predictions with explanations
    print("\n" + "="*70)
    print("SAMPLE PREDICTION WITH SHAP EXPLANATION")
    print("="*70)
    
    # Load test data
    df = pd.read_csv('ml/data/engineered_features.csv')
    sample = df.sample(3)
    
    X_sample, _ = classifier.prepare_data(sample)
    
    # Get predictions with stratification
    results = classifier.predict_with_stratification(X_sample)
    explanations = classifier.explain_prediction(X_sample, top_n=5)
    
    for i, (result, explanation) in enumerate(zip(results, explanations)):
        print(f"\nSample {i+1}:")
        print(f"  Predicted Class: {result['prediction']} ({'High Risk' if result['prediction'] == 1 else 'Low/Moderate'})")
        print(f"  Probability: {result['probability']:.4f}")
        print(f"  Risk Tier: {result['risk_tier']}")
        print(f"  Clinical Action: {result['clinical_action']}")
        print(f"\n  Top 5 Contributing Features:")
        for feature in explanation:
            print(f"    {feature['contribution_rank']}. {feature['interpretation']}")
            print(f"       SHAP: {feature['shap_value']:+.4f} ({feature['impact_direction']})")
