# User schemas
# Exercise schemas (already exists)
from src.schemas.exercise import (ExerciseBase, ExerciseCreate,
                                  ExerciseResponse, ExerciseUpdate)
# ExerciseSession schemas
from src.schemas.exercise_session import (ExerciseSessionBase,
                                          ExerciseSessionCreate,
                                          ExerciseSessionResponse,
                                          ExerciseSessionUpdate,
                                          ExerciseSessionWithDetails)
# Session schemas
from src.schemas.session import (SessionBase, SessionCreate, SessionResponse,
                                 SessionUpdate, SessionWithDetails)
# Set schemas
from src.schemas.set import (SetBase, SetCreate, SetResponse, SetUpdate,
                             SetWithExerciseSession)
# Template schemas
from src.schemas.template import (TemplateBase, TemplateCreate,
                                  TemplateResponse, TemplateUpdate,
                                  TemplateWithExerciseSessions)
from src.schemas.user import (UserBase, UserCreate, UserResponse, UserUpdate,
                              UserWithSessions)

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
