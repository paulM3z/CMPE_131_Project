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
from app.models.club import Club, ClubMembership, ClubRole
from app.models.event import Event, EventAttendee, Tag
from app.services.auth_service import hash_password
from app.services.club_service import create_club, join_club, get_membership
from app.services.event_service import create_event, rsvp_event, get_or_create_tag
from app.schemas.club import ClubCreate
from app.schemas.event import EventCreate


def seed():
    create_tables()
    db = SessionLocal()

    try:
        # ------------------------------------------------------------------
        # Users
        # ------------------------------------------------------------------
        print("Creating users...")

        admin = User(
            username="admin",
            email="admin@campushub.edu",
            hashed_password=hash_password("admin1234"),
            is_admin=True,
            phone_number="+1 (408) 555-0001",
        )
        db.add(admin)

        alice = User(
            username="alice",
            email="alice@sjsu.edu",
            hashed_password=hash_password("password123"),
            phone_number="+1 (408) 555-0100",
        )
        db.add(alice)

        bob = User(
            username="bob",
            email="bob@sjsu.edu",
            hashed_password=hash_password("password123"),
            phone_number="+1 (408) 555-0200",
        )
        db.add(bob)

        db.flush()

        # Default settings for each user
        for user in [admin, alice, bob]:
            db.add(UserSettings(user_id=user.id))

        db.commit()
        db.refresh(admin)
        db.refresh(alice)
        db.refresh(bob)
        print(f"  ✓ Users created: admin, alice, bob")

        # ------------------------------------------------------------------
        # Clubs
        # ------------------------------------------------------------------
        print("Creating clubs...")

        photo_club = create_club(db, ClubCreate(
            name="SJSU Photography Club",
            description="Explore campus through a lens. Weekly photo walks and workshops.",
        ), creator=alice)

        cs_club = create_club(db, ClubCreate(
            name="Computer Science Club",
            description="Coding competitions, hackathons, and tech talks. All skill levels welcome.",
        ), creator=alice)

        hiking_club = create_club(db, ClubCreate(
            name="Bay Area Hiking Club",
            description="Weekend hikes around the Bay Area. Bring good shoes.",
            is_private=True,
        ), creator=bob)

        # Bob joins Photography and CS clubs
        join_club(db, bob, photo_club)
        join_club(db, bob, cs_club)

        # Admin joins CS club
        join_club(db, admin, cs_club)

        db.refresh(photo_club)
        db.refresh(cs_club)
        db.refresh(hiking_club)
        print(f"  ✓ Clubs created: {photo_club.name}, {cs_club.name}, {hiking_club.name}")

        # ------------------------------------------------------------------
        # Events
        # ------------------------------------------------------------------
        print("Creating events...")

        e1 = create_event(db, EventCreate(
            title="Spring Photography Walk",
            description="Join us for a guided walk around campus to practice street and nature photography. All skill levels welcome — bring any camera or phone.",
            location="Campus Entrance, SJSU",
            event_date=date(2025, 4, 20),
            event_time=time(10, 0),
            capacity=30,
            club_id=photo_club.id,
            tags=["photography", "outdoor", "beginner-friendly"],
        ), creator=alice)

        e2 = create_event(db, EventCreate(
            title="Spring Hackathon 2025",
            description="24-hour coding competition. Form teams of 2-4 and build something amazing. Prizes for top 3 teams. Food and coffee provided.",
            location="Engineering Building, Room 301",
            event_date=date(2025, 5, 3),
            event_time=time(9, 0),
            capacity=80,
            club_id=cs_club.id,
            tags=["hackathon", "coding", "competition", "networking"],
        ), creator=alice)

        e3 = create_event(db, EventCreate(
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

        e4 = create_event(db, EventCreate(
            title="Tech Industry Networking Night",
            description="Meet engineers and recruiters from local tech companies. Bring business cards and your resume. Business casual dress.",
            location="Student Union Ballroom, SJSU",
            event_date=date(2025, 5, 15),
            event_time=time(18, 0),
            capacity=150,
            tags=["networking", "career", "tech"],
        ), creator=admin)

        e5 = create_event(db, EventCreate(
            title="Campus Car Show",
            description="Show off your ride or just come enjoy the cars. Open to all students. Free entry.",
            location="South Campus Parking Lot D",
            event_date=date(2025, 6, 7),
            event_time=time(12, 0),
            tags=["car show", "outdoor", "free"],
        ), creator=bob)

        db.refresh(e1); db.refresh(e2); db.refresh(e3); db.refresh(e4); db.refresh(e5)
        print(f"  ✓ Events created: {e1.title}, {e2.title}, {e3.title}, {e4.title}, {e5.title}")

        # ------------------------------------------------------------------
        # RSVPs
        # ------------------------------------------------------------------
        print("Creating RSVPs...")
        rsvp_event(db, alice, e2)   # alice → hackathon
        rsvp_event(db, bob, e1)     # bob → photo walk
        rsvp_event(db, bob, e4)     # bob → networking night
        rsvp_event(db, admin, e4)   # admin → networking night
        rsvp_event(db, admin, e2)   # admin → hackathon
        print("  ✓ RSVPs created")

        # ------------------------------------------------------------------
        # Summary
        # ------------------------------------------------------------------
        print("\n✅ Seed complete!")
        print("\nTest accounts:")
        print("  Username: admin    Password: admin1234  (Administrator)")
        print("  Username: alice    Password: password123")
        print("  Username: bob      Password: password123")
        print("\nStart the server:  uvicorn app.main:app --reload")
        print("Open:              http://localhost:8000")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
