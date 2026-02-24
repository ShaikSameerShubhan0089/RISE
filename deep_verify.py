
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')

def deep_verify():
    url = os.getenv("DATABASE_URL")
    engine = create_engine(url)
    
    with engine.connect() as conn:
        print("--- Checking Assessments for TRUE Booleans ---")
        # Find any rows where stunting or wasting is True
        query = text("SELECT assessment_id, stunting, wasting, autism_screen_flag FROM assessments WHERE stunting = True OR wasting = True LIMIT 5")
        results = conn.execute(query).fetchall()
        print(f"Rows with True values: {len(results)}")
        for r in results:
            print(f" ID: {r[0]}, Stunting: {r[1]}, Wasting: {r[2]}, Autism Flag: {r[3]}")
            
        print("\n--- Checking SHAP Explanations Data ---")
        query = text("SELECT prediction_id, feature_name, shap_value FROM shap_explanations LIMIT 5")
        results = conn.execute(query).fetchall()
        for r in results:
            print(f" PredID: {r[0]}, Feature: {r[1]}, SHAP: {r[2]}")
            
        # Count some unique prediction_ids in SHAP
        query = text("SELECT COUNT(DISTINCT prediction_id) FROM shap_explanations")
        unique_preds = conn.execute(query).scalar()
        print(f"\nUnique Prediction IDs in SHAP: {unique_preds}")

if __name__ == "__main__":
    deep_verify()
