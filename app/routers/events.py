"""
Event routes: list, create, view, edit, delete, RSVP.
"""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.event import EventCreate
from app.config import MAX_EVENT_CAPACITY
from app.services import event_service
from app.services.email_service import send_rsvp_cancellation, send_rsvp_confirmation

router = APIRouter(prefix="/events", tags=["events"])
templates = Jinja2Templates(directory="app/templates")


def _flash(request: Request, message: str, category: str = "info") -> None:
    request.session["flash"] = {"message": message, "category": category}


def _parse_optional_int(value: str, field_name: str) -> int | None:
    value = value.strip()
    if not value:
        return None
    if not value.isdigit():
        raise ValueError(f"{field_name} must be a whole number.")
    if len(value) > len(str(MAX_EVENT_CAPACITY)):
        raise ValueError(f"{field_name} must be {MAX_EVENT_CAPACITY:,} or less.")
    return int(value)


# ---------------------------------------------------------------------------
# Event list
# ---------------------------------------------------------------------------

@router.get("", response_class=HTMLResponse)
async def event_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import date
    events = event_service.list_events(db, upcoming_only=False)
    # Build set of event IDs the user has RSVP'd to for the template
    rsvp_event_ids = {a.event_id for a in current_user.event_attendances}
    return templates.TemplateResponse(
        request,
        "events/list.html",
        {
            "events": events,
            "current_user": current_user,
            "rsvp_event_ids": rsvp_event_ids,
            "today": date.today(),
        },
    )


# ---------------------------------------------------------------------------
# Create event
# ---------------------------------------------------------------------------

@router.get("/create", response_class=HTMLResponse)
async def create_event_get(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.club_service import get_user_clubs
    user_clubs = get_user_clubs(db, current_user.id)
    return templates.TemplateResponse(
        request,
        "events/create.html",
        {"current_user": current_user, "user_clubs": user_clubs},
    )


@router.post("/create", response_class=HTMLResponse)
async def create_event_post(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    location: str = Form(""),
    map_query: str = Form(""),
    event_date: str = Form(...),
    event_time: str = Form(""),
    capacity: str = Form(""),
    is_private: bool = Form(False),
    club_id: str = Form(""),
    tags: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.club_service import get_user_clubs

    errors: list[str] = []
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    try:
        data = EventCreate(
            title=title,
            description=description or None,
            location=location or None,
            map_query=map_query or None,
            event_date=event_date,
            event_time=event_time or None,
            capacity=_parse_optional_int(capacity, "Capacity"),
            is_private=is_private,
            club_id=_parse_optional_int(club_id, "Hosting club"),
            tags=tag_list,
        )
    except (ValidationError, ValueError) as e:
        if isinstance(e, ValidationError):
            for err in e.errors():
                errors.append(err["msg"].replace("Value error, ", ""))
        else:
            errors.append(str(e))

        user_clubs = get_user_clubs(db, current_user.id)
        return templates.TemplateResponse(
            request,
            "events/create.html",
            {
                "current_user": current_user,
                "user_clubs": user_clubs,
                "errors": errors,
                "form": {
                    "title": title, "description": description,
                    "location": location, "map_query": map_query, "event_date": event_date,
                    "event_time": event_time, "capacity": capacity,
                    "tags": tags, "club_id": club_id, "is_private": is_private,
                },
            },
            status_code=422,
        )

    event = event_service.create_event(db, data, current_user)
    _flash(request, f"Event '{event.title}' created!", "success")
    return RedirectResponse(url=f"/events/{event.id}", status_code=303)


# ---------------------------------------------------------------------------
# Event detail
# ---------------------------------------------------------------------------

@router.get("/{event_id}", response_class=HTMLResponse)
async def event_detail(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = event_service.get_event_by_id(db, event_id)
    if not event:
        _flash(request, "Event not found.", "error")
        return RedirectResponse(url="/events", status_code=302)

    rsvp = event_service.get_rsvp(db, current_user.id, event_id)
    can_edit = event_service.can_edit_event(current_user, event)

    return templates.TemplateResponse(
        request,
        "events/detail.html",
        {
            "event": event,
            "current_user": current_user,
            "rsvp": rsvp,
            "can_edit": can_edit,
        },
    )


# ---------------------------------------------------------------------------
# Edit event
# ---------------------------------------------------------------------------

@router.get("/{event_id}/edit", response_class=HTMLResponse)
async def edit_event_get(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = event_service.get_event_by_id(db, event_id)
    if not event:
        return RedirectResponse(url="/events", status_code=302)
    if not event_service.can_edit_event(current_user, event):
        _flash(request, "You don't have permission to edit this event.", "error")
        return RedirectResponse(url=f"/events/{event_id}", status_code=302)

    from app.services.club_service import get_user_clubs
    user_clubs = get_user_clubs(db, current_user.id)
    existing_tags = ",".join(t.name for t in event.tags)

    return templates.TemplateResponse(
        request,
        "events/create.html",
        {
            "current_user": current_user,
            "user_clubs": user_clubs,
            "edit_mode": True,
            "event": event,
            "form": {
                "title": event.title,
                "description": event.description or "",
                "location": event.location or "",
                "map_query": event.map_query or "",
                "event_date": str(event.event_date),
                "event_time": str(event.event_time) if event.event_time else "",
                "capacity": str(event.capacity) if event.capacity else "",
                "tags": existing_tags,
                "club_id": str(event.club_id) if event.club_id else "",
                "is_private": event.is_private,
            },
        },
    )


@router.post("/{event_id}/edit", response_class=HTMLResponse)
async def edit_event_post(
    event_id: int,
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    location: str = Form(""),
    map_query: str = Form(""),
    event_date: str = Form(...),
    event_time: str = Form(""),
    capacity: str = Form(""),
    is_private: bool = Form(False),
    club_id: str = Form(""),
    tags: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = event_service.get_event_by_id(db, event_id)
    if not event:
        return RedirectResponse(url="/events", status_code=303)
    if not event_service.can_edit_event(current_user, event):
        _flash(request, "Permission denied.", "error")
        return RedirectResponse(url=f"/events/{event_id}", status_code=303)

    errors: list[str] = []
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    try:
        from app.schemas.event import EventUpdate
        data = EventUpdate(
            title=title,
            description=description or None,
            location=location or None,
            map_query=map_query or None,
            event_date=event_date,
            event_time=event_time or None,
            capacity=_parse_optional_int(capacity, "Capacity"),
            is_private=is_private,
            club_id=_parse_optional_int(club_id, "Hosting club"),
            tags=tag_list,
        )
    except (ValidationError, ValueError) as e:
        if isinstance(e, ValidationError):
            for err in e.errors():
                errors.append(err["msg"].replace("Value error, ", ""))
        else:
            errors.append(str(e))
        from app.services.club_service import get_user_clubs
        return templates.TemplateResponse(
            request,
            "events/create.html",
            {
                "current_user": current_user,
                "user_clubs": get_user_clubs(db, current_user.id),
                "errors": errors,
                "edit_mode": True,
                "event": event,
                "form": {"title": title, "description": description, "location": location,
                         "map_query": map_query,
                         "event_date": event_date, "event_time": event_time,
                         "capacity": capacity, "tags": tags,
                         "club_id": club_id, "is_private": is_private},
            },
            status_code=422,
        )

    event_service.update_event(db, event, data)
    _flash(request, "Event updated.", "success")
    return RedirectResponse(url=f"/events/{event_id}", status_code=303)


# ---------------------------------------------------------------------------
# Delete event
# ---------------------------------------------------------------------------

@router.post("/{event_id}/delete")
async def delete_event(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = event_service.get_event_by_id(db, event_id)
    if not event:
        return RedirectResponse(url="/events", status_code=303)
    if not event_service.can_edit_event(current_user, event):
        _flash(request, "Permission denied.", "error")
        return RedirectResponse(url=f"/events/{event_id}", status_code=303)

    title = event.title
    event_service.delete_event(db, event)
    _flash(request, f"Event '{title}' deleted.", "info")
    return RedirectResponse(url="/events", status_code=303)


# ---------------------------------------------------------------------------
# RSVP
# ---------------------------------------------------------------------------

@router.post("/{event_id}/rsvp")
async def rsvp(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = event_service.get_event_by_id(db, event_id)
    if not event:
        _flash(request, "Event not found.", "error")
        return RedirectResponse(url="/events", status_code=303)

    try:
        event_service.rsvp_event(db, current_user, event)
        _flash(request, "You're going! RSVP confirmed.", "success")
        send_rsvp_confirmation(
            to_email=current_user.email,
            username=current_user.username,
            event_title=event.title,
            event_date=str(event.event_date),
            event_location=event.location,
        )
    except ValueError as e:
        _flash(request, str(e), "error")

    return RedirectResponse(url=f"/events/{event_id}", status_code=303)


@router.post("/{event_id}/cancel-rsvp")
async def cancel_rsvp(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = event_service.get_event_by_id(db, event_id)
    if not event:
        return RedirectResponse(url="/events", status_code=303)

    try:
        event_service.cancel_rsvp(db, current_user, event)
        _flash(request, "RSVP cancelled.", "info")
        send_rsvp_cancellation(
            to_email=current_user.email,
            username=current_user.username,
            event_title=event.title,
        )
    except ValueError as e:
        _flash(request, str(e), "error")

    return RedirectResponse(url=f"/events/{event_id}", status_code=303)
