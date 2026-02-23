
import os
import sys

sys.path.append(os.getcwd())

from database import get_db
import models

def check_users():
    db = next(get_db())
    roles = ['system_admin', 'district_officer', 'supervisor', 'state_admin']
    
    print(f"{'Email':<40} | {'Role':<15} | {'State':<5} | {'Dist':<5} | {'Mandal':<5} | {'Center':<5}")
    print("-" * 100)
    
    for role in roles:
        users = db.query(models.User).filter(models.User.role == role).all()
        for user in users:
            print(f"{user.email:<40} | {user.role:<15} | {str(user.state_id):<5} | {str(user.district_id):<5} | {str(user.mandal_id):<5} | {str(user.center_id):<5}")

if __name__ == "__main__":
    check_users()
