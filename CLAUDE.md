# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Progressive Overload Tracker API built with FastAPI and SQLAlchemy. The application tracks workout sessions, exercises, sets, and user progress for strength training. It uses PostgreSQL as the primary database with Alembic for migrations.

## Database Architecture

The core domain models form a hierarchical structure:
- **User**: Individual users with username/name
- **Session**: Workout sessions belonging to users  
- **Exercise**: Exercise definitions with category/equipment enums
- **ExerciseSession**: Junction linking exercises to sessions/templates
- **Set**: Individual sets with weight/reps/unit data
- **Template**: Reusable workout templates

Key relationships:
- User → Sessions (one-to-many with cascade delete)
- Session → ExerciseSession → Sets (hierarchical with cascade delete)
- Exercise → ExerciseSession (many-to-many through junction)
- Template → ExerciseSession (optional template association)

## Development Commands

### Database Operations
```bash
# Start PostgreSQL with Docker
docker-compose up -d

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

### Application
```bash
# Install dependencies  
pip install -r requirements.txt

# Run development server
uvicorn src.main:app --reload

# Run tests
pytest

# Code quality tools
black .
isort .
flake8 .
mypy src/
```

## Configuration

- Environment variables loaded via `src/config.py` using pydantic-settings
- Database URL configured through `DATABASE_URL` environment variable
- Copy `.env.example` to `.env` for local development
- Alembic configured to use the same database URL via `alembic.ini`

## Code Structure

- `src/models/`: SQLAlchemy domain models with proper relationships
- `src/models/enums.py`: String enums for category, equipment, and units
- `src/database/database.py`: Database session management and Base class
- `src/config.py`: Pydantic settings with environment variable loading
- `src/schemas/`: Pydantic schemas for API serialization (basic structure exists)
- `src/routers/`: FastAPI route handlers (empty, to be implemented)
- `migrations/`: Alembic migration files with proper model imports

## Development Notes

- Uses SQLAlchemy 2.0+ syntax with declarative base
- Pydantic V2 for configuration and future API schemas
- String-based enums for better API compatibility
- Proper foreign key relationships with cascade deletion
- Migration environment properly imports all models for autogenerate support
- FastAPI app currently has minimal setup with welcome endpoint