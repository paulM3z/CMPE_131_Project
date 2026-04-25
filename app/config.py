"""
Application configuration loaded from environment variables.
Copy .env.example to .env and update values before running.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Database connection string — defaults to local SQLite for easy setup
DATABASE_URL: str = os.getenv(
    "DATABASE_URL", "sqlite:///./campus_events.db"
)

# JWT signing key — MUST be changed in production
SECRET_KEY: str = os.getenv(
    "SECRET_KEY", "changeme-please-use-a-real-secret-in-production-32-chars-min"
)

# Session middleware signing key — MUST be changed in production
SESSION_SECRET_KEY: str = os.getenv(
    "SESSION_SECRET_KEY", "changeme-session-secret-also-needs-to-be-strong"
)

# JWT algorithm — HS256 is fine for symmetric signing
ALGORITHM: str = "HS256"

# How long login tokens last (minutes)
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
)

BASE_DIR = Path(__file__).resolve().parent.parent
PROFILE_UPLOAD_DIR = Path(
    os.getenv("PROFILE_UPLOAD_DIR", str(BASE_DIR / "app" / "static" / "uploads" / "profile_photos"))
)
PROFILE_UPLOAD_WEB_PATH = "/static/uploads/profile_photos"
MAX_PROFILE_PHOTO_BYTES: int = 20 * 1024 * 1024
