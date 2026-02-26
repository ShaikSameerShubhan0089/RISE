"""
Quick data & label audit for cleaned_client_data.csv

Produces:
- ml/data/audit_summary.json
- ml/data/suspicious_records.csv

Run: python ml/data_audit.py
"""
import os
import sys
import json
import pandas as pd
from pathlib import Path

# allow importing ml package
sys.path.append(str(Path(__file__).parent.parent))

from ml.feature_engineering import FeatureEngineer, validate_data


def main():
    data_path = 'ml/data/cleaned_client_data.csv'
    out_dir = 'ml/data'
    os.makedirs(out_dir, exist_ok=True)

    if not os.path.exists(data_path):
        print(f"Data not found: {data_path}")
        return

    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} records from {data_path}")

    engineer = FeatureEngineer()
    df_e = engineer.engineer_features(df)

    # Module-level validation helper
    validation = validate_data(df_e)

    # Find suspicious records
    suspicious_idx = set()

    # Missing target
    if 'autism_risk' in df_e.columns:
        missing_target = df_e[df_e['autism_risk'].isnull()].index.tolist()
        suspicious_idx.update(missing_target)

    # Out-of-range DQ or age
    dq_cols = ['gross_motor_dq', 'fine_motor_dq', 'language_dq', 'cognitive_dq', 'socio_emotional_dq', 'composite_dq']
    for col in dq_cols:
        if col in df_e.columns:
            bad = df_e[(df_e[col] < 0) | (df_e[col] > 100)].index.tolist()
            suspicious_idx.update(bad)

    if 'age_months' in df_e.columns:
        bad_age = df_e[(df_e['age_months'] < 0) | (df_e['age_months'] > 72)].index.tolist()
        suspicious_idx.update(bad_age)

    # Duplicates (child_id + assessment_cycle)
    if {'child_id', 'assessment_cycle'}.issubset(df_e.columns):
        dup_mask = df_e.duplicated(subset=['child_id', 'assessment_cycle'], keep=False)
        dup_idx = df_e[dup_mask].index.tolist()
        suspicious_idx.update(dup_idx)

    # Extreme composite DQ outliers
    if 'composite_dq' in df_e.columns:
        outliers = df_e[(df_e['composite_dq'] < 20) | (df_e['composite_dq'] > 120)].index.tolist()
        suspicious_idx.update(outliers)

    suspicious = df_e.loc[sorted(suspicious_idx)].copy()

    summary = {
        'total_records': int(len(df_e)),
        'suspicious_count': int(len(suspicious)),
        'validation_warnings': validation.get('warnings', []),
        'missing_values_sample': {k: int(v) for k, v in validation.get('missing_values', {}).items() if v > 0}
    }

    # Save outputs
    summary_path = os.path.join(out_dir, 'audit_summary.json')
    suspicious_path = os.path.join(out_dir, 'suspicious_records.csv')

    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    if len(suspicious) > 0:
        suspicious.to_csv(suspicious_path, index=False)
        print(f"Wrote {len(suspicious)} suspicious records to {suspicious_path}")
    else:
        # Ensure previous file removed if none
        if os.path.exists(suspicious_path):
            os.remove(suspicious_path)

    print("Audit summary:")
    print(json.dumps(summary, indent=2))
    print(f"Saved summary to {summary_path}")


if __name__ == '__main__':
    main()
