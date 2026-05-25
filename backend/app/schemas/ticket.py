from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime, timezone


def _utcnow():
    return datetime.now(timezone.utc)


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc)
    return dt.replace(tzinfo=timezone.utc)


class TicketCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    status: str = "new"
    priority: str = "medium"
    deadline: Optional[datetime] = None
    assignee_id: Optional[int] = None
    author_id: Optional[int] = None
    category_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("название должно содержать минимум 3 символа")
        return v.strip()

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        allowed = {"low", "medium", "high"}
        if v not in allowed:
            raise ValueError(f"приоритет должен быть одним из: низкий, средний, высокий")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        allowed = {"new", "in_progress", "done", "cancelled", "on_moderation", "closed"}
        if v not in allowed:
            raise ValueError(f"статус должен быть одним из: новая, в работе, завершено, отменено, на модерации, закрыто")
        return v

    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, v):
        if v is not None:
            if _to_utc(v) < _utcnow():
                raise ValueError("срок должен быть в будущем")
        return v


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    deadline: Optional[datetime] = None
    assignee_id: Optional[int] = None
    author_id: Optional[int] = None
    category_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is not None and len(v.strip()) < 3:
            raise ValueError("название должно содержать минимум 3 символа")
        return v.strip() if v is not None else v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        allowed = {"low", "medium", "high"}
        if v is not None and v not in allowed:
            raise ValueError(f"приоритет должен быть одним из: низкий, средний, высокий")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        allowed = {"new", "in_progress", "done", "cancelled", "on_moderation", "closed"}
        if v is not None and v not in allowed:
            raise ValueError(f"статус должен быть одним из: новая, в работе, завершено, отменено, на модерации, закрыто")
        return v

    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, v):
        if v is not None:
            if _to_utc(v) < _utcnow():
                raise ValueError("срок должен быть в будущем")
        return v


class TicketRead(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str
    deadline: Optional[datetime] = None
    assignee_id: Optional[int] = None
    author_id: Optional[int] = None
    category_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
