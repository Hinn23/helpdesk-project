from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_optional_user
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/tickets/{ticket_id}/history", tags=["history"])


@router.get("")
def get_history(ticket_id: int, db: Session = Depends(get_db), _=Depends(get_optional_user)):
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.ticket_id == ticket_id)
        .order_by(AuditLog.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": l.id,
            "user_name": l.user_name,
            "action": l.action,
            "field": l.field,
            "old_value": l.old_value,
            "new_value": l.new_value,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]
