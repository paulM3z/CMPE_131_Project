# Import all models so SQLAlchemy registers them for create_all / Alembic autogenerate
from app.models.user import User, UserSettings       # noqa: F401
from app.models.club import Club, ClubRole, ClubMembership  # noqa: F401
from app.models.event import Event, EventAttendee, Tag, event_tags  # noqa: F401
