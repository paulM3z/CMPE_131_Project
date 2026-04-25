"""
Event-related database models.

Tables:
  events          — event info (title, location, date/time, capacity, visibility)
  event_attendees — RSVP/attendance records (many-to-many users ↔ events)
  tags            — reusable tag labels (e.g. "music", "networking")
  event_tags      — association table linking events to tags

Design notes:
  - Events can be standalone or linked to a club via club_id
  - capacity=None means unlimited attendance
  - is_private=True events are only visible to club members (Phase 2 enforces this)
  - RSVP is_public flag lets attendees hide their attendance (Phase 2 UI)
"""
from datetime import date, datetime, time
from urllib.parse import quote_plus
from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey, Integer,
    String, Table, Time, UniqueConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# Association table for the many-to-many Event ↔ Tag relationship
event_tags = Table(
    "event_tags",
    Base.metadata,
    Column("event_id", Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    location: Mapped[str | None] = mapped_column(String(300), nullable=True)
    map_query: Mapped[str | None] = mapped_column(String(500), nullable=True)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    event_time: Mapped[time | None] = mapped_column(Time, nullable=True)

    # None = unlimited; Phase 2 enforces cap in RSVP service
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Phase 2: private events visible only to members with the right role
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Who created this event
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Optional: event belongs to a club
    club_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("clubs.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    creator: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", back_populates="created_events"
    )
    club: Mapped["Club | None"] = relationship(  # type: ignore[name-defined]
        "Club", back_populates="events"
    )
    attendees: Mapped[list["EventAttendee"]] = relationship(
        "EventAttendee", back_populates="event", cascade="all, delete-orphan"
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary=event_tags, back_populates="events"
    )

    @property
    def attendee_count(self) -> int:
        return len(self.attendees)

    @property
    def has_limited_capacity(self) -> bool:
        return self.capacity is not None and self.capacity > 0

    @property
    def fill_percentage(self) -> int | None:
        if not self.has_limited_capacity:
            return None
        return min(int((self.attendee_count / self.capacity) * 100), 100)

    @property
    def spots_filled_text(self) -> str | None:
        if not self.has_limited_capacity:
            return None
        return f"{self.attendee_count}/{self.capacity} spots filled"

    @property
    def hype_status(self) -> dict[str, str] | None:
        if not self.has_limited_capacity:
            return None

        fill_percentage = self.fill_percentage or 0
        if fill_percentage <= 30:
            return {
                "label": "\U0001F7E2 Just Getting Started",
                "badge_class": "badge-hype-green",
                "progress_class": "bg-hype-green",
            }
        if fill_percentage <= 60:
            return {
                "label": "\U0001F7E1 Getting Popular",
                "badge_class": "badge-hype-yellow",
                "progress_class": "bg-hype-yellow",
            }
        if fill_percentage <= 85:
            return {
                "label": "\U0001F7E0 Hype Building! \U0001F525",
                "badge_class": "badge-hype-orange",
                "progress_class": "bg-hype-orange",
            }
        if fill_percentage < 100:
            return {
                "label": "\U0001F534 Almost Full! \u26A0\uFE0F",
                "badge_class": "badge-hype-red",
                "progress_class": "bg-hype-red",
            }
        return {
            "label": "\u26AB Sold Out! \U0001F480",
            "badge_class": "badge-hype-black",
            "progress_class": "bg-hype-black",
        }

    @property
    def is_full(self) -> bool:
        if not self.has_limited_capacity:
            return False
        return self.attendee_count >= self.capacity

    @property
    def resolved_map_query(self) -> str | None:
        if self.map_query:
            return self.map_query
        return self.location

    @property
    def google_maps_url(self) -> str | None:
        if not self.resolved_map_query:
            return None
        return f"https://www.google.com/maps/search/?api=1&query={quote_plus(self.resolved_map_query)}"

    @property
    def google_maps_embed_url(self) -> str | None:
        if not self.resolved_map_query:
            return None
        return f"https://www.google.com/maps?q={quote_plus(self.resolved_map_query)}&output=embed"

    def __repr__(self) -> str:
        return f"<Event id={self.id} title={self.title!r} date={self.event_date}>"


class EventAttendee(Base):
    """
    RSVP record: one row per (user, event) pair.
    Unique constraint prevents double-RSVP.
    """
    __tablename__ = "event_attendees"
    __table_args__ = (
        UniqueConstraint("event_id", "user_id", name="uq_event_attendee"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Phase 2: let attendees hide their name from the public attendee list
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    rsvp_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    event: Mapped["Event"] = relationship("Event", back_populates="attendees")
    user: Mapped["User"] = relationship("User", back_populates="event_attendances")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return f"<EventAttendee event_id={self.event_id} user_id={self.user_id}>"


class Tag(Base):
    """
    Reusable tag (e.g. "music", "networking", "car show").
    Tags are shared across all events — not per-club.
    Phase 2: search/filter events by tag.
    """
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    events: Mapped[list["Event"]] = relationship(
        "Event", secondary=event_tags, back_populates="tags"
    )

    def __repr__(self) -> str:
        return f"<Tag id={self.id} name={self.name!r}>"
