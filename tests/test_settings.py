from pathlib import Path

from app.config import PROFILE_UPLOAD_DIR
from app.models.user import User


PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    b"\x90wS\xde"
    b"\x00\x00\x00\x0cIDAT\x08\x99c`\x00\x00\x00\x02\x00\x01"
    b"\xe2!\xbc3"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


class TestSettings:

    def test_upload_profile_photo_success(self, logged_in_client, db):
        resp = logged_in_client.post(
            "/settings/profile-photo",
            files={"profile_photo": ("avatar.png", PNG_BYTES, "image/png")},
            follow_redirects=False,
        )
        assert resp.status_code == 303

        user = db.query(User).filter(User.username == "testuser").first()
        assert user is not None
        assert user.profile_photo_path is not None
        saved_file = PROFILE_UPLOAD_DIR / Path(user.profile_photo_path).name
        assert saved_file.exists()

        saved_file.unlink(missing_ok=True)

    def test_upload_profile_photo_rejects_large_file(self, logged_in_client, db):
        resp = logged_in_client.post(
            "/settings/profile-photo",
            files={"profile_photo": ("huge.png", b"a" * (20 * 1024 * 1024 + 1), "image/png")},
            follow_redirects=True,
        )
        assert resp.status_code == 200
        assert b"exceeds the 20 mb limit" in resp.content.lower()

        user = db.query(User).filter(User.username == "testuser").first()
        assert user is not None
        assert user.profile_photo_path is None
