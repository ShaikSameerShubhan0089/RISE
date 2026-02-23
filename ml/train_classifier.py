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
from ml.models.autism_risk_classifier import AutismRiskClassifier

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
    """Generate professional learning curves for logloss, auc, and error"""
    epochs = len(evals_result['validation_0']['logloss'])
    x_axis = range(0, epochs)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # 1. Logloss
    axes[0].plot(x_axis, evals_result['validation_0']['logloss'], label='Train')
    axes[0].plot(x_axis, evals_result['validation_1']['logloss'], label='Val')
    axes[0].set_title('Log Loss')
    axes[1].set_xlabel('Epochs')
    axes[0].legend()
    
    # 2. AUC
    axes[1].plot(x_axis, evals_result['validation_0']['auc'], label='Train')
    axes[1].plot(x_axis, evals_result['validation_1']['auc'], label='Val')
    axes[1].set_title('ROC-AUC')
    axes[1].set_xlabel('Epochs')
    axes[1].legend()
    
    # 3. Error
    axes[2].plot(x_axis, evals_result['validation_0']['error'], label='Train')
    axes[2].plot(x_axis, evals_result['validation_1']['error'], label='Val')
    axes[2].set_title('Classification Error')
    axes[2].set_xlabel('Epochs')
    axes[2].legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'learning_curves.png'))
    plt.close()

def main():
    # Setup directories
    save_dir = 'ml/models/saved/classifier'
    eval_dir = 'ml/evaluation/classifier'
    os.makedirs(save_dir, exist_ok=True)
    os.makedirs(eval_dir, exist_ok=True)
    
    logger = setup_logging(save_dir)
    logger.info("="*60)
    logger.info("TRAINING STARTED: Autism Risk Classifier (Model A)")
    logger.info("="*60)

    # 1. Load data
    data_path = 'ml/data/cleaned_client_data.csv'
    if not os.path.exists(data_path):
        logger.error(f"Data file {data_path} not found. Run clean_dataset.py first.")
        return

    df = pd.read_csv(data_path)
    logger.info(f"Loaded {len(df)} records from {data_path}")

    # 2. Feature Engineering
    logger.info("Performing clinical feature engineering...")
    engineer = FeatureEngineer()
    df_engineered = engineer.engineer_features(df)

    # 3. Prepare for training
    classifier = AutismRiskClassifier(model_version='v1.0')
    X, y = classifier.prepare_data(df_engineered)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.15, random_state=42, stratify=y_train
    )

    logger.info(f"Dataset split: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")

    # 4. Train
    logger.info("Starting XGBoost training with imbalance handling...")
    eval_result = classifier.train(X_train, y_train, X_val, y_val)

    # 5. Visualizations & Metrics
    logger.info("Generating learning curves...")
    if eval_result:
        plot_learning_curves(eval_result, eval_dir)
    
    # Save training metadata
    meta = {
        'timestamp': datetime.now().isoformat(),
        'model_type': 'XGBClassifier',
        'features': classifier.feature_names,
        'train_size': len(X_train),
        'val_size': len(X_val),
        'final_metrics': {k: v[-1] for k, v in eval_result['validation_1'].items()} if eval_result else {}
    }
    with open(os.path.join(save_dir, 'training_meta.json'), 'w') as f:
        json.dump(meta, f, indent=4)

    # 6. Save model
    save_path = os.path.join(save_dir, 'autism_risk_classifier_v1.pkl')
    classifier.save_model(save_path)
    
    logger.info(f"SUCCESS: Model and reports saved.")
    logger.info("="*60)

if __name__ == "__main__":
    main()
