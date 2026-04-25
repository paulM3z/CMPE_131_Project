"""
Shared FastAPI dependencies used across multiple routers.

Auth pattern for HTML routes:
  - get_current_user: raises NotAuthenticatedException (caught by global handler → redirect to /auth/login)
  - get_current_user_optional: returns None if not authenticated (for pages visible to guests)
"""
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import decode_access_token


class NotAuthenticatedException(Exception):
    """Raised when a protected route is accessed without a valid session."""
    pass


class ForbiddenException(Exception):
    """Raised when a user lacks permission for an action."""
    def __init__(self, message: str = "You don't have permission to do that."):
        self.message = message
        super().__init__(message)


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Dependency for protected HTML routes.
    Returns the authenticated User or raises NotAuthenticatedException.
    The global exception handler in main.py converts this to a redirect.
    """
    from app.models.user import User

    token = request.cookies.get("access_token")
    if not token:
        raise NotAuthenticatedException()

    user_id = decode_access_token(token)
    if user_id is None:
        raise NotAuthenticatedException()

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise NotAuthenticatedException()

    return user


def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    """
    Dependency for public routes that show extra content to logged-in users.
    Returns User or None — never raises.
    """
    try:
        return get_current_user(request, db)
    except NotAuthenticatedException:
        return None
