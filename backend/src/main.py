import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from src.logging_config import setup_logging
from src.routers import exercises, sessions, templates, users

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Progressive Overload Tracker API",
    description="""
    ## Progressive Overload Tracker API

    A comprehensive fitness tracking API designed to help users track workouts
    and achieve progressive overload through intelligent workout suggestions.

    ### Key Features

    * **Exercise Management**: Comprehensive exercise database with categories
      and equipment types
    * **Workout Sessions**: Track complete workouts with exercises, sets, reps,
      and weights
    * **Progressive Overload**: Get intelligent suggestions based on workout
      history and personal records
    * **Workout Templates**: Create and reuse workout plans
    * **Session Copying**: "Repeat last workout" workflow for easy progression
      tracking
    * **Exercise History**: View personal records, recent performance, and
      progression trends
    * **Flexible Ordering**: Organize exercises and sets in your preferred
      order

    ### Progressive Overload Workflow

    1. Create or copy a previous workout session
    2. Check exercise history for personal records and progression suggestions
    3. Complete workout with adjusted weights/reps based on suggestions
    4. Save session and track improvement over time

    ### API Organization

    * **Exercises**: Manage exercise definitions and view performance history
    * **Sessions**: Create, copy, and manage workout sessions
    * **Templates**: Create reusable workout plans
    * **Users**: Manage user accounts
    """,
    version="1.0.0",
    contact={
        "name": "Progressive Overload Tracker",
        "url": "https://github.com/gileadraab/progressive-overload-tracker",
    },
    license_info={
        "name": "MIT",
    },
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure response compression for better performance
# Compresses responses larger than 1KB with gzip encoding
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(exercises.router)
app.include_router(users.router)
app.include_router(sessions.router)
app.include_router(templates.router)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - returns a welcome message.

    Use /docs for interactive API documentation (Swagger UI).
    Use /redoc for alternative documentation (ReDoc).
    """
    return {
        "message": "Welcome to the Progressive Overload Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
async def health():
    """
    Health check endpoint for monitoring and container orchestration.

    Returns a simple status message indicating the API is running.
    """
    return {"status": "healthy", "version": "1.0.0"}
