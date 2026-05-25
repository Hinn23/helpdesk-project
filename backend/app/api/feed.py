from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_optional_user
from app.models.ticket import Ticket
from app.models.comment import Comment
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("")
def get_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_user),
):
    from app.models.user import User
    users_map = {u.id: {"name": u.name, "avatar": u.avatar} for u in db.query(User).all()}

    is_admin = current_user and current_user.role in ("admin", "manager")
    mod_ticket_ids = set()
    if not is_admin:
        mod_ticket_ids = {t.id for t in db.query(Ticket.id).filter(Ticket.status == "on_moderation").all()}

    tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).limit(limit * 2).all()
    comments = db.query(Comment).order_by(Comment.created_at.desc()).limit(limit * 2).all()
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit * 2).all()

    events = []

    for t in tickets:
        if t.id in mod_ticket_ids:
            continue
        author = users_map.get(t.author_id or 0, {})
        events.append({
            "type": "ticket_created",
            "id": f"t{t.id}",
            "timestamp": t.created_at.isoformat() if t.created_at else None,
            "user_name": author.get("name", "Неизвестно"),
            "user_avatar": author.get("avatar"),
            "user_id": t.author_id,
            "ticket_id": t.id,
            "ticket_title": t.title,
            "ticket_status": t.status,
            "ticket_priority": t.priority,
        })

    for c in comments:
        if c.ticket_id in mod_ticket_ids:
            continue
        events.append({
            "type": "comment",
            "id": f"c{c.id}",
            "timestamp": c.created_at.isoformat() if c.created_at else None,
            "user_name": c.author_name,
            "user_id": c.author_id,
            "ticket_id": c.ticket_id,
            "text": c.text[:200],
        })

    for log in logs:
        if log.ticket_id in mod_ticket_ids:
            continue
        user = users_map.get(log.user_id or 0, {})
        events.append({
            "type": "update",
            "id": f"l{log.id}",
            "timestamp": log.created_at.isoformat() if log.created_at else None,
            "user_name": log.user_name or user.get("name", "system"),
            "user_id": log.user_id,
            "ticket_id": log.ticket_id,
            "field": log.field,
            "old_value": log.old_value,
            "new_value": log.new_value,
            "action": log.action,
        })

    events.sort(key=lambda e: e.get("timestamp") or "", reverse=True)
    return events[skip:skip + limit]
