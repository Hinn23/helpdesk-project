from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.user_friend import UserFriend
from app.repositories.user_repo import UserRepository
from app.sse import events as sse_events

router = APIRouter(prefix="/friends", tags=["friends"])


@router.get("")
def list_friends(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rows = (
        db.query(UserFriend)
        .filter(
            or_(
                UserFriend.user_id == current_user.id,
                UserFriend.friend_id == current_user.id,
            ),
            UserFriend.status == "accepted",
        )
        .order_by(UserFriend.created_at.desc())
        .all()
    )
    repo = UserRepository(db)
    friends = []
    for r in rows:
        friend_id = r.friend_id if r.user_id == current_user.id else r.user_id
        friend = repo.get_by_id(friend_id)
        if friend:
            friends.append({
                "id": friend.id, "name": friend.name, "avatar": friend.avatar,
                "role": friend.role, "status": friend.status or "active",
            })
    return friends


@router.get("/requests")
def list_requests(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rows = (
        db.query(UserFriend)
        .filter(UserFriend.friend_id == current_user.id, UserFriend.status == "pending")
        .order_by(UserFriend.created_at.desc())
        .all()
    )
    repo = UserRepository(db)
    requests = []
    for r in rows:
        sender = repo.get_by_id(r.user_id)
        if sender:
            requests.append({
                "id": r.id,
                "user_id": sender.id, "name": sender.name, "avatar": sender.avatar,
                "role": sender.role, "created_at": r.created_at.isoformat() if r.created_at else None,
            })
    return requests


@router.post("/{user_id}")
def send_request(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.id == user_id:
        raise HTTPException(400, "Нельзя добавить себя в друзья")
    repo = UserRepository(db)
    if not repo.get_by_id(user_id):
        raise HTTPException(404, "Пользователь не найден")
    existing = db.query(UserFriend).filter(
        or_(
            (UserFriend.user_id == current_user.id) & (UserFriend.friend_id == user_id),
            (UserFriend.user_id == user_id) & (UserFriend.friend_id == current_user.id),
        )
    ).first()
    if existing:
        if existing.status == "pending":
            return {"message": "Заявка уже отправлена"}
        if existing.status == "accepted":
            return {"message": "Уже в друзьях"}
        if existing.status == "blocked":
            raise HTTPException(403, "Пользователь заблокирован")
    db.add(UserFriend(user_id=current_user.id, friend_id=user_id, status="pending"))
    db.commit()
    # SSE notification
    sse_events.broadcast_sync("friend_request", {
        "from_user_id": current_user.id,
        "from_user_name": current_user.name,
        "to_user_id": user_id,
    })
    return {"message": "Заявка в друзья отправлена"}


@router.post("/{user_id}/accept")
def accept_request(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    req = db.query(UserFriend).filter(
        UserFriend.user_id == user_id,
        UserFriend.friend_id == current_user.id,
        UserFriend.status == "pending",
    ).first()
    if not req:
        raise HTTPException(404, "Заявка не найдена")
    req.status = "accepted"
    db.commit()
    sse_events.broadcast_sync("friend_accepted", {
        "by_user_id": current_user.id,
        "by_user_name": current_user.name,
        "from_user_id": user_id,
    })
    return {"message": "Заявка принята"}


@router.post("/{user_id}/reject")
def reject_request(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    req = db.query(UserFriend).filter(
        UserFriend.user_id == user_id,
        UserFriend.friend_id == current_user.id,
        UserFriend.status == "pending",
    ).first()
    if not req:
        raise HTTPException(404, "Заявка не найдена")
    db.delete(req)
    db.commit()
    return {"message": "Заявка отклонена"}


@router.post("/{user_id}/unblock")
def unblock_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    existing = db.query(UserFriend).filter(
        UserFriend.user_id == current_user.id,
        UserFriend.friend_id == user_id,
        UserFriend.status == "blocked",
    ).first()
    if not existing:
        raise HTTPException(404, "Не в блоке")
    db.delete(existing)
    db.commit()
    return {"message": "Пользователь разблокирован"}


@router.delete("/{user_id}")
def remove_friend(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    existing = db.query(UserFriend).filter(
        or_(
            (UserFriend.user_id == current_user.id) & (UserFriend.friend_id == user_id),
            (UserFriend.user_id == user_id) & (UserFriend.friend_id == current_user.id),
        ),
        UserFriend.status == "accepted",
    ).first()
    if not existing:
        raise HTTPException(404, "Не в друзьях")
    db.delete(existing)
    db.commit()
    return {"message": "Друг удалён"}


_ROLE_HIERARCHY = {"user": 0, "moderator": 1, "junior_admin": 2, "admin": 3}

@router.post("/{user_id}/block")
def block_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.id == user_id:
        raise HTTPException(400, "Нельзя заблокировать себя")
    repo = UserRepository(db)
    target = repo.get_by_id(user_id)
    if not target:
        raise HTTPException(404, "Пользователь не найден")
    if _ROLE_HIERARCHY.get(target.role, 0) > _ROLE_HIERARCHY.get(current_user.role, 0):
        raise HTTPException(403, "Нельзя заблокировать пользователя с более высокой ролью")
    existing = db.query(UserFriend).filter(
        or_(
            (UserFriend.user_id == current_user.id) & (UserFriend.friend_id == user_id),
            (UserFriend.user_id == user_id) & (UserFriend.friend_id == current_user.id),
        )
    ).first()
    if existing:
        existing.status = "blocked"
    else:
        db.add(UserFriend(user_id=current_user.id, friend_id=user_id, status="blocked"))
    db.commit()
    return {"message": "Пользователь заблокирован"}
