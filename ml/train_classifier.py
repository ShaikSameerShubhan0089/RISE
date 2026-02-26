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
from sklearn.metrics import precision_recall_curve
from imblearn.over_sampling import SMOTE

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

    # 3.5 Apply SMOTE to training data for class balance
    logger.info("Applying SMOTE to balance training data...")
    original_distribution = pd.Series(y_train).value_counts().to_dict()
    logger.info(f"Original training distribution: {original_distribution}")
    
    smote = SMOTE(random_state=42, k_neighbors=5)
    X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
    balanced_distribution = pd.Series(y_train_balanced).value_counts().to_dict()
    logger.info(f"After SMOTE: {balanced_distribution}")

    # 4. Train
    logger.info("Starting XGBoost training with imbalance handling...")
    # If Optuna best params exist, load and pass them into training
    optuna_params_path = 'ml/models/saved/xgb_optuna_best.json'
    xgb_params = None
    if os.path.exists(optuna_params_path):
        try:
            with open(optuna_params_path, 'r') as f:
                opt = json.load(f)
            # Optuna JSON stores params under 'best_params'
            xgb_params = opt.get('best_params') or opt.get('best_params', None)
            logger.info(f"Loaded Optuna best params from {optuna_params_path}")
        except Exception as e:
            logger.warning(f"Could not load Optuna params: {e}")

    eval_result = classifier.train(X_train_balanced, y_train_balanced, X_val, y_val, xgb_params=xgb_params)
    
    # 4.5 Find optimal decision threshold
    logger.info("Finding optimal decision threshold for clinical use...")
    y_val_pred_proba = classifier.model.predict_proba(classifier.scaler.transform(X_val))[:, 1]
    precision, recall, thresholds = precision_recall_curve(y_val, y_val_pred_proba)
    
    # Find threshold where recall >= 0.75 (catch 75%+ of autism cases)
    optimal_idx = np.where(recall >= 0.75)[0]
    if len(optimal_idx) > 0:
        optimal_threshold = thresholds[optimal_idx[-1]]
        logger.info(f"Optimal threshold: {optimal_threshold:.3f} (targets 75%+ recall)")
        classifier.optimal_threshold = optimal_threshold
    else:
        logger.warning("Could not find threshold with 75% recall, using maximum available recall")
        best_idx = np.argmax(recall)
        classifier.optimal_threshold = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
        logger.info(f"Using threshold: {classifier.optimal_threshold:.3f} with recall: {recall[best_idx]:.3f}")

    # 5. Visualizations & Metrics
    logger.info("Generating learning curves...")
    if eval_result:
        plot_learning_curves(eval_result, eval_dir)
    
    # Save training metadata
    # convert any numpy/float32 values into native types for JSON
    serialized_metrics = {}
    if eval_result:
        for k, v in eval_result['validation_1'].items():
            val = v[-1]
            try:
                serialized_metrics[k] = float(val)
            except Exception:
                serialized_metrics[k] = val
    
    thr = getattr(classifier, 'optimal_threshold', None)
    if thr is not None:
        try:
            thr = float(thr)
        except Exception:
            pass

    meta = {
        'timestamp': datetime.now().isoformat(),
        'model_type': 'XGBClassifier',
        'features': classifier.feature_names,
        'train_size': len(X_train),
        'val_size': len(X_val),
        'final_metrics': serialized_metrics,
        # record the threshold found during training so that evaluation can reuse it
        'optimal_threshold': thr
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
