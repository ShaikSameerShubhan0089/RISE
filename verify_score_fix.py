import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_flipped_risk():
    # 1. Login to get token
    login_data = {"email": "admin@cdss.gov.in", "password": "admin123"}
    login_res = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        return
    
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get a child ID
    children_res = requests.get(f"{BASE_URL}/children", headers=headers)
    if children_res.status_code != 200 or not children_res.json():
        print("Failed to fetch children")
        return
    child_id = children_res.json()[0]["child_id"]
    
    # 3. Define Payloads
    payload_high_dq = {
        "child_id": child_id,
        "model_type": "Model A",
        "inputs": {
            "gross_motor_dq": 155.5,
            "fine_motor_dq": 140.25,
            "language_dq": 130.0,
            "cognitive_dq": 120.5,
            "socio_emotional_dq": 110.75,
            "composite_dq": 135.0,
            "adhd_risk": False,
            "behavior_risk": False,
            "caregiver_engagement_score": 75.5,
            "stimulation_score": 80.0,
            "language_exposure_score": 90.5
        }
    }
    
    payload_low_dq = {
        "child_id": child_id,
        "model_type": "Model A",
        "inputs": {
            "gross_motor_dq": 60.5,
            "fine_motor_dq": 62.0,
            "language_dq": 58.5,
            "cognitive_dq": 65.0,
            "socio_emotional_dq": 55.0,
            "composite_dq": 60.0,
            "adhd_risk": True,
            "behavior_risk": True,
            "caregiver_engagement_score": 40.0,
            "stimulation_score": 45.0,
            "language_exposure_score": 40.0
        }
    }
    
    print(f"\n--- Case 1: High DQ (135.0 Composite) ---")
    res_high = requests.post(f"{BASE_URL}/predictions/run", headers=headers, json=payload_high_dq)
    if res_high.status_code == 200:
        data = res_high.json()
        print(f"Risk Tier: {data.get('risk_tier')}")
        print(f"Probability: {data.get('combined_high_probability'):.4f}")
        print("Top 3 Drivers:")
        for feat in data.get('top_features', [])[:3]:
            print(f"  - {feat['feature_name']}: {feat['shap_value']:+.4f} ({feat['impact_direction']})")
    else:
        print(f"Error {res_high.status_code}: {res_high.text}")

    print(f"\n--- Case 2: Low DQ (60.0 Composite) ---")
    res_low = requests.post(f"{BASE_URL}/predictions/run", headers=headers, json=payload_low_dq)
    if res_low.status_code == 200:
        data = res_low.json()
        print(f"Risk Tier: {data.get('risk_tier')}")
        print(f"Probability: {data.get('combined_high_probability'):.4f}")
        print("Top 3 Drivers:")
        for feat in data.get('top_features', [])[:3]:
            print(f"  - {feat['feature_name']}: {feat['shap_value']:+.4f} ({feat['impact_direction']})")
    else:
        print(f"Error {res_low.status_code}: {res_low.text}")

if __name__ == "__main__":
    test_flipped_risk()
