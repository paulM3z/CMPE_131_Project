"""
Database seed script — populates the DB with sample data for development.

Run after creating the database:
  python seed.py

Creates:
  - 3 users (1 admin, 2 students)
  - 3 clubs
  - 5 events with tags
  - Memberships and RSVPs
"""
import sys
from datetime import date, time

# Ensure the project root is in Python path
sys.path.insert(0, ".")

from app.database import SessionLocal, create_tables
from app.models.user import User, UserSettings
from app.models.club import Club
from app.models.event import Event
from app.services.auth_service import hash_password
from app.services.club_service import create_club, join_club, get_membership
from app.services.event_service import create_event, rsvp_event, get_rsvp
from app.schemas.club import ClubCreate
from app.schemas.event import EventCreate


def get_or_create_user(db, *, username, email, password, is_admin=False, phone_number=None):
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.email = email
        user.hashed_password = hash_password(password)
        user.is_admin = is_admin
        user.phone_number = phone_number
    else:
        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            is_admin=is_admin,
            phone_number=phone_number,
        )
        db.add(user)
        db.flush()

    if not user.settings:
        db.add(UserSettings(user_id=user.id))
    return user


def get_or_create_club(db, data, creator):
    club = db.query(Club).filter(Club.name == data.name).first()
    if club:
        club.description = data.description
        club.is_private = data.is_private
        return club
    return create_club(db, data, creator=creator)


def ensure_membership(db, user, club):
    if not get_membership(db, user.id, club.id):
        join_club(db, user, club)


def get_or_create_event(db, data, creator):
    event = db.query(Event).filter(
        Event.title == data.title,
        Event.event_date == data.event_date,
    ).first()
    if event:
        event.description = data.description
        event.location = data.location
        event.map_query = data.map_query
        event.event_time = data.event_time
        event.capacity = data.capacity
        event.is_private = data.is_private
        event.club_id = data.club_id
        return event
    return create_event(db, data, creator=creator)


def ensure_rsvp(db, user, event):
    if not get_rsvp(db, user.id, event.id):
        rsvp_event(db, user, event)


def seed():
    create_tables()
    db = SessionLocal()

    try:
        # ------------------------------------------------------------------
        # Users
        # ------------------------------------------------------------------
        print("Creating users...")

        admin = get_or_create_user(
            db,
            username="admin",
            email="admin@campushub.edu",
            password="admin1234",
            is_admin=True,
            phone_number="+1 (408) 555-0001",
        )

        alice = get_or_create_user(
            db,
            username="alice",
            email="alice@sjsu.edu",
            password="password123",
            phone_number="+1 (408) 555-0100",
        )

        bob = get_or_create_user(
            db,
            username="bob",
            email="bob@sjsu.edu",
            password="password123",
            phone_number="+1 (408) 555-0200",
        )

        db.commit()
        db.refresh(admin)
        db.refresh(alice)
        db.refresh(bob)
        print("  OK Users ready: admin, alice, bob")

        # ------------------------------------------------------------------
        # Clubs
        # ------------------------------------------------------------------
        print("Creating clubs...")

        photo_club = get_or_create_club(db, ClubCreate(
            name="SJSU Photography Club",
            description="Explore campus through a lens. Weekly photo walks and workshops.",
        ), creator=alice)

        cs_club = get_or_create_club(db, ClubCreate(
            name="Computer Science Club",
            description="Coding competitions, hackathons, and tech talks. All skill levels welcome.",
        ), creator=alice)

        hiking_club = get_or_create_club(db, ClubCreate(
            name="Bay Area Hiking Club",
            description="Weekend hikes around the Bay Area. Bring good shoes.",
            is_private=True,
        ), creator=bob)

        # Bob joins Photography and CS clubs
        ensure_membership(db, bob, photo_club)
        ensure_membership(db, bob, cs_club)

        # Admin joins CS club
        ensure_membership(db, admin, cs_club)

        db.refresh(photo_club)
        db.refresh(cs_club)
        db.refresh(hiking_club)
        print(f"  OK Clubs ready: {photo_club.name}, {cs_club.name}, {hiking_club.name}")

        # ------------------------------------------------------------------
        # Events
        # ------------------------------------------------------------------
        print("Creating events...")

        e1 = get_or_create_event(db, EventCreate(
            title="Spring Photography Walk",
            description="Join us for a guided walk around campus to practice street and nature photography. All skill levels welcome — bring any camera or phone.",
            location="Campus Entrance, SJSU",
            event_date=date(2025, 4, 20),
            event_time=time(10, 0),
            capacity=30,
            club_id=photo_club.id,
            tags=["photography", "outdoor", "beginner-friendly"],
        ), creator=alice)

        e2 = get_or_create_event(db, EventCreate(
            title="Spring Hackathon 2025",
            description="24-hour coding competition. Form teams of 2-4 and build something amazing. Prizes for top 3 teams. Food and coffee provided.",
            location="Engineering Building, Room 301",
            event_date=date(2025, 5, 3),
            event_time=time(9, 0),
            capacity=80,
            club_id=cs_club.id,
            tags=["hackathon", "coding", "competition", "networking"],
        ), creator=alice)

        e3 = get_or_create_event(db, EventCreate(
            title="Mt. Tamalpais Day Hike",
            description="Moderate 8-mile loop with stunning views of the Bay. Meet at the Pantoll trailhead. Bring water, snacks, and sunscreen.",
            location="Mt. Tamalpais State Park",
            event_date=date(2025, 4, 27),
            event_time=time(8, 30),
            capacity=20,
            is_private=True,
            club_id=hiking_club.id,
            tags=["hiking", "outdoor", "nature"],
        ), creator=bob)

        e4 = get_or_create_event(db, EventCreate(
            title="Tech Industry Networking Night",
            description="Meet engineers and recruiters from local tech companies. Bring business cards and your resume. Business casual dress.",
            location="Student Union Ballroom, SJSU",
            event_date=date(2025, 5, 15),
            event_time=time(18, 0),
            capacity=150,
            tags=["networking", "career", "tech"],
        ), creator=admin)

        e5 = get_or_create_event(db, EventCreate(
            title="Campus Car Show",
            description="Show off your ride or just come enjoy the cars. Open to all students. Free entry.",
            location="South Campus Parking Lot D",
            event_date=date(2025, 6, 7),
            event_time=time(12, 0),
            tags=["car show", "outdoor", "free"],
        ), creator=bob)

        db.refresh(e1); db.refresh(e2); db.refresh(e3); db.refresh(e4); db.refresh(e5)
        print(f"  OK Events ready: {e1.title}, {e2.title}, {e3.title}, {e4.title}, {e5.title}")

        # ------------------------------------------------------------------
        # RSVPs
        # ------------------------------------------------------------------
        print("Creating RSVPs...")
        ensure_rsvp(db, alice, e2)   # alice -> hackathon
        ensure_rsvp(db, bob, e1)     # bob -> photo walk
        ensure_rsvp(db, bob, e4)     # bob -> networking night
        ensure_rsvp(db, admin, e4)   # admin -> networking night
        ensure_rsvp(db, admin, e2)   # admin -> hackathon
        print("  OK RSVPs ready")

        # ------------------------------------------------------------------
        # Summary
        # ------------------------------------------------------------------
        print("\nSeed complete!")
        print("\nTest accounts:")
        print("  Username: admin    Password: admin1234  (Administrator)")
        print("  Username: alice    Password: password123")
        print("  Username: bob      Password: password123")
        print("\nStart the server:  uvicorn app.main:app --reload")
        print("Open:              http://localhost:8000")

    except Exception as e:
        db.rollback()
        print(f"\nSeed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
