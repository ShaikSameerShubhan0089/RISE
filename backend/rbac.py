"""
Role-Based Access Control (RBAC)
Implements permission checks for different user roles
"""

from typing import List, Callable
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from functools import wraps

from auth import get_current_user
from database import get_db
import models


# Role hierarchy and permissions
ROLE_HIERARCHY = {
    'system_admin': 5,        # Full access
    'state_admin': 4,         # State-level access
    'district_officer': 3,    # District-level access
    'supervisor': 2,          # Mandal-level access
    'anganwadi_worker': 1,    # Center-level access
    'parent': 0               # Child-specific access only
}


class RoleChecker:
    """
    Dependency class for role-based access control
    
    Usage:
        @app.get("/admin-only")
        async def admin_route(user: models.User = Depends(RoleChecker(['system_admin', 'state_admin']))):
            ...
    """
    
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: models.User = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}"
            )
        return current_user


def require_role(allowed_roles: List[str]):
    """
    Decorator for role-based access control
    
    Usage:
        @require_role(['system_admin'])
        def admin_function(user: models.User):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user: models.User = Depends(get_current_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def check_child_access(
    user: models.User,
    child_id: int,
    db: Session
) -> bool:
    """
    Check if user has access to a specific child
    
    Access rules:
    - system_admin: All children
    - state_admin: All children in their state
    - district_officer: All children in their district
    - supervisor: All children in their mandal
    - anganwadi_worker: Children in their center
    - parent: Only their own children (via parent_child_mapping)
    
    Returns:
        True if user has access, False otherwise
    """
    # Get child
    child = db.query(models.Child).filter(models.Child.child_id == child_id).first()
    
    if not child:
        return False
    
    # System admin has access to all
    if user.role == 'system_admin':
        return True
    
    # Parent - check mapping
    if user.role == 'parent':
        mapping = db.query(models.ParentChildMapping).filter(
            models.ParentChildMapping.user_id == user.user_id,
            models.ParentChildMapping.child_id == child_id
        ).first()
        return mapping is not None
    
    # Get child's center and location hierarchy
    center = db.query(models.AnganwadiCenter).filter(
        models.AnganwadiCenter.center_id == child.center_id
    ).first()
    
    if not center:
        return False
    
    mandal = db.query(models.Mandal).filter(
        models.Mandal.mandal_id == center.mandal_id
    ).first()
    
    if not mandal:
        return False
    
    district = db.query(models.District).filter(
        models.District.district_id == mandal.district_id
    ).first()
    
    if not district:
        return False
    
    # Check based on role
    if user.role == 'anganwadi_worker':
        return child.center_id == user.center_id
    
    elif user.role == 'supervisor':
        return center.mandal_id == user.mandal_id
    
    elif user.role == 'district_officer':
        return mandal.district_id == user.district_id
    
    elif user.role == 'state_admin':
        return district.state_id == user.state_id
    
    return False


def check_assessment_access(
    user: models.User,
    assessment_id: int,
    db: Session
) -> bool:
    """
    Check if user has access to a specific assessment
    Based on access to the child
    """
    assessment = db.query(models.Assessment).filter(
        models.Assessment.assessment_id == assessment_id
    ).first()
    
    if not assessment:
        return False
    
    return check_child_access(user, assessment.child_id, db)


def check_center_access(
    user: models.User,
    center_id: int,
    db: Session
) -> bool:
    """
    Check if user has access to a specific center
    """
    if user.role == 'system_admin':
        return True
    
    center = db.query(models.AnganwadiCenter).filter(
        models.AnganwadiCenter.center_id == center_id
    ).first()
    
    if not center:
        return False
    
    if user.role == 'anganwadi_worker':
        return center_id == user.center_id
    
    elif user.role == 'supervisor':
        return center.mandal_id == user.mandal_id
    
    elif user.role == 'district_officer':
        mandal = db.query(models.Mandal).filter(
            models.Mandal.mandal_id == center.mandal_id
        ).first()
        return mandal and mandal.district_id == user.district_id
    
    elif user.role == 'state_admin':
        mandal = db.query(models.Mandal).filter(
            models.Mandal.mandal_id == center.mandal_id
        ).first()
        if not mandal:
            return False
        
        district = db.query(models.District).filter(
            models.District.district_id == mandal.district_id
        ).first()
        return district and district.state_id == user.state_id
    
    return False


def filter_children_by_access(
    user: models.User,
    db: Session,
    query = None
):
    """
    Get children query filtered by user's access level
    
    Returns:
        SQLAlchemy query for children the user can access
    """
    if query is None:
        query = db.query(models.Child)
    
    if user.role == 'system_admin':
        # Access to all children
        return query
    
    elif user.role == 'parent':
        # Only children mapped to this parent
        child_ids = db.query(models.ParentChildMapping.child_id).filter(
            models.ParentChildMapping.user_id == user.user_id
        ).subquery()
        return query.filter(models.Child.child_id.in_(child_ids))
    
    elif user.role == 'anganwadi_worker':
        # Children in their center
        return query.filter(models.Child.center_id == user.center_id)
    
    elif user.role == 'supervisor':
        # Children in centers in their mandal
        center_ids = db.query(models.AnganwadiCenter.center_id).filter(
            models.AnganwadiCenter.mandal_id == user.mandal_id
        ).subquery()
        return query.filter(models.Child.center_id.in_(center_ids))
    
    elif user.role == 'district_officer':
        # Optimized joined subquery
        center_ids = db.query(models.AnganwadiCenter.center_id).join(
            models.Mandal, models.AnganwadiCenter.mandal_id == models.Mandal.mandal_id
        ).filter(
            models.Mandal.district_id == user.district_id
        ).subquery()
        
        return query.filter(models.Child.center_id.in_(center_ids))
    
    elif user.role == 'state_admin':
        # Optimized joined subquery
        center_ids = db.query(models.AnganwadiCenter.center_id).join(
            models.Mandal, models.AnganwadiCenter.mandal_id == models.Mandal.mandal_id
        ).join(
            models.District, models.Mandal.district_id == models.District.district_id
        ).filter(
            models.District.state_id == user.state_id
        ).subquery()
        
        return query.filter(models.Child.center_id.in_(center_ids))
    
    # Default: no access
    print(f"RBAC WARNING: Role {user.role} has no defined child access logic")
    return query.filter(False)


def can_create_assessment(user: models.User, child_id: int, db: Session) -> bool:
    """
    Check if user can create assessment for a child
    Only anganwadi_worker, supervisor, and admins can create assessments
    """
    if user.role not in ['anganwadi_worker', 'supervisor', 'district_officer', 'state_admin', 'system_admin']:
        return False
    
    return check_child_access(user, child_id, db)


def can_manage_referrals(user: models.User) -> bool:
    """
    Check if user can manage (create/update) referrals
    """
    return user.role in ['district_officer', 'state_admin', 'system_admin', 'supervisor', 'anganwadi_worker']


def can_view_district_summary(user: models.User, district_id: int, db: Session) -> bool:
    """
    Check if user can view district summary
    """
    if user.role in ['system_admin']:
        return True
    
    if user.role == 'state_admin':
        district = db.query(models.District).filter(
            models.District.district_id == district_id
        ).first()
        return district and district.state_id == user.state_id
    
    if user.role == 'district_officer':
        return district_id == user.district_id
    
    return False


# Parent-specific access guard
async def require_parent_or_role(
    allowed_roles: List[str],
    child_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dependency that allows access if user is parent of the child OR has specified role
    
    Usage:
        @app.get("/children/{child_id}")
        async def get_child(
            child_id: int,
            access_check = Depends(lambda: require_parent_or_role(['anganwadi_worker', 'supervisor'], child_id))
        ):
            ...
    """
    # If user has allowed role
    if current_user.role in allowed_roles:
        if not check_child_access(current_user, child_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this child"
            )
        return current_user
    
    # If user is parent
    if current_user.role == 'parent':
        if not check_child_access(current_user, child_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this child"
            )
        return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Access denied. Required roles: {', '.join(allowed_roles + ['parent'])}"
    )
