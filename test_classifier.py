"""
Test Script: Evaluate the trained Autism Risk Classifier on test set
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import json  # used for reading/writing metadata and metrics

sys.path.append(str(Path(__file__).parent.parent))

from ml.feature_engineering import FeatureEngineer
from ml.models.autism_risk_classifier import AutismRiskClassifier
from sklearn.model_selection import train_test_split

def main():
    print("="*70)
    print("AUTISM RISK CLASSIFIER - TEST EVALUATION")
    print("="*70)
    
    # Load data
    data_path = 'ml/data/cleaned_client_data.csv'
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found")
        return
    
    df = pd.read_csv(data_path)
    print(f"\nLoaded {len(df)} records")
    
    # Feature Engineering
    engineer = FeatureEngineer()
    df_engineered = engineer.engineer_features(df)
    
    # Prepare data
    classifier = AutismRiskClassifier(model_version='v1.0')
    X, y = classifier.prepare_data(df_engineered)
    
    # Split data same way as training
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.15, random_state=42, stratify=y_train
    )
    
    print(f"Test set size: {len(X_test)} samples")
    print(f"Test set class distribution: {pd.Series(y_test).value_counts().to_dict()}")
    
    # Load trained model
    model_path = 'ml/models/saved/classifier/autism_risk_classifier_v1.pkl'
    if not os.path.exists(model_path):
        print(f"\nError: Model not found at {model_path}")
        print("Please run train_classifier.py first")
        return
    
    print(f"\nLoading model from {model_path}...")
    classifier = AutismRiskClassifier.load_model(model_path)
    print(f"Model loaded successfully")
    # load threshold from training metadata if available
    threshold = None
    meta_path = 'ml/models/saved/classifier/training_meta.json'
    if os.path.exists(meta_path):
        try:
            with open(meta_path) as mf:
                meta = json.load(mf)
            threshold = meta.get('optimal_threshold')
            print(f"Loaded optimal threshold from metadata: {threshold}")
        except Exception as e:
            print(f"Warning: could not read threshold from metadata: {e}")
    if threshold is None:
        # fallback default or recompute using test set (less desirable)
        threshold = 0.5
        print("No threshold found in metadata; using default 0.5")
    classifier.optimal_threshold = threshold
    print(f"Optimal threshold set to: {classifier.optimal_threshold:.3f}")
    
    # Evaluate on test set
    print("\n" + "="*70)
    print("TEST SET EVALUATION (Unseen Data)")
    print("="*70)
    
    metrics = classifier.evaluate(X_test, y_test, verbose=True)
    
    # Generate plots
    print("\nGenerating evaluation plots...")
    eval_dir = 'ml/evaluation/classifier'
    os.makedirs(eval_dir, exist_ok=True)
    
    plot_path = os.path.join(eval_dir, 'evaluation_dashboard_improved.png')
    classifier.plot_evaluation(X_test, y_test, save_path=plot_path)
    
    # Save metrics to JSON
    metrics_path = os.path.join(eval_dir, 'test_metrics_improved.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=4)
    print(f"Metrics saved to {metrics_path}")
    
    # Generate SHAP explanations for sample predictions
    print("\n" + "="*70)
    print("SAMPLE PREDICTIONS WITH EXPLANATIONS")
    print("="*70)
    
    # Get some high-risk and low-risk predictions
    predictions, probabilities = classifier.predict(X_test)
    
    # Find examples
    high_risk_idx = np.where(probabilities >= 0.75)[0]
    low_risk_idx = np.where(probabilities < 0.25)[0]
    
    print(f"\nHigh Risk Predictions (prob >= 0.75): {len(high_risk_idx)} cases")
    print(f"Low Risk Predictions (prob < 0.25): {len(low_risk_idx)} cases")
    
    if len(high_risk_idx) > 0:
        print(f"\n--- Example High Risk Case ---")
        idx = high_risk_idx[0]
        sample = X_test.iloc[[idx]]
        pred, prob = classifier.predict(sample)
        print(f"Probability: {prob[0]:.3f}")
        
        explanations = classifier.explain_prediction(sample, top_n=5)
        print(f"Top contributing features:")
        for exp in explanations[0]:
            print(f"  {exp['feature_name']:30s} = {exp['feature_value']:8.2f}  "
                  f"({exp['impact_direction']:15s}, SHAP={exp['shap_value']:7.4f})")
    
    if len(low_risk_idx) > 0:
        print(f"\n--- Example Low Risk Case ---")
        idx = low_risk_idx[0]
        sample = X_test.iloc[[idx]]
        pred, prob = classifier.predict(sample)
        print(f"Probability: {prob[0]:.3f}")
        
        explanations = classifier.explain_prediction(sample, top_n=5)
        print(f"Top contributing features:")
        for exp in explanations[0]:
            print(f"  {exp['feature_name']:30s} = {exp['feature_value']:8.2f}  "
                  f"({exp['impact_direction']:15s}, SHAP={exp['shap_value']:7.4f})")
    
    print("\n" + "="*70)
    print("EVALUATION COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
