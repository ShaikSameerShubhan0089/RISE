"""
Dashboard Routes
Provides summary stats, table data, and chart data for role-based dashboards.
All endpoints are scoped to the logged-in user's jurisdiction via RBAC.
System Admin can additionally filter by district_id and mandal_id.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, case
from typing import List, Optional

from database import get_db
import models
from auth import get_current_user
from rbac import filter_children_by_access

router = APIRouter()


def _get_center_ids_for_user(
    user: models.User,
    db: Session,
    district_id: Optional[int] = None,
    mandal_id: Optional[int] = None,
    center_id: Optional[int] = None,
) -> List[int]:
    """Return center_ids accessible to the current user with hierarchical filtering support."""
    
    if user.role == "system_admin":
        query = db.query(models.AnganwadiCenter.center_id)
        if center_id:
            query = query.filter(models.AnganwadiCenter.center_id == center_id)
        elif mandal_id:
            query = query.filter(models.AnganwadiCenter.mandal_id == mandal_id)
        elif district_id:
            mandal_ids_sq = db.query(models.Mandal.mandal_id).filter(
                models.Mandal.district_id == district_id
            ).subquery()
            query = query.filter(models.AnganwadiCenter.mandal_id.in_(mandal_ids_sq))
        return [r[0] for r in query.all()]

    if user.role == "state_admin":
        # Base scope: all centers in the state
        query = db.query(models.AnganwadiCenter.center_id).join(
            models.Mandal, models.AnganwadiCenter.mandal_id == models.Mandal.mandal_id
        ).join(
            models.District, models.Mandal.district_id == models.District.district_id
        ).filter(models.District.state_id == user.state_id)

        if center_id:
            query = query.filter(models.AnganwadiCenter.center_id == center_id)
        elif mandal_id:
            query = query.filter(models.AnganwadiCenter.mandal_id == mandal_id)
        elif district_id:
            query = query.filter(models.District.district_id == district_id)
        
        return [r[0] for r in query.all()]

    if user.role == "district_officer":
        # Base scope: all centers in the district
        query = db.query(models.AnganwadiCenter.center_id).join(
            models.Mandal, models.AnganwadiCenter.mandal_id == models.Mandal.mandal_id
        ).filter(models.Mandal.district_id == user.district_id)

        if center_id:
            query = query.filter(models.AnganwadiCenter.center_id == center_id)
        elif mandal_id:
            query = query.filter(models.AnganwadiCenter.mandal_id == mandal_id)
            
        return [r[0] for r in query.all()]

    if user.role == "supervisor":
        # Base scope: all centers in the mandal
        query = db.query(models.AnganwadiCenter.center_id).filter(
            models.AnganwadiCenter.mandal_id == user.mandal_id
        )

        if center_id:
            query = query.filter(models.AnganwadiCenter.center_id == center_id)
            
        return [r[0] for r in query.all()]

    if user.role == "anganwadi_worker":
        return [user.center_id] if user.center_id else []

    if user.role == "parent":
        # Scoped only to their children's centers (though endpoints now filter by child_id too)
        cids_sq = db.query(models.ParentChildMapping.child_id).filter(
            models.ParentChildMapping.user_id == user.user_id
        ).subquery()
        center_ids = db.query(models.Child.center_id).filter(
            models.Child.child_id.in_(cids_sq)
        ).distinct().all()
        return [r[0] for r in center_ids]

    return []


@router.get("/districts-for-state")
async def districts_for_state(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Returns districts within the state_admin's assigned state."""
    if current_user.role not in ("state_admin", "system_admin"):
        raise HTTPException(status_code=403, detail="Not authorized.")
    
    state_id = current_user.state_id
    if not state_id:
        return []
        
    rows = db.query(models.District).filter(
        models.District.state_id == state_id
    ).order_by(models.District.district_name).all()
    
    return [{"district_id": d.district_id, "district_name": d.district_name} for d in rows]



# ── New: Districts list (system_admin only) ──────────────────────────────────

@router.get("/districts")
async def list_districts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Return all districts. Accessible to system_admin only."""
    if current_user.role != "system_admin":
        raise HTTPException(status_code=403, detail="System Admin access required.")
    rows = db.query(models.District).order_by(models.District.district_name).all()
    return [{"district_id": d.district_id, "district_name": d.district_name} for d in rows]


# ── New: Mandals for a district (system_admin only) ──────────────────────────

@router.get("/mandals")
async def list_mandals(
    district_id: int = Query(..., description="District ID to fetch mandals for"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Return all mandals for a given district. Accessible to system_admin, state_admin, district_officer."""
    if current_user.role not in ("system_admin", "state_admin", "district_officer", "supervisor"):
        raise HTTPException(status_code=403, detail="Access denied.")
    rows = db.query(models.Mandal).filter(
        models.Mandal.district_id == district_id
    ).order_by(models.Mandal.mandal_name).all()
    return [{"mandal_id": m.mandal_id, "mandal_name": m.mandal_name} for m in rows]


# ── Mandals for district_officer's own district ───────────────────────────────

@router.get("/mandals-for-district")
async def mandals_for_district(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Returns mandals within the district_officer's assigned district."""
    if current_user.role not in ("district_officer", "system_admin", "state_admin"):
        raise HTTPException(status_code=403, detail="Not authorized.")
    district_id = current_user.district_id
    if not district_id:
        return []
    rows = db.query(models.Mandal).filter(
        models.Mandal.district_id == district_id
    ).order_by(models.Mandal.mandal_name).all()
    return [{"mandal_id": m.mandal_id, "mandal_name": m.mandal_name} for m in rows]


# ── Centers for supervisor's own mandal ───────────────────────────────────────

@router.get("/centers-for-mandal")
async def centers_for_mandal(
    mandal_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Returns AWC centers within a given mandal or the supervisor's assigned mandal."""
    if current_user.role not in ("supervisor", "district_officer", "system_admin", "state_admin"):
        raise HTTPException(status_code=403, detail="Not authorized.")
    
    # Use provided mandal_id, or default to current_user's mandal if they are a supervisor
    target_mandal_id = mandal_id or current_user.mandal_id
    
    if not target_mandal_id:
        return []
    
    # Jurisdictional check for admins
    if current_user.role == "supervisor" and target_mandal_id != current_user.mandal_id:
        raise HTTPException(status_code=403, detail="Supervisors can only view centers in their own mandal.")
        
    rows = db.query(models.AnganwadiCenter).filter(
        models.AnganwadiCenter.mandal_id == target_mandal_id
    ).order_by(models.AnganwadiCenter.center_name).all()
    return [{"center_id": c.center_id, "center_name": c.center_name, "center_code": c.center_code} for c in rows]


# ── Summary ──────────────────────────────────────────────────────────────────

@router.get("/summary")
async def dashboard_summary(
    district_id: Optional[int] = Query(None),
    mandal_id: Optional[int] = Query(None),
    center_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Key counts for the dashboard summary cards."""
    center_ids = _get_center_ids_for_user(current_user, db, district_id, mandal_id, center_id)

    total_children = db.query(models.Child).filter(
        models.Child.center_id.in_(center_ids)
    ).count()
    active_children = db.query(models.Child).filter(
        models.Child.center_id.in_(center_ids),
        models.Child.status == "Active"
    ).count()

    child_ids = [r[0] for r in db.query(models.Child.child_id).filter(
        models.Child.center_id.in_(center_ids)
    ).all()]

    total_interventions = db.query(models.Intervention).filter(
        models.Intervention.child_id.in_(child_ids)
    ).count()
    active_interventions = db.query(models.Intervention).filter(
        models.Intervention.child_id.in_(child_ids),
        models.Intervention.end_date == None
    ).count()

    total_assessments = db.query(models.Assessment).filter(
        models.Assessment.child_id.in_(child_ids)
    ).count()

    # User counts scoped to the selected district/mandal for system_admin
    if current_user.role == "system_admin":
        users_q = db.query(models.User)
        if mandal_id:
            users_q = users_q.filter(models.User.mandal_id == mandal_id)
        elif district_id:
            users_q = users_q.filter(models.User.district_id == district_id)
    elif current_user.role == "state_admin":
        users_q = db.query(models.User).filter(models.User.state_id == current_user.state_id)
    elif current_user.role == "district_officer":
        users_q = db.query(models.User).filter(models.User.district_id == current_user.district_id)
    elif current_user.role == "supervisor":
        users_q = db.query(models.User).filter(models.User.mandal_id == current_user.mandal_id)
    elif current_user.role == "anganwadi_worker":
        # Workers in center + parents of children in center
        parent_ids_sq = db.query(models.ParentChildMapping.user_id).join(
            models.Child, models.ParentChildMapping.child_id == models.Child.child_id
        ).filter(models.Child.center_id == current_user.center_id).subquery()
        users_q = db.query(models.User).filter(or_(
            models.User.center_id == current_user.center_id,
            models.User.user_id.in_(parent_ids_sq)
        ))
    else:
        users_q = db.query(models.User).filter(models.User.mandal_id == current_user.mandal_id)

    workers = users_q.filter(models.User.role == "anganwadi_worker").count()
    supervisors = users_q.filter(models.User.role == "supervisor").count()
    total_centers = len(center_ids)

    return {
        "total_children": total_children,
        "active_children": active_children,
        "total_interventions": total_interventions,
        "active_interventions": active_interventions,
        "total_assessments": total_assessments,
        "workers": workers,
        "supervisors": supervisors,
        "total_centers": total_centers,
    }


# ── Children ─────────────────────────────────────────────────────────────────

@router.get("/children")
async def dashboard_children(
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    lang: str = "en",
    district_id: Optional[int] = Query(None),
    mandal_id: Optional[int] = Query(None),
    center_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Children list with center_name joined, scoped by user role."""
    center_ids = _get_center_ids_for_user(current_user, db, district_id, mandal_id, center_id)

    # ── Parent: filter by their own children only (not whole center) ──────────
    if current_user.role == "parent":
        my_child_ids = [
            r[0] for r in db.query(models.ParentChildMapping.child_id).filter(
                models.ParentChildMapping.user_id == current_user.user_id
            ).all()
        ]
        query = db.query(
            models.Child,
            models.AnganwadiCenter.center_name
        ).join(
            models.AnganwadiCenter,
            models.Child.center_id == models.AnganwadiCenter.center_id
        ).filter(
            models.Child.child_id.in_(my_child_ids)
        )
    else:
        query = db.query(
            models.Child,
            models.AnganwadiCenter.center_name
        ).join(
            models.AnganwadiCenter,
            models.Child.center_id == models.AnganwadiCenter.center_id
        ).filter(
            models.Child.center_id.in_(center_ids)
        )

    if status_filter:
        query = query.filter(models.Child.status == status_filter)

    if search:
        query = query.filter(
            (models.Child.first_name.ilike(f"%{search}%")) |
            (models.Child.last_name.ilike(f"%{search}%")) |
            (models.Child.unique_child_code.ilike(f"%{search}%"))
        )

    rows = query.order_by(
        models.AnganwadiCenter.center_name,
        models.Child.first_name
    ).limit(200).all()

    result = []
    # Instantiate planner for localization
    from ml.intervention_planner import InterventionPlanner
    planner = InterventionPlanner()

    for child, center_name in rows:
        result.append({
            "child_id": child.child_id,
            "unique_child_code": child.unique_child_code,
            "first_name": child.first_name,
            "last_name": child.last_name or "",
            "dob": str(child.dob) if child.dob else None,
            "gender": planner.localize_value(child.gender, lang=lang),
            "center_name": center_name,
            "caregiver_name": child.caregiver_name,
            "caregiver_phone": child.caregiver_phone,
            "status": planner.localize_value(child.status, lang=lang),
        })
    return result


# ── Interventions ─────────────────────────────────────────────────────────────

@router.get("/interventions")
async def dashboard_interventions(
    search: Optional[str] = None,
    category: Optional[str] = None,
    lang: str = "en",
    district_id: Optional[int] = Query(None),
    mandal_id: Optional[int] = Query(None),
    center_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Interventions with child_name and center_name joined."""
    center_ids = _get_center_ids_for_user(current_user, db, district_id, mandal_id, center_id)

    # ── Parent: scope to own children, not whole center ─────────────────────
    if current_user.role == "parent":
        child_ids_q = db.query(models.ParentChildMapping.child_id).filter(
            models.ParentChildMapping.user_id == current_user.user_id
        ).subquery()
    else:
        child_ids_q = db.query(models.Child.child_id).filter(
            models.Child.center_id.in_(center_ids)
        ).subquery()

    query = db.query(
        models.Intervention,
        models.Child.first_name,
        models.Child.last_name,
        models.AnganwadiCenter.center_name
    ).join(
        models.Child, models.Intervention.child_id == models.Child.child_id
    ).join(
        models.AnganwadiCenter, models.Child.center_id == models.AnganwadiCenter.center_id
    ).filter(
        models.Intervention.child_id.in_(child_ids_q)
    )

    if category:
        query = query.filter(models.Intervention.intervention_category == category)

    if search:
        query = query.filter(
            (models.Child.first_name.ilike(f"%{search}%")) |
            (models.Child.last_name.ilike(f"%{search}%")) |
            (models.Intervention.intervention_type.ilike(f"%{search}%"))
        )

    rows = query.order_by(
        models.Intervention.start_date.desc()
    ).limit(200).all()

    # Instantiate planner for localization
    from ml.intervention_planner import InterventionPlanner
    planner = InterventionPlanner()

    result = []
    for intv, first_name, last_name, center_name in rows:
        row = {
            "intervention_id": intv.intervention_id,
            "child_name": f"{first_name} {last_name or ''}".strip(),
            "center_name": center_name,
            "intervention_type": intv.intervention_type,
            "intervention_category": intv.intervention_category,
            "start_date": str(intv.start_date) if intv.start_date else None,
            "end_date": str(intv.end_date) if intv.end_date else None,
            "sessions_completed": intv.sessions_completed,
            "total_sessions_planned": intv.total_sessions_planned,
            "compliance_percentage": intv.compliance_percentage,
            "improvement_status": intv.improvement_status,
            "provider_name": intv.provider_name,
            "provider_contact": intv.provider_contact,
        }
        # Localize dynamic fields
        planner.localize_item(row, ["intervention_category", "improvement_status"], lang=lang)
        result.append(row)
    return result


# ── Users ─────────────────────────────────────────────────────────────────────

@router.get("/users")
async def dashboard_users(
    role_filter: Optional[str] = None,
    district_id: Optional[int] = Query(None),
    mandal_id: Optional[int] = Query(None),
    center_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Users scoped by the current user's jurisdiction."""
    if current_user.role == "system_admin":
        base_q = db.query(models.User, models.AnganwadiCenter.center_name).outerjoin(
            models.AnganwadiCenter, models.User.center_id == models.AnganwadiCenter.center_id
        )

        if mandal_id:
            # Collect centers in this mandal
            mandal_obj = db.query(models.Mandal).filter(models.Mandal.mandal_id == mandal_id).first()
            center_ids_sq = db.query(models.AnganwadiCenter.center_id).filter(
                models.AnganwadiCenter.mandal_id == mandal_id
            ).subquery()
            # Parents whose child is enrolled in a center in this mandal
            parent_ids_sq = db.query(models.ParentChildMapping.user_id).join(
                models.Child, models.ParentChildMapping.child_id == models.Child.child_id
            ).filter(models.Child.center_id.in_(center_ids_sq)).subquery()
            conditions = [
                models.User.center_id.in_(center_ids_sq),                 # AWC workers
                models.User.mandal_id == mandal_id,                       # supervisors
                models.User.district_id == mandal_obj.district_id if mandal_obj else False,   # district officers
                models.User.state_id == mandal_obj.district.state_id if mandal_obj else False, # state admins
                models.User.role == "system_admin",                        # system admins (global)
                models.User.user_id.in_(parent_ids_sq),                   # parents via PCM
            ]
            query = base_q.filter(or_(*conditions))

        elif district_id:
            # Collect all mandal_ids and center_ids for this district
            mandal_ids_sq = db.query(models.Mandal.mandal_id).filter(
                models.Mandal.district_id == district_id
            ).subquery()
            center_ids_sq = db.query(models.AnganwadiCenter.center_id).filter(
                models.AnganwadiCenter.mandal_id.in_(mandal_ids_sq)
            ).subquery()
            district_obj = db.query(models.District).filter(
                models.District.district_id == district_id
            ).first()
            # Parents whose child is enrolled in a center in this district
            parent_ids_sq = db.query(models.ParentChildMapping.user_id).join(
                models.Child, models.ParentChildMapping.child_id == models.Child.child_id
            ).filter(models.Child.center_id.in_(center_ids_sq)).subquery()
            conditions = [
                models.User.center_id.in_(center_ids_sq),                 # AWC workers
                models.User.mandal_id.in_(mandal_ids_sq),                 # supervisors
                models.User.district_id == district_id,                   # district officers
                models.User.state_id == district_obj.state_id if district_obj else False,  # state admins
                models.User.role == "system_admin",                        # system admins (global)
                models.User.user_id.in_(parent_ids_sq),                   # parents via PCM
            ]
            query = base_q.filter(or_(*conditions))

        else:
            # No filter — return all users
            query = base_q

    elif current_user.role == "state_admin":
        query = db.query(models.User, models.AnganwadiCenter.center_name).outerjoin(
            models.AnganwadiCenter, models.User.center_id == models.AnganwadiCenter.center_id
        ).filter(models.User.state_id == current_user.state_id)

    elif current_user.role == "district_officer":
        base_q = db.query(models.User, models.AnganwadiCenter.center_name).outerjoin(
            models.AnganwadiCenter, models.User.center_id == models.AnganwadiCenter.center_id
        )
        if mandal_id:
            # Drill into a specific mandal
            center_ids_in_mandal_sq = db.query(models.AnganwadiCenter.center_id).filter(
                models.AnganwadiCenter.mandal_id == mandal_id
            ).subquery()
            parent_ids_sq = db.query(models.ParentChildMapping.user_id).join(
                models.Child, models.ParentChildMapping.child_id == models.Child.child_id
            ).filter(models.Child.center_id.in_(center_ids_in_mandal_sq)).subquery()
            query = base_q.filter(or_(
                models.User.center_id.in_(center_ids_in_mandal_sq),
                models.User.mandal_id == mandal_id,
                models.User.district_id == current_user.district_id,
                models.User.user_id.in_(parent_ids_sq),
            ))
        else:
            query = base_q.filter(models.User.district_id == current_user.district_id)

    elif current_user.role == "supervisor":
        # Supervisor
        base_q = db.query(models.User, models.AnganwadiCenter.center_name).outerjoin(
            models.AnganwadiCenter, models.User.center_id == models.AnganwadiCenter.center_id
        )
        if center_id:
            # Drill into a specific center
            parent_ids_sq = db.query(models.ParentChildMapping.user_id).join(
                models.Child, models.ParentChildMapping.child_id == models.Child.child_id
            ).filter(models.Child.center_id == center_id).subquery()
            query = base_q.filter(or_(
                models.User.center_id == center_id,
                models.User.user_id.in_(parent_ids_sq),
            ))
        else:
            query = base_q.filter(models.User.mandal_id == current_user.mandal_id)

    elif current_user.role == "anganwadi_worker":
        # Anganwadi Worker: see staff in THEIR center OR parents of children in THEIR center
        parent_ids_sq = db.query(models.ParentChildMapping.user_id).join(
            models.Child, models.ParentChildMapping.child_id == models.Child.child_id
        ).filter(models.Child.center_id == current_user.center_id).subquery()
        
        query = db.query(models.User, models.AnganwadiCenter.center_name).outerjoin(
            models.AnganwadiCenter, models.User.center_id == models.AnganwadiCenter.center_id
        ).filter(or_(
            models.User.center_id == current_user.center_id,
            models.User.user_id.in_(parent_ids_sq)
        ))

    else:
        # Default fallback (e.g. parent sees only themselves)
        query = db.query(models.User, models.AnganwadiCenter.center_name).outerjoin(
            models.AnganwadiCenter, models.User.center_id == models.AnganwadiCenter.center_id
        ).filter(models.User.user_id == current_user.user_id)


    if role_filter:
        query = query.filter(models.User.role == role_filter)

    rows = query.order_by(models.User.role, models.User.full_name).all()
    result = []
    for user, center_name in rows:
        result.append({
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "center_name": center_name or "N/A",
            "status": user.status,
        })
    return result


# ── Charts ────────────────────────────────────────────────────────────────────

@router.get("/charts")
async def dashboard_charts(
    district_id: Optional[int] = Query(None),
    mandal_id: Optional[int] = Query(None),
    center_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Pre-aggregated data for charts."""
    center_ids = _get_center_ids_for_user(current_user, db, district_id, mandal_id, center_id)

    # Children per center
    rows = db.query(
        models.AnganwadiCenter.center_name,
        func.count(models.Child.child_id).label("count")
    ).join(
        models.Child, models.AnganwadiCenter.center_id == models.Child.center_id
    ).filter(
        models.AnganwadiCenter.center_id.in_(center_ids)
    ).group_by(models.AnganwadiCenter.center_name).all()
    children_per_center = [{"center": r[0], "count": r[1]} for r in rows]

    # Intervention categories
    child_ids_q = db.query(models.Child.child_id).filter(
        models.Child.center_id.in_(center_ids)
    ).subquery()
    cat_rows = db.query(
        models.Intervention.intervention_category,
        func.count(models.Intervention.intervention_id).label("count")
    ).filter(
        models.Intervention.child_id.in_(child_ids_q),
        models.Intervention.intervention_category != None
    ).group_by(models.Intervention.intervention_category).all()
    intervention_categories = [{"category": r[0], "count": r[1]} for r in cat_rows]

    # Improvement status
    status_rows = db.query(
        models.Intervention.improvement_status,
        func.count(models.Intervention.intervention_id).label("count")
    ).filter(
        models.Intervention.child_id.in_(child_ids_q),
        models.Intervention.improvement_status != None
    ).group_by(models.Intervention.improvement_status).all()
    improvement_status = [{"status": r[0], "count": r[1]} for r in status_rows]

    # Gender distribution
    gender_rows = db.query(
        models.Child.gender,
        func.count(models.Child.child_id).label("count")
    ).filter(
        models.Child.center_id.in_(center_ids)
    ).group_by(models.Child.gender).all()
    gender_distribution = [{"gender": r[0] or "Unknown", "count": r[1]} for r in gender_rows]

    return {
        "children_per_center": children_per_center,
        "intervention_categories": intervention_categories,
        "improvement_status": improvement_status,
        "gender_distribution": gender_distribution,
    }


# ── Child Growth (longitudinal line chart) ───────────────────────────────────

@router.get("/child-growth/{child_id}")
async def child_growth(
    child_id: int,
    lang: str = "en",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Return all assessment cycles for a child, sorted ascending, for growth line charts.
    Access is verified by RBAC — the calling user must have access to the child's center.
    """
    child = db.query(models.Child).filter(models.Child.child_id == child_id).first()
    if not child:
        raise HTTPException(status_code=404, detail="Child not found.")

    # Verify access
    allowed_centers = _get_center_ids_for_user(current_user, db)
    if child.center_id not in allowed_centers:
        raise HTTPException(status_code=403, detail="Access denied.")

    assessments = (
        db.query(models.Assessment)
        .filter(models.Assessment.child_id == child_id)
        .order_by(models.Assessment.assessment_cycle)
        .all()
    )

    # Get latest prediction for Problem A/B insights
    latest_prediction = None
    if assessments:
        latest_assessment = assessments[-1]
        latest_prediction_obj = db.query(models.ModelPrediction).filter(
            models.ModelPrediction.assessment_id == latest_assessment.assessment_id
        ).order_by(models.ModelPrediction.prediction_timestamp.desc()).first()
        
        if latest_prediction_obj:
            # Join SHAP
            shap_exps = db.query(models.SHAPExplanation).filter(
                models.SHAPExplanation.prediction_id == latest_prediction_obj.prediction_id
            ).all()
            
            # Map for frontend
            latest_prediction = {
                "risk_tier": latest_prediction_obj.risk_tier,
                "probability": latest_prediction_obj.combined_high_probability,
                "escalation_probability": latest_prediction_obj.escalation_probability,
                "predicted_escalation": latest_prediction_obj.predicted_escalation,
                "clinical_action": latest_prediction_obj.clinical_action,
                "top_features": [
                    {
                        "feature_name": s.feature_name,
                        "feature_value": s.feature_value,
                        "shap_value": s.shap_value,
                        "impact_direction": "Increases Risk" if s.shap_value > 0 else "Decreases Risk"
                    } for s in shap_exps
                ]
            }
            
            # Inject AI recommendations if InterventionPlanner available
            try:
                from ml.intervention_planner import InterventionPlanner
                planner = InterventionPlanner()
                latest_prediction["recommendations"] = planner.generate_pathway(latest_prediction["top_features"], lang=lang)
                latest_prediction["clinical_summary"] = planner.get_clinical_summary(
                    latest_prediction["risk_tier"],
                    latest_prediction["probability"],
                    lang=lang
                )
                # Apply deep localization to the entire prediction object (Tiers, SHAP, etc.)
                latest_prediction = planner.localize_prediction(latest_prediction, lang=lang)
            except Exception:
                latest_prediction["recommendations"] = []

    datapoints = []
    for a in assessments:
        datapoints.append({
            "cycle": a.assessment_cycle,
            "assessment_date": str(a.assessment_date) if a.assessment_date else None,
            "age_months": a.age_months,
            # DQ Scores
            "gross_motor_dq": a.gross_motor_dq,
            "fine_motor_dq": a.fine_motor_dq,
            "language_dq": a.language_dq,
            "cognitive_dq": a.cognitive_dq,
            "socio_emotional_dq": a.socio_emotional_dq,
            "composite_dq": a.composite_dq,
            "delayed_domains": a.delayed_domains,
            # Neuro-Behavioral Screening
            "autism_screen_flag": a.autism_screen_flag,
            "adhd_risk": a.adhd_risk,
            "behavior_risk": a.behavior_risk,
            "attention_score": a.attention_score,
            "behavior_score": a.behavior_score,
            # Nutrition / Health Indicators
            "stunting": a.stunting,
            "wasting": a.wasting,
            "anemia": a.anemia,
            "nutrition_score": a.nutrition_score,
            # Environmental
            "stimulation_score": a.stimulation_score,
            "caregiver_engagement_score": a.caregiver_engagement_score,
            "language_exposure_score": a.language_exposure_score,
        })

    # Instantiate planner for localization
    from ml.intervention_planner import InterventionPlanner
    planner = InterventionPlanner()

    return {
        "child_id": child.child_id,
        "child_name": f"{child.first_name} {child.last_name or ''}".strip(),
        "unique_child_code": child.unique_child_code,
        "gender": planner.localize_value(child.gender, lang=lang),
        "centre": child.center.center_name if child.center else "N/A",
        "caregiver": child.caregiver_name,
        "status": planner.localize_value(child.status, lang=lang),
        "datapoints": datapoints,
        "latest_prediction": latest_prediction
    }


# ── Analytics (system_admin only) ─────────────────────────────────────────────

@router.get("/analytics/summary")
async def analytics_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Top-level metric cards for analytics page."""
    _ANALYTICS_ROLES = ("system_admin", "state_admin", "district_officer")
    if current_user.role not in _ANALYTICS_ROLES:
        raise HTTPException(status_code=403, detail="Access denied")

    # Scope user counts by jurisdiction
    uq = db.query(models.User)
    if current_user.role == "state_admin" and current_user.state_id:
        uq = uq.filter(models.User.state_id == current_user.state_id)
    elif current_user.role == "district_officer" and current_user.district_id:
        uq = uq.filter(models.User.district_id == current_user.district_id)

    total_users = uq.count()
    active_users = uq.filter(models.User.status == "Active").count()
    revoked_users = total_users - active_users

    # Scope children / centers by jurisdiction
    center_ids = _get_center_ids_for_user(current_user, db)
    total_children = db.query(models.Child).filter(models.Child.center_id.in_(center_ids)).count()
    active_centers = len(center_ids)

    child_ids_sq = db.query(models.Child.child_id).filter(
        models.Child.center_id.in_(center_ids)
    ).subquery()
    assess_ids_sq = db.query(models.Assessment.assessment_id).filter(
        models.Assessment.child_id.in_(child_ids_sq)
    ).subquery()
    total_predictions = db.query(models.ModelPrediction).filter(
        models.ModelPrediction.assessment_id.in_(assess_ids_sq)
    ).count()

    from datetime import timedelta, datetime as dt
    now = dt.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    new_this_week = uq.filter(models.User.created_at >= week_ago).count()
    new_this_month = uq.filter(models.User.created_at >= month_ago).count()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "revoked_users": revoked_users,
        "total_children": total_children,
        "total_predictions": total_predictions,
        "active_centers": active_centers,
        "new_users_week": new_this_week,
        "new_users_month": new_this_month,
    }


@router.get("/analytics/users")
async def analytics_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """User counts grouped by role, plus active/revoked breakdown per role."""
    _ANALYTICS_ROLES = ("system_admin", "state_admin", "district_officer")
    if current_user.role not in _ANALYTICS_ROLES:
        raise HTTPException(status_code=403, detail="Access denied")

    uq = db.query(models.User)
    if current_user.role == "state_admin" and current_user.state_id:
        uq = uq.filter(models.User.state_id == current_user.state_id)
    elif current_user.role == "district_officer" and current_user.district_id:
        uq = uq.filter(models.User.district_id == current_user.district_id)

    role_counts = uq.with_entities(
        models.User.role,
        func.count(models.User.user_id).label("total"),
        func.sum(case((models.User.status == "Active", 1), else_=0)).label("active"),
        func.sum(case((models.User.status == "Revoked", 1), else_=0)).label("revoked"),
    ).group_by(models.User.role).all()

    return [
        {
            "role": r.role,
            "total": r.total,
            "active": int(r.active or 0),
            "revoked": int(r.revoked or 0),
        }
        for r in role_counts
    ]


@router.get("/analytics/children")
async def analytics_children(
    period: str = "month",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Children enrollment counts over time grouped by day."""
    _ANALYTICS_ROLES = ("system_admin", "state_admin", "district_officer")
    if current_user.role not in _ANALYTICS_ROLES:
        raise HTTPException(status_code=403, detail="Access denied")

    from datetime import timedelta, datetime as dt
    now = dt.utcnow()
    if period == "week":
        since = now - timedelta(days=7)
    elif period == "year":
        since = now - timedelta(days=365)
    else:
        since = now - timedelta(days=30)

    center_ids = _get_center_ids_for_user(current_user, db)
    rows = db.query(
        func.date(models.Child.enrollment_date).label("date"),
        func.count(models.Child.child_id).label("count"),
    ).filter(
        models.Child.center_id.in_(center_ids),
        models.Child.enrollment_date >= since.date()
    ).group_by(
        func.date(models.Child.enrollment_date)
    ).order_by("date").all()

    return [{"date": str(r.date), "count": r.count} for r in rows]


@router.get("/analytics/predictions")
async def analytics_predictions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Predictions grouped by risk tier and model version."""
    _ANALYTICS_ROLES = ("system_admin", "state_admin", "district_officer")
    if current_user.role not in _ANALYTICS_ROLES:
        raise HTTPException(status_code=403, detail="Access denied")

    center_ids = _get_center_ids_for_user(current_user, db)
    child_ids_sq = db.query(models.Child.child_id).filter(
        models.Child.center_id.in_(center_ids)
    ).subquery()
    assess_ids_sq = db.query(models.Assessment.assessment_id).filter(
        models.Assessment.child_id.in_(child_ids_sq)
    ).subquery()

    # Risk tier distribution
    risk_rows = db.query(
        models.ModelPrediction.risk_tier,
        func.count(models.ModelPrediction.prediction_id).label("count"),
    ).filter(
        models.ModelPrediction.assessment_id.in_(assess_ids_sq),
        models.ModelPrediction.risk_tier.isnot(None)
    ).group_by(models.ModelPrediction.risk_tier).all()

    # Model usage (Model A vs B)
    model_rows = db.query(
        models.ModelPrediction.model_version,
        func.count(models.ModelPrediction.prediction_id).label("count"),
    ).filter(
        models.ModelPrediction.assessment_id.in_(assess_ids_sq)
    ).group_by(models.ModelPrediction.model_version).all()

    return {
        "risk_distribution": [{"tier": r.risk_tier, "count": r.count} for r in risk_rows],
        "model_usage": [{"model": r.model_version, "count": r.count} for r in model_rows],
    }
