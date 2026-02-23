import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import json
from datetime import datetime
from pathlib import Path
from sklearn.model_selection import train_test_split

# Add parent directory to path to reach ml module
sys.path.append(str(Path(__file__).parent.parent))

from ml.feature_engineering import FeatureEngineer
from ml.models.risk_escalation_predictor import RiskEscalationPredictor

def setup_logging(save_dir):
    """Setup dual logging to file and console"""
    log_path = os.path.join(save_dir, 'training.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def plot_learning_curves(evals_result, save_dir):
    """Generate professional learning curves"""
    if not evals_result or 'validation_0' not in evals_result:
        return
        
    epochs = len(evals_result['validation_0']['logloss'])
    x_axis = range(0, epochs)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # 1. Logloss
    axes[0].plot(x_axis, evals_result['validation_0']['logloss'], label='Train')
    if 'validation_1' in evals_result:
        axes[0].plot(x_axis, evals_result['validation_1']['logloss'], label='Val')
    axes[0].set_title('Log Loss')
    axes[0].set_xlabel('Epochs')
    axes[0].legend()
    
    # 2. AUC
    axes[1].plot(x_axis, evals_result['validation_0']['auc'], label='Train')
    if 'validation_1' in evals_result:
        axes[1].plot(x_axis, evals_result['validation_1']['auc'], label='Val')
    axes[1].set_title('ROC-AUC')
    axes[1].set_xlabel('Epochs')
    axes[1].legend()
    
    # 3. Error
    axes[2].plot(x_axis, evals_result['validation_0']['error'], label='Train')
    if 'validation_1' in evals_result:
        axes[2].plot(x_axis, evals_result['validation_1']['error'], label='Val')
    axes[2].set_title('Classification Error')
    axes[2].set_xlabel('Epochs')
    axes[2].legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'learning_curves.png'))
    plt.close()

def prepare_escalation_data(df, logger):
    """Prepare longitudinal data for escalation modeling"""
    escalation_data = []
    child_ids = df['child_id'].unique()
    logger.info(f"Scanning {len(child_ids)} children for longitudinal patterns...")
    
    for child_id in child_ids:
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
    # Setup directories
    save_dir = 'ml/models/saved/escalation'
    eval_dir = 'ml/evaluation/escalation'
    os.makedirs(save_dir, exist_ok=True)
    os.makedirs(eval_dir, exist_ok=True)
    
    logger = setup_logging(save_dir)
    logger.info("="*60)
    logger.info("TRAINING STARTED: Risk Escalation Predictor (Model B)")
    logger.info("="*60)

    # 1. Load data
    data_path = 'ml/data/cleaned_client_data.csv'
    if not os.path.exists(data_path):
        logger.error(f"Data file {data_path} not found.")
        return

    df = pd.read_csv(data_path)
    logger.info("Performing feature engineering...")
    engineer = FeatureEngineer()
    df_engineered = engineer.engineer_features(df)

    # 2. Prepare longitudinal data
    logger.info("Extracting escalation labels...")
    df_escalation = prepare_escalation_data(df_engineered, logger)

    if len(df_escalation) == 0:
        logger.warning("No longitudinal data found (requires multiple cycles per child).")
        logger.info("Workflow completed: Model B architecture ready but training skipped due to data constraints.")
        return

    # 3. Prepare for training
    predictor = RiskEscalationPredictor(model_version='v1.0')
    X, y = predictor.prepare_data(df_escalation)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if y.nunique() > 1 else None
    )
    
    # Val split
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.15, random_state=42, stratify=y_train if y_train.nunique() > 1 else None
    )

    logger.info(f"Training on {len(X_train)} samples, validating on {len(X_val)}.")

    # 4. Train
    eval_result = predictor.train(X_train, y_train, X_val, y_val)

    # 5. Visualizations & Metrics
    if eval_result:
        plot_learning_curves(eval_result, eval_dir)
    
    meta = {
        'timestamp': datetime.now().isoformat(),
        'model_type': 'XGBClassifier',
        'features': predictor.feature_names,
        'train_size': len(X_train),
        'val_size': len(X_val),
        'final_metrics': {k: v[-1] for k, v in eval_result['validation_1'].items()} if eval_result else {}
    }
    with open(os.path.join(save_dir, 'training_meta.json'), 'w') as f:
        json.dump(meta, f, indent=4)

    # 6. Save
    save_path = os.path.join(save_dir, 'risk_escalation_predictor_v1.pkl')
    predictor.save_model(save_path)
    
    logger.info(f"SUCCESS: Model B saved to {save_path}")
    logger.info("="*60)

if __name__ == "__main__":
    main()
