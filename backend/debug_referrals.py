
import os
import sys

# Add the current directory to sys.path so we can import our modules
sys.path.append(os.getcwd())

from database import get_db
import models
import rbac
from sqlalchemy.orm import Session
from sqlalchemy import or_

def test_visibility():
    db = next(get_db())
    admin = db.query(models.User).filter(models.User.email == 'admin@cdss.gov.in').first()
    if not admin:
        print("Admin user not found")
        return

    print(f"Testing for user: {admin.full_name} (Role: {admin.role})")
    
    # 1. Total referrals in DB
    total_refs = db.query(models.Referral).count()
    print(f"Total referrals in DB: {total_refs}")
    
    # 2. Filtered children
    children_q = rbac.filter_children_by_access(admin, db)
    child_ids_sq = children_q.with_entities(models.Child.child_id).subquery()
    
    # 3. Query with JOINS
    query = db.query(
        models.Referral, 
        models.Child.first_name, 
        models.Child.last_name, 
        models.AnganwadiCenter.center_name
    ).join(
        models.Child, models.Referral.child_id == models.Child.child_id
    ).join(
        models.AnganwadiCenter, models.Child.center_id == models.AnganwadiCenter.center_id
    ).filter(
        models.Referral.child_id.in_(child_ids_sq)
    )
    
    results = query.all()
    print(f"Results with JOINS: {len(results)}")
    
    if results:
        ref, fname, lname, cname = results[0]
        print(f"Sample: Ref ID {ref.referral_id}, Child: {fname} {lname}, Center: {cname}")

    # 4. Check for orphans (referrals without centers)
    orphans = db.query(models.Referral).join(models.Child).outerjoin(models.AnganwadiCenter).filter(models.AnganwadiCenter.center_id == None).count()
    print(f"Referrals with children BUT NO centers: {orphans}")

if __name__ == "__main__":
    test_visibility()
