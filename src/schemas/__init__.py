# User schemas
from src.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithSessions
)

# Session schemas
from src.schemas.session import (
    SessionBase,
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionWithDetails
)

# Set schemas
from src.schemas.set import (
    SetBase,
    SetCreate,
    SetUpdate,
    SetResponse,
    SetWithExerciseSession
)

# Template schemas
from src.schemas.template import (
    TemplateBase,
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateWithExerciseSessions
)

# ExerciseSession schemas
from src.schemas.exercise_session import (
    ExerciseSessionBase,
    ExerciseSessionCreate,
    ExerciseSessionUpdate,
    ExerciseSessionResponse,
    ExerciseSessionWithDetails
)

# Exercise schemas (already exists)
from src.schemas.exercise import (
    ExerciseBase,
    ExerciseCreate,
    ExerciseUpdate,
    ExerciseResponse
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserWithSessions",

    # Session schemas
    "SessionBase",
    "SessionCreate",
    "SessionUpdate",
    "SessionResponse",
    "SessionWithDetails",

    # Set schemas
    "SetBase",
    "SetCreate",
    "SetUpdate",
    "SetResponse",
    "SetWithExerciseSession",

    # Template schemas
    "TemplateBase",
    "TemplateCreate",
    "TemplateUpdate",
    "TemplateResponse",
    "TemplateWithExerciseSessions",

    # ExerciseSession schemas
    "ExerciseSessionBase",
    "ExerciseSessionCreate",
    "ExerciseSessionUpdate",
    "ExerciseSessionResponse",
    "ExerciseSessionWithDetails",

    # Exercise schemas
    "ExerciseBase",
    "ExerciseCreate",
    "ExerciseUpdate",
    "ExerciseResponse",
]

# Rebuild models to resolve forward references
# This must happen after all schemas are imported
SessionWithDetails.model_rebuild()
TemplateWithExerciseSessions.model_rebuild()
ExerciseSessionWithDetails.model_rebuild()
UserWithSessions.model_rebuild()
SetWithExerciseSession.model_rebuild()