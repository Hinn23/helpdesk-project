from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, Header
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from app.database import get_db
from app.models.user import User
from app.repositories.user_repo import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_REFRESH_SECRET_KEY = SECRET_KEY + "_refresh"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, _REFRESH_SECRET_KEY, algorithm=ALGORITHM)


def verify_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, _REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise JWTError
        return payload
    except JWTError:
        raise HTTPException(401, AUTH_ERRORS["bad_token"])


AUTH_ERRORS = {
    "no_auth": "Ты кто такой? Давай авторизуйся",
    "bad_scheme": "Схема auth не та. Используй Bearer, друг",
    "bad_token": "Токен битый. Или время вышло. Или ты шалишь",
    "user_not_found": "Такого пользователя нет. Проверь email или создай аккаунт",
    "bad_role": "Роль '{}'? Не знаем таких. Доступны: admin, user, guest",
    "admin_only": "Тут нужен админ. А ты не он. Сорри",
    "no_perms": "Не хватает прав доступа. Попроси админа",
    "write_access": "Писать сюда нельзя. Только читать.",
}


def get_current_user(
    authorization: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    if x_user_role:
        return _get_role_user(x_user_role, db)
    if not authorization:
        raise HTTPException(401, AUTH_ERRORS["no_auth"])
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(401, AUTH_ERRORS["bad_scheme"])
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(401, AUTH_ERRORS["bad_token"])
    user = UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(401, AUTH_ERRORS["user_not_found"])
    if user.status == "banned":
        raise HTTPException(403, "Ваш аккаунт заблокирован за нарушение правил")
    return user


def get_optional_user(
    authorization: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if x_user_role:
        return _get_role_user(x_user_role, db)
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        return UserRepository(db).get_by_id(user_id)
    except (JWTError, ValueError, TypeError):
        return None


_ROLE_IDS = {"guest": -1, "support": -2, "manager": -3, "admin": -4}

def _get_role_user(role: str, db: Session) -> User:
    if role not in ("admin", "user", "guest", "support", "manager"):
        raise HTTPException(400, AUTH_ERRORS["bad_role"].format(role))
    return User(id=_ROLE_IDS.get(role, 0), name=role.capitalize(), email=f"{role}@xrole.local", password="", role=role)


def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(403, AUTH_ERRORS["admin_only"])
    return current_user


def role_required(*roles: str):
    def checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(403, AUTH_ERRORS["no_perms"])
        return current_user
    return checker


def check_write_permission(current_user: Optional[User] = Depends(get_optional_user)):
    if not current_user or current_user.role == "guest":
        raise HTTPException(403, AUTH_ERRORS["write_access"])
    return current_user
