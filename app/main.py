"""
FastAPI application entry point.

Startup order:
  1. Create DB tables (if they don't exist)
  2. Mount static files
  3. Register session middleware (for flash messages)
  4. Register global exception handlers
  5. Include all routers

To run:
  uvicorn app.main:app --reload --port 8000
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import EVENT_REMINDER_CHECK_SECONDS, PROFILE_UPLOAD_DIR, SESSION_SECRET_KEY
from app.database import SessionLocal, create_tables
from app.dependencies import ForbiddenException, NotAuthenticatedException
from app.routers import auth, clubs, events, settings, users

# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    PROFILE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    reminder_task = asyncio.create_task(_event_reminder_loop())
    yield
    reminder_task.cancel()
    try:
        await reminder_task
    except asyncio.CancelledError:
        pass


async def _event_reminder_loop() -> None:
    from app.services.reminder_service import send_due_event_reminders

    while True:
        try:
            with SessionLocal() as db:
                send_due_event_reminders(db)
        except Exception as exc:
            print(f"[REMINDER ERROR] Failed to process reminders: {exc}")
        await asyncio.sleep(EVENT_REMINDER_CHECK_SECONDS)


# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Campus Event & Club Management System",
    description="Manage campus clubs and events.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

# Session middleware must be added BEFORE routers so flash messages work
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    session_cookie="session",
    max_age=60 * 60 * 24,  # 24 hours
    https_only=False,      # Set True in production with HTTPS
    same_site="lax",
)

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(NotAuthenticatedException)
async def not_authenticated_handler(request: Request, exc: NotAuthenticatedException):
    """Redirect unauthenticated users to the login page."""
    next_url = request.url.path
    return RedirectResponse(url=f"/auth/login?next={next_url}", status_code=302)


@app.exception_handler(ForbiddenException)
async def forbidden_handler(request: Request, exc: ForbiddenException):
    """Redirect to dashboard with an error flash on permission denied."""
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="app/templates")
    request.session["flash"] = {"message": exc.message, "category": "error"}
    return RedirectResponse(url="/", status_code=302)


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(clubs.router)
app.include_router(events.router)
app.include_router(settings.router)
