"""
Tests for event creation, editing, deletion, and RSVP logic.

Coverage:
  - Create event (standalone)
  - Create event (linked to club)
  - Invalid event data rejected
  - Edit event (creator only)
  - Delete event (creator only)
  - RSVP to an event
  - Cancel RSVP
  - Cannot RSVP twice
  - Cannot RSVP when at capacity
  - Non-creator cannot edit/delete event
"""
import pytest


def _register_and_login(client, username, email):
    client.post("/auth/register", data={
        "username": username,
        "email": email,
        "password": "password123",
        "confirm_password": "password123",
    }, follow_redirects=False)
    client.post("/auth/login", data={
        "username": username, "password": "password123",
    }, follow_redirects=False)


class TestEventCreation:

    def test_create_event_success(self, logged_in_client):
        resp = logged_in_client.post("/events/create", data={
            "title": "Spring Bash",
            "description": "A big party",
            "location": "Main Quad",
            "event_date": "2025-05-01",
            "event_time": "18:00",
            "capacity": "100",
            "is_private": "",
            "club_id": "",
            "tags": "music, outdoor",
        }, follow_redirects=False)
        assert resp.status_code == 303
        assert "/events/" in resp.headers["location"]

    def test_create_event_minimal(self, logged_in_client):
        """Only title and date are required."""
        resp = logged_in_client.post("/events/create", data={
            "title": "Quick Meetup",
            "event_date": "2025-06-15",
            "description": "",
            "location": "",
            "event_time": "",
            "capacity": "",
            "is_private": "",
            "club_id": "",
            "tags": "",
        }, follow_redirects=False)
        assert resp.status_code == 303

    def test_create_event_no_title(self, logged_in_client):
        resp = logged_in_client.post("/events/create", data={
            "title": "",
            "event_date": "2025-06-01",
        }, follow_redirects=False)
        assert resp.status_code == 422

    def test_create_event_short_title(self, logged_in_client):
        resp = logged_in_client.post("/events/create", data={
            "title": "Hi",
            "event_date": "2025-06-01",
            "description": "", "location": "", "event_time": "",
            "capacity": "", "is_private": "", "club_id": "", "tags": "",
        }, follow_redirects=False)
        assert resp.status_code == 422

    def test_create_event_stores_tags(self, logged_in_client, db):
        logged_in_client.post("/events/create", data={
            "title": "Tag Test Event",
            "event_date": "2025-07-04",
            "description": "", "location": "", "event_time": "",
            "capacity": "", "is_private": "", "club_id": "",
            "tags": "music, networking",
        }, follow_redirects=False)

        from app.models.event import Event
        event = db.query(Event).filter(Event.title == "Tag Test Event").first()
        assert event is not None
        tag_names = {t.name for t in event.tags}
        assert "music" in tag_names
        assert "networking" in tag_names

    def test_create_event_stores_google_maps_query(self, logged_in_client, db):
        logged_in_client.post("/events/create", data={
            "title": "Mapped Event",
            "event_date": "2025-07-10",
            "description": "",
            "location": "Student Union",
            "map_query": "San Jose State University Student Union",
            "event_time": "",
            "capacity": "",
            "is_private": "",
            "club_id": "",
            "tags": "",
        }, follow_redirects=False)

        from app.models.event import Event
        event = db.query(Event).filter(Event.title == "Mapped Event").first()
        assert event is not None
        assert event.map_query == "San Jose State University Student Union"
        assert "google.com/maps" in event.google_maps_url

    def test_capacity_can_be_50000(self, logged_in_client, db):
        resp = logged_in_client.post("/events/create", data={
            "title": "Large Capacity Event",
            "event_date": "2025-07-12",
            "description": "",
            "location": "",
            "map_query": "",
            "event_time": "",
            "capacity": "50000",
            "is_private": "",
            "club_id": "",
            "tags": "",
        }, follow_redirects=False)
        assert resp.status_code == 303

        from app.models.event import Event
        event = db.query(Event).filter(Event.title == "Large Capacity Event").first()
        assert event is not None
        assert event.capacity == 50000

    def test_capacity_over_50000_rejected(self, logged_in_client):
        resp = logged_in_client.post("/events/create", data={
            "title": "Too Large Event",
            "event_date": "2025-07-12",
            "description": "",
            "location": "",
            "map_query": "",
            "event_time": "",
            "capacity": "50001",
            "is_private": "",
            "club_id": "",
            "tags": "",
        }, follow_redirects=False)
        assert resp.status_code == 422

    def test_private_club_event_hidden_from_non_members(self, client, db):
        _register_and_login(client, "clubhost", "clubhost@example.com")
        client.post("/clubs/create", data={
            "name": "Private Events Club",
            "description": "",
            "is_private": "",
        }, follow_redirects=False)

        from app.models.club import Club
        club = db.query(Club).filter(Club.name == "Private Events Club").first()
        client.post("/events/create", data={
            "title": "Members Only Mixer",
            "event_date": "2025-07-13",
            "description": "Only approved club members should see this.",
            "location": "",
            "map_query": "",
            "event_time": "",
            "capacity": "",
            "is_private": "true",
            "club_id": str(club.id),
            "tags": "",
        }, follow_redirects=False)
        client.post("/auth/logout", follow_redirects=False)

        _register_and_login(client, "outsider", "outsider@example.com")
        resp = client.get("/events")
        assert resp.status_code == 200
        assert b"Members Only Mixer" not in resp.content

    def test_event_hype_meter_properties(self, logged_in_client, db):
        logged_in_client.post("/events/create", data={
            "title": "Hype Event",
            "event_date": "2025-07-11",
            "description": "",
            "location": "",
            "map_query": "",
            "event_time": "",
            "capacity": "10",
            "is_private": "",
            "club_id": "",
            "tags": "",
        }, follow_redirects=False)

        from app.models.event import Event, EventAttendee
        from app.models.user import User
        from app.services.auth_service import hash_password
        event = db.query(Event).filter(Event.title == "Hype Event").first()
        assert event is not None

        for idx in range(2, 8):
            user = User(
                username=f"hypeuser{idx}",
                email=f"hypeuser{idx}@example.com",
                hashed_password=hash_password("password123"),
            )
            db.add(user)
            db.flush()
            db.add(EventAttendee(event_id=event.id, user_id=user.id))
        db.commit()
        db.refresh(event)

        assert event.has_limited_capacity is True
        assert event.fill_percentage == 60
        assert event.spots_filled_text == "6/10 spots filled"
        assert "Getting Popular" in event.hype_status["label"]

        extra_user = User(
            username="hypeuser8",
            email="hypeuser8@example.com",
            hashed_password=hash_password("password123"),
        )
        db.add(extra_user)
        db.flush()
        db.add(EventAttendee(event_id=event.id, user_id=extra_user.id))
        db.commit()
        db.refresh(event)

        assert event.fill_percentage == 70
        assert "Hype Building!" in event.hype_status["label"]

    def test_creator_can_edit_own_event(self, logged_in_client, db):
        logged_in_client.post("/events/create", data={
            "title": "Editable Event",
            "event_date": "2025-08-01",
            "description": "", "location": "", "event_time": "",
            "capacity": "", "is_private": "", "club_id": "", "tags": "",
        }, follow_redirects=False)

        from app.models.event import Event
        event = db.query(Event).filter(Event.title == "Editable Event").first()

        resp = logged_in_client.post(f"/events/{event.id}/edit", data={
            "title": "Updated Event Title",
            "event_date": "2025-08-02",
            "description": "", "location": "", "event_time": "",
            "capacity": "", "is_private": "", "club_id": "", "tags": "",
        }, follow_redirects=False)
        assert resp.status_code == 303

        db.expire(event)
        updated = db.query(Event).filter(Event.id == event.id).first()
        assert updated.title == "Updated Event Title"

    def test_non_creator_cannot_edit_event(self, client, db):
        # User 1 creates event
        _register_and_login(client, "creator1", "creator1@example.com")
        client.post("/events/create", data={
            "title": "Owners Event",
            "event_date": "2025-09-01",
            "description": "", "location": "", "event_time": "",
            "capacity": "", "is_private": "", "club_id": "", "tags": "",
        }, follow_redirects=False)
        client.post("/auth/logout", follow_redirects=False)

        # User 2 tries to edit
        _register_and_login(client, "intruder1", "intruder1@example.com")
        from app.models.event import Event
        event = db.query(Event).filter(Event.title == "Owners Event").first()

        resp = client.post(f"/events/{event.id}/edit", data={
            "title": "Hacked Title",
            "event_date": "2025-09-01",
            "description": "", "location": "", "event_time": "",
            "capacity": "", "is_private": "", "club_id": "", "tags": "",
        }, follow_redirects=True)
        assert resp.status_code == 200
        # Title should NOT have changed
        db.expire(event)
        unchanged = db.query(Event).filter(Event.id == event.id).first()
        assert unchanged.title == "Owners Event"


class TestEventRSVP:

    def test_rsvp_success(self, logged_in_client, db):
        logged_in_client.post("/events/create", data={
            "title": "RSVP Test Event",
            "event_date": "2025-10-01",
            "description": "", "location": "", "event_time": "",
            "capacity": "", "is_private": "", "club_id": "", "tags": "",
        }, follow_redirects=False)

        from app.models.event import Event
        event = db.query(Event).filter(Event.title == "RSVP Test Event").first()
        resp = logged_in_client.post(f"/events/{event.id}/rsvp", follow_redirects=False)
        assert resp.status_code == 303

        from app.models.event import EventAttendee
        attendee = db.query(EventAttendee).filter(EventAttendee.event_id == event.id).first()
        assert attendee is not None

    def test_cannot_rsvp_twice(self, logged_in_client, db):
        logged_in_client.post("/events/create", data={
            "title": "Double RSVP Event",
            "event_date": "2025-11-01",
            "description": "", "location": "", "event_time": "",
            "capacity": "", "is_private": "", "club_id": "", "tags": "",
        }, follow_redirects=False)

        from app.models.event import Event
        event = db.query(Event).filter(Event.title == "Double RSVP Event").first()
        logged_in_client.post(f"/events/{event.id}/rsvp", follow_redirects=False)
        # Second RSVP should silently show error flash, not crash
        resp = logged_in_client.post(f"/events/{event.id}/rsvp", follow_redirects=True)
        assert resp.status_code == 200

        from app.models.event import EventAttendee
        count = db.query(EventAttendee).filter(EventAttendee.event_id == event.id).count()
        assert count == 1  # still only one record

    def test_capacity_limit_enforced(self, client, db):
        # Creator creates event with capacity 1
        _register_and_login(client, "host1", "host1@example.com")
        client.post("/events/create", data={
            "title": "Tiny Event",
            "event_date": "2025-12-01",
            "description": "", "location": "", "event_time": "",
            "capacity": "1", "is_private": "", "club_id": "", "tags": "",
        }, follow_redirects=False)
        from app.models.event import Event
        event = db.query(Event).filter(Event.title == "Tiny Event").first()

        # User 2 RSVPs — fills the 1 spot
        client.post("/auth/logout", follow_redirects=False)
        _register_and_login(client, "rsvp1", "rsvp1@example.com")
        client.post(f"/events/{event.id}/rsvp", follow_redirects=False)

        # User 3 tries to RSVP — should be blocked
        client.post("/auth/logout", follow_redirects=False)
        _register_and_login(client, "rsvp2", "rsvp2@example.com")
        resp = client.post(f"/events/{event.id}/rsvp", follow_redirects=True)
        assert resp.status_code == 200  # Shows error flash, doesn't crash

        from app.models.event import EventAttendee
        count = db.query(EventAttendee).filter(EventAttendee.event_id == event.id).count()
        assert count == 1  # Only rsvp1 got in

    def test_cancel_rsvp(self, logged_in_client, db):
        logged_in_client.post("/events/create", data={
            "title": "Cancel RSVP Event",
            "event_date": "2025-12-15",
            "description": "", "location": "", "event_time": "",
            "capacity": "", "is_private": "", "club_id": "", "tags": "",
        }, follow_redirects=False)

        from app.models.event import Event
        event = db.query(Event).filter(Event.title == "Cancel RSVP Event").first()
        logged_in_client.post(f"/events/{event.id}/rsvp", follow_redirects=False)
        resp = logged_in_client.post(f"/events/{event.id}/cancel-rsvp", follow_redirects=False)
        assert resp.status_code == 303

        from app.models.event import EventAttendee
        count = db.query(EventAttendee).filter(EventAttendee.event_id == event.id).count()
        assert count == 0

    def test_leaving_club_removes_club_event_rsvps(self, client, db):
        _register_and_login(client, "clubowner", "clubowner@example.com")
        client.post("/clubs/create", data={
            "name": "RSVP Cleanup Club",
            "description": "",
            "is_private": "",
        }, follow_redirects=False)

        from app.models.club import Club
        club = db.query(Club).filter(Club.name == "RSVP Cleanup Club").first()
        client.post("/events/create", data={
            "title": "Cleanup Club Event",
            "event_date": "2025-12-20",
            "description": "",
            "location": "",
            "map_query": "",
            "event_time": "",
            "capacity": "",
            "is_private": "true",
            "club_id": str(club.id),
            "tags": "",
        }, follow_redirects=False)
        client.post("/auth/logout", follow_redirects=False)

        _register_and_login(client, "clubmember", "clubmember@example.com")
        client.post(f"/clubs/{club.id}/join", follow_redirects=False)

        from app.models.event import Event, EventAttendee
        event = db.query(Event).filter(Event.title == "Cleanup Club Event").first()
        client.post(f"/events/{event.id}/rsvp", follow_redirects=False)
        assert db.query(EventAttendee).filter(
            EventAttendee.event_id == event.id
        ).count() == 1

        client.post(f"/clubs/{club.id}/leave", follow_redirects=False)
        assert db.query(EventAttendee).filter(
            EventAttendee.event_id == event.id
        ).count() == 0
