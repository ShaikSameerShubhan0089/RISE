import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def get_token():
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@cdss.gov.in",
        "password": "admin123"
    })
    return res.json()["access_token"]

def test_registration():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Unique names for each run
    ts = int(time.time())
    data = {
        "first_name": "TestChild",
        "last_name": str(ts),
        "dob": "2022-01-01",
        "gender": "Male",
        "center_id": 1,
        "caregiver_name": "Test Caregiver",
        "caregiver_email": f"parent_{ts}@example.com",
        "caregiver_relationship": "Mother",
        "create_parent_account": True,
        "parent_password": "password123"
    }
    
    print("\n--- Testing Child + Parent Registration ---")
    res = requests.post(f"{BASE_URL}/children", json=data, headers=headers)
    if res.status_code == 201:
        child = res.json()
        print(f"Registered Child: {child['first_name']} (ID: {child['child_id']})")
        return child['child_id']
    else:
        print(f"Registration failed: {res.status_code} - {res.text}")
        return None

def test_prediction(child_id):
    if not child_id: return
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "child_id": child_id,
        "model_type": "Model A",
        "inputs": {
            "gross_motor_dq": 85.0,
            "fine_motor_dq": 82.0,
            "language_dq": 65.0,
            "cognitive_dq": 78.0,
            "socio_emotional_dq": 70.0,
            "composite_dq": 76.0,
            "adhd_risk": False,
            "stunting": False,
            "caregiver_engagement_score": 80.0,
            "stimulation_score": 75.0
        }
    }
    
    print("\n--- Testing Real-Time Prediction ---")
    res = requests.post(f"{BASE_URL}/predictions/run", json=data, headers=headers)
    if res.status_code == 200:
        pred = res.json()
        print(f"Prediction Success!")
        print(f"Risk Class: {pred['predicted_risk_class']}")
        print(f"Probability: {pred['combined_high_probability']:.2f}")
        print(f"Top Feature: {pred['top_features'][0]['feature_name']}")
    else:
        print(f"Prediction failed: {res.status_code} - {res.text}")

if __name__ == "__main__":
    cid = test_registration()
    test_prediction(cid)
