
from app import create_app
from extensions import db
from models import User, Resource

app = create_app()

DEMO_PASSWORD = "Relay123!"

PEOPLE = [
    (
        "student",
        "student@relay.demo",
        "Demo Student",
        "verified",
        "oscilloscope,3d-printer",
    ),
    (
        "trainready",
        "trained@relay.demo",
        "Trained Student",
        "verified",
        "laser-cutter",
    ),
    (
        "untrained",
        "untrained@relay.demo",
        "Untrained Student",
        "verified",
        "untrained",
    ),
    (
        "owner",
        "owner@relay.demo",
        "Demo Owner",
        "staff",
        "staff",
    ),
    (
        "admin",
        "admin@relay.demo",
        "Demo Admin",
        "staff",
        "staff",
    ),
]

RESOURCES = [
    (
        "Digital Oscilloscope",
        "Four-channel bench oscilloscope",
        "Electronics",
        "Engineering Lab A",
        "oscilloscope",
    ),
    (
        "3D Printer – MakerBot",
        "Fused filament fabrication printer",
        "Fabrication",
        "Innovation Workshop",
        "3d-printer",
    ),
    (
        "DSLR Camera Kit",
        "Camera, tripod and two lenses",
        "Media",
        "Media Resource Room",
        "",
    ),
    (
        "Laser Cutter",
        "60W enclosed laser cutter",
        "Fabrication",
        "Innovation Workshop",
        "laser-cutter",
    ),
    (
        "Project Robotics Kit",
        "Sensors, motors and controller boards",
        "Electronics",
        "Robotics Lab",
        "robotics",
    ),
    (
        "Microscopy Suite",
        "Compound microscope and imaging camera",
        "Laboratory",
        "Biology Lab",
        "lab-safety",
    ),
    (
        "Podcast Studio",
        "Sound booth with four microphones",
        "Media",
        "Creative Hub",
        "",
    ),
    (
        "Workshop Power Tools",
        "Drill, saw and measurement set",
        "Workshop",
        "Central Workshop",
        "workshop-safety",
    ),
    (
        "Quiet Project Room",
        "Four-seat reservable collaboration room",
        "Spaces",
        "Library Level 2",
        "",
    ),
    (
        "Soldering Station",
        "Temperature-controlled soldering bench",
        "Electronics",
        "Engineering Lab B",
        "electronics",
    ),
]


def seed_database():
    with app.app_context():
        try:
            # Create missing database tables.
            # This does not delete existing tables or records.
            db.create_all()

            print("Starting database seed...")
            print(f"Existing users: {User.query.count()}")
            print(f"Existing resources: {Resource.query.count()}")

            users_by_role = {}

            # Create missing demo accounts, but preserve existing accounts.
            for role, email, name, status, training in PEOPLE:
                user = User.query.filter_by(email=email).first()

                if user is None:
                    user = User(
                        name=name,
                        email=email,
                        role=role,
                        institution_status=status,
                        training_status=training,
                    )
                    user.set_password(DEMO_PASSWORD)
                    db.session.add(user)
                    print(f"Created demo user: {email}")
                else:
                    print(f"Preserved existing user: {email}")

                users_by_role[role] = user

            # Ensure new users have IDs before assigning resource owners.
            db.session.flush()

            # Prefer the demo owner. If unavailable, use an existing staff
            # account rather than assigning resources to an unrelated student.
            owner = users_by_role.get("owner")

            if owner is None:
                owner = User.query.filter_by(role="staff").first()

            if owner is None:
                raise RuntimeError(
                    "No staff owner is available for the demo resources."
                )

            # Add missing resources by name without duplicating existing ones.
            for name, desc, category, location, training in RESOURCES:
                resource = Resource.query.filter_by(name=name).first()

                if resource is not None:
                    print(f"Preserved existing resource: {name}")
                    continue

                resource = Resource(
                    name=name,
                    description=desc,
                    category=category,
                    location=location,
                    owner_id=owner.id,
                    availability="Mon–Fri, 09:00–18:00",
                    training_required=training,
                    active=True,
                    usage_limit=3,
                )

                db.session.add(resource)
                print(f"Added resource: {name}")

            # Commit users and resources together.
            db.session.commit()

            print("\nDatabase seeding completed successfully.")
            print(f"Total users: {User.query.count()}")
            print(f"Total resources: {Resource.query.count()}")

            active_count = Resource.query.filter_by(active=True).count()
            print(f"Active resources: {active_count}")

        except Exception:
            db.session.rollback()
            print("Database seeding failed. Changes were rolled back.")
            raise


if __name__ == "__main__":
    seed_database()
