"""
Authentication Routes
Login, token generation, and user management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from datetime import timedelta

from database import get_db
import models
import schemas
from auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from rbac import RoleChecker

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
async def login(
    credentials: schemas.UserLogin,
    db: Session = Depends(get_db)
):
    """
    User login endpoint
    
    Returns JWT access token on successful authentication
    """
    # Authenticate user
    user = authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role
        },
        expires_delta=access_token_expires
    )
    
    # Convert user to response model
    user_response = schemas.UserResponse.from_orm(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }


@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(
    current_user: models.User = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return current_user


@router.post("/users", response_model=schemas.UserResponse)
async def create_user(
    user_create: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RoleChecker(['system_admin', 'state_admin', 'district_officer', 'supervisor', 'anganwadi_worker']))
):
    """
    Create new user (system_admin, state_admin, district_officer, supervisor, or anganwadi_worker)
    """
    # Role-based restriction for state_admin
    if current_user.role == 'state_admin':
        if user_create.role not in ['district_officer', 'supervisor', 'anganwadi_worker', 'parent']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="State Admin can only create District Officer, Supervisor, AWC Worker, or Parent roles"
            )
        # Force state_id to be same as state_admin's
        user_create.state_id = current_user.state_id
    
    # Role-based restriction for district_officer
    elif current_user.role == 'district_officer':
        if user_create.role not in ['supervisor', 'anganwadi_worker', 'parent']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="District Officer can only create Supervisor, AWC Worker, or Parent roles"
            )
        # Force state_id and district_id to be same as district_officer's
        user_create.state_id = current_user.state_id
        user_create.district_id = current_user.district_id
    
    # Role-based restriction for supervisor
    elif current_user.role == 'supervisor':
        if user_create.role not in ['anganwadi_worker', 'parent']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Supervisor can only create AWC Worker or Parent roles"
            )
        # Force jurisdiction to be same as supervisor's
        user_create.state_id = current_user.state_id
        user_create.district_id = current_user.district_id
        user_create.mandal_id = current_user.mandal_id

    # Role-based restriction for anganwadi_worker
    elif current_user.role == 'anganwadi_worker':
        if user_create.role != 'parent':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="AWC Worker can only create Parent accounts"
            )
        # Force jurisdiction to be same as anganwadi_worker's
        user_create.state_id = current_user.state_id
        user_create.district_id = current_user.district_id
        user_create.mandal_id = current_user.mandal_id
        user_create.center_id = current_user.center_id
    # Check if email already exists
    existing_user = db.query(models.User).filter(
        models.User.email == user_create.email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    new_user = models.User(
        full_name=user_create.full_name,
        email=user_create.email,
        password_hash=get_password_hash(user_create.password),
        role=user_create.role,
        state_id=user_create.state_id,
        district_id=user_create.district_id,
        mandal_id=user_create.mandal_id,
        center_id=user_create.center_id,
        status="Active",
        email_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.put("/users/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RoleChecker(['system_admin', 'state_admin', 'district_officer', 'supervisor', 'anganwadi_worker']))
):
    """
    Update user (system_admin, state_admin, district_officer, supervisor, or anganwadi_worker)
    """
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Jurisdiction check for state_admin
    if current_user.role == 'state_admin':
        if user.state_id != current_user.state_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage users within your state"
            )
        if user.role not in ['district_officer', 'supervisor', 'anganwadi_worker', 'parent']:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot update users with higher privileges"
            )
        if user_update.role and user_update.role not in ['district_officer', 'supervisor', 'anganwadi_worker', 'parent']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="State Admin can only assign District Officer, Supervisor, AWC Worker, or Parent roles"
            )
        # Ensure state_id remains locked
        user_update.state_id = current_user.state_id
    
    # Jurisdiction check for district_officer
    elif current_user.role == 'district_officer':
        if user.district_id != current_user.district_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage users within your district"
            )
        if user.role not in ['supervisor', 'anganwadi_worker', 'parent']:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot update users with higher privileges"
            )
        if user_update.role and user_update.role not in ['supervisor', 'anganwadi_worker', 'parent']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="District Officer can only assign Supervisor, AWC Worker, or Parent roles"
            )
        # Ensure state_id and district_id remain locked
        user_update.state_id = current_user.state_id
        user_update.district_id = current_user.district_id

    # Jurisdiction check for supervisor
    elif current_user.role == 'supervisor':
        if user.mandal_id != current_user.mandal_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage users within your mandal"
            )
        if user.role not in ['anganwadi_worker', 'parent']:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot update users with higher privileges"
            )
        if user_update.role and user_update.role not in ['anganwadi_worker', 'parent']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Supervisor can only assign AWC Worker or Parent roles"
            )
        # Ensure hierarchy remains locked
        user_update.state_id = current_user.state_id
        user_update.district_id = current_user.district_id
        user_update.mandal_id = current_user.mandal_id

    # Jurisdiction check for anganwadi_worker
    elif current_user.role == 'anganwadi_worker':
        if user.center_id != current_user.center_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage users within your center"
            )
        if user.role != 'parent':
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update parent accounts"
            )
        if user_update.role and user_update.role != 'parent':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="AWC Worker can only assign the Parent role"
            )
        # Ensure hierarchy remains locked
        user_update.state_id = current_user.state_id
        user_update.district_id = current_user.district_id
        user_update.mandal_id = current_user.mandal_id
        user_update.center_id = current_user.center_id
    
    # Update fields only if provided
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.role is not None:
        user.role = user_update.role
    if user_update.state_id is not None:
        user.state_id = user_update.state_id
    if user_update.district_id is not None:
        user.district_id = user_update.district_id
    if user_update.mandal_id is not None:
        user.mandal_id = user_update.mandal_id
    if user_update.center_id is not None:
        user.center_id = user_update.center_id
    if user_update.email is not None:
        user.email = user_update.email
    
    # Update password if provided
    if user_update.password:
        user.password_hash = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/users", response_model=list[schemas.UserResponse])
async def list_users(
    role: str = None,
    status: str = None,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RoleChecker(['system_admin', 'state_admin', 'district_officer', 'supervisor', 'anganwadi_worker']))
):
    """
    List users (filtered by role/status/search if specified)
    """
    query = db.query(models.User).options(
        joinedload(models.User.district),
        joinedload(models.User.mandal),
        joinedload(models.User.center)
    )
    
    if role:
        query = query.filter(models.User.role == role)
    if status:
        query = query.filter(models.User.status == status)
    if search:
        query = query.filter(
            (models.User.full_name.ilike(f"%{search}%")) |
            (models.User.email.ilike(f"%{search}%"))
        )
    
    # Scope by user's jurisdiction
    if current_user.role == 'state_admin':
        query = query.filter(models.User.state_id == current_user.state_id)
    elif current_user.role == 'district_officer':
        query = query.filter(models.User.district_id == current_user.district_id)
    elif current_user.role == 'supervisor':
        query = query.filter(models.User.mandal_id == current_user.mandal_id)
    elif current_user.role == 'anganwadi_worker':
        parent_ids_sq = db.query(models.ParentChildMapping.user_id).join(
            models.Child, models.ParentChildMapping.child_id == models.Child.child_id
        ).filter(models.Child.center_id == current_user.center_id).subquery()
        query = query.filter(or_(
            models.User.center_id == current_user.center_id,
            models.User.user_id.in_(parent_ids_sq)
        ))
    
    users = query.order_by(models.User.full_name).all()
    
    # Populate readable names for the Pydantic schema
    for u in users:
        u.district_name = u.district.district_name if u.district else None
        u.mandal_name = u.mandal.mandal_name if u.mandal else None
        u.center_name = u.center.center_name if u.center else None
        
    return users


@router.patch("/users/{user_id}/status", response_model=schemas.UserResponse)
async def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RoleChecker(['system_admin', 'state_admin', 'district_officer', 'supervisor', 'anganwadi_worker']))
):
    """Toggle user status between Active and Revoked (system_admin, state_admin, district_officer, supervisor, or anganwadi_worker)"""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.role == 'state_admin':
        if user.state_id != current_user.state_id:
            raise HTTPException(status_code=403, detail="You can only manage users within your state")
        if user.role not in ['district_officer', 'supervisor', 'anganwadi_worker', 'parent']:
            raise HTTPException(status_code=403, detail="You cannot revoke users with higher privileges")

    if current_user.role == 'district_officer':
        if user.district_id != current_user.district_id:
            raise HTTPException(status_code=403, detail="You can only manage users within your district")
        if user.role not in ['supervisor', 'anganwadi_worker', 'parent']:
            raise HTTPException(status_code=403, detail="You cannot revoke users with higher privileges")

    if current_user.role == 'supervisor':
        if user.mandal_id != current_user.mandal_id:
            raise HTTPException(status_code=403, detail="You can only manage users within your mandal")
        if user.role not in ['anganwadi_worker', 'parent']:
            raise HTTPException(status_code=403, detail="You cannot revoke users with higher privileges")

    if current_user.role == 'anganwadi_worker':
        if user.center_id != current_user.center_id:
            raise HTTPException(status_code=403, detail="You can only manage users within your center")
        if user.role != 'parent':
            raise HTTPException(status_code=403, detail="You can only revoke parent accounts")

    if user.user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot revoke your own account")
    
    user.status = "Revoked" if user.status == "Active" else "Active"
    db.commit()
    db.refresh(user)
    return user


class PasswordReset(BaseModel):
    new_password: str

@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    body: PasswordReset,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RoleChecker(['system_admin', 'state_admin', 'district_officer', 'supervisor', 'anganwadi_worker']))
):
    """Reset a user's password (system_admin, state_admin, district_officer, supervisor, or anganwadi_worker)"""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.role == 'state_admin':
        if user.state_id != current_user.state_id:
            raise HTTPException(status_code=403, detail="You can only manage users within your state")
        if user.role not in ['district_officer', 'supervisor', 'anganwadi_worker', 'parent']:
            raise HTTPException(status_code=403, detail="You cannot manage users with higher privileges")

    if current_user.role == 'district_officer':
        if user.district_id != current_user.district_id:
            raise HTTPException(status_code=403, detail="You can only manage users within your district")
        if user.role not in ['supervisor', 'anganwadi_worker', 'parent']:
            raise HTTPException(status_code=403, detail="You cannot manage users with higher privileges")

    if current_user.role == 'supervisor':
        if user.mandal_id != current_user.mandal_id:
            raise HTTPException(status_code=403, detail="You can only manage users within your mandal")
        if user.role not in ['anganwadi_worker', 'parent']:
            raise HTTPException(status_code=403, detail="You cannot manage users with higher privileges")

    if current_user.role == 'anganwadi_worker':
        if user.center_id != current_user.center_id:
            raise HTTPException(status_code=403, detail="You can only manage users within your center")
        if user.role != 'parent':
            raise HTTPException(status_code=403, detail="You can only manage parent accounts")
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    user.password_hash = get_password_hash(body.new_password)
    db.commit()
    return {"message": f"Password reset successfully for {user.full_name}"}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RoleChecker(['system_admin', 'state_admin', 'district_officer', 'supervisor', 'anganwadi_worker']))
):
    """Delete a user account (with jurisdictional safety)"""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    # Jurisdictional checks
    if current_user.role == 'state_admin':
        if user.state_id != current_user.state_id:
            raise HTTPException(status_code=403, detail="You can only manage users within your state")
    elif current_user.role == 'district_officer':
        if user.district_id != current_user.district_id:
            raise HTTPException(status_code=403, detail="You can only manage users within your district")
    elif current_user.role == 'supervisor':
        if user.mandal_id != current_user.mandal_id:
            raise HTTPException(status_code=403, detail="You can only manage users within your mandal")
    elif current_user.role == 'anganwadi_worker':
        if user.center_id != current_user.center_id:
            raise HTTPException(status_code=403, detail="You can only manage users within your center")
        if user.role != 'parent':
            raise HTTPException(status_code=403, detail="AWC Workers can only delete parent accounts")

    try:
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete user because they have linked records (assessments, children, etc.). Try revoking access instead."
        )
