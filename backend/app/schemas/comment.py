from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class CommentCreate(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("текст не должен быть пустым")
        return v.strip()


class CommentUpdate(BaseModel):
    text: Optional[str] = None


class CommentRead(BaseModel):
    id: int
    ticket_id: int
    author_id: int
    author_name: str
    text: str
    created_at: datetime
    thanks_count: int = 0
    is_thanked: bool = False
    is_response: int = 0

    model_config = {"from_attributes": True}
