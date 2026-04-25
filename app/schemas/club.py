"""Pydantic schemas for Club validation."""
from pydantic import BaseModel, field_validator


class ClubCreate(BaseModel):
    name: str
    description: str | None = None
    is_private: bool = False

    @field_validator("name")
    @classmethod
    def name_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Club name must be at least 2 characters.")
        if len(v) > 100:
            raise ValueError("Club name must be at most 100 characters.")
        return v

    @field_validator("description")
    @classmethod
    def description_valid(cls, v: str | None) -> str | None:
        if v:
            v = v.strip()
            if len(v) > 1000:
                raise ValueError("Description must be at most 1000 characters.")
        return v or None


class ClubUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_private: bool | None = None

    @field_validator("name")
    @classmethod
    def name_valid(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Club name must be at least 2 characters.")
        if len(v) > 100:
            raise ValueError("Club name must be at most 100 characters.")
        return v


class ClubResponse(BaseModel):
    id: int
    name: str
    description: str | None
    is_private: bool
    created_by: int | None

    model_config = {"from_attributes": True}
