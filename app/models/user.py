"""
User-related database models.

Tables:
  users          — core account info and auth credentials
  user_settings  — per-user preferences (language, theme, text size)

Design notes:
  - Passwords are NEVER stored in plain text (see services/auth_service.py for hashing)
  - is_admin flag is a simple system-level admin; Phase 2 adds granular roles
  - UserSettings is created automatically when a user registers
"""
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    profile_photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Account status — deactivated users cannot log in
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # System-level admin flag — grants access to admin-only features
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # One-to-one: settings created on registration
    settings: Mapped["UserSettings"] = relationship(
        "UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    # Clubs this user belongs to (via ClubMembership join table)
    club_memberships: Mapped[list["ClubMembership"]] = relationship(  # type: ignore[name-defined]
        "ClubMembership", back_populates="user", cascade="all, delete-orphan"
    )

    # Clubs this user created
    created_clubs: Mapped[list["Club"]] = relationship(  # type: ignore[name-defined]
        "Club", back_populates="creator", foreign_keys="Club.created_by"
    )

    # Events this user created
    created_events: Mapped[list["Event"]] = relationship(  # type: ignore[name-defined]
        "Event", back_populates="creator"
    )

    # Events this user has RSVP'd to
    event_attendances: Mapped[list["EventAttendee"]] = relationship(  # type: ignore[name-defined]
        "EventAttendee", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"

    @property
    def profile_photo_url(self) -> str | None:
        if not self.profile_photo_path:
            return None
        return self.profile_photo_path


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # Phase 1: language preference
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)

    # Phase 2: UI theming (scaffolded now, activated in Phase 2)
    theme: Mapped[str] = mapped_column(String(10), default="light", nullable=False)
    text_size: Mapped[str] = mapped_column(String(10), default="medium", nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="settings")

    def __repr__(self) -> str:
        return f"<UserSettings user_id={self.user_id} lang={self.language!r}>"
