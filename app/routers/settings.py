"""
Settings routes: account preferences and profile updates.

All changes go through the settings page at /settings.
Each form submits to a dedicated endpoint to keep validation clean.
"""
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.config import MAX_PROFILE_PHOTO_BYTES, PROFILE_UPLOAD_DIR, PROFILE_UPLOAD_WEB_PATH
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import (
    UserUpdateEmail,
    UserUpdatePassword,
    UserUpdatePhone,
    UserUpdateSettings,
    UserUpdateUsername,
)
from app.services import user_service

router = APIRouter(prefix="/settings", tags=["settings"])
templates = Jinja2Templates(directory="app/templates")

SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "de": "German",
    "zh": "中文",
    "ja": "日本語",
    "ko": "한국어",
    "pt": "Português",
    "ar": "العربية",
}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


def _flash(request: Request, message: str, category: str = "info") -> None:
    request.session["flash"] = {"message": message, "category": category}


async def _save_profile_photo(upload: UploadFile) -> str:
    filename = upload.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS or upload.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError("Invalid image type. Please upload JPG, PNG, GIF, or WEBP.")

    PROFILE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = PROFILE_UPLOAD_DIR / f"{uuid4().hex}{extension}"
    total_size = 0
    try:
        with file_path.open("wb") as output:
            while True:
                chunk = await upload.read(1024 * 1024)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > MAX_PROFILE_PHOTO_BYTES:
                    raise ValueError("Upload file exceeds the 20 MB limit.")
                output.write(chunk)
    except Exception:
        file_path.unlink(missing_ok=True)
        raise
    finally:
        await upload.close()

    return f"{PROFILE_UPLOAD_WEB_PATH}/{file_path.name}"


@router.get("", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request,
        "settings/index.html",
        {
            "current_user": current_user,
            "languages": SUPPORTED_LANGUAGES,
        },
    )


# ---------------------------------------------------------------------------
# Change username
# ---------------------------------------------------------------------------

@router.post("/username", response_class=HTMLResponse)
async def update_username(
    request: Request,
    username: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    errors: list[str] = []
    try:
        data = UserUpdateUsername(username=username.strip())
    except ValidationError as e:
        for err in e.errors():
            errors.append(err["msg"].replace("Value error, ", ""))

    if not errors:
        existing = user_service.get_user_by_username(db, data.username)
        if existing and existing.id != current_user.id:
            errors.append("That username is already taken.")

    if errors:
        _flash(request, errors[0], "error")
        return RedirectResponse(url="/settings", status_code=303)

    user_service.update_username(db, current_user, data.username)
    _flash(request, "Username updated successfully.", "success")
    return RedirectResponse(url="/settings", status_code=303)


# ---------------------------------------------------------------------------
# Change email
# ---------------------------------------------------------------------------

@router.post("/email", response_class=HTMLResponse)
async def update_email(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    errors: list[str] = []
    try:
        data = UserUpdateEmail(email=email)
    except ValidationError as e:
        for err in e.errors():
            errors.append(err["msg"].replace("Value error, ", ""))

    if not errors:
        existing = user_service.get_user_by_email(db, email)
        if existing and existing.id != current_user.id:
            errors.append("That email is already in use.")

    if errors:
        _flash(request, errors[0], "error")
        return RedirectResponse(url="/settings", status_code=303)

    user_service.update_email(db, current_user, data.email)
    _flash(request, "Email updated successfully.", "success")
    return RedirectResponse(url="/settings", status_code=303)


# ---------------------------------------------------------------------------
# Change password
# ---------------------------------------------------------------------------

@router.post("/password", response_class=HTMLResponse)
async def update_password(
    request: Request,
    current_password: str | None = Form(None),
    new_password: str | None = Form(None),
    confirm_password: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    errors: list[str] = []
    current_password = (current_password or "").strip()
    new_password = (new_password or "").strip()
    confirm_password = (confirm_password or "").strip()

    if not current_password:
        errors.append("Current password is required.")
    if not new_password:
        errors.append("New password is required.")
    if not confirm_password:
        errors.append("Confirm password is required.")

    data = None
    if not errors:
        try:
            data = UserUpdatePassword(
                current_password=current_password,
                new_password=new_password,
                confirm_password=confirm_password,
            )
        except ValidationError as e:
            for err in e.errors():
                errors.append(err["msg"].replace("Value error, ", ""))

    if not errors and data is not None:
        if not data.passwords_match():
            errors.append("New passwords do not match.")

    if not errors and data is not None:
        from app.services.auth_service import verify_password
        if not verify_password(current_password, current_user.hashed_password):
            errors.append("Current password is incorrect.")

    if errors:
        _flash(request, errors[0], "error")
        return RedirectResponse(url="/settings", status_code=303)

    user_service.update_password(db, current_user, data.new_password)
    _flash(request, "Password updated. Please log in again.", "success")
    # Invalidate the current session by clearing the cookie
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response


# ---------------------------------------------------------------------------
# Change phone number
# ---------------------------------------------------------------------------

@router.post("/phone", response_class=HTMLResponse)
async def update_phone(
    request: Request,
    phone_number: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    errors: list[str] = []
    try:
        data = UserUpdatePhone(phone_number=phone_number.strip() or None)
    except ValidationError as e:
        for err in e.errors():
            errors.append(err["msg"].replace("Value error, ", ""))

    if errors:
        _flash(request, errors[0], "error")
        return RedirectResponse(url="/settings", status_code=303)

    user_service.update_phone(db, current_user, data.phone_number)
    _flash(request, "Phone number updated.", "success")
    return RedirectResponse(url="/settings", status_code=303)


@router.post("/profile-photo", response_class=HTMLResponse)
async def update_profile_photo(
    request: Request,
    profile_photo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not profile_photo or not profile_photo.filename:
        _flash(request, "Please choose an image file to upload.", "error")
        return RedirectResponse(url="/settings", status_code=303)

    try:
        saved_path = await _save_profile_photo(profile_photo)
    except ValueError as exc:
        _flash(request, str(exc), "error")
        return RedirectResponse(url="/settings", status_code=303)
    except OSError:
        _flash(request, "We couldn't save that image. Please try again.", "error")
        return RedirectResponse(url="/settings", status_code=303)

    # Remove the old photo from disk before saving the new path
    if current_user.profile_photo_path:
        old_file = PROFILE_UPLOAD_DIR / Path(current_user.profile_photo_path).name
        old_file.unlink(missing_ok=True)

    user_service.update_profile_photo(db, current_user, saved_path)
    _flash(request, "Profile photo updated.", "success")
    return RedirectResponse(url="/settings", status_code=303)


# ---------------------------------------------------------------------------
# Change UI preferences (language, theme, text size)
# ---------------------------------------------------------------------------

@router.post("/preferences", response_class=HTMLResponse)
async def update_preferences(
    request: Request,
    language: str = Form("en"),
    theme: str = Form("light"),
    text_size: str = Form("medium"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    errors: list[str] = []
    try:
        data = UserUpdateSettings(language=language, theme=theme, text_size=text_size)
    except ValidationError as e:
        for err in e.errors():
            errors.append(err["msg"].replace("Value error, ", ""))

    if errors:
        _flash(request, errors[0], "error")
        return RedirectResponse(url="/settings", status_code=303)

    user_service.update_user_settings(db, current_user, data)
    _flash(request, "Preferences saved.", "success")
    return RedirectResponse(url="/settings", status_code=303)
