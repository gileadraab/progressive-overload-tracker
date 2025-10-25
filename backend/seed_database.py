"""Database seed script for progressive overload tracker.

This script populates the database with sample data including:
- Sample users with hashed passwords
- Common exercises (bench press, squat, deadlift, etc.)
- Sample workout sessions
- Sample templates

Usage:
    python seed_database.py
"""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.database.database import SessionLocal, engine
from src.models import Base, CategoryEnum, EquipmentEnum, Exercise, ExerciseSession
from src.models import Session as WorkoutSession
from src.models import Set, Template, UnitEnum, User
from src.services.auth_service import hash_password


def create_sample_exercises(db: Session) -> dict[str, Exercise]:
    """Create common exercises."""
    exercises = [
        # Chest
        Exercise(
            name="Barbell Bench Press",
            category=CategoryEnum.CHEST,
            subcategory="Compound",
            equipment=EquipmentEnum.BARBELL,
        ),
        Exercise(
            name="Dumbbell Incline Press",
            category=CategoryEnum.CHEST,
            subcategory="Compound",
            equipment=EquipmentEnum.DUMBBELL,
        ),
        Exercise(
            name="Cable Fly",
            category=CategoryEnum.CHEST,
            subcategory="Isolation",
            equipment=EquipmentEnum.MACHINE,
        ),
        Exercise(
            name="Push-ups",
            category=CategoryEnum.CHEST,
            subcategory="Compound",
            equipment=EquipmentEnum.BODYWEIGHT,
        ),
        # Back
        Exercise(
            name="Barbell Deadlift",
            category=CategoryEnum.BACK,
            subcategory="Compound",
            equipment=EquipmentEnum.BARBELL,
        ),
        Exercise(
            name="Pull-ups",
            category=CategoryEnum.BACK,
            subcategory="Compound",
            equipment=EquipmentEnum.BODYWEIGHT,
        ),
        Exercise(
            name="Barbell Row",
            category=CategoryEnum.BACK,
            subcategory="Compound",
            equipment=EquipmentEnum.BARBELL,
        ),
        Exercise(
            name="Lat Pulldown",
            category=CategoryEnum.BACK,
            subcategory="Compound",
            equipment=EquipmentEnum.MACHINE,
        ),
        # Legs
        Exercise(
            name="Barbell Squat",
            category=CategoryEnum.LEGS,
            subcategory="Compound",
            equipment=EquipmentEnum.BARBELL,
        ),
        Exercise(
            name="Leg Press",
            category=CategoryEnum.LEGS,
            subcategory="Compound",
            equipment=EquipmentEnum.MACHINE,
        ),
        Exercise(
            name="Romanian Deadlift",
            category=CategoryEnum.LEGS,
            subcategory="Compound",
            equipment=EquipmentEnum.BARBELL,
        ),
        Exercise(
            name="Leg Extension",
            category=CategoryEnum.LEGS,
            subcategory="Isolation",
            equipment=EquipmentEnum.MACHINE,
        ),
        # Shoulders
        Exercise(
            name="Overhead Press",
            category=CategoryEnum.SHOULDERS,
            subcategory="Compound",
            equipment=EquipmentEnum.BARBELL,
        ),
        Exercise(
            name="Dumbbell Lateral Raise",
            category=CategoryEnum.SHOULDERS,
            subcategory="Isolation",
            equipment=EquipmentEnum.DUMBBELL,
        ),
        Exercise(
            name="Face Pulls",
            category=CategoryEnum.SHOULDERS,
            subcategory="Isolation",
            equipment=EquipmentEnum.MACHINE,
        ),
        # Arms
        Exercise(
            name="Barbell Curl",
            category=CategoryEnum.ARMS,
            subcategory="Isolation",
            equipment=EquipmentEnum.BARBELL,
        ),
        Exercise(
            name="Tricep Pushdown",
            category=CategoryEnum.ARMS,
            subcategory="Isolation",
            equipment=EquipmentEnum.MACHINE,
        ),
        Exercise(
            name="Hammer Curl",
            category=CategoryEnum.ARMS,
            subcategory="Isolation",
            equipment=EquipmentEnum.DUMBBELL,
        ),
        # Core
        Exercise(
            name="Plank",
            category=CategoryEnum.CORE,
            subcategory="Isometric",
            equipment=EquipmentEnum.BODYWEIGHT,
        ),
        Exercise(
            name="Cable Crunch",
            category=CategoryEnum.CORE,
            subcategory="Isolation",
            equipment=EquipmentEnum.MACHINE,
        ),
    ]

    db.add_all(exercises)
    db.commit()

    # Return dict for easy reference
    return {ex.name: ex for ex in exercises}


def create_sample_users(db: Session) -> list[User]:
    """Create sample users with hashed passwords."""
    users = [
        User(
            username="demo_user",
            name="Demo User",
            email="demo@example.com",
            password_hash=hash_password("demo1234"),
        ),
        User(
            username="john_doe",
            name="John Doe",
            email="john@example.com",
            password_hash=hash_password("password123"),
        ),
    ]

    db.add_all(users)
    db.commit()
    return users


def create_sample_sessions(
    db: Session, user: User, exercises: dict[str, Exercise]
) -> list[WorkoutSession]:
    """Create sample workout sessions with progressive overload."""
    sessions = []

    # Week 1: Push Day
    session1 = WorkoutSession(
        user_id=user.id,
        date=datetime.now() - timedelta(days=14),
        notes="First push day - establishing baseline",
    )
    db.add(session1)
    db.flush()

    # Bench press
    es1 = ExerciseSession(
        session_id=session1.id, exercise_id=exercises["Barbell Bench Press"].id, order=1
    )
    db.add(es1)
    db.flush()
    sets1 = [
        Set(
            exercise_session_id=es1.id, weight=60.0, reps=10, unit=UnitEnum.kg, order=1
        ),
        Set(
            exercise_session_id=es1.id, weight=60.0, reps=10, unit=UnitEnum.kg, order=2
        ),
        Set(exercise_session_id=es1.id, weight=60.0, reps=8, unit=UnitEnum.kg, order=3),
    ]
    db.add_all(sets1)

    # Incline press
    es2 = ExerciseSession(
        session_id=session1.id,
        exercise_id=exercises["Dumbbell Incline Press"].id,
        order=2,
    )
    db.add(es2)
    db.flush()
    sets2 = [
        Set(
            exercise_session_id=es2.id, weight=20.0, reps=12, unit=UnitEnum.kg, order=1
        ),
        Set(
            exercise_session_id=es2.id, weight=20.0, reps=10, unit=UnitEnum.kg, order=2
        ),
        Set(
            exercise_session_id=es2.id, weight=20.0, reps=10, unit=UnitEnum.kg, order=3
        ),
    ]
    db.add_all(sets2)

    sessions.append(session1)

    # Week 2: Push Day (Progressive Overload)
    session2 = WorkoutSession(
        user_id=user.id,
        date=datetime.now() - timedelta(days=7),
        notes="Progressive overload - increased weight",
    )
    db.add(session2)
    db.flush()

    # Bench press (increased weight)
    es3 = ExerciseSession(
        session_id=session2.id, exercise_id=exercises["Barbell Bench Press"].id, order=1
    )
    db.add(es3)
    db.flush()
    sets3 = [
        Set(
            exercise_session_id=es3.id, weight=62.5, reps=10, unit=UnitEnum.kg, order=1
        ),
        Set(
            exercise_session_id=es3.id, weight=62.5, reps=10, unit=UnitEnum.kg, order=2
        ),
        Set(exercise_session_id=es3.id, weight=62.5, reps=9, unit=UnitEnum.kg, order=3),
    ]
    db.add_all(sets3)

    sessions.append(session2)

    # Week 1: Pull Day
    session3 = WorkoutSession(
        user_id=user.id,
        date=datetime.now() - timedelta(days=12),
        notes="Back and biceps",
    )
    db.add(session3)
    db.flush()

    # Deadlift
    es4 = ExerciseSession(
        session_id=session3.id, exercise_id=exercises["Barbell Deadlift"].id, order=1
    )
    db.add(es4)
    db.flush()
    sets4 = [
        Set(
            exercise_session_id=es4.id, weight=100.0, reps=5, unit=UnitEnum.kg, order=1
        ),
        Set(
            exercise_session_id=es4.id, weight=100.0, reps=5, unit=UnitEnum.kg, order=2
        ),
        Set(
            exercise_session_id=es4.id, weight=100.0, reps=5, unit=UnitEnum.kg, order=3
        ),
    ]
    db.add_all(sets4)

    # Pull-ups
    es5 = ExerciseSession(
        session_id=session3.id, exercise_id=exercises["Pull-ups"].id, order=2
    )
    db.add(es5)
    db.flush()
    sets5 = [
        Set(exercise_session_id=es5.id, weight=0.0, reps=8, unit=UnitEnum.kg, order=1),
        Set(exercise_session_id=es5.id, weight=0.0, reps=7, unit=UnitEnum.kg, order=2),
        Set(exercise_session_id=es5.id, weight=0.0, reps=6, unit=UnitEnum.kg, order=3),
    ]
    db.add_all(sets5)

    sessions.append(session3)

    # Week 1: Leg Day
    session4 = WorkoutSession(
        user_id=user.id, date=datetime.now() - timedelta(days=10), notes="Leg day"
    )
    db.add(session4)
    db.flush()

    # Squat
    es6 = ExerciseSession(
        session_id=session4.id, exercise_id=exercises["Barbell Squat"].id, order=1
    )
    db.add(es6)
    db.flush()
    sets6 = [
        Set(exercise_session_id=es6.id, weight=80.0, reps=8, unit=UnitEnum.kg, order=1),
        Set(exercise_session_id=es6.id, weight=80.0, reps=8, unit=UnitEnum.kg, order=2),
        Set(exercise_session_id=es6.id, weight=80.0, reps=7, unit=UnitEnum.kg, order=3),
    ]
    db.add_all(sets6)

    sessions.append(session4)

    db.commit()
    return sessions


def create_sample_templates(
    db: Session, user: User, exercises: dict[str, Exercise]
) -> list[Template]:
    """Create sample workout templates."""
    templates = []

    # Push Day Template
    template1 = Template(
        name="Push Day (Chest, Shoulders, Triceps)",
        description="Compound and isolation exercises for pushing muscles",
        user_id=user.id,
        is_global=False,
    )
    db.add(template1)
    db.flush()

    # Add exercises to template
    es1 = ExerciseSession(
        template_id=template1.id,
        exercise_id=exercises["Barbell Bench Press"].id,
        order=1,
    )
    es2 = ExerciseSession(
        template_id=template1.id,
        exercise_id=exercises["Dumbbell Incline Press"].id,
        order=2,
    )
    es3 = ExerciseSession(
        template_id=template1.id, exercise_id=exercises["Overhead Press"].id, order=3
    )
    es4 = ExerciseSession(
        template_id=template1.id, exercise_id=exercises["Tricep Pushdown"].id, order=4
    )
    db.add_all([es1, es2, es3, es4])
    templates.append(template1)

    # Pull Day Template
    template2 = Template(
        name="Pull Day (Back, Biceps)",
        description="Compound and isolation exercises for pulling muscles",
        user_id=user.id,
        is_global=False,
    )
    db.add(template2)
    db.flush()

    es5 = ExerciseSession(
        template_id=template2.id, exercise_id=exercises["Barbell Deadlift"].id, order=1
    )
    es6 = ExerciseSession(
        template_id=template2.id, exercise_id=exercises["Pull-ups"].id, order=2
    )
    es7 = ExerciseSession(
        template_id=template2.id, exercise_id=exercises["Barbell Row"].id, order=3
    )
    es8 = ExerciseSession(
        template_id=template2.id, exercise_id=exercises["Barbell Curl"].id, order=4
    )
    db.add_all([es5, es6, es7, es8])
    templates.append(template2)

    # Leg Day Template
    template3 = Template(
        name="Leg Day",
        description="Complete lower body workout",
        user_id=user.id,
        is_global=False,
    )
    db.add(template3)
    db.flush()

    es9 = ExerciseSession(
        template_id=template3.id, exercise_id=exercises["Barbell Squat"].id, order=1
    )
    es10 = ExerciseSession(
        template_id=template3.id, exercise_id=exercises["Romanian Deadlift"].id, order=2
    )
    es11 = ExerciseSession(
        template_id=template3.id, exercise_id=exercises["Leg Press"].id, order=3
    )
    es12 = ExerciseSession(
        template_id=template3.id, exercise_id=exercises["Leg Extension"].id, order=4
    )
    db.add_all([es9, es10, es11, es12])
    templates.append(template3)

    # Global Beginner Template
    template4 = Template(
        name="Beginner Full Body",
        description="Full body workout for beginners (3x per week)",
        user_id=user.id,
        is_global=True,
    )
    db.add(template4)
    db.flush()

    es13 = ExerciseSession(
        template_id=template4.id, exercise_id=exercises["Barbell Squat"].id, order=1
    )
    es14 = ExerciseSession(
        template_id=template4.id,
        exercise_id=exercises["Barbell Bench Press"].id,
        order=2,
    )
    es15 = ExerciseSession(
        template_id=template4.id, exercise_id=exercises["Barbell Row"].id, order=3
    )
    es16 = ExerciseSession(
        template_id=template4.id, exercise_id=exercises["Overhead Press"].id, order=4
    )
    db.add_all([es13, es14, es15, es16])
    templates.append(template4)

    db.commit()
    return templates


def seed_database():
    """Main seeding function."""
    print("🌱 Starting database seeding...")

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if already seeded
        existing_exercises = db.query(Exercise).count()
        if existing_exercises > 0:
            print("⚠️  Database already contains data. Skipping seed.")
            return

        # Create sample data
        print("📝 Creating exercises...")
        exercises = create_sample_exercises(db)
        print(f"✅ Created {len(exercises)} exercises")

        print("👤 Creating users...")
        users = create_sample_users(db)
        print(f"✅ Created {len(users)} users")

        print("💪 Creating workout sessions...")
        sessions = create_sample_sessions(db, users[0], exercises)
        print(f"✅ Created {len(sessions)} workout sessions")

        print("📋 Creating templates...")
        templates = create_sample_templates(db, users[0], exercises)
        print(f"✅ Created {len(templates)} templates")

        print("\n🎉 Database seeding complete!")
        print("\n📊 Summary:")
        print(f"   - {len(exercises)} exercises")
        print(f"   - {len(users)} users")
        print(f"   - {len(sessions)} workout sessions")
        print(f"   - {len(templates)} templates (including 1 global)")
        print("\n🔑 Test credentials:")
        print("   Email: demo@example.com")
        print("   Password: demo1234")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
