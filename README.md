# Progressive Overload Tracker

A FastAPI-based REST API for tracking strength training workouts and progressive overload. This application helps users log exercises, sets, reps, and weights to monitor their training progress over time.

## Features

- User management and workout session tracking
- Exercise library with categorization (chest, back, legs, etc.)
- Equipment tracking (barbell, dumbbell, machine, etc.)
- Set logging with weight, reps, and units
- Workout templates for recurring routines
- Database-driven with proper relational modeling

## Tech Stack

- **Backend**: FastAPI (Python 3.9+)
- **Database**: PostgreSQL with SQLAlchemy 2.0 ORM
- **Migrations**: Alembic
- **Validation**: Pydantic V2
- **Development**: Docker Compose for local database
- **Code Quality**: Black, isort, flake8, mypy, pytest

## Architecture

The application uses a clean domain model architecture:

```
User → Session → ExerciseSession → Set
              ↘ Exercise ↗
Template → ExerciseSession
```

- **Users** have multiple workout **Sessions**
- **Sessions** contain **ExerciseSessions** (exercises performed in that session)
- **ExerciseSessions** link **Exercises** with **Sets** (weight/reps data)
- **Templates** allow reusable workout routines

## Development Setup

### Prerequisites
- Python 3.9+
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd progressive-overload-tracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred database credentials
   ```

4. **Start PostgreSQL database**
   ```bash
   docker-compose up -d
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   uvicorn src.main:app --reload
   ```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

### Development Commands

```bash
# Run tests
pytest

# Code formatting and linting
black .
isort .
flake8 .
mypy src/

# Database operations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Stop database
docker-compose down
```

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive OpenAPI documentation.
