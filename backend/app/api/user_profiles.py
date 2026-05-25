from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user, get_optional_user
from app.models.user import User
from app.models.ticket import Ticket
from app.models.user_follow import UserFollow
from app.models.user_friend import UserFriend
from app.models.user_warning import UserWarning
from app.models.comment_thanks import CommentThanks
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["users-public"])


@router.get("/{user_id}/profile")
def get_user_profile(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_optional_user)):
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    if current_user and current_user.id != user_id:
        blocked = db.query(UserFriend).filter(
            (UserFriend.user_id == user_id) & (UserFriend.friend_id == current_user.id) & (UserFriend.status == "blocked")
        ).first()
        if blocked:
            raise HTTPException(403, "Пользователь заблокировал вас")

    tickets_count = db.query(Ticket).filter(Ticket.author_id == user_id).count()
    followers_count = db.query(UserFollow).filter(UserFollow.followed_id == user_id).count()
    following_count = db.query(UserFollow).filter(UserFollow.follower_id == user_id).count()

    is_following = False
    if current_user and current_user.id != user_id:
        is_following = db.query(UserFollow).filter(
            UserFollow.follower_id == current_user.id,
            UserFollow.followed_id == user_id,
        ).first() is not None

    tickets = (
        db.query(Ticket)
        .filter(Ticket.author_id == user_id)
        .order_by(Ticket.created_at.desc())
        .limit(20)
        .all()
    )

    warnings_count = db.query(UserWarning).filter(UserWarning.user_id == user_id).count()
    friends_count = db.query(UserFriend).filter(
        (UserFriend.user_id == user_id) | (UserFriend.friend_id == user_id)
    ).count()
    is_friend = False
    has_blocked = False
    if current_user and current_user.id != user_id:
        is_friend = db.query(UserFriend).filter(
            (UserFriend.user_id == current_user.id) & (UserFriend.friend_id == user_id) |
            (UserFriend.user_id == user_id) & (UserFriend.friend_id == current_user.id)
        ).first() is not None
        has_blocked = db.query(UserFriend).filter(
            UserFriend.user_id == current_user.id,
            UserFriend.friend_id == user_id,
            UserFriend.status == "blocked",
        ).first() is not None
    total_thanks = db.query(CommentThanks).join(User, CommentThanks.user_id == User.id).filter(
        User.id == user_id
    ).count()

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "status": user.status or "active",
        "avatar": user.avatar,
        "tickets_count": tickets_count,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
        "warnings_count": warnings_count,
        "friends_count": friends_count,
        "is_friend": is_friend,
        "has_blocked": has_blocked,
        "thanks_count": total_thanks,
        "tickets": [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in tickets
        ],
    }


@router.post("/{user_id}/follow")
def toggle_follow(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.id == user_id:
        raise HTTPException(400, "Нельзя подписаться на самого себя")

    repo = UserRepository(db)
    if not repo.get_by_id(user_id):
        raise HTTPException(404, "Пользователь не найден")

    existing = db.query(UserFollow).filter(
        UserFollow.follower_id == current_user.id,
        UserFollow.followed_id == user_id,
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        return {"following": False, "message": "Отписка оформлена"}
    else:
        db.add(UserFollow(follower_id=current_user.id, followed_id=user_id))
        db.commit()
        return {"following": True, "message": "Подписка оформлена"}


@router.get("/{user_id}/followers")
def list_followers(user_id: int, db: Session = Depends(get_db), _=Depends(get_optional_user)):
    repo = UserRepository(db)
    if not repo.get_by_id(user_id):
        raise HTTPException(404, "Пользователь не найден")
    follows = (
        db.query(UserFollow)
        .filter(UserFollow.followed_id == user_id)
        .order_by(UserFollow.created_at.desc())
        .all()
    )
    users = [repo.get_by_id(f.follower_id) for f in follows if repo.get_by_id(f.follower_id)]
    return [
        {"id": u.id, "name": u.name, "avatar": u.avatar, "role": u.role}
        for u in users
    ]


@router.get("/{user_id}/following")
def list_following(user_id: int, db: Session = Depends(get_db), _=Depends(get_optional_user)):
    repo = UserRepository(db)
    if not repo.get_by_id(user_id):
        raise HTTPException(404, "Пользователь не найден")
    follows = (
        db.query(UserFollow)
        .filter(UserFollow.follower_id == user_id)
        .order_by(UserFollow.created_at.desc())
        .all()
    )
    users = [repo.get_by_id(f.followed_id) for f in follows if repo.get_by_id(f.followed_id)]
    return [
        {"id": u.id, "name": u.name, "avatar": u.avatar, "role": u.role}
        for u in users
    ]
