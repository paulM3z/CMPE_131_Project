"""
Auth routes: register, login, logout.

Flow:
  GET  /auth/register  → show registration form
  POST /auth/register  → validate input, create user, redirect to login
  GET  /auth/login     → show login form
  POST /auth/login     → authenticate, set JWT cookie, redirect to dashboard
  POST /auth/logout    → clear JWT cookie, redirect to login
"""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import create_access_token
from app.services.user_service import (
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_by_username,
)

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


def _flash(request: Request, message: str, category: str = "info") -> None:
    request.session["flash"] = {"message": message, "category": category}


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    # Already logged in → go to dashboard
    if request.cookies.get("access_token"):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(request, "auth/register.html")


@router.post("/register", response_class=HTMLResponse)
async def register_post(
    request: Request,
    username: str | None = Form(None),
    email: str | None = Form(None),
    password: str | None = Form(None),
    confirm_password: str | None = Form(None),
    phone_number: str = Form(""),
    db: Session = Depends(get_db),
):
    errors: list[str] = []
    username = (username or "").strip()
    email = (email or "").strip()
    password = (password or "").strip()
    confirm_password = (confirm_password or "").strip()

    if not username:
        errors.append("Username is required.")
    if not email:
        errors.append("Email is required.")
    if not password:
        errors.append("Password is required.")
    if not confirm_password:
        errors.append("Confirm password is required.")

    # Basic confirm-password check before Pydantic validation
    if password and confirm_password and password != confirm_password:
        errors.append("Passwords do not match.")

    data = None
    if not errors:
        try:
            data = UserCreate(
                username=username,
                email=email,
                password=password,
                phone_number=phone_number or None,
            )
        except ValidationError as e:
            for err in e.errors():
                errors.append(err["msg"].replace("Value error, ", ""))

    if not errors and data is not None:
        if get_user_by_username(db, data.username):
            errors.append("That username is already taken.")
        if get_user_by_email(db, data.email):
            errors.append("An account with that email already exists.")

    if errors:
        return templates.TemplateResponse(
            request,
            "auth/register.html",
            {
                "errors": errors,
                "form": {"username": username, "email": email, "phone_number": phone_number},
            },
            status_code=422,
        )

    create_user(db, data)
    _flash(request, "Account created! Please log in.", "success")
    return RedirectResponse(url="/auth/login", status_code=303)


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    if request.cookies.get("access_token"):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(request, "auth/login.html")


@router.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    username: str | None = Form(None),
    password: str | None = Form(None),
    db: Session = Depends(get_db),
):
    username = (username or "").strip()
    password = (password or "").strip()

    if not username or not password:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {
                "error": "Invalid username or password.",
                "form": {"username": username},
            },
            status_code=401,
        )

    try:
        login_data = UserLogin(username=username, password=password)
    except ValidationError:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {
                "error": "Invalid username or password.",
                "form": {"username": username},
            },
            status_code=401,
        )

    user = authenticate_user(db, login_data.username, login_data.password)

    if not user:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {
                "error": "Invalid username or password.",
                "form": {"username": username},
            },
            status_code=401,
        )

    token = create_access_token(user.id)
    raw_next = request.query_params.get("next", "/")
    # Only allow relative paths — reject anything starting with "//" or containing a scheme
    next_url = raw_next if (raw_next.startswith("/") and not raw_next.startswith("//")) else "/"

    response = RedirectResponse(url=next_url, status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,    # not accessible via JS — protects against XSS
        samesite="lax",   # protects against CSRF for most cases
        secure=False,     # set True in production with HTTPS
        max_age=60 * 60 * 24,  # 24 hours
    )
    return response


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

@router.post("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response
