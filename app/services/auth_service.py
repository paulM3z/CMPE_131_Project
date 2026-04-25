"""
Authentication service: password hashing, JWT creation/verification.

Security choices:
  - bcrypt (industry standard, adaptive cost factor — used directly, no passlib wrapper)
  - JWT via python-jose (HS256 symmetric signing with SECRET_KEY)
  - Tokens stored in HTTP-only cookies (not localStorage — resistant to XSS)
"""
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash of the given password."""
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > 72:
        raise ValueError("Password is too long.")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if the plain password matches the stored hash."""
    try:
        password_bytes = plain_password.encode("utf-8")
        if len(password_bytes) > 72:
            return False
        return bcrypt.checkpw(password_bytes, hashed_password.encode("utf-8"))
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(user_id: int) -> str:
    """
    Create a signed JWT encoding the user's ID.
    The token expires after ACCESS_TOKEN_EXPIRE_MINUTES.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),   # 'sub' (subject) is the standard JWT claim for identity
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """
    Decode a JWT and return the user ID (int) from the 'sub' claim.
    Returns None if the token is invalid, expired, or malformed.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            return None
        return int(user_id_str)
    except (JWTError, ValueError):
        return None
