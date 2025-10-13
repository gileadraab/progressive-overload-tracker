from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy import String, cast as sql_cast, desc, select
from sqlalchemy.orm import Session

from src.models.enums import CategoryEnum, EquipmentEnum
from src.models.exercise import Exercise
from src.models.exercise_session import ExerciseSession
from src.models.session import Session as WorkoutSession
from src.models.set import Set
from src.schemas.exercise import ExerciseCreate, ExerciseUpdate


def get_exercises(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[CategoryEnum] = None,
    equipment: Optional[EquipmentEnum] = None,
) -> List[Exercise]:
    """
    Get all exercises from the database with optional filtering.

    Args:
        db: The database session.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        category: Optional category filter.
        equipment: Optional equipment filter.

    Returns:
        A list of exercises.
    """
    query = select(Exercise)

    if category:
        query = query.where(Exercise.category == category)
    if equipment:
        query = query.where(Exercise.equipment == equipment)

    result = db.execute(query.offset(skip).limit(limit))
    return list(result.scalars().all())


def search_exercises(query: str, db: Session) -> List[Exercise]:
    """
    Search exercises by name, category, or subcategory.

    Args:
        query: The search term.
        db: The database session.

    Returns:
        A list of exercises matching the search query.
    """
    search = f"%{query}%"
    result = db.execute(
        select(Exercise).where(
            (Exercise.name.ilike(search))
            | (sql_cast(Exercise.category, String).ilike(search))
            | (Exercise.subcategory.ilike(search))
        )
    )
    return list(result.scalars().all())


def get_exercise(exercise_id: int, db: Session) -> Exercise:
    """
    Get a single exercise by its ID.

    Args:
        exercise_id: The ID of the exercise to retrieve.
        db: The database session.

    Raises:
        HTTPException: If the exercise with the given ID is not found.

    Returns:
        The retrieved exercise.
    """
    exercise = db.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found",
        )
    return exercise


def create_exercise(exercise: ExerciseCreate, db: Session) -> Exercise:
    """
    Create a new exercise in the database.

    Args:
        exercise: The exercise data to create.
        db: The database session.

    Returns:
        The newly created exercise.
    """
    db_exercise = Exercise(**exercise.model_dump())
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


def update_exercise(
    exercise_id: int, exercise: ExerciseUpdate, db: Session
) -> Exercise:
    """
    Update an existing exercise in the database.

    Args:
        exercise_id: The ID of the exercise to update.
        exercise: The exercise data to update.
        db: The database session.

    Raises:
        HTTPException: If the exercise with the given ID is not found.

    Returns:
        The updated exercise.
    """
    db_exercise = db.get(Exercise, exercise_id)
    if not db_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found",
        )

    update_data = exercise.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_exercise, field, value)

    db.commit()
    db.refresh(db_exercise)
    return db_exercise


def delete_exercise(exercise_id: int, db: Session) -> None:
    """
    Delete an exercise from the database.

    Args:
        exercise_id: The ID of the exercise to delete.
        db: The database session.

    Raises:
        HTTPException: If the exercise with the given ID is not found.
    """
    exercise = db.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found",
        )
    db.delete(exercise)
    db.commit()


def calculate_one_rep_max(weight: float, reps: int) -> float:
    """
    Calculate estimated 1 rep max using Brzycki formula.

    Args:
        weight: The weight lifted.
        reps: The number of repetitions performed.

    Returns:
        Estimated 1 rep max.
    """
    if reps == 1:
        return weight
    if reps >= 37:
        # Formula breaks down for high reps, just return weight
        return weight
    return weight * (36 / (37 - reps))


def calculate_progression(
    recent_sets: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    Calculate progressive overload suggestion based on recent performance.

    Args:
        recent_sets: List of sets from the most recent session.

    Returns:
        Dictionary with recommended weight, reps, and rationale, or None if no data.
    """
    if not recent_sets:
        return None

    # Find the best set by total volume (weight × reps)
    best_set = max(recent_sets, key=lambda s: s["weight"] * s["reps"])

    # Progressive overload: add weight if they hit target reps (8+)
    if best_set["reps"] >= 8:
        # Unit-aware increment: 2.5kg for kg, 1 stack for stacks
        increment = 2.5 if best_set["unit"] == "kg" else 1
        unit_label = "kg" if best_set["unit"] == "kg" else "stack"

        return {
            "recommended_weight": best_set["weight"] + increment,
            "recommended_reps": best_set["reps"],
            "rationale": f"You hit target reps - increase weight by {increment} {unit_label}",
        }
    else:
        return {
            "recommended_weight": best_set["weight"],
            "recommended_reps": best_set["reps"] + 1,
            "rationale": "Keep weight, aim for more reps",
        }


def get_exercise_history(exercise_id: int, user_id: int, db: Session) -> Dict[str, Any]:
    """
    Get historical performance data for an exercise for a specific user.

    Args:
        exercise_id: The ID of the exercise.
        user_id: The ID of the user.
        db: The database session.

    Returns:
        Dictionary containing last performed, personal best, recent sessions,
        and progression suggestion.
    """
    # Verify exercise exists
    exercise = db.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found",
        )

    # Get all sets for this exercise by this user, ordered by date (newest first)
    # Secondary sort by ID ensures deterministic ordering when dates are equal
    query = (
        select(Set, WorkoutSession.date, WorkoutSession.id)
        .join(ExerciseSession, Set.exercise_session_id == ExerciseSession.id)
        .join(WorkoutSession, ExerciseSession.session_id == WorkoutSession.id)
        .where(ExerciseSession.exercise_id == exercise_id)
        .where(WorkoutSession.user_id == user_id)
        .where(WorkoutSession.id.isnot(None))  # Only actual sessions, not templates
        .order_by(desc(WorkoutSession.date), desc(WorkoutSession.id))
    )

    results = db.execute(query).all()

    if not results:
        return {
            "exercise_id": exercise_id,
            "last_performed": None,
            "personal_best": None,
            "recent_sessions": [],
            "progression_suggestion": None,
        }

    # Convert to list of dicts for easier processing
    all_sets = [
        {
            "weight": set_obj.weight,
            "reps": set_obj.reps,
            "unit": set_obj.unit.value,
            "date": date,
            "session_id": session_id,
        }
        for set_obj, date, session_id in results
    ]

    # Find personal best (highest estimated 1RM)
    best_set = max(
        all_sets, key=lambda s: calculate_one_rep_max(s["weight"], s["reps"])
    )

    # Get last performed (most recent session)
    last_session_date = results[0][1]
    last_session_id = results[0][2]
    last_session_sets = [
        {"weight": s.weight, "reps": s.reps, "unit": s.unit.value}
        for s, date, sid in results
        if sid == last_session_id
    ]

    # Get recent session summaries (last 5 sessions)
    session_summaries = {}
    for set_obj, date, session_id in results:
        if session_id not in session_summaries:
            session_summaries[session_id] = {
                "session_id": session_id,
                "date": date.isoformat() if isinstance(date, datetime) else str(date),
                "sets": [],
            }
        session_summaries[session_id]["sets"].append(
            {"weight": set_obj.weight, "reps": set_obj.reps, "unit": set_obj.unit.value}
        )

    recent_sessions = list(session_summaries.values())[:5]
    for session in recent_sessions:
        best = max(session["sets"], key=lambda s: s["weight"] * s["reps"])
        session["best_set"] = best

    # Calculate progression suggestion
    suggestion = calculate_progression(last_session_sets)

    # Calculate total volume for last session
    total_volume = sum(s["weight"] * s["reps"] for s in last_session_sets)
    max_weight = max(s["weight"] for s in last_session_sets)

    return {
        "exercise_id": exercise_id,
        "last_performed": {
            "session_id": last_session_id,
            "date": (
                last_session_date.isoformat()
                if isinstance(last_session_date, datetime)
                else str(last_session_date)
            ),
            "sets": last_session_sets,
            "max_weight": max_weight,
            "total_volume": total_volume,
        },
        "personal_best": {
            "weight": best_set["weight"],
            "reps": best_set["reps"],
            "date": (
                best_set["date"].isoformat()
                if isinstance(best_set["date"], datetime)
                else str(best_set["date"])
            ),
            "session_id": best_set["session_id"],
            "estimated_1rm": calculate_one_rep_max(
                best_set["weight"], best_set["reps"]
            ),
        },
        "recent_sessions": recent_sessions,
        "progression_suggestion": suggestion,
    }
