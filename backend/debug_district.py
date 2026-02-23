
import os
import sys

# Add the current directory to sys.path so we can import our modules
sys.path.append(os.getcwd())

from database import get_db
import models
import auth
from sqlalchemy.orm import Session
from datetime import timedelta

def test_district_access():
    db = next(get_db())
    # Find a district officer
    do = db.query(models.User).filter(models.User.role == 'district_officer').first()
    if not do:
        print("No district officer found in DB")
        return

    print(f"Testing for user: {do.full_name} (Email: {do.email})")
    print(f"Role: {do.role}, District ID: {do.district_id}, Status: {do.status}")
    
    # Generate token
    token = auth.create_access_token(data={
        "user_id": do.user_id,
        "email": do.email,
        "role": do.role
    })
    print(f"\nGenerated Token: {token}")
    
    # Test get_current_user logic manually
    try:
        from auth import decode_access_token
        payload = decode_access_token(token)
        print(f"\nDecoded Payload: {payload}")
        
        user_id = payload.get("user_id")
        user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if user:
            print(f"User validated: {user.full_name}")
            if user.status != "Active":
                print("ERROR: User is NOT Active")
            else:
                print("User status is Active")
        else:
            print("ERROR: User not found in DB from user_id in token")
            
    except Exception as e:
        print(f"ERROR in token/user validation: {e}")

    # Test list_children logic manually
    try:
        from rbac import filter_children_by_access
        query = filter_children_by_access(do, db)
        count = query.count()
        print(f"\nChildren accessible to {do.role}: {count}")
    except Exception as e:
        print(f"ERROR in filter_children_by_access: {e}")

if __name__ == "__main__":
    test_district_access()
