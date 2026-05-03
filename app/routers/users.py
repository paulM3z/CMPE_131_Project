"""
User-facing routes: dashboard.
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.club_service import get_user_clubs
from app.services.event_service import list_events

router = APIRouter(tags=["users"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Main dashboard: show the user's clubs and upcoming events."""
    from datetime import date
    user_clubs = get_user_clubs(db, current_user.id)
    upcoming_events = list_events(db, limit=10, upcoming_only=True, current_user=current_user)
    rsvp_event_ids = {a.event_id for a in current_user.event_attendances}

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "current_user": current_user,
            "user_clubs": user_clubs,
            "upcoming_events": upcoming_events,
            "rsvp_event_ids": rsvp_event_ids,
            "today": date.today(),
        },
    )
