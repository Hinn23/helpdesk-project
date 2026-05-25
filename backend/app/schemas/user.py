from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from app.config import ALLOWED_EMAIL_DOMAINS


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "user"

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if "@" not in v:
            raise ValueError("email должен содержать @")
        if ALLOWED_EMAIL_DOMAINS:
            domain = v.split("@")[1].lower()
            if domain not in ALLOWED_EMAIL_DOMAINS:
                raise ValueError(f"домен {domain} не допускается, разрешены: {', '.join(sorted(ALLOWED_EMAIL_DOMAINS))}")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None and len(v.strip()) < 3:
            raise ValueError("имя должно содержать минимум 3 символа")
        return v.strip() if v is not None else v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v.strip()) < 6:
            raise ValueError("пароль должен содержать минимум 6 символов")
        return v


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v is None:
            return v
        if "@" not in v:
            raise ValueError("email должен содержать @")
        if ALLOWED_EMAIL_DOMAINS:
            domain = v.split("@")[1].lower()
            if domain not in ALLOWED_EMAIL_DOMAINS:
                raise ValueError(f"домен {domain} не допускается, разрешены: {', '.join(sorted(ALLOWED_EMAIL_DOMAINS))}")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is None:
            return v
        if len(v.strip()) < 3:
            raise ValueError("имя должно содержать минимум 3 символа")
        return v.strip()


class UserRead(BaseModel):
    id: int
    name: str
    email: str
    role: str

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    email: str
    password: str
