"""
Event service: create/update/delete events, manage tags, RSVP logic.

Business rules:
  - Any authenticated user can create a standalone event
  - Users with can_create_events in a club can create club events
  - Only the creator (or a club owner) can edit/delete an event
  - RSVP is blocked if the event is at capacity (Phase 2 active, scaffolded now)
  - Tags are reused globally — created on first use, looked up on subsequent use
"""
from datetime import date
from sqlalchemy.orm import Session

from app.models.event import Event, EventAttendee, Tag
from app.models.user import User
from app.schemas.event import EventCreate, EventUpdate


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def get_event_by_id(db: Session, event_id: int) -> Event | None:
    return db.query(Event).filter(Event.id == event_id).first()


def list_events(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    club_id: int | None = None,
    upcoming_only: bool = False,
) -> list[Event]:
    """
    List events with optional filters.
    Phase 2 addition: filter by tag, by private/public.
    """
    query = db.query(Event)
    if club_id is not None:
        query = query.filter(Event.club_id == club_id)
    if upcoming_only:
        query = query.filter(Event.event_date >= date.today())
    return (
        query.order_by(Event.event_date.asc(), Event.event_time.asc())
             .offset(skip)
             .limit(limit)
             .all()
    )


def get_rsvp(db: Session, user_id: int, event_id: int) -> EventAttendee | None:
    return db.query(EventAttendee).filter(
        EventAttendee.user_id == user_id,
        EventAttendee.event_id == event_id,
    ).first()


# ---------------------------------------------------------------------------
# Tag helpers
# ---------------------------------------------------------------------------

def get_or_create_tag(db: Session, name: str) -> Tag:
    """Return an existing tag by name (case-insensitive) or create it."""
    name = name.strip().lower()
    tag = db.query(Tag).filter(Tag.name == name).first()
    if not tag:
        tag = Tag(name=name)
        db.add(tag)
        db.flush()
    return tag


def _sync_tags(db: Session, event: Event, tag_names: list[str]) -> None:
    """Replace the event's tags with the given list."""
    tags = [get_or_create_tag(db, n) for n in tag_names if n.strip()]
    event.tags = tags


# ---------------------------------------------------------------------------
# Create / Update / Delete
# ---------------------------------------------------------------------------

def create_event(db: Session, data: EventCreate, creator: User) -> Event:
    event = Event(
        title=data.title,
        description=data.description,
        location=data.location,
        map_query=data.map_query,
        event_date=data.event_date,
        event_time=data.event_time,
        capacity=data.capacity,
        is_private=data.is_private,
        created_by=creator.id,
        club_id=data.club_id,
    )
    db.add(event)
    db.flush()

    _sync_tags(db, event, data.tags)

    db.commit()
    db.refresh(event)
    return event


def update_event(db: Session, event: Event, data: EventUpdate) -> Event:
    event.title = data.title
    event.description = data.description
    event.location = data.location
    event.map_query = data.map_query
    event.event_date = data.event_date
    event.event_time = data.event_time
    event.capacity = data.capacity
    event.is_private = data.is_private
    event.club_id = data.club_id

    _sync_tags(db, event, data.tags)

    db.commit()
    db.refresh(event)
    return event


def delete_event(db: Session, event: Event) -> None:
    db.delete(event)
    db.commit()


# ---------------------------------------------------------------------------
# RSVP / Attendance
# ---------------------------------------------------------------------------

def rsvp_event(db: Session, user: User, event: Event) -> EventAttendee:
    """
    RSVP the user to the event.
    Raises ValueError if already RSVP'd or event is at capacity.
    """
    existing = get_rsvp(db, user.id, event.id)
    if existing:
        raise ValueError("You have already RSVP'd to this event.")

    if event.is_full:
        raise ValueError(
            f"This event is at capacity ({event.capacity} attendees)."
        )

    attendee = EventAttendee(event_id=event.id, user_id=user.id)
    db.add(attendee)
    db.commit()
    db.refresh(attendee)
    return attendee


def cancel_rsvp(db: Session, user: User, event: Event) -> None:
    """Remove the user's RSVP from the event."""
    attendee = get_rsvp(db, user.id, event.id)
    if not attendee:
        raise ValueError("You have not RSVP'd to this event.")
    db.delete(attendee)
    db.commit()


# ---------------------------------------------------------------------------
# Permission checks
# ---------------------------------------------------------------------------

def can_edit_event(user: User, event: Event) -> bool:
    """
    Return True if the user is allowed to edit/delete this event.
    Phase 2: also allow club owners and users with can_create_events.
    """
    if user.is_admin:
        return True
    return event.created_by == user.id
