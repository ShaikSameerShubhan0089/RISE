import pandas as pd
from ml.models.autism_risk_classifier import AutismRiskClassifier
from ml.feature_engineering import FeatureEngineer
import os
import sys

def verify_data(file_path):
    print(f"Verifying {file_path}...")
    df = pd.read_csv(file_path)
    
    # 1. Check for expected columns
    classifier = AutismRiskClassifier()
    engineer = FeatureEngineer()
    
    # Apply feature engineering to see if it works
    print("Applying feature engineering...")
    try:
        df_engineered = engineer.engineer_features(df)
        print("Feature engineering successful")
    except Exception as e:
        print(f"Feature engineering failed: {e}")
        return
    
    # Try prepare_data
    print("Preparing data for model...")
    try:
        X, y = classifier.prepare_data(df_engineered)
        print("prepare_data successful")
        print(f"Features (X) shape: {X.shape}")
        print(f"Target (y) distribution: {y.value_counts().to_dict()}")
    except Exception as e:
        print(f"prepare_data failed: {e}")
        # Print columns to help debug
        print("Columns in engineered df:", df_engineered.columns.tolist())
        return

    print("\nData verification passed! The cleaned dataset is ready for model training.")

if __name__ == "__main__":
    data_path = r'C:\Users\S Sameer\Desktop\autism - Copy\ml\data\cleaned_client_data.csv'
    verify_data(data_path)
