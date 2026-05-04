from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.cdr import CDR


def _apply_user_filter(query, user_id):
    """Eğer user_id verilmişse sadece o kullanıcının çağrılarını filtrele."""
    if user_id is not None:
        query = query.filter(CDR.user_id == user_id)
    return query


def get_recent_calls(
    db: Session,
    limit: int = 50,
    user_id=None,
    extension: Optional[str] = None,  # kept for signature compat, ignored
) -> list[CDR]:
    query = db.query(CDR)
    query = _apply_user_filter(query, user_id)
    return query.order_by(CDR.baslangic_zamani.desc()).limit(limit).all()


def get_call_stats(db: Session, user_id=None, extension: Optional[str] = None) -> dict:
    base = db.query(CDR)
    base = _apply_user_filter(base, user_id)

    total = base.with_entities(func.count()).scalar() or 0

    def _count(durum_val: str) -> int:
        q = db.query(func.count()).select_from(CDR)
        q = _apply_user_filter(q, user_id)
        return q.filter(CDR.durum == durum_val).scalar() or 0

    answered  = _count("cevaplandi")
    no_answer = _count("cevaplanmadi")
    busy      = _count("mesgul")
    failed    = _count("aktarildi")

    dur_q = db.query(
        func.coalesce(func.sum(CDR.konusma_suresi), 0),
        func.coalesce(func.avg(CDR.konusma_suresi), 0),
    ).select_from(CDR)
    dur_q = _apply_user_filter(dur_q, user_id)
    total_duration, avg_duration = dur_q.first()

    answer_rate = (answered / total * 100) if total > 0 else 0.0

    return {
        "total_calls": total,
        "answered_calls": answered,
        "no_answer_calls": no_answer,
        "busy_calls": busy,
        "failed_calls": failed,
        "total_duration_seconds": int(total_duration),
        "avg_duration_seconds": round(float(avg_duration), 2),
        "answer_rate_percent": round(answer_rate, 2),
    }
