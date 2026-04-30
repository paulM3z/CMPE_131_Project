"""Pydantic schemas for Event validation."""
from datetime import date, time
from pydantic import BaseModel, field_validator

from app.config import MAX_EVENT_CAPACITY


class EventCreate(BaseModel):
    title: str
    description: str | None = None
    location: str | None = None
    map_query: str | None = None
    event_date: date
    event_time: time | None = None
    capacity: int | None = None
    is_private: bool = False
    club_id: int | None = None
    tags: list[str] = []

    @field_validator("title")
    @classmethod
    def title_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Title must be at least 3 characters.")
        if len(v) > 200:
            raise ValueError("Title must be at most 200 characters.")
        return v

    @field_validator("location", "map_query")
    @classmethod
    def optional_text_valid(cls, v: str | None) -> str | None:
        if v is None:
            return None
        value = v.strip()
        return value or None

    @field_validator("capacity")
    @classmethod
    def capacity_valid(cls, v: int | None) -> int | None:
        if v is not None and v < 1:
            raise ValueError("Capacity must be at least 1.")
        if v is not None and v > MAX_EVENT_CAPACITY:
            raise ValueError(f"Capacity must be {MAX_EVENT_CAPACITY:,} or less.")
        return v

    @field_validator("tags")
    @classmethod
    def tags_valid(cls, v: list[str]) -> list[str]:
        return [t.strip().lower() for t in v if t.strip()][:10]  # max 10 tags


class EventUpdate(EventCreate):
    """Same fields as create — all updatable."""
    pass


class EventResponse(BaseModel):
    id: int
    title: str
    description: str | None
    location: str | None
    map_query: str | None
    event_date: date
    event_time: time | None
    capacity: int | None
    is_private: bool
    created_by: int | None
    club_id: int | None

    model_config = {"from_attributes": True}
