"""
Club-related database models.

Tables:
  clubs            — club info and metadata
  club_roles       — roles that can be assigned to club members (Owner, Member, custom)
  club_memberships — many-to-many between users and clubs, with an optional role

Design notes:
  - Every club gets two default roles on creation: "Owner" and "Member"
  - The user who creates a club is assigned the "Owner" role automatically
  - Phase 2: permission flags (can_manage_members, etc.) are scaffolded here
  - Phase 2: is_private clubs require approval to join
"""
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Club(Base):
    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Phase 2: private clubs require admin approval to join
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # User who created this club
    creator: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User", back_populates="created_clubs", foreign_keys=[created_by]
    )

    # All membership records for this club
    memberships: Mapped[list["ClubMembership"]] = relationship(
        "ClubMembership", back_populates="club", cascade="all, delete-orphan"
    )

    # Roles defined for this club
    roles: Mapped[list["ClubRole"]] = relationship(
        "ClubRole", back_populates="club", cascade="all, delete-orphan"
    )

    # Events hosted by this club
    events: Mapped[list["Event"]] = relationship(  # type: ignore[name-defined]
        "Event", back_populates="club"
    )

    @property
    def member_count(self) -> int:
        return len([m for m in self.memberships if m.is_approved])

    def __repr__(self) -> str:
        return f"<Club id={self.id} name={self.name!r}>"


class ClubRole(Base):
    """
    A role that can be assigned to club members.
    Each club has at least two system roles: Owner and Member.
    Phase 2: clubs can create custom roles with granular permission flags.
    """
    __tablename__ = "club_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    club_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Permission flags (Phase 2 activates these in the UI)
    can_manage_members: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_create_events: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_edit_club: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # If True, new members are automatically assigned this role on join
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    club: Mapped["Club"] = relationship("Club", back_populates="roles")
    memberships: Mapped[list["ClubMembership"]] = relationship(
        "ClubMembership", back_populates="role"
    )

    def __repr__(self) -> str:
        return f"<ClubRole id={self.id} club_id={self.club_id} name={self.name!r}>"


class ClubMembership(Base):
    """
    Join table: which users belong to which clubs, and what role they have.
    Unique constraint prevents a user from having duplicate memberships.
    """
    __tablename__ = "club_memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "club_id", name="uq_club_membership"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    club_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False
    )
    # Nullable: member might have no specific role assigned (falls back to default)
    role_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("club_roles.id", ondelete="SET NULL"), nullable=True
    )

    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Phase 2: private clubs use this to gate access
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="club_memberships")  # type: ignore[name-defined]
    club: Mapped["Club"] = relationship("Club", back_populates="memberships")
    role: Mapped["ClubRole | None"] = relationship("ClubRole", back_populates="memberships")

    def __repr__(self) -> str:
        return f"<ClubMembership user_id={self.user_id} club_id={self.club_id}>"
