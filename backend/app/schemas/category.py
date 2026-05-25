from pydantic import BaseModel, field_validator
from typing import Optional


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = ""

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError("название должно содержать минимум 2 символа")
        return v.strip()


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryRead(BaseModel):
    id: int
    name: str
    description: str

    model_config = {"from_attributes": True}
