import os, uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserUpdate, UserRead
from app.services.user_service import UserService
from pydantic import BaseModel
from app.auth import create_access_token, create_refresh_token, verify_refresh_token, get_current_user, verify_password, hash_password, AUTH_ERRORS
from app.mail import send_email
from jose import JWTError, jwt
from app.config import SECRET_KEY, ALGORITHM, FRONTEND_URL


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    svc = UserService(db)
    if svc.repo.get_by_email(data.email):
        raise HTTPException(400, "Этот email уже занят. Хакеры, идите лесом")
    if svc.repo.get_by_name(data.name):
        raise HTTPException(400, "Это имя уже занято. Будь оригинальнее")

    import random
    from app.models.registration_code import RegistrationCode
    code = str(random.randint(100000, 999999))

    existing_code = db.query(RegistrationCode).filter(RegistrationCode.email == data.email).first()
    if existing_code:
        db.delete(existing_code)
        db.commit()

    db.add(RegistrationCode(email=data.email, name=data.name, password=hash_password(data.password), code=code))
    db.commit()

    send_email(data.email, "Код подтверждения регистрации",
        f"Привет, {data.name}!\n\nТвой код подтверждения: {code}\n\nВведи его на сайте, чтобы завершить регистрацию.")

    return {"message": "Код отправлен на почту", "email": data.email, "code_for_test": code}


@router.post("/verify-email")
def verify_email(data: dict, db: Session = Depends(get_db)):
    email = data.get("email", "")
    code = data.get("code", "")
    from app.models.registration_code import RegistrationCode
    reg = db.query(RegistrationCode).filter(RegistrationCode.email == email, RegistrationCode.code == code).first()
    if not reg:
        raise HTTPException(400, "Неверный код подтверждения")
    from app.models.user import User
    user = User(name=reg.name, email=reg.email, password=reg.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.delete(reg)
    db.commit()
    token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh = create_refresh_token({"sub": str(user.id)})
    send_email(email, "Добро пожаловать в Helpdesk Lite!",
        f"Привет, {reg.name}!\n\nРегистрация завершена. Добро пожаловать!")
    return {"access_token": token, "refresh_token": refresh, "token_type": "bearer", "user_id": user.id, "role": user.role, "name": user.name}


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    svc = UserService(db)
    user = svc.repo.get_by_email(data.email)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Неверный email или пароль. Может, ты нас взламываешь?")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh = create_refresh_token({"sub": str(user.id)})
    return {"access_token": token, "refresh_token": refresh, "token_type": "bearer", "user_id": user.id, "role": user.role, "name": user.name}


@router.post("/refresh")
def refresh(token_data: dict, db: Session = Depends(get_db)):
    payload = verify_refresh_token(token_data.get("refresh_token", ""))
    user_id = int(payload.get("sub"))
    svc = UserService(db)
    try:
        user = svc.get_by_id(user_id)
    except ValueError:
        raise HTTPException(401, "Пользователь не найден")
    new_token = create_access_token({"sub": str(user.id), "role": user.role})
    new_refresh = create_refresh_token({"sub": str(user.id)})
    return {"access_token": new_token, "refresh_token": new_refresh, "token_type": "bearer", "user_id": user.id, "role": user.role, "name": user.name}


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "avatar": current_user.avatar,
        "status": current_user.status or "active",
    }


@router.put("/me", response_model=UserRead)
def update_me(data: UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    svc = UserService(db)
    try:
        return svc.update(current_user.id, data)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.put("/me/password")
def change_password(data: PasswordChange, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if not verify_password(data.current_password, current_user.password):
        raise HTTPException(400, "Текущий пароль неверен")
    if len(data.new_password.strip()) < 6:
        raise HTTPException(400, "Новый пароль должен быть минимум 6 символов")
    current_user.password = hash_password(data.new_password)
    db.commit()
    return {"message": "Пароль изменён"}


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    svc = UserService(db)
    user = svc.repo.get_by_email(data.email)
    if not user:
        return {"message": "Если такой email существует, ссылка для сброса пароля была отправлена"}
    reset_token = jwt.encode(
        {"sub": str(user.id), "exp": datetime.utcnow() + timedelta(minutes=30), "type": "reset"},
        SECRET_KEY, algorithm=ALGORITHM,
    )
    reset_link = f"{FRONTEND_URL}/reset-password?token={reset_token}"
    send_email(user.email, "Сброс пароля Helpdesk Lite",
        f"Привет!\n\nДля сброса пароля перейди по ссылке:\n{reset_link}\n\nСсылка действует 30 минут.")
    return {"reset_link": reset_link, "message": "Ссылка для сброса пароля отправлена на почту"}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "reset":
            raise HTTPException(400, "Неверный токен сброса")
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(400, "Токен истёк или недействителен")
    svc = UserService(db)
    try:
        user = svc.get_by_id(user_id)
    except ValueError:
        raise HTTPException(404, "Пользователь не найден")
    if len(data.new_password.strip()) < 6:
        raise HTTPException(400, "Пароль должен быть минимум 6 символов")
    user.password = hash_password(data.new_password)
    db.commit()
    return {"message": "Пароль успешно изменён"}


@router.get("/me/tickets")
def my_tickets(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    from app.models.ticket import Ticket
    total = db.query(Ticket).filter(Ticket.author_id == current_user.id).count()
    return {"total": total}


AVATAR_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)
MAX_AVATAR_SIZE = 2 * 1024 * 1024


@router.post("/me/avatar", status_code=200)
async def upload_avatar(file: UploadFile = File(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    contents = await file.read()
    if len(contents) > MAX_AVATAR_SIZE:
        raise HTTPException(413, "Файл больше 2 МБ")
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    if ext.lower() not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        raise HTTPException(400, "Разрешены только JPG, PNG, GIF, WebP")
    filename = f"avatar_{current_user.id}{ext}"
    filepath = os.path.join(AVATAR_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(contents)
    current_user.avatar = filename
    db.commit()
    return {"avatar": filename}


@router.get("/{user_id}/avatar")
def get_user_avatar(user_id: int, db: Session = Depends(get_db)):
    from app.repositories.user_repo import UserRepository
    user = UserRepository(db).get_by_id(user_id)
    if not user or not user.avatar:
        raise HTTPException(404, "Аватар не найден")
    filepath = os.path.join(AVATAR_DIR, user.avatar)
    if not os.path.exists(filepath):
        raise HTTPException(404, "Файл аватара не найден")
    return FileResponse(filepath)


@router.delete("/me/avatar")
def delete_avatar(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.avatar:
        filepath = os.path.join(AVATAR_DIR, current_user.avatar)
        if os.path.exists(filepath):
            os.remove(filepath)
        current_user.avatar = None
        db.commit()
    return {"message": "Аватар удалён"}
