"""
Pydantic schemas for User validation.

Separate schemas for:
  - input (what the client sends)
  - output (what we return to the client)
  - internal (what we use between layers)

This prevents accidentally exposing hashed_password in API responses.
"""
import re
from pydantic import BaseModel, EmailStr, field_validator

MAX_BCRYPT_PASSWORD_BYTES = 72


# ---------------------------------------------------------------------------
# Registration / Creation
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone_number: str | None = None

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters.")
        if len(v) > 50:
            raise ValueError("Username must be at most 50 characters.")
        if not re.match(r"^[a-zA-Z0-9_.-]+$", v):
            raise ValueError("Username may only contain letters, numbers, underscores, dots, and hyphens.")
        return v

    @field_validator("password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if len(v.encode("utf-8")) > MAX_BCRYPT_PASSWORD_BYTES:
            raise ValueError("Password is too long or contains too many special characters. Please keep it under 72 bytes.")
        return v

    @field_validator("phone_number")
    @classmethod
    def phone_valid(cls, v: str | None) -> str | None:
        if v is None:
            return v
        # Strip whitespace; allow digits, spaces, dashes, parentheses, +
        v = v.strip()
        if v and not re.match(r"^[\d\s\-\(\)\+]+$", v):
            raise ValueError("Phone number contains invalid characters.")
        return v or None


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class UserLogin(BaseModel):
    username: str
    password: str


# ---------------------------------------------------------------------------
# Settings updates (each field is optional — user only sends what they change)
# ---------------------------------------------------------------------------

class UserUpdateUsername(BaseModel):
    username: str

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters.")
        if len(v) > 50:
            raise ValueError("Username must be at most 50 characters.")
        if not re.match(r"^[a-zA-Z0-9_.-]+$", v):
            raise ValueError("Username may only contain letters, numbers, underscores, dots, and hyphens.")
        return v


class UserUpdateEmail(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def email_normalized(cls, v: EmailStr) -> str:
        return str(v).strip().lower()


class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def new_password_valid(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("New password must be at least 8 characters.")
        if len(v.encode("utf-8")) > MAX_BCRYPT_PASSWORD_BYTES:
            raise ValueError("New password is too long or contains too many special characters. Please keep it under 72 bytes.")
        return v

    def passwords_match(self) -> bool:
        return self.new_password == self.confirm_password


class UserUpdatePhone(BaseModel):
    phone_number: str | None = None

    @field_validator("phone_number")
    @classmethod
    def phone_valid(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if v and not re.match(r"^[\d\s\-\(\)\+]+$", v):
            raise ValueError("Phone number contains invalid characters.")
        return v or None


class UserUpdateSettings(BaseModel):
    language: str | None = None
    theme: str | None = None
    text_size: str | None = None

    @field_validator("language")
    @classmethod
    def language_valid(cls, v: str | None) -> str | None:
        allowed = {"en", "es", "fr", "de", "zh", "ja", "ko", "pt", "ar"}
        if v and v not in allowed:
            raise ValueError(f"Language must be one of: {', '.join(sorted(allowed))}")
        return v

    @field_validator("theme")
    @classmethod
    def theme_valid(cls, v: str | None) -> str | None:
        if v and v not in {"light", "dark"}:
            raise ValueError("Theme must be 'light' or 'dark'.")
        return v

    @field_validator("text_size")
    @classmethod
    def text_size_valid(cls, v: str | None) -> str | None:
        if v and v not in {"small", "medium", "large"}:
            raise ValueError("Text size must be 'small', 'medium', or 'large'.")
        return v


# ---------------------------------------------------------------------------
# Response (what we send back — NO password fields)
# ---------------------------------------------------------------------------

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    phone_number: str | None
    profile_photo_path: str | None
    is_admin: bool

    model_config = {"from_attributes": True}
