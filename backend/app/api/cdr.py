from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.cdr import CDRRead, CDRStats
from app.services import cdr_service

router = APIRouter(prefix="/cdr", tags=["CDR"])


def _user_id_for_user(user: User):
    """Admin tüm çağrıları görsün (None), diğerleri kendi UUID'leri üzerinden."""
    if user.role_name == "admin":
        return None
    return user.id


@router.get("/recent", response_model=list[CDRRead])
def recent_calls(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    uid = _user_id_for_user(current_user)
    return cdr_service.get_recent_calls(db, limit=limit, user_id=uid)


@router.get("/stats", response_model=CDRStats)
def call_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    uid = _user_id_for_user(current_user)
    return cdr_service.get_call_stats(db, user_id=uid)
