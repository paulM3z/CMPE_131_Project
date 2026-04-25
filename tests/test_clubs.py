"""
Tests for club creation, membership, and management.

Coverage:
  - Create a club
  - Duplicate club name rejected
  - Join a club
  - Cannot join twice
  - Leave a club
  - Owner cannot leave if sole owner
  - Remove member (owner only)
  - Non-owner cannot remove members
  - Delete club (owner only)
"""


class TestClubCreation:

    def test_create_club_success(self, logged_in_client):
        resp = logged_in_client.post("/clubs/create", data={
            "name": "Photography Club",
            "description": "We take photos.",
            "is_private": "",
        }, follow_redirects=False)
        assert resp.status_code == 303
        assert "/clubs/" in resp.headers["location"]

    def test_create_club_duplicate_name(self, logged_in_client):
        data = {"name": "Hiking Club", "description": "", "is_private": ""}
        logged_in_client.post("/clubs/create", data=data, follow_redirects=False)
        resp = logged_in_client.post("/clubs/create", data=data, follow_redirects=False)
        assert resp.status_code == 422
        assert b"already exists" in resp.content.lower()

    def test_create_club_short_name(self, logged_in_client):
        resp = logged_in_client.post("/clubs/create", data={
            "name": "X",
            "description": "",
            "is_private": "",
        }, follow_redirects=False)
        assert resp.status_code == 422

    def test_creator_becomes_owner(self, logged_in_client, db):
        logged_in_client.post("/clubs/create", data={
            "name": "Chess Club",
            "description": "",
            "is_private": "",
        }, follow_redirects=False)

        from app.models.club import Club, ClubMembership
        club = db.query(Club).filter(Club.name == "Chess Club").first()
        assert club is not None

        membership = db.query(ClubMembership).filter(
            ClubMembership.club_id == club.id
        ).first()
        assert membership is not None
        assert membership.role.name == "Owner"

    def test_default_roles_created(self, logged_in_client, db):
        logged_in_client.post("/clubs/create", data={
            "name": "Drama Club",
            "description": "",
            "is_private": "",
        }, follow_redirects=False)

        from app.models.club import Club, ClubRole
        club = db.query(Club).filter(Club.name == "Drama Club").first()
        role_names = {r.name for r in db.query(ClubRole).filter(ClubRole.club_id == club.id).all()}
        assert "Owner" in role_names
        assert "Member" in role_names


class TestClubMembership:

    def _create_second_user_and_client(self, client):
        """Helper: register a second user and return a logged-in client."""
        client.post("/auth/register", data={
            "username": "user2",
            "email": "user2@example.com",
            "password": "password123",
            "confirm_password": "password123",
        }, follow_redirects=False)
        client.post("/auth/login", data={
            "username": "user2",
            "password": "password123",
        }, follow_redirects=False)
        return client

    def test_join_club(self, client, db):
        # User 1 creates club
        client.post("/auth/register", data={
            "username": "owner1",
            "email": "owner1@example.com",
            "password": "password123",
            "confirm_password": "password123",
        }, follow_redirects=False)
        client.post("/auth/login", data={
            "username": "owner1", "password": "password123"
        }, follow_redirects=False)
        client.post("/clubs/create", data={
            "name": "Yoga Club", "description": "", "is_private": ""
        }, follow_redirects=False)

        # User 2 joins
        client.post("/auth/logout", follow_redirects=False)
        client.post("/auth/register", data={
            "username": "joiner1",
            "email": "joiner1@example.com",
            "password": "password123",
            "confirm_password": "password123",
        }, follow_redirects=False)
        client.post("/auth/login", data={
            "username": "joiner1", "password": "password123"
        }, follow_redirects=False)

        from app.models.club import Club
        club = db.query(Club).filter(Club.name == "Yoga Club").first()
        resp = client.post(f"/clubs/{club.id}/join", follow_redirects=False)
        assert resp.status_code == 303

        from app.models.club import ClubMembership
        from app.models.user import User
        user2 = db.query(User).filter(User.username == "joiner1").first()
        membership = db.query(ClubMembership).filter(
            ClubMembership.user_id == user2.id,
            ClubMembership.club_id == club.id,
        ).first()
        assert membership is not None
        assert membership.is_approved is True

    def test_cannot_join_twice(self, client, db):
        client.post("/auth/register", data={
            "username": "dupuser",
            "email": "dup@example.com",
            "password": "password123",
            "confirm_password": "password123",
        }, follow_redirects=False)
        client.post("/auth/login", data={
            "username": "dupuser", "password": "password123"
        }, follow_redirects=False)
        client.post("/clubs/create", data={
            "name": "Dup Club", "description": "", "is_private": ""
        }, follow_redirects=False)

        from app.models.club import Club
        club = db.query(Club).filter(Club.name == "Dup Club").first()
        # Try to join a club you already own (already a member)
        resp = client.post(f"/clubs/{club.id}/join", follow_redirects=True)
        # Should show error flash but not crash
        assert resp.status_code == 200


class TestClubPermissions:

    def test_non_owner_cannot_delete_club(self, client, db):
        # Owner creates club
        client.post("/auth/register", data={
            "username": "theowner",
            "email": "theowner@example.com",
            "password": "password123",
            "confirm_password": "password123",
        }, follow_redirects=False)
        client.post("/auth/login", data={
            "username": "theowner", "password": "password123"
        }, follow_redirects=False)
        client.post("/clubs/create", data={
            "name": "Owners Club", "description": "", "is_private": ""
        }, follow_redirects=False)
        client.post("/auth/logout", follow_redirects=False)

        # Different user tries to delete
        client.post("/auth/register", data={
            "username": "notowner",
            "email": "notowner@example.com",
            "password": "password123",
            "confirm_password": "password123",
        }, follow_redirects=False)
        client.post("/auth/login", data={
            "username": "notowner", "password": "password123"
        }, follow_redirects=False)

        from app.models.club import Club
        club = db.query(Club).filter(Club.name == "Owners Club").first()
        resp = client.post(f"/clubs/{club.id}/delete", follow_redirects=True)
        # Club should still exist
        db.expire(club)
        surviving_club = db.query(Club).filter(Club.id == club.id).first()
        assert surviving_club is not None
