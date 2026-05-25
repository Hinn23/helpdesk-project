from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserRead
from app.services.user_service import UserService
from app.auth import get_current_user, admin_required, get_optional_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=dict)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    svc = UserService(db)
    items = svc.get_all(skip, limit)
    total = svc.repo.count()
    return {
        "items": [UserRead.model_validate(u) for u in items],
        "total": total,
        "page": skip // limit + 1,
        "limit": limit,
        "pages": (total + limit - 1) // limit if total else 0,
    }


@router.get("/search")
def search_users(
    q: str = Query("", min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _=Depends(get_optional_user),
):
    if not q.strip():
        return []
    like = f"%{q.strip()}%"
    from app.models.user import User
    users = (
        db.query(User)
        .filter(or_(User.name.ilike(like), User.email.ilike(like)))
        .limit(limit)
        .all()
    )
    return [
        {"id": u.id, "name": u.name, "email": u.email, "role": u.role, "avatar": u.avatar}
        for u in users
    ]


@router.get("/me", response_model=UserRead)
def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db), _=Depends(admin_required)):
    try:
        return UserService(db).get_by_id(user_id)
    except ValueError:
        raise HTTPException(404, f"Юзер #{user_id}? Не знаем такого. Может, он забанился с горя?")


@router.post("/", response_model=UserRead, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db), _=Depends(admin_required)):
    try:
        return UserService(db).create(data)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), _=Depends(admin_required)):
    try:
        return UserService(db).update(user_id, data)
    except ValueError:
        raise HTTPException(404, f"Юзер #{user_id} в пролёте. Не нашли такого")


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), _=Depends(admin_required)):
    try:
        UserService(db).delete(user_id)
    except ValueError:
        raise HTTPException(404, f"Юзер #{user_id} не найден. Может, он сам удалился от стыда?")
