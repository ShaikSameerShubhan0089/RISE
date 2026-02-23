import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import shap
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, roc_curve, precision_recall_curve, auc

# Add parent directory to path to reach ml module
sys.path.append(str(Path(__file__).parent.parent))

from ml.feature_engineering import FeatureEngineer
from ml.models.risk_escalation_predictor import RiskEscalationPredictor

def plot_evaluation_dashboard(y_true, y_probs, eval_dir):
    """Generate professional evaluation charts for escalation"""
    y_pred = (y_probs >= 0.5).astype(int)
    cm = confusion_matrix(y_true, y_pred)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # 1. Confusion Matrix
    sns.heatmap(cm, annot=True, fmt='d', cmap='Oranges', ax=axes[0])
    axes[0].set_title('Confusion Matrix (Escalation)')
    axes[0].set_xlabel('Predicted')
    axes[0].set_ylabel('Actual')
    
    # 2. ROC Curve
    fpr, tpr, _ = roc_curve(y_true, y_probs)
    roc_auc = auc(fpr, tpr)
    axes[1].plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC (area = {roc_auc:.2f})')
    axes[1].plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    axes[1].set_title('ROC Curve')
    axes[1].set_xlabel('False Positive Rate')
    axes[1].set_ylabel('True Positive Rate')
    axes[1].legend(loc="lower right")
    
    # 3. Precision-Recall Curve
    precision, recall, _ = precision_recall_curve(y_true, y_probs)
    pr_auc = auc(recall, precision)
    axes[2].plot(recall, precision, color='red', lw=2, label=f'PR (area = {pr_auc:.2f})')
    axes[2].set_title('Precision-Recall Curve')
    axes[2].set_xlabel('Recall')
    axes[2].set_ylabel('Precision')
    axes[2].legend(loc="lower left")
    
    plt.tight_layout()
    plt.savefig(os.path.join(eval_dir, 'evaluation_dashboard.png'))
    plt.close()

def plot_shap_summary(predictor, X_test, eval_dir):
    """Generate SHAP feature importance plot for Model B"""
    X_test_scaled = predictor.scaler.transform(X_test)
    explainer = shap.TreeExplainer(predictor.model)
    shap_values = explainer.shap_values(X_test_scaled)
    
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X_test_scaled, feature_names=predictor.feature_names, show=False)
    plt.title('SHAP Feature Importance (Escalation)')
    plt.tight_layout()
    plt.savefig(os.path.join(eval_dir, 'shap_summary.png'))
    plt.close()

def prepare_escalation_data(df):
    """Longitudinal data preparation (eval context)"""
    escalation_data = []
    for child_id in df['child_id'].unique():
        child_assessments = df[df['child_id'] == child_id].sort_values('assessment_cycle')
        if len(child_assessments) < 2: continue
        for i in range(len(child_assessments) - 1):
            current = child_assessments.iloc[i]
            next_assessment = child_assessments.iloc[i + 1]
            will_escalate = (current['autism_risk'] == 0) and (next_assessment['autism_risk'] == 1)
            row = current.to_dict()
            row['will_escalate'] = int(will_escalate)
            escalation_data.append(row)
    return pd.DataFrame(escalation_data)

def main():
    print("="*60)
    print("TESTING: Risk Escalation Predictor (Model B)")
    print("="*60)

    # 1. Load model
    save_dir = 'ml/models/saved/escalation'
    eval_dir = 'ml/evaluation/escalation'
    os.makedirs(eval_dir, exist_ok=True)
    
    model_path = os.path.join(save_dir, 'risk_escalation_predictor_v1.pkl')
    if not os.path.exists(model_path):
        print(f"Error: {model_path} not found. Ensure Model B training succeeded.")
        return

    print(f"Loading model from {model_path}...")
    predictor = RiskEscalationPredictor.load_model(model_path)

    # 2. Load data
    data_path = 'ml/data/cleaned_client_data.csv'
    df = pd.read_csv(data_path)
    engineer = FeatureEngineer()
    df_engineered = engineer.engineer_features(df)
    df_escalation = prepare_escalation_data(df_engineered)

    if len(df_escalation) == 0:
        print("\n[!] No longitudinal data to test.")
        return

    X, y = predictor.prepare_data(df_escalation)
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if y.nunique() > 1 else None
    )

    # 3. Get metrics and probabilities
    preds, probs = predictor.predict(X_test)
    
    # Generate charts
    print("Generating evaluation dashboard...")
    plot_evaluation_dashboard(y_test, probs, eval_dir)
    
    print("Generating SHAP feature importance...")
    plot_shap_summary(predictor, X_test, eval_dir)

    # 4. Standard Metrics Output
    metrics = predictor.evaluate(X_test, y_test, verbose=True)
    
    # Save test results
    report = {
        'metrics': metrics,
        'confusion_matrix': confusion_matrix(y_test, preds).tolist(),
        'test_size': len(X_test)
    }
    with open(os.path.join(eval_dir, 'test_report.json'), 'w') as f:
        json.dump(report, f, indent=4)

    print(f"\nSUCCESS: Evaluation artifacts saved to {eval_dir}")
    print("="*60)

if __name__ == "__main__":
    main()
