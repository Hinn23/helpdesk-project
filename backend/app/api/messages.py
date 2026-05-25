from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.database import get_db
from app.auth import get_current_user
from app.models.private_message import PrivateMessage
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.sse import events as sse_events

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/conversations")
def list_conversations(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    subquery = (
        db.query(
            PrivateMessage,
        )
        .filter(
            or_(PrivateMessage.sender_id == current_user.id, PrivateMessage.recipient_id == current_user.id)
        )
        .order_by(PrivateMessage.created_at.desc())
        .all()
    )
    conv_users = {}
    for msg in subquery:
        other_id = msg.recipient_id if msg.sender_id == current_user.id else msg.sender_id
        if other_id not in conv_users:
            conv_users[other_id] = {
                "last_message": msg.text[:100],
                "last_time": msg.created_at.isoformat() if msg.created_at else None,
                "unread": 0,
            }
    unread_counts = (
        db.query(PrivateMessage.recipient_id, PrivateMessage.sender_id)
        .filter(PrivateMessage.recipient_id == current_user.id, PrivateMessage.is_read == 0)
        .all()
    )
    for r in unread_counts:
        if r.sender_id in conv_users:
            conv_users[r.sender_id]["unread"] += 1

    repo = UserRepository(db)
    result = []
    for other_id, data in conv_users.items():
        user = repo.get_by_id(other_id)
        if user:
            result.append({
                "user_id": user.id, "name": user.name, "avatar": user.avatar,
                "last_message": data["last_message"], "last_time": data["last_time"],
                "unread": data["unread"],
            })
    result.sort(key=lambda x: x["last_time"] or "", reverse=True)
    return result


@router.get("/{user_id}")
def get_conversation(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    repo = UserRepository(db)
    if not repo.get_by_id(user_id):
        raise HTTPException(404, "Пользователь не найден")
    messages = (
        db.query(PrivateMessage)
        .filter(
            or_(
                (PrivateMessage.sender_id == current_user.id) & (PrivateMessage.recipient_id == user_id),
                (PrivateMessage.sender_id == user_id) & (PrivateMessage.recipient_id == current_user.id),
            )
        )
        .order_by(PrivateMessage.created_at.asc())
        .all()
    )
    return [
        {
            "id": m.id, "sender_id": m.sender_id, "text": m.text,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "is_read": m.is_read or 0,
        }
        for m in messages
    ]


@router.post("/{user_id}")
def send_message(user_id: int, data: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.id == user_id:
        raise HTTPException(400, "Нельзя отправить сообщение себе")
    repo = UserRepository(db)
    if not repo.get_by_id(user_id):
        raise HTTPException(404, "Пользователь не найден")
    text = (data.get("text") or "").strip()
    if not text:
        raise HTTPException(400, "Сообщение не может быть пустым")
    msg = PrivateMessage(sender_id=current_user.id, recipient_id=user_id, text=text)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    sse_events.broadcast_sync("new_message", {
        "from_user_id": current_user.id,
        "from_user_name": current_user.name,
        "to_user_id": user_id,
        "text": text[:100],
    })
    return {"message": "Сообщение отправлено", "id": msg.id}


@router.post("/read/{user_id}")
def mark_read(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db.query(PrivateMessage).filter(
        PrivateMessage.sender_id == user_id,
        PrivateMessage.recipient_id == current_user.id,
        PrivateMessage.is_read == 0,
    ).update({"is_read": 1})
    db.commit()
    return {"message": "Прочитано"}
