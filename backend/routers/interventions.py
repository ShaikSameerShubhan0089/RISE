"""
Intervention Management Routes
Track intervention programs and outcomes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas
from auth import get_current_user
from rbac import (
    RoleChecker,
    check_child_access
)

router = APIRouter()


@router.post("", response_model=schemas.InterventionResponse, status_code=status.HTTP_201_CREATED)
async def create_intervention(
    intervention_create: schemas.InterventionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RoleChecker(['supervisor', 'district_officer', 'state_admin', 'system_admin']))
):
    """
    Create a new intervention program for a child
    """
    # Check access to child
    if not check_child_access(current_user, intervention_create.child_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this child"
        )
    
    # Create intervention
    new_intervention = models.Intervention(
        **intervention_create.dict(),
        created_by=current_user.user_id,
        sessions_completed=0
    )
    
    db.add(new_intervention)
    db.commit()
    db.refresh(new_intervention)
    
    return new_intervention


@router.put("/{intervention_id}", response_model=schemas.InterventionResponse)
async def update_intervention(
    intervention_id: int,
    intervention_update: schemas.InterventionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RoleChecker(['supervisor', 'district_officer', 'state_admin', 'system_admin']))
):
    """
    Update intervention progress and outcomes
    """
    intervention = db.query(models.Intervention).filter(
        models.Intervention.intervention_id == intervention_id
    ).first()
    
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
    
    # Check access
    if not check_child_access(current_user, intervention.child_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this intervention"
        )
    
    # Update fields
    if intervention_update.sessions_completed is not None:
        intervention.sessions_completed = intervention_update.sessions_completed
        
        # Calculate compliance if total sessions planned
        if intervention.total_sessions_planned:
            intervention.compliance_percentage = (
                intervention_update.sessions_completed / intervention.total_sessions_planned * 100
            )
    
    if intervention_update.compliance_percentage is not None:
        intervention.compliance_percentage = intervention_update.compliance_percentage
    
    if intervention_update.improvement_status:
        intervention.improvement_status = intervention_update.improvement_status
    
    if intervention_update.delay_reduction_months is not None:
        intervention.delay_reduction_months = intervention_update.delay_reduction_months
    
    if intervention_update.outcome_notes:
        intervention.outcome_notes = intervention_update.outcome_notes
    
    if intervention_update.end_date:
        intervention.end_date = intervention_update.end_date
        
        # Calculate actual duration
        if intervention.start_date:
            days = (intervention_update.end_date - intervention.start_date).days
            intervention.actual_duration_weeks = days // 7
    
    db.commit()
    db.refresh(intervention)
    
    return intervention


@router.get("/{intervention_id}", response_model=schemas.InterventionResponse)
async def get_intervention(
    intervention_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get intervention details
    """
    intervention = db.query(models.Intervention).filter(
        models.Intervention.intervention_id == intervention_id
    ).first()
    
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
    
    # Check access
    if not check_child_access(current_user, intervention.child_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this intervention"
        )
    
    return intervention


@router.get("/child/{child_id}", response_model=List[schemas.InterventionResponse])
async def get_child_interventions(
    child_id: int,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all interventions for a child
    """
    # Check access
    if not check_child_access(current_user, child_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this child"
        )
    
    query = db.query(models.Intervention).filter(
        models.Intervention.child_id == child_id
    )
    
    # Filter for active only
    if active_only:
        query = query.filter(models.Intervention.end_date.is_(None))
    
    interventions = query.order_by(models.Intervention.start_date.desc()).all()
    
    return interventions


@router.get("", response_model=List[schemas.InterventionResponse])
async def list_interventions(
    category: str = None,
    improvement_status: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RoleChecker(['supervisor', 'district_officer', 'state_admin', 'system_admin']))
):
    """
    List interventions accessible to current user
    """
    from rbac import filter_children_by_access
    
    # Get accessible children
    accessible_children_query = filter_children_by_access(current_user, db)
    child_ids = [child.child_id for child in accessible_children_query.all()]
    
    # Query interventions
    query = db.query(models.Intervention).filter(
        models.Intervention.child_id.in_(child_ids)
    )
    
    # Apply filters
    if category:
        query = query.filter(models.Intervention.intervention_category == category)
    
    if improvement_status:
        query = query.filter(models.Intervention.improvement_status == improvement_status)
    
    interventions = query.order_by(models.Intervention.start_date.desc()).all()
    
    return interventions
