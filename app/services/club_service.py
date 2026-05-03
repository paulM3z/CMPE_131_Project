"""
Club service: create clubs, manage memberships and roles.

Business rules:
  - Club names are globally unique
  - Creating a club auto-creates two roles: "Owner" and "Member"
  - The creator is added as a member with the "Owner" role
  - "Member" is the default role (is_default=True) for new joiners
  - A user cannot join a club they're already in
  - Only the Owner (or system admin) can remove members or delete the club
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.club import Club, ClubMembership, ClubRole
from app.models.event import Event, EventAttendee
from app.models.user import User
from app.schemas.club import ClubCreate, ClubUpdate


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def get_club_by_id(db: Session, club_id: int) -> Club | None:
    return db.query(Club).filter(Club.id == club_id).first()


def get_club_by_name(db: Session, name: str) -> Club | None:
    return db.query(Club).filter(Club.name == name).first()


def list_clubs(db: Session, skip: int = 0, limit: int = 100) -> list[Club]:
    return db.query(Club).order_by(Club.name).offset(skip).limit(limit).all()


def get_membership(db: Session, user_id: int, club_id: int) -> ClubMembership | None:
    return db.query(ClubMembership).filter(
        ClubMembership.user_id == user_id,
        ClubMembership.club_id == club_id,
    ).first()


def get_user_clubs(db: Session, user_id: int) -> list[Club]:
    """Return all clubs a user is an approved member of."""
    return (
        db.query(Club)
        .join(ClubMembership, ClubMembership.club_id == Club.id)
        .filter(
            ClubMembership.user_id == user_id,
            ClubMembership.is_approved == True,
        )
        .order_by(Club.name)
        .all()
    )


# ---------------------------------------------------------------------------
# Role helpers
# ---------------------------------------------------------------------------

def get_owner_role(db: Session, club_id: int) -> ClubRole | None:
    return db.query(ClubRole).filter(
        ClubRole.club_id == club_id,
        ClubRole.name == "Owner",
    ).first()


def get_default_role(db: Session, club_id: int) -> ClubRole | None:
    """Return the role that gets auto-assigned to new members."""
    return db.query(ClubRole).filter(
        ClubRole.club_id == club_id,
        ClubRole.is_default == True,
    ).first()


def is_club_owner(db: Session, user_id: int, club_id: int) -> bool:
    """Return True if the user holds the Owner role in this club."""
    membership = get_membership(db, user_id, club_id)
    if not membership or not membership.role:
        return False
    return membership.role.name == "Owner"


def can_manage_members(db: Session, user_id: int, club_id: int) -> bool:
    """Return True if the user can add/remove members for this club."""
    return is_club_owner(db, user_id, club_id)


def _delete_member_club_event_rsvps(db: Session, user_id: int, club_id: int) -> int:
    club_event_ids = select(Event.id).where(Event.club_id == club_id)
    return (
        db.query(EventAttendee)
        .filter(
            EventAttendee.user_id == user_id,
            EventAttendee.event_id.in_(club_event_ids),
        )
        .delete(synchronize_session=False)
    )


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def create_club(db: Session, data: ClubCreate, creator: User) -> Club:
    """
    Create a new club, its default roles, and add the creator as Owner.
    """
    club = Club(
        name=data.name,
        description=data.description,
        is_private=data.is_private,
        created_by=creator.id,
    )
    db.add(club)
    db.flush()  # need club.id for roles

    # Create the two default roles
    owner_role = ClubRole(
        club_id=club.id,
        name="Owner",
        description="Full control over this club.",
        can_manage_members=True,
        can_create_events=True,
        can_edit_club=True,
        is_default=False,
    )
    member_role = ClubRole(
        club_id=club.id,
        name="Member",
        description="Standard club member.",
        can_manage_members=False,
        can_create_events=False,
        can_edit_club=False,
        is_default=True,
    )
    db.add(owner_role)
    db.add(member_role)
    db.flush()  # need role IDs for membership

    # Add creator as a member with Owner role
    membership = ClubMembership(
        user_id=creator.id,
        club_id=club.id,
        role_id=owner_role.id,
        is_approved=True,
    )
    db.add(membership)

    db.commit()
    db.refresh(club)
    return club


def update_club(db: Session, club: Club, data: ClubUpdate) -> Club:
    if data.name is not None:
        club.name = data.name
    if data.description is not None:
        club.description = data.description
    if data.is_private is not None:
        club.is_private = data.is_private
    db.commit()
    db.refresh(club)
    return club


# ---------------------------------------------------------------------------
# Membership
# ---------------------------------------------------------------------------

def join_club(db: Session, user: User, club: Club) -> ClubMembership:
    """
    Add the user to the club with the default member role.
    Raises ValueError if already a member or if the club is full/private (Phase 2).
    """
    existing = get_membership(db, user.id, club.id)
    if existing:
        raise ValueError("You are already a member of this club.")

    default_role = get_default_role(db, club.id)
    membership = ClubMembership(
        user_id=user.id,
        club_id=club.id,
        role_id=default_role.id if default_role else None,
        # Private clubs pend approval; public clubs auto-approve
        is_approved=not club.is_private,
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def leave_club(db: Session, user: User, club: Club) -> None:
    """
    Remove the user from the club.
    Raises ValueError if the user is the sole Owner.
    """
    membership = get_membership(db, user.id, club.id)
    if not membership:
        raise ValueError("You are not a member of this club.")

    # Prevent orphaning the club with no owner
    if membership.role and membership.role.name == "Owner":
        owner_count = (
            db.query(ClubMembership)
            .join(ClubRole, ClubRole.id == ClubMembership.role_id)
            .filter(
                ClubMembership.club_id == club.id,
                ClubRole.name == "Owner",
            )
            .count()
        )
        if owner_count <= 1:
            raise ValueError(
                "You are the only owner. Transfer ownership before leaving."
            )

    _delete_member_club_event_rsvps(db, user.id, club.id)
    db.delete(membership)
    db.commit()


def remove_member(db: Session, target_user_id: int, club: Club) -> None:
    """Remove a specific member from the club (called by an owner/manager)."""
    membership = get_membership(db, target_user_id, club.id)
    if not membership:
        raise ValueError("That user is not a member of this club.")
    _delete_member_club_event_rsvps(db, target_user_id, club.id)
    db.delete(membership)
    db.commit()


def delete_club(db: Session, club: Club) -> None:
    """Delete a club and all related data (cascade handles memberships, roles)."""
    db.delete(club)
    db.commit()
