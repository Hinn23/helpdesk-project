from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.user_warning import UserWarning
from app.models.audit_log import AuditLog
from app.repositories.user_repo import UserRepository
from app.sse import events as sse_events

router = APIRouter(prefix="/admin/users", tags=["admin"])


def _staff_required(current_user):
    if current_user.role not in ("admin", "junior_admin", "moderator"):
        raise HTTPException(403, "Недостаточно прав")
    return current_user

def _senior_required(current_user):
    if current_user.role not in ("admin", "junior_admin"):
        raise HTTPException(403, "Только младший админ и выше")
    return current_user

def _admin_required(current_user):
    if current_user.role != "admin":
        raise HTTPException(403, "Только главный админ")
    return current_user


@router.get("/")
def list_all_users(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _staff_required(current_user)
    users = db.query(User).all()
    return [
        {
            "id": u.id, "name": u.name, "email": u.email, "role": u.role,
            "status": u.status or "active", "avatar": u.avatar,
        }
        for u in users
    ]


@router.put("/{user_id}/role")
def set_role(user_id: int, data: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _admin_required(current_user)
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    new_role = data.get("role", "")
    allowed = {"user", "admin", "junior_admin", "moderator"}
    if new_role not in allowed:
        raise HTTPException(400, f"Недопустимая роль: {new_role}")
    user.role = new_role
    db.commit()
    return {"message": f"Роль изменена на {new_role}"}


@router.put("/{user_id}/status")
def set_status(user_id: int, data: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _senior_required(current_user)
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    new_status = data.get("status", "")
    if new_status not in ("active", "warned", "banned"):
        raise HTTPException(400, "Статус: active, warned, banned")
    user.status = new_status
    db.commit()
    action_text = {"banned": "заблокирован", "active": "разблокирован", "warned": "получил предупреждение"}.get(new_status, "изменён")
    sse_events.broadcast_sync("user_status", {"user_id": user_id, "user_name": user.name, "admin_name": current_user.name, "action": action_text})
    return {"message": f"Статус изменён на {new_status}"}


@router.post("/{user_id}/warn")
def warn_user(user_id: int, data: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _senior_required(current_user)
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    reason = data.get("reason", "Нарушение правил")
    warning = UserWarning(user_id=user_id, admin_id=current_user.id, reason=reason)
    db.add(warning)
    user.status = "warned"
    db.commit()
    sse_events.broadcast_sync("user_warning", {"user_id": user_id, "user_name": user.name, "admin_name": current_user.name, "reason": reason})
    return {"message": "Предупреждение выдано"}


@router.get("/{user_id}/warnings")
def list_warnings(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _staff_required(current_user)
    warnings = db.query(UserWarning).filter(UserWarning.user_id == user_id).order_by(UserWarning.created_at.desc()).all()
    return [
        {
            "id": w.id, "reason": w.reason, "admin_id": w.admin_id,
            "created_at": w.created_at.isoformat() if w.created_at else None,
        }
        for w in warnings
    ]


@router.get("/audit")
def get_audit_log(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    _staff_required(current_user)
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    return [
        {
            "id": l.id, "user_name": l.user_name, "action": l.action,
            "field": l.field, "old_value": l.old_value, "new_value": l.new_value,
            "ticket_id": l.ticket_id, "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]
