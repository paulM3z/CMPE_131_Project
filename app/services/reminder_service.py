"""Background reminder checks for upcoming RSVP'd events."""
from datetime import datetime, time, timedelta

from sqlalchemy.orm import Session, joinedload

from app.config import EVENT_REMINDER_HOURS_BEFORE
from app.models.event import Event, EventAttendee
from app.services.email_service import send_event_reminder

_sent_reminders: set[tuple[int, int, str]] = set()


def _event_datetime(event: Event) -> datetime:
    return datetime.combine(event.event_date, event.event_time or time(hour=9))


def send_due_event_reminders(db: Session, now: datetime | None = None) -> int:
    """Send reminder emails for RSVP'd events starting within the reminder window."""
    now = now or datetime.now()
    window_end = now + timedelta(hours=EVENT_REMINDER_HOURS_BEFORE)
    sent_count = 0

    attendees = (
        db.query(EventAttendee)
        .options(joinedload(EventAttendee.event), joinedload(EventAttendee.user))
        .join(Event)
        .filter(Event.event_date >= now.date())
        .all()
    )

    for attendee in attendees:
        event = attendee.event
        user = attendee.user
        starts_at = _event_datetime(event)
        reminder_key = (attendee.user_id, attendee.event_id, starts_at.isoformat())

        if starts_at < now or starts_at > window_end or reminder_key in _sent_reminders:
            continue

        send_event_reminder(
            to_email=user.email,
            username=user.username,
            event_title=event.title,
            event_date=str(event.event_date),
            event_time=event.event_time.strftime("%I:%M %p") if event.event_time else None,
            event_location=event.location,
        )
        _sent_reminders.add(reminder_key)
        sent_count += 1

    return sent_count
