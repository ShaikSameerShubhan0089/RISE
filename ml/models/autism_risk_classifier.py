"""
Model A: Autism Risk Classification Model
Binary classification: Low/Moderate (0) vs High (1) autism risk
Uses XGBoost with calibration and SHAP explanations
"""

import numpy as np
import pandas as pd
import pickle
import os
from datetime import datetime
from typing import Dict, Tuple
import warnings
import sys
warnings.filterwarnings('ignore')

# ML libraries
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    roc_auc_score, roc_curve, classification_report, confusion_matrix,
    precision_recall_curve, f1_score, brier_score_loss
)
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
import xgboost as xgb
import shap

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns


class AutismRiskClassifier:
    """
    XGBoost-based binary classifier for autism risk stratification
    Includes calibration and SHAP explainability
    """
    
    def __init__(self, model_version='v1.0'):
        self.model_version = model_version
        self.model = None
        self.calibrated_model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.label_encoders = {}
        self.shap_explainer = None
        self.optimal_threshold = 0.5  # Default, will be optimized during training
        
        # Performance metrics
        self.metrics = {}
        
        # Risk stratification thresholds
        self.risk_thresholds = {
            'low': (0.0, 0.25),         # < 0.25: Low Risk
            'mild': (0.25, 0.50),       # 0.25-0.50: Mild Concern
            'moderate': (0.50, 0.75),   # 0.50-0.75: Moderate Risk
            'high': (0.75, 1.01)        # > 0.75: High Risk
        }
        
        self.clinical_actions = {
            'low': 'Routine Monitoring',
            'mild': 'Enhanced Monitoring & Reassessment',
            'moderate': 'Specialist Referral Recommended',
            'high': 'Immediate Specialist Referral Required'
        }
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare data for training
        Returns: X (features), y (target)
        """
        df = df.copy()
        
        # Encode categorical features
        if 'gender' in df.columns:
            if 'gender' not in self.label_encoders:
                self.label_encoders['gender'] = LabelEncoder()
                df['gender_encoded'] = self.label_encoders['gender'].fit_transform(df['gender'])
            else:
                df['gender_encoded'] = self.label_encoders['gender'].transform(df['gender'])
        
        # Feature columns
        feature_cols = [
            # DQ Scores
            'gross_motor_dq', 'fine_motor_dq', 'language_dq',
            'cognitive_dq', 'socio_emotional_dq', 'composite_dq',
            
            # Delays (boolean -> int)
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
            'age_months', 'gender_encoded',
            
            # Engineered features
            'scii', 'nsi', 'erm', 'dbs'
        ]
        
        # Convert boolean columns to int
        bool_cols = ['gross_motor_delay', 'fine_motor_delay', 'language_delay',
                     'cognitive_delay', 'socio_emotional_delay', 'adhd_risk',
                     'behavior_risk', 'stunting', 'wasting', 'anemia']
        
        for col in bool_cols:
            if col in df.columns:
                df[col] = df[col].astype(int)
        
        X = df[feature_cols]
        y = df['autism_risk']
        
        self.feature_names = feature_cols
        
        return X, y
    
    def train(self, X_train, y_train, X_val=None, y_val=None, 
              hyperparameter_tuning=False, xgb_params: dict = None):
        """
        Train XGBoost model with optional hyperparameter tuning
        """
        print(f"Training Autism Risk Classifier {self.model_version}...")
        print(f"Training samples: {len(X_train)}")
        print(f"Class distribution: {pd.Series(y_train).value_counts().to_dict()}")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        if hyperparameter_tuning:
            print("\nPerforming hyperparameter tuning...")
            params = {
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.05, 0.1],
                'n_estimators': [100, 200, 300],
                'min_child_weight': [1, 3, 5],
                'subsample': [0.7, 0.8, 1.0],
                'colsample_bytree': [0.7, 0.8, 1.0]
            }
            
            xgb_model = xgb.XGBClassifier(
                objective='binary:logistic',
                random_state=42,
                use_label_encoder=False,
                eval_metric='logloss'
            )
            
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            grid_search = GridSearchCV(
                xgb_model, params, cv=cv, scoring='roc_auc',
                n_jobs=-1, verbose=1
            )
            grid_search.fit(X_train_scaled, y_train)
            
            self.model = grid_search.best_estimator_
            print(f"Best parameters: {grid_search.best_params_}")
            print(f"Best CV ROC-AUC: {grid_search.best_score_:.4f}")
        
        else:
            # Default parameters optimized for clinical use with regularization
            pos_count = np.sum(y_train)
            neg_count = len(y_train) - pos_count
            scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1
            print(f"Using scale_pos_weight: {scale_pos_weight:.2f}")
            # If Optuna / external params provided, use them (merge with safe defaults)
            if xgb_params:
                params = xgb_params.copy()
                # Ensure required args exist / are safe
                params.setdefault('objective', 'binary:logistic')
                params.setdefault('use_label_encoder', False)
                params.setdefault('random_state', 42)
                params.setdefault('eval_metric', ['logloss', 'auc', 'error'])
                params['scale_pos_weight'] = scale_pos_weight

                self.model = xgb.XGBClassifier(**params)
            else:
                self.model = xgb.XGBClassifier(
                    max_depth=4,                 # Reduced from 5 to prevent overfitting
                    learning_rate=0.03,          # Reduced from 0.05 for slower learning
                    n_estimators=300,            # Increased from 200 since learning is slower
                    min_child_weight=5,          # Increased from 3 for less split flexibility
                    subsample=0.7,               # Reduced from 0.8 for less data per tree
                    colsample_bytree=0.7,       # Reduced from 0.8 for less features per tree
                    gamma=1,                     # Minimum loss reduction for split
                    reg_alpha=0.1,               # L1 regularization
                    reg_lambda=1.0,              # L2 regularization
                    objective='binary:logistic',
                    random_state=42,
                    use_label_encoder=False,
                    eval_metric=['logloss', 'auc', 'error'],
                    scale_pos_weight=scale_pos_weight
                )
            
            # Fit with early stopping if validation set provided
            if X_val is not None and y_val is not None:
                X_val_scaled = self.scaler.transform(X_val)
                eval_set = [(X_train_scaled, y_train), (X_val_scaled, y_val)]
                
                self.model.fit(
                    X_train_scaled, y_train,
                    eval_set=eval_set,
                    verbose=10
                )
            else:
                self.model.fit(X_train_scaled, y_train)
        
        # Apply calibration
        self._calibrate_model(X_train_scaled, y_train)
        
        # Initialize SHAP explainer
        self._init_shap_explainer(X_train_scaled)

        print("Model training complete")
        return getattr(self.model, 'evals_result', lambda: {})()
    
    def _calibrate_model(self, X_train, y_train):
        """Apply probability calibration using Platt Scaling"""
        print("\nApplying probability calibration (Platt Scaling)...")
        
        self.calibrated_model = CalibratedClassifierCV(
            self.model,
            method='sigmoid',  # Platt scaling
            cv=5
        )
        
        self.calibrated_model.fit(X_train, y_train)
        print("Calibration complete")
    
    def _init_shap_explainer(self, X_sample):
        """Initialize SHAP TreeExplainer"""
        print("\nInitializing SHAP explainer...")
        self.shap_explainer = shap.TreeExplainer(self.model)
        print("SHAP explainer ready")
    
    def predict(self, X, use_calibration=False, threshold=None):
        """
        Make predictions with optional custom threshold
        
        Args:
            X: Input features
            use_calibration: Whether to use calibrated probabilities
            threshold: Custom decision threshold (default: self.optimal_threshold)
        
        Returns:
            predictions: Binary class predictions (0 or 1)
            probabilities: Probability of high risk class
        """
        X_scaled = self.scaler.transform(X)
        
        if threshold is None:
            threshold = self.optimal_threshold
        
        if use_calibration and self.calibrated_model:
            probabilities = self.calibrated_model.predict_proba(X_scaled)[:, 1]
            predictions = (probabilities >= threshold).astype(int)
        else:
            probabilities = self.model.predict_proba(X_scaled)[:, 1]
            predictions = (probabilities >= threshold).astype(int)
        
        return predictions, probabilities
    
    def predict_with_stratification(self, X):
        """
        Predict with risk tier stratification
        
        Returns dict with:
        - prediction: Binary class
        - probability: Probability of high risk
        - risk_tier: Low/Mild/Moderate/High
        - clinical_action: Recommended action
        """
        predictions, probabilities = self.predict(X)
        
        results = []
        for pred, prob in zip(predictions, probabilities):
            # Determine risk tier
            tier = self._get_risk_tier(prob)
            
            results.append({
                'prediction': int(pred),
                'probability': round(float(prob), 4),
                'risk_tier': tier.title(),
                'clinical_action': self.clinical_actions[tier]
            })
        
        return results
    
    def _get_risk_tier(self, probability):
        """Map probability to risk tier"""
        for tier, (low, high) in self.risk_thresholds.items():
            if low <= probability < high:
                return tier
        return 'high'
    
    def explain_prediction(self, X, top_n=5):
        """
        Generate SHAP explanations for predictions
        
        Returns list of dicts with top N feature contributions
        """
        X_scaled = self.scaler.transform(X)
        shap_values = self.shap_explainer.shap_values(X_scaled)
        
        explanations = []
        for i in range(len(X)):
            # Get feature contributions
            contributions = []
            for j, feature_name in enumerate(self.feature_names):
                contributions.append({
                    'feature_name': feature_name,
                    'feature_value': float(X.iloc[i, j]) if hasattr(X, 'iloc') else float(X[i, j]),
                    'shap_value': float(shap_values[i, j]),
                    'contribution_rank': None
                })
            
            # Sort by absolute SHAP value
            contributions = sorted(
                contributions,
                key=lambda x: abs(x['shap_value']),
                reverse=True
            )
            
            # Add rank and interpretation
            for rank, contrib in enumerate(contributions[:top_n], 1):
                contrib['contribution_rank'] = rank
                contrib['impact_direction'] = 'Increases Risk' if contrib['shap_value'] > 0 else 'Decreases Risk'
                contrib['interpretation'] = self._interpret_feature(
                    contrib['feature_name'],
                    contrib['feature_value'],
                    contrib['shap_value']
                )
            
            explanations.append(contributions[:top_n])
        
        return explanations
    
    def _interpret_feature(self, feature_name, value, shap_value):
        """Generate clinical interpretation for feature contribution"""
        is_positive = shap_value > 0
        
        # Standardized Clinical Interpretations (Problem A)
        interpretations = {
            'socio_emotional_dq': f"Social-Emotional DQ ({value:.1f}) is {'below' if value < 85 else 'near'} normative levels",
            'language_dq': f"Language development quotient ({value:.1f}) indicates {'significant delay' if value < 70 else 'potential concern' if value < 85 else 'normative performance'}",
            'behavior_score': f"{'Elevated' if value > 15 else 'Moderate'} behavioral concerns identified (Score: {value:.1f})",
            'scii': f"Social Communication Impairment Index is {'High' if value > 40 else 'Notable'} at {value:.1f}",
            'nsi': f"Neurodevelopmental Severity Index indicates {'high' if value > 0.6 else 'moderate'} clinical burden ({value:.3f})",
            'erm': f"Environmental Risk Modifier shows {'limited' if value < 50 else 'moderate'} support engagement ({value:.1f})",
            'dbs': f"Delay Burden Score ({value:.2f}) {'contributes significantly to' if is_positive else 'mitigates'} overall risk",
            'delayed_domains': f"Multiple ({int(value)}) developmental domains show significant delays",
            'composite_dq': f"Overall Composite DQ of {value:.1f} {'suggests global delay' if value < 70 else 'is being monitored'}",
            'caregiver_engagement_score': f"Caregiver engagement level ({value:.1f}) {'requires strengthening' if value < 60 else 'is a protective factor'}",
            'gross_motor_dq': f"Gross motor performance at {value:.1f} shows {'delay' if value < 70 else 'atypical patterns'}",
            'fine_motor_dq': f"Fine motor development quotient ({value:.1f}) is {'low' if value < 75 else 'within range'}",
            'autism_screen_flag': f"Screening flag is {'Active' if value > 0.5 else 'Clear'} for neurodevelopmental markers",
        }
        
        return interpretations.get(feature_name, f"Feature '{feature_name}' (Value: {value:.2f}) {'increases' if is_positive else 'decreases'} predicted risk")
    
    def evaluate(self, X_test, y_test, verbose=True):
        """
        Comprehensive model evaluation
        
        Computes:
        - ROC-AUC
        - Sensitivity (Recall)
        - Specificity
        - F1 Score
        - Confusion Matrix
        - Calibration metrics
        """
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
        brier = brier_score_loss(y_test, probabilities)
        
        self.metrics = {
            'roc_auc': round(roc_auc, 4),
            'sensitivity': round(sensitivity, 4),
            'specificity': round(specificity, 4),
            'f1_score': round(f1, 4),
            'brier_score': round(brier, 4),
            'confusion_matrix': cm.tolist(),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_positives': int(tp)
        }
        
        if verbose:
            print("\n" + "="*60)
            print("MODEL EVALUATION RESULTS")
            print("="*60)
            print(f"ROC-AUC Score:      {roc_auc:.4f}")
            print(f"Sensitivity:        {sensitivity:.4f}")
            print(f"Specificity:        {specificity:.4f}")
            print(f"F1 Score:           {f1:.4f}")
            print(f"Brier Score:        {brier:.4f} (lower is better)")
            print(f"\nConfusion Matrix:")
            print(f"  TN: {tn:4d}  |  FP: {fp:4d}")
            print(f"  FN: {fn:4d}  |  TP: {tp:4d}")
            print("="*60)
        
        return self.metrics
    
    def plot_evaluation(self, X_test, y_test, save_path=None):
        """Generate evaluation plots"""
        predictions, probabilities = self.predict(X_test)
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. ROC Curve
        fpr, tpr, _ = roc_curve(y_test, probabilities)
        axes[0, 0].plot(fpr, tpr, label=f'ROC-AUC = {self.metrics["roc_auc"]:.4f}')
        axes[0, 0].plot([0, 1], [0, 1], 'k--', label='Random')
        axes[0, 0].set_xlabel('False Positive Rate')
        axes[0, 0].set_ylabel('True Positive Rate')
        axes[0, 0].set_title('ROC Curve')
        axes[0, 0].legend()
        
        # 2. Precision-Recall Curve
        precision, recall, _ = precision_recall_curve(y_test, probabilities)
        axes[0, 1].plot(recall, precision, label=f'F1 = {self.metrics["f1_score"]:.4f}')
        axes[0, 1].set_xlabel('Recall (Sensitivity)')
        axes[0, 1].set_ylabel('Precision')
        axes[0, 1].set_title('Precision-Recall Curve')
        axes[0, 1].legend()
        
        # 3. Calibration Curve
        prob_true, prob_pred = calibration_curve(y_test, probabilities, n_bins=10)
        axes[1, 0].plot(prob_pred, prob_true, marker='o', label='Calibrated XGB')
        axes[1, 0].plot([0, 1], [0, 1], 'k--', label='Perfectly Calibrated')
        axes[1, 0].set_xlabel('Mean Predicted Probability')
        axes[1, 0].set_ylabel('Fraction of Positives')
        axes[1, 0].set_title('Calibration Curve (Reliability Diagram)')
        axes[1, 0].legend()
        
        # 4. Feature Importance (XGBoost Internal)
        feat_importances = pd.Series(self.model.feature_importances_, index=self.feature_names)
        feat_importances.nlargest(10).plot(kind='barh', ax=axes[1, 1])
        axes[1, 1].set_title('Top 10 Feature Importances')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            print(f"Evaluation plots saved to {save_path}")
        
        return fig

    def save_model(self, file_path):
        """Save trained model and associated components"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'calibrated_model': self.calibrated_model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'label_encoders': self.label_encoders,
            'model_version': self.model_version,
            'metrics': self.metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(file_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {file_path}")

    @classmethod
    def load_model(cls, file_path):
        """Load saved model and return instance"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No model found at {file_path}")
            
        with open(file_path, 'rb') as f:
            model_data = pickle.load(f)
        
        instance = cls(model_version=model_data.get('model_version', 'v1.0'))
        instance.model = model_data['model']
        instance.calibrated_model = model_data.get('calibrated_model')
        instance.scaler = model_data['scaler']
        instance.feature_names = model_data['feature_names']
        instance.label_encoders = model_data['label_encoders']
        instance.metrics = model_data.get('metrics', {})
        
        # Re-initialize SHAP explainer
        instance._init_shap_explainer(None)
        
        return instance


if __name__ == '__main__':
    # Test script with dummy data
    print("Testing AutismRiskClassifier...")
    
    # Create dummy data
    data = []
    for _ in range(100):
        row = {
            'gross_motor_dq': np.random.uniform(40, 100),
            'fine_motor_dq': np.random.uniform(40, 100),
            'language_dq': np.random.uniform(40, 100),
            'cognitive_dq': np.random.uniform(40, 100),
            'socio_emotional_dq': np.random.uniform(40, 100),
            'composite_dq': np.random.uniform(40, 100),
            'gross_motor_delay': np.random.choice([0, 1]),
            'fine_motor_delay': np.random.choice([0, 1]),
            'language_delay': np.random.choice([0, 1]),
            'cognitive_delay': np.random.choice([0, 1]),
            'socio_emotional_delay': np.random.choice([0, 1]),
            'delayed_domains': np.random.randint(0, 5),
            'adhd_risk': np.random.choice([0, 1]),
            'behavior_risk': np.random.choice([0, 1]),
            'attention_score': np.random.uniform(0, 100),
            'behavior_score': np.random.uniform(0, 100),
            'stunting': np.random.choice([0, 1]),
            'wasting': np.random.choice([0, 1]),
            'anemia': np.random.choice([0, 1]),
            'nutrition_score': np.random.uniform(0, 100),
            'caregiver_engagement_score': np.random.uniform(0, 100),
            'language_exposure_score': np.random.uniform(0, 100),
            'parent_child_interaction_score': np.random.uniform(0, 100),
            'stimulation_score': np.random.uniform(0, 100),
            'age_months': np.random.randint(18, 60),
            'gender': np.random.choice(['Male', 'Female']),
            'scii': np.random.uniform(0, 100),
            'nsi': np.random.uniform(0, 1),
            'erm': np.random.uniform(0, 100),
            'dbs': np.random.uniform(0, 1),
            'autism_risk': np.random.choice([0, 1])
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    
    classifier = AutismRiskClassifier()
    X, y = classifier.prepare_data(df)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    classifier.train(X_train, y_train)
    metrics = classifier.evaluate(X_test, y_test)
    
    print("\nSample prediction:")
    sample = X_test.iloc[:1]
    result = classifier.predict_with_stratification(sample)[0]
    print(result)
    
    print("\nSample SHAP explanation:")
    explanation = classifier.explain_prediction(sample)[0]
    for e in explanation:
        print(f"  {e['feature_name']}: {e['interpretation']} ({e['impact_direction']})")
