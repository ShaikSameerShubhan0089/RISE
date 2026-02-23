"""
Referral Management Routes
Create and track specialist referrals
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from database import get_db
import models
import schemas
from auth import get_current_user
from rbac import (
    RoleChecker,
    check_child_access,
    check_assessment_access,
    can_manage_referrals,
    filter_children_by_access
)

router = APIRouter()


@router.post("", response_model=schemas.ReferralResponse, status_code=status.HTTP_201_CREATED)
async def create_referral(
    referral_create: schemas.ReferralCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new referral
    Can be auto-generated based on high risk or manually created
    """
    # Check permissions
    if not can_manage_referrals(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create referrals"
        )
    
    # Check access to child
    if not check_child_access(current_user, referral_create.child_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this child"
        )
    
    # Check access to assessment
    if not check_assessment_access(current_user, referral_create.assessment_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this assessment"
        )
    
    # Get latest prediction for risk level
    prediction = db.query(models.ModelPrediction).filter(
        models.ModelPrediction.assessment_id == referral_create.assessment_id
    ).order_by(models.ModelPrediction.prediction_timestamp.desc()).first()
    
    risk_level = prediction.risk_tier if prediction else "Unknown"
    
    # Create referral
    new_referral = models.Referral(
        assessment_id=referral_create.assessment_id,
        child_id=referral_create.child_id,
        risk_level_at_referral=risk_level,
        referral_reason=referral_create.referral_reason,
        referred_to=referral_create.referred_to,
        specialist_type=referral_create.specialist_type,
        facility_name=referral_create.facility_name,
        facility_contact=referral_create.facility_contact,
        expected_completion_date=referral_create.expected_completion_date,
        referral_generated=True,
        auto_generated=False,  # Manual creation
        status="Pending",
        created_by=current_user.user_id
    )
    
    db.add(new_referral)
    db.commit()
    db.refresh(new_referral)
    
    return new_referral


@router.put("/{referral_id}", response_model=schemas.ReferralResponse)
async def update_referral(
    referral_id: int,
    referral_update: schemas.ReferralUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update referral status and outcome
    """
    if not can_manage_referrals(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update referrals"
        )
    
    referral = db.query(models.Referral).filter(
        models.Referral.referral_id == referral_id
    ).first()
    
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    
    # Check access to child
    if not check_child_access(current_user, referral.child_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this referral"
        )
    
    # Update fields
    if referral_update.status:
        referral.status = referral_update.status
        if referral_update.status == "Completed":
            referral.referral_completed = True
    
    if referral_update.completion_date:
        referral.completion_date = referral_update.completion_date
    
    if referral_update.outcome_summary:
        referral.outcome_summary = referral_update.outcome_summary
    
    if referral_update.diagnosis_received:
        referral.diagnosis_received = referral_update.diagnosis_received
    
    referral.updated_by = current_user.user_id
    
    db.commit()
    db.refresh(referral)
    
    return referral


@router.get("/{referral_id}", response_model=schemas.ReferralResponse)
async def get_referral(
    referral_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get referral details
    """
    # Outerjoin with Child and AnganwadiCenter to be robust
    res = db.query(models.Referral, models.Child.first_name, models.Child.last_name, models.AnganwadiCenter.center_name).outerjoin(
        models.Child, models.Referral.child_id == models.Child.child_id
    ).outerjoin(
        models.AnganwadiCenter, models.Child.center_id == models.AnganwadiCenter.center_id
    ).filter(models.Referral.referral_id == referral_id).first()
    
    if not res:
        raise HTTPException(status_code=404, detail="Referral not found")
    
    referral, fname, lname, cname = res
    
    # Check access
    if not check_child_access(current_user, referral.child_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this referral"
        )
    
    # Enrich response
    referral.child_name = f"{fname} {lname}" if lname else fname
    referral.center_name = cname
    
    return referral


@router.get("/child/{child_id}", response_model=List[schemas.ReferralResponse])
async def get_child_referrals(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all referrals for a child
    """
    # Check access
    if not check_child_access(current_user, child_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this child"
        )
    
    # Outerjoin with Child and AnganwadiCenter to be robust
    query = db.query(models.Referral, models.Child.first_name, models.Child.last_name, models.AnganwadiCenter.center_name).outerjoin(
        models.Child, models.Referral.child_id == models.Child.child_id
    ).outerjoin(
        models.AnganwadiCenter, models.Child.center_id == models.AnganwadiCenter.center_id
    ).filter(models.Referral.child_id == child_id).order_by(models.Referral.referral_date.desc())
    
    results = query.all()
    referrals = []
    for r, fname, lname, cname in results:
        r.child_name = f"{fname} {lname}" if lname else fname
        r.center_name = cname
        referrals.append(r)
    
    return referrals


@router.get("", response_model=List[schemas.ReferralResponse])
async def list_referrals(
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    List referrals accessible to current user
    """
    from sqlalchemy import or_

    # Base query joined with Child and Center
    query = db.query(
        models.Referral, 
        models.Child.first_name, 
        models.Child.last_name, 
        models.AnganwadiCenter.center_name
    ).join(
        models.Child, models.Referral.child_id == models.Child.child_id
    ).join(
        models.AnganwadiCenter, models.Child.center_id == models.AnganwadiCenter.center_id
    )
    
    # Apply the same RBAC filter logic used for the Children tab
    # Since we've already joined Child and AnganwadiCenter, this is very efficient
    query = filter_children_by_access(current_user, db, query=query)
    
    # Apply status filter
    if status_filter:
        query = query.filter(models.Referral.status == status_filter)
    
    # Add a safety limit for performance
    results = query.order_by(models.Referral.referral_date.desc()).limit(200).all()
    
    referrals = []
    for r, fname, lname, cname in results:
        r.child_name = f"{fname} {lname}" if lname else fname
        r.center_name = cname
        referrals.append(r)
    
    return referrals
