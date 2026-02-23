"""
Assessment Management Routes
Submit and retrieve developmental assessments
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
    check_child_access,
    can_create_assessment
)

router = APIRouter()


@router.post("", response_model=schemas.AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment_create: schemas.AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RoleChecker(['anganwadi_worker', 'supervisor', 'district_officer', 'state_admin', 'system_admin']))
):
    """
    Submit a new developmental assessment
    Automatically triggers risk prediction
    """
    # Check if can create assessment for this child
    if not can_create_assessment(current_user, assessment_create.child_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot create assessments for this child"
        )
    
    # Check if child exists
    child = db.query(models.Child).filter(
        models.Child.child_id == assessment_create.child_id
    ).first()
    
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    
    # Check if assessment cycle already exists
    existing = db.query(models.Assessment).filter(
        models.Assessment.child_id == assessment_create.child_id,
        models.Assessment.assessment_cycle == assessment_create.assessment_cycle
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Assessment cycle {assessment_create.assessment_cycle} already exists for this child"
        )
    
    # Create assessment
    new_assessment = models.Assessment(
        **assessment_create.dict(),
        assessed_by=current_user.user_id
    )
    
    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)
    
    return new_assessment


@router.get("/{assessment_id}", response_model=schemas.AssessmentResponse)
async def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get assessment details
    """
    from rbac import check_assessment_access
    
    # Check access
    if not check_assessment_access(current_user, assessment_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this assessment"
        )
    
    assessment = db.query(models.Assessment).filter(
        models.Assessment.assessment_id == assessment_id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return assessment


@router.get("", response_model=List[schemas.AssessmentResponse])
async def list_recent_assessments(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RoleChecker(['anganwadi_worker', 'supervisor', 'district_officer', 'state_admin', 'system_admin']))
):
    """
    List recent assessments accessible to current user
    """
    from rbac import filter_children_by_access
    
    # Get accessible children IDs
    accessible_children_query = filter_children_by_access(current_user, db)
    child_ids = [child.child_id for child in accessible_children_query.all()]
    
    # Get recent assessments for these children
    assessments = db.query(models.Assessment).filter(
        models.Assessment.child_id.in_(child_ids)
    ).order_by(
        models.Assessment.assessment_date.desc()
    ).limit(limit).all()
    
    return assessments
