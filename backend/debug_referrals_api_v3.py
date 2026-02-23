
import os
import sys
import json
import traceback

sys.path.append(os.getcwd())

from database import get_db
import models
import auth
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_referrals_api():
    db = next(get_db())
    # Test all roles the user mentioned
    roles = ['system_admin', 'district_officer', 'supervisor', 'state_admin']
    
    for role in roles:
        print(f"\n" + "="*50)
        print(f"TESTING ROLE: {role}")
        print("="*50)
        
        user = db.query(models.User).filter(models.User.role == role).first()
        if not user:
            print(f"CRITICAL: No user found for role {role}. Check seed data.")
            continue
            
        print(f"User Found: {user.email} (ID: {user.user_id})")
        
        token = auth.create_access_token(data={
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role
        })
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            print(f"Requesting GET /api/referrals...")
            response = client.get("/api/referrals", headers=headers)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"ERROR: Backend returned non-200!")
                print(f"Response Body: {response.text}")
            else:
                data = response.json()
                print(f"SUCCESS: Received {len(data)} referrals")
                if len(data) > 0:
                    print(f"Sample data: Child={data[0].get('child_name')}, Risk={data[0].get('risk_level_at_referral')}")
                    
        except Exception as e:
            print(f"EXCEPTION: {str(e)}")
            traceback.print_exc()
        
        print(f"Finished testing role: {role}")

if __name__ == "__main__":
    test_referrals_api()
