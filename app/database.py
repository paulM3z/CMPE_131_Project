"""
Database setup: SQLAlchemy engine, session factory, and base model class.
Supports both SQLite (local dev) and PostgreSQL (production) via DATABASE_URL.
"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import DATABASE_URL

# SQLite requires check_same_thread=False for multi-threaded use with FastAPI
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args)

# Each request gets its own session, closed when the request finishes
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def get_db():
    """FastAPI dependency: yields a database session, always closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables defined in models. Called at app startup."""
    # Import models here so SQLAlchemy registers them before create_all
    from app.models import user, club, event  # noqa: F401
    Base.metadata.create_all(bind=engine)
    _ensure_runtime_columns()


def _ensure_runtime_columns() -> None:
    """Add columns expected by newer code when running against an older local DB."""
    inspector = inspect(engine)

    existing_user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "profile_photo_path" not in existing_user_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE users ADD COLUMN profile_photo_path VARCHAR(500)"))

    existing_event_columns = {column["name"] for column in inspector.get_columns("events")}
    if "map_query" not in existing_event_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE events ADD COLUMN map_query VARCHAR(500)"))
