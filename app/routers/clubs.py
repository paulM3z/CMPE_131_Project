"""
Club routes: list, create, view detail, join/leave, manage members.

All routes require authentication (uses get_current_user dependency).
"""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.club import ClubCreate
from app.services import club_service

router = APIRouter(prefix="/clubs", tags=["clubs"])
templates = Jinja2Templates(directory="app/templates")


def _flash(request: Request, message: str, category: str = "info") -> None:
    request.session["flash"] = {"message": message, "category": category}


# ---------------------------------------------------------------------------
# Club list
# ---------------------------------------------------------------------------

@router.get("", response_class=HTMLResponse)
async def club_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    clubs = club_service.list_clubs(db)
    user_club_ids = {m.club_id for m in current_user.club_memberships if m.is_approved}
    return templates.TemplateResponse(
        request,
        "clubs/list.html",
        {
            "clubs": clubs,
            "current_user": current_user,
            "user_club_ids": user_club_ids,
        },
    )


# ---------------------------------------------------------------------------
# Create club
# ---------------------------------------------------------------------------

@router.get("/create", response_class=HTMLResponse)
async def create_club_get(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request,
        "clubs/create.html",
        {"current_user": current_user},
    )


@router.post("/create", response_class=HTMLResponse)
async def create_club_post(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    is_private: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    errors: list[str] = []

    try:
        data = ClubCreate(
            name=name,
            description=description or None,
            is_private=is_private,
        )
    except ValidationError as e:
        for err in e.errors():
            errors.append(err["msg"].replace("Value error, ", ""))
        return templates.TemplateResponse(
            request,
            "clubs/create.html",
            {
                "current_user": current_user,
                "errors": errors,
                "form": {"name": name, "description": description},
            },
            status_code=422,
        )

    if club_service.get_club_by_name(db, data.name):
        errors.append("A club with that name already exists.")
        return templates.TemplateResponse(
            request,
            "clubs/create.html",
            {
                "current_user": current_user,
                "errors": errors,
                "form": {"name": name, "description": description},
            },
            status_code=422,
        )

    club = club_service.create_club(db, data, current_user)
    _flash(request, f"Club '{club.name}' created successfully!", "success")
    return RedirectResponse(url=f"/clubs/{club.id}", status_code=303)


# ---------------------------------------------------------------------------
# Club detail
# ---------------------------------------------------------------------------

@router.get("/{club_id}", response_class=HTMLResponse)
async def club_detail(
    club_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club = club_service.get_club_by_id(db, club_id)
    if not club:
        _flash(request, "Club not found.", "error")
        return RedirectResponse(url="/clubs", status_code=302)

    membership = club_service.get_membership(db, current_user.id, club_id)
    is_owner = club_service.is_club_owner(db, current_user.id, club_id)
    can_manage = club_service.can_manage_members(db, current_user.id, club_id)

    # Load all memberships with user info for the member list
    from app.models.club import ClubMembership
    memberships = (
        db.query(ClubMembership)
        .filter(ClubMembership.club_id == club_id, ClubMembership.is_approved == True)
        .all()
    )

    return templates.TemplateResponse(
        request,
        "clubs/detail.html",
        {
            "club": club,
            "current_user": current_user,
            "membership": membership,
            "is_owner": is_owner,
            "can_manage": can_manage,
            "memberships": memberships,
        },
    )


# ---------------------------------------------------------------------------
# Join / Leave
# ---------------------------------------------------------------------------

@router.post("/{club_id}/join")
async def join_club(
    club_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club = club_service.get_club_by_id(db, club_id)
    if not club:
        _flash(request, "Club not found.", "error")
        return RedirectResponse(url="/clubs", status_code=303)

    try:
        club_service.join_club(db, current_user, club)
        msg = (
            "Join request submitted — waiting for approval."
            if club.is_private
            else f"You've joined {club.name}!"
        )
        _flash(request, msg, "success")
    except ValueError as e:
        _flash(request, str(e), "error")

    return RedirectResponse(url=f"/clubs/{club_id}", status_code=303)


@router.post("/{club_id}/leave")
async def leave_club(
    club_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club = club_service.get_club_by_id(db, club_id)
    if not club:
        _flash(request, "Club not found.", "error")
        return RedirectResponse(url="/clubs", status_code=303)

    try:
        club_service.leave_club(db, current_user, club)
        _flash(request, f"You've left {club.name}.", "info")
    except ValueError as e:
        _flash(request, str(e), "error")

    return RedirectResponse(url=f"/clubs/{club_id}", status_code=303)


# ---------------------------------------------------------------------------
# Remove a member (owner/manager only)
# ---------------------------------------------------------------------------

@router.post("/{club_id}/members/{target_user_id}/remove")
async def remove_member(
    club_id: int,
    target_user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Authorization check
    if not club_service.can_manage_members(db, current_user.id, club_id) and not current_user.is_admin:
        _flash(request, "You don't have permission to remove members.", "error")
        return RedirectResponse(url=f"/clubs/{club_id}", status_code=303)

    # Can't remove yourself through this route — use /leave instead
    if target_user_id == current_user.id:
        _flash(request, "Use the Leave button to remove yourself.", "error")
        return RedirectResponse(url=f"/clubs/{club_id}", status_code=303)

    club = club_service.get_club_by_id(db, club_id)
    if not club:
        return RedirectResponse(url="/clubs", status_code=303)

    try:
        club_service.remove_member(db, target_user_id, club)
        _flash(request, "Member removed.", "success")
    except ValueError as e:
        _flash(request, str(e), "error")

    return RedirectResponse(url=f"/clubs/{club_id}", status_code=303)


# ---------------------------------------------------------------------------
# Delete club (owner only)
# ---------------------------------------------------------------------------

@router.post("/{club_id}/delete")
async def delete_club(
    club_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    club = club_service.get_club_by_id(db, club_id)
    if not club:
        return RedirectResponse(url="/clubs", status_code=303)

    if not club_service.is_club_owner(db, current_user.id, club_id) and not current_user.is_admin:
        _flash(request, "Only the club owner can delete this club.", "error")
        return RedirectResponse(url=f"/clubs/{club_id}", status_code=303)

    name = club.name
    club_service.delete_club(db, club)
    _flash(request, f"Club '{name}' has been deleted.", "info")
    return RedirectResponse(url="/clubs", status_code=303)
