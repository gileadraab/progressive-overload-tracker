# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Database Operations
- Start PostgreSQL database: `docker-compose up -d`
- Run database migrations: `alembic upgrade head`
- Create new migration: `alembic revision --autogenerate -m "description"`

### Running the Application
- Start FastAPI server: `uvicorn src.main:app --reload`
- The API will be available at http://localhost:8000

### Code Quality
- Format code: `black .`
- Sort imports: `isort .` 
- Lint code: `flake8 .`
- Type checking: `mypy src/`
- Run tests: `pytest`

### Environment Setup
- Copy `.env.example` to `.env` and configure DATABASE_URL
- Install dependencies: `pip install -r requirements.txt`

## Architecture

This is a FastAPI-based progressive overload fitness tracking application with the following structure:

### Core Models (SQLAlchemy with PostgreSQL)
- **User**: User accounts with username and optional display name
- **Session**: Workout sessions linked to users with timestamps
- **Exercise**: Exercise definitions with categories (chest, back, legs, shoulders, arms, core) and equipment types (machine, dumbbell, barbell, bodyweight, kettlebell, resistance_band)
- **ExerciseSession**: Links exercises to sessions (many-to-many relationship)
- **Set**: Individual exercise sets with weight, reps, and units (kg/stacks)
- **Template**: Reusable workout templates

### Key Relationships
- Users have many Sessions (cascade delete)
- Sessions contain multiple ExerciseSession records
- ExerciseSession links Exercise and Session
- Sets belong to both Session and ExerciseSession
- Enums are used for consistent categorization (CategoryEnum, EquipmentEnum, UnitEnum)

### Database Management
- Uses Alembic for schema migrations
- PostgreSQL as primary database with SQLite fallback
- Database configuration via environment variables in `src/config.py`
- Connection management in `src/database/database.py`

### Project Structure
- `src/models/`: SQLAlchemy model definitions
- `src/schemas/`: Pydantic schemas for API serialization  
- `src/routers/`: FastAPI route handlers (currently empty)
- `src/services/`: Business logic layer (currently empty)
- `migrations/`: Alembic database migration files

The application follows a clean architecture pattern with separate layers for models, schemas, routing, and services.