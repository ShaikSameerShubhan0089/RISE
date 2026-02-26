"""
Short Optuna hyperparameter tuning for XGBoost classifier.

Run: python ml/optuna_xgb_tune.py --trials 20
Outputs best params to ml/models/saved/xgb_optuna_best.json
"""
import os
import sys
import json
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import optuna
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import make_scorer, f1_score
import xgboost as xgb

from ml.feature_engineering import FeatureEngineer
from ml.models.autism_risk_classifier import AutismRiskClassifier


def load_data():
    data_path = 'ml/data/cleaned_client_data.csv'
    df = pd.read_csv(data_path)
    engineer = FeatureEngineer()
    df_e = engineer.engineer_features(df)

    clf = AutismRiskClassifier()
    X, y = clf.prepare_data(df_e)
    return X, y


def objective(trial, X, y):
    params = {
        'max_depth': trial.suggest_int('max_depth', 3, 8),
        'learning_rate': trial.suggest_loguniform('learning_rate', 1e-3, 0.3),
        'n_estimators': trial.suggest_int('n_estimators', 100, 500),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
        'gamma': trial.suggest_float('gamma', 0.0, 5.0),
        'reg_alpha': trial.suggest_float('reg_alpha', 0.0, 1.0),
        'reg_lambda': trial.suggest_float('reg_lambda', 0.0, 5.0),
        'use_label_encoder': False,
        'eval_metric': 'logloss',
        'n_jobs': 1,
        'random_state': 42
    }

    model = xgb.XGBClassifier(**params)

    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    scorer = make_scorer(f1_score)

    scores = cross_val_score(model, X, y, cv=cv, scoring=scorer, n_jobs=1)
    return float(np.mean(scores))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trials', type=int, default=20)
    args = parser.parse_args()

    X, y = load_data()
    print(f"Loaded data X={X.shape}, y={y.shape}")

    def _objective(trial):
        return objective(trial, X, y)

    study = optuna.create_study(direction='maximize')
    study.optimize(_objective, n_trials=args.trials)

    best = study.best_trial
    print("Best F1 (CV):", best.value)
    print("Best params:")
    print(best.params)

    out_dir = 'ml/models/saved'
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'xgb_optuna_best.json')
    with open(out_path, 'w') as f:
        json.dump({'best_score': float(best.value), 'best_params': best.params}, f, indent=2)

    print(f"Saved best params to {out_path}")


if __name__ == '__main__':
    main()
