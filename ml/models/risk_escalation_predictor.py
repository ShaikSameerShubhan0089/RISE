"""
Model B: Risk Escalation Prediction Model
Predicts if a child will transition to high risk in the next assessment cycle
Uses longitudinal features and previous risk status
"""

import numpy as np
import pandas as pd
import pickle
import os
from datetime import datetime
from typing import Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

# ML libraries
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix, f1_score
from sklearn.calibration import CalibratedClassifierCV
import xgboost as xgb
import shap


class RiskEscalationPredictor:
    """
    Binary classifier to predict autism risk escalation
    Target: Will child move to High risk in next cycle?
    """
    
    def __init__(self, model_version='v1.0'):
        self.model_version = model_version
        self.model = None
        self.calibrated_model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.shap_explainer = None
        self.metrics = {}
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare longitudinal data for escalation prediction
        
        Requires:
        - Previous cycle autism_risk
        - Delta features (dq_delta, behavior_delta, etc.)
        - Previous delay counts
        
        Target: did_escalate (0 or 1)
        """
        df = df.copy()
        
        # Feature columns for escalation
        feature_cols = [
            # Previous assessment metrics
            'composite_dq',
            'socio_emotional_dq',
            'language_dq',
            'behavior_score',
            'delayed_domains',
            
            # Longitudinal changes
            'dq_delta',
            'behavior_delta',
            'socio_emotional_delta',
            'environmental_delta',
            'delay_delta',
            'nutrition_delta',
            
            # Clinical indices
            'scii',
            'nsi',
            'erm',
            'dbs',
            
            # Demographics & time
            'age_months',
            'days_since_last_assessment'
        ]
        
        # Only include rows where we have a next assessment to check
        # This is computed during feature engineering for longitudinal data
        
        X = df[feature_cols]
        y = df['will_escalate'] if 'will_escalate' in df.columns else None
        
        self.feature_names = feature_cols
        
        return X, y
    
    def train(self, X_train, y_train, X_val=None, y_val=None):
        """Train XGBoost escalation predictor"""
        print(f"Training Risk Escalation Predictor {self.model_version}...")
        print(f"Training samples: {len(X_train)}")
        print(f"Escalation distribution: {pd.Series(y_train).value_counts().to_dict()}")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        self.model = xgb.XGBClassifier(
            max_depth=4,
            learning_rate=0.05,
            n_estimators=150,
            min_child_weight=2,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='binary:logistic',
            random_state=42,
            use_label_encoder=False,
            eval_metric=['logloss', 'auc', 'error']
        )
        
        # Fit with early stopping if validation set provided
        if X_val is not None and y_val is not None:
            X_val_scaled = self.scaler.transform(X_val)
            eval_set = [(X_train_scaled, y_train), (X_val_scaled, y_val)]
            
            self.model.fit(
                X_train_scaled, y_train,
                eval_set=eval_set,
                verbose=False
            )
        else:
            self.model.fit(X_train_scaled, y_train)
        
        # Apply calibration
        self._calibrate_model(X_train_scaled, y_train)
        
        # Initialize SHAP
        self._init_shap_explainer(X_train_scaled)

        print("Model training complete")
        return getattr(self.model, 'evals_result', lambda: {})()
    
    def _calibrate_model(self, X_train, y_train):
        """Apply probability calibration"""
        print("Applying probability calibration...")
        
        self.calibrated_model = CalibratedClassifierCV(
            self.model,
            method='sigmoid',
            cv=3
        )
        
        self.calibrated_model.fit(X_train, y_train)
        print("Calibration complete")
    
    def _init_shap_explainer(self, X_sample):
        """Initialize SHAP explainer"""
        self.shap_explainer = shap.TreeExplainer(self.model)
    
    def predict(self, X, use_calibration=True):
        """
        Predict escalation probability
        
        Returns:
            predictions: Binary predictions (0 = no escalation, 1 = will escalate)
            probabilities: Escalation probability (0-1)
        """
        X_scaled = self.scaler.transform(X)
        
        if use_calibration and self.calibrated_model:
            probabilities = self.calibrated_model.predict_proba(X_scaled)[:, 1]
            predictions = (probabilities >= 0.5).astype(int)
        else:
            probabilities = self.model.predict_proba(X_scaled)[:, 1]
            predictions = self.model.predict(X_scaled)
        
        return predictions, probabilities
    
    def explain_prediction(self, X, top_n=5):
        """Generate SHAP explanations for escalation predictions"""
        X_scaled = self.scaler.transform(X)
        shap_values = self.shap_explainer.shap_values(X_scaled)
        
        explanations = []
        for i in range(len(X)):
            contributions = []
            for j, feature_name in enumerate(self.feature_names):
                contributions.append({
                    'feature_name': feature_name,
                    'feature_value': float(X.iloc[i, j]) if hasattr(X, 'iloc') else float(X[i, j]),
                    'shap_value': float(shap_values[i, j]),
                })
            
            # Sort by absolute SHAP value
            contributions = sorted(
                contributions,
                key=lambda x: abs(x['shap_value']),
                reverse=True
            )
            
            # Add interpretation for top features
            for rank, contrib in enumerate(contributions[:top_n], 1):
                contrib['contribution_rank'] = rank
                contrib['impact_direction'] = 'Increases Escalation Risk' if contrib['shap_value'] > 0 else 'Reduces Escalation Risk'
                contrib['interpretation'] = self._interpret_feature(
                    contrib['feature_name'],
                    contrib['feature_value'],
                    contrib['shap_value']
                )
            
            explanations.append(contributions[:top_n])
        
        return explanations
    
    def _interpret_feature(self, feature_name, value, shap_value):
        """Generate clinical interpretation"""
        interpretations = {
            'dq_delta': f"DQ change: {value:+.1f} points",
            'behavior_delta': f"Behavior change: {value:+.1f} points",
            'socio_emotional_delta': f"Socio-emotional change: {value:+.1f} points",
            'environmental_delta': f"Environmental support change: {value:+.1f} points",
            'delay_delta': f"Change in delayed domains: {int(value):+d}",
            'nutrition_delta': f"Nutrition change: {value:+.1f} points",
        }
        
        return interpretations.get(feature_name, f"{feature_name}: {value:.2f}")
    
    def evaluate(self, X_test, y_test, verbose=True):
        """Evaluate escalation prediction model"""
        predictions, probabilities = self.predict(X_test)
        
        # ROC-AUC
        roc_auc = roc_auc_score(y_test, probabilities)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, predictions)
        tn, fp, fn, tp = cm.ravel()
        
        # Metrics
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        f1 = f1_score(y_test, predictions)
        
        self.metrics = {
            'roc_auc': round(roc_auc, 4),
            'sensitivity': round(sensitivity, 4),
            'specificity': round(specificity, 4),
            'f1_score': round(f1, 4),
            'confusion_matrix': cm.tolist(),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_positives': int(tp)
        }
        
        if verbose:
            print("\n" + "="*60)
            print("RISK ESCALATION PREDICTOR - EVALUATION RESULTS")
            print("="*60)
            print(f"ROC-AUC Score:      {roc_auc:.4f} {'✓ PASS' if roc_auc >= 0.82 else '✗ BELOW TARGET (0.82)'}")
            print(f"Sensitivity:        {sensitivity:.4f}")
            print(f"Specificity:        {specificity:.4f}")
            print(f"F1 Score:           {f1:.4f}")
            print(f"\nConfusion Matrix:")
            print(f"  TN: {tn:4d}  |  FP: {fp:4d}")
            print(f"  FN: {fn:4d}  |  TP: {tp:4d}")
            print("="*60)
        
        return self.metrics
    
    def save_model(self, path):
        """Save trained model"""
        model_artifacts = {
            'model': self.model,
            'calibrated_model': self.calibrated_model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_version': self.model_version,
            'metrics': self.metrics,
            'trained_at': datetime.now().isoformat()
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_artifacts, f)
        
        print(f"Escalation model saved to {path}")
    
    @classmethod
    def load_model(cls, path):
        """Load trained model"""
        with open(path, 'rb') as f:
            artifacts = pickle.load(f)
        
        predictor = cls(model_version=artifacts['model_version'])
        predictor.model = artifacts['model']
        predictor.calibrated_model = artifacts['calibrated_model']
        predictor.scaler = artifacts['scaler']
        predictor.feature_names = artifacts['feature_names']
        predictor.metrics = artifacts['metrics']
        
        # Reinitialize SHAP
        if predictor.model:
            sample_data = np.random.randn(10, len(predictor.feature_names))
            predictor._init_shap_explainer(sample_data)
        
        print(f"Escalation model loaded from {path}")
        
        return predictor


if __name__ == '__main__':
    print("Risk Escalation Predictor\n")
    pass
