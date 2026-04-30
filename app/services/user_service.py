"""
User service: CRUD operations and settings management for users.
All DB operations live here — routers call service functions, not the ORM directly.
"""
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import PROFILE_UPLOAD_DIR
from app.models.user import User, UserSettings
from app.schemas.user import UserCreate, UserUpdateSettings
from app.services.auth_service import hash_password, verify_password


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def create_user(db: Session, data: UserCreate) -> User:
    """
    Create a new user and their default settings row.
    Caller is responsible for checking that username/email aren't taken first.
    """
    user = User(
        username=data.username,
        email=data.email.lower(),
        phone_number=data.phone_number,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.flush()  # get user.id before committing

    # Create default settings for the new user
    settings = UserSettings(user_id=user.id)
    db.add(settings)

    db.commit()
    db.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """
    Return the User if username and password are correct, else None.
    Uses case-insensitive username lookup.
    """
    user = db.query(User).filter(
        User.username == username,
        User.is_active == True,
    ).first()

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# ---------------------------------------------------------------------------
# Settings & profile updates
# ---------------------------------------------------------------------------

def update_username(db: Session, user: User, new_username: str) -> User:
    user.username = new_username
    db.commit()
    db.refresh(user)
    return user


def update_email(db: Session, user: User, new_email: str) -> User:
    user.email = new_email.lower()
    db.commit()
    db.refresh(user)
    return user


def update_password(db: Session, user: User, new_password: str) -> User:
    user.hashed_password = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user


def update_phone(db: Session, user: User, phone_number: str | None) -> User:
    user.phone_number = phone_number
    db.commit()
    db.refresh(user)
    return user


def update_profile_photo(db: Session, user: User, profile_photo_path: str | None) -> User:
    old_photo_path = user.profile_photo_path
    user.profile_photo_path = profile_photo_path
    db.commit()
    db.refresh(user)

    if old_photo_path and old_photo_path != profile_photo_path:
        old_file = PROFILE_UPLOAD_DIR / Path(old_photo_path).name
        try:
            if old_file.is_file() and PROFILE_UPLOAD_DIR in old_file.parents:
                old_file.unlink()
        except OSError:
            pass

    return user


def ensure_user_settings(db: Session, user: User) -> UserSettings:
    """Return settings for a user, creating the row for older accounts if needed."""
    if user.settings:
        return user.settings

    settings = UserSettings(user_id=user.id)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    db.refresh(user)
    return settings


def update_user_settings(db: Session, user: User, data: UserUpdateSettings) -> UserSettings:
    """Update UI preferences (language, theme, text size)."""
    settings = ensure_user_settings(db, user)

    if data.language is not None:
        settings.language = data.language
    if data.theme is not None:
        settings.theme = data.theme
    if data.text_size is not None:
        settings.text_size = data.text_size

    db.commit()
    db.refresh(settings)
    return settings
