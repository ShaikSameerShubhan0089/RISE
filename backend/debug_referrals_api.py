
import os
import sys
import json

# Add the current directory to sys.path so we can import our modules
sys.path.append(os.getcwd())

from database import get_db
import models
import auth
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_referrals_api():
    db = next(get_db())
    roles = ['system_admin', 'district_officer', 'supervisor']
    
    for role in roles:
        print(f"\n--- Testing Role: {role} ---")
        user = db.query(models.User).filter(models.User.role == role).first()
        if not user:
            print(f"Skipping {role}: No user found")
            continue
            
        token = auth.create_access_token(data={
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role
        })
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            print(f"Calling /api/referrals as {role}...")
            response = client.get("/api/referrals", headers=headers)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Error Response Body: {response.text}")
            else:
                data = response.json()
                print(f"Success! Found {len(data)} referrals")
                if len(data) > 0:
                    print(f"Data mapping check: {data[0].keys()}")
                    
        except Exception as e:
            import traceback
            print(f"Exception during request: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    test_referrals_api()
