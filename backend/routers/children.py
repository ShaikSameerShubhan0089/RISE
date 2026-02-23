"""
Children Management Routes
Child registration and information retrieval
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
    filter_children_by_access
)

router = APIRouter()


@router.post("", response_model=schemas.ChildResponse, status_code=status.HTTP_201_CREATED)
async def create_child(
    child_create: schemas.ChildCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RoleChecker(['anganwadi_worker', 'supervisor', 'district_officer', 'state_admin', 'system_admin']))
):
    """
    Register a new child
    """
    # Check center access
    from rbac import check_center_access
    
    if not check_center_access(current_user, child_create.center_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this center"
        )
    
    # Generate unique child code if not provided
    if not child_create.unique_child_code:
        # Get center code
        center = db.query(models.AnganwadiCenter).filter(
            models.AnganwadiCenter.center_id == child_create.center_id
        ).first()
        
        if not center:
            raise HTTPException(status_code=404, detail="Center not found")
        
        # Generate code: CENTER-YEAR-SEQUENCE
        year = date.today().year
        count = db.query(models.Child).filter(
            models.Child.center_id == child_create.center_id
        ).count() + 1
        
        unique_code = f"{center.center_code}-{year}-{count:03d}"
    else:
        unique_code = child_create.unique_child_code
    
    # Check if code exists
    existing = db.query(models.Child).filter(
        models.Child.unique_child_code == unique_code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Child code already exists"
        )
    
    # Create child
    new_child = models.Child(
        unique_child_code=unique_code,
        first_name=child_create.first_name,
        last_name=child_create.last_name,
        dob=child_create.dob,
        gender=child_create.gender,
        center_id=child_create.center_id,
        caregiver_name=child_create.caregiver_name,
        caregiver_relationship=child_create.caregiver_relationship,
        caregiver_education=child_create.caregiver_education,
        caregiver_phone=child_create.caregiver_phone,
        caregiver_email=child_create.caregiver_email,
        caregiver_additional_info=child_create.caregiver_additional_info,
        status="Active"
    )
    
    db.add(new_child)
    db.flush()  # Get child_id
    
    # Handle Parent Account Creation
    if child_create.create_parent_account:
        if not child_create.caregiver_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Caregiver email is required for parent account creation"
            )
        
        if not child_create.parent_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent password is required for parent account creation"
            )
            
        # Check if user already exists
        existing_user = db.query(models.User).filter(
            models.User.email == child_create.caregiver_email
        ).first()
        
        if existing_user:
            parent_user = existing_user
            # Optionally update role if not parent? For now just link
        else:
            from auth import get_password_hash
            
            parent_user = models.User(
                full_name=child_create.caregiver_name or f"Parent of {child_create.first_name}",
                email=child_create.caregiver_email,
                password_hash=get_password_hash(child_create.parent_password),
                role="parent",
                center_id=child_create.center_id,
                status="Active"
            )
            db.add(parent_user)
            db.flush()  # Get user_id
            
        # Create mapping
        mapping = models.ParentChildMapping(
            user_id=parent_user.user_id,
            child_id=new_child.child_id,
            relationship_type=child_create.caregiver_relationship or "Parent",
            is_primary_contact=True
        )
        db.add(mapping)

    db.commit()
    db.refresh(new_child)
    
    return new_child


@router.get("/{child_id}", response_model=schemas.ChildResponse)
async def get_child(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get child details
    Accessible by: staff with access + parents
    """
    # Check access
    if not check_child_access(current_user, child_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this child"
        )
    
    child = db.query(models.Child).filter(models.Child.child_id == child_id).first()
    
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    
    return child


@router.get("", response_model=List[schemas.ChildResponse])
async def list_children(
    search: str = None,
    risk_tier: str = None,
    status_filter: str = None,
    center_id: int = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    List children accessible to current user with search and risk filters
    """
    # Get base query filtered by user's access
    # We query Child and AnganwadiCenter.center_name
    query = db.query(
        models.Child,
        models.AnganwadiCenter.center_name
    ).outerjoin(
        models.AnganwadiCenter, models.Child.center_id == models.AnganwadiCenter.center_id
    )
    
    # Apply access filtering (refactored to return the query object)
    from rbac import filter_children_by_access
    query = filter_children_by_access(current_user, db, query=query)
    
    # Search filter (name or ID)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (models.Child.first_name.ilike(search_fmt)) | 
            (models.Child.last_name.ilike(search_fmt)) | 
            (models.Child.unique_child_code.ilike(search_fmt))
        )
    
    # Risk tier filter
    if risk_tier:
        from sqlalchemy import func
        # Subquery for latest assessment per child
        latest_assessment_sub = db.query(
            models.Assessment.child_id,
            func.max(models.Assessment.assessment_id).label('latest_id')
        ).group_by(models.Assessment.child_id).subquery()
        
        # Join with predictions
        query = query.join(
            latest_assessment_sub, 
            models.Child.child_id == latest_assessment_sub.c.child_id
        ).join(
            models.ModelPrediction,
            models.ModelPrediction.assessment_id == latest_assessment_sub.c.latest_id
        ).filter(models.ModelPrediction.risk_tier == risk_tier)

    # Apply additional filters
    if status_filter:
        query = query.filter(models.Child.status == status_filter)
    
    if center_id:
        query = query.filter(models.Child.center_id == center_id)
    
    # Apply safety limit and sort by enrollment date
    results = query.order_by(models.Child.enrollment_date.desc()).limit(200).all()
    
    # Format response: combine Child object with center_name
    children = []
    for child, center_name in results:
        child_dict = schemas.ChildResponse.from_orm(child)
        child_dict.center_name = center_name
        children.append(child_dict)
        
    return children


@router.put("/{child_id}", response_model=schemas.ChildResponse)
async def update_child(
    child_id: int,
    child_update: schemas.ChildCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RoleChecker(['anganwadi_worker', 'supervisor', 'district_officer', 'state_admin', 'system_admin']))
):
    """
    Update child information
    """
    # Check access
    if not check_child_access(current_user, child_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this child"
        )
    
    child = db.query(models.Child).filter(models.Child.child_id == child_id).first()
    
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    
    # Update fields
    child.first_name = child_update.first_name
    child.last_name = child_update.last_name
    child.dob = child_update.dob
    child.gender = child_update.gender
    child.caregiver_name = child_update.caregiver_name
    child.caregiver_relationship = child_update.caregiver_relationship
    child.caregiver_education = child_update.caregiver_education
    child.caregiver_phone = child_update.caregiver_phone
    child.caregiver_email = child_update.caregiver_email
    child.caregiver_additional_info = child_update.caregiver_additional_info
    
    db.commit()
    db.refresh(child)
    
    return child


@router.get("/{child_id}/assessments", response_model=List[schemas.AssessmentResponse])
async def get_child_assessments(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all assessments for a child (longitudinal view)
    """
    # Check access
    if not check_child_access(current_user, child_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this child"
        )
    
    assessments = db.query(models.Assessment).filter(
        models.Assessment.child_id == child_id
    ).order_by(models.Assessment.assessment_cycle).all()
    
    return assessments
