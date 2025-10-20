# Progressive Overload Tracker

A comprehensive fitness tracking application with intelligent workout suggestions and progressive overload tracking.

## Features

### Core Functionality
- **Exercise Management**: Comprehensive exercise database with categories (chest, back, legs, shoulders, arms, core) and equipment types
- **Workout Sessions**: Track complete workouts with exercises, sets, reps, and weights
- **Progressive Overload Tracking**: Get intelligent suggestions based on workout history and personal records
- **Workout Templates**: Create and reuse workout plans
- **Session Copying**: "Repeat last workout" workflow for easy progression tracking
- **Exercise History**: View personal records, recent performance, and progression trends
- **Flexible Ordering**: Organize exercises and sets in your preferred order

### Progressive Overload Features
The API calculates and provides:
- Personal best (highest estimated 1RM using Brzycki formula)
- Last performed workout details
- Recent session summaries (last 5 workouts)
- Smart progression suggestions (when to increase weight vs reps)
- Volume tracking (weight × reps × sets)

### Performance & Reliability
- Database connection pooling for concurrent requests
- GZip compression for efficient data transfer
- Structured logging for monitoring and debugging
- Comprehensive error handling
- 99% test coverage (236 tests)

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (with SQLite fallback)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Testing**: pytest
- **Code Quality**: black, isort, flake8, mypy, bandit

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/gileadraab/progressive-overload-tracker.git
cd progressive-overload-tracker

# Set up environment variables
cp .env.example .env
# Edit .env if needed (default values work for Docker)

# Start the services (Docker Compose automatically reads .env)
docker-compose up -d

# The API will be available at http://localhost:8000
```

### Local Development

```bash
# Install dependencies
poetry install

# Set up environment variables
cp .env.example .env
# Edit .env with your local database configuration

# Run database migrations
poetry run alembic upgrade head

# Start the development server
poetry run uvicorn src.main:app --reload

# The API will be available at http://localhost:8000
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Progressive Overload Workflow

1. **Create or copy a previous workout session**
   ```bash
   GET /sessions/from-session/{id}?user_id=1
   ```

2. **Check exercise history for personal records and suggestions**
   ```bash
   GET /exercises/{id}/history?user_id=1
   ```

3. **Complete workout with adjusted weights/reps**
   ```bash
   POST /sessions/
   ```

4. **Track improvement over time**
   - View updated personal bests
   - See progression suggestions
   - Monitor volume increases

## Development

### Available Commands

```bash
# Install dependencies
make install

# Run tests
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Run linting
make lint

# Type checking
make type-check

# Run database migrations
make migrate

# Create new migration
make migrate-create

# Start Docker services
make docker-up

# Stop Docker services
make docker-down
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/test_api/test_exercises.py

# Run with verbose output
poetry run pytest -v
```

### Code Quality

The project uses pre-commit hooks to ensure code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

Hooks include:
- black (code formatting)
- isort (import sorting)
- flake8 (linting)
- mypy (type checking)
- bandit (security checks)

## Project Structure

```
progressive-overload-tracker/
├── src/
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── routers/         # FastAPI route handlers
│   ├── services/        # Business logic layer
│   ├── database/        # Database configuration
│   ├── logging_config.py
│   ├── config.py
│   └── main.py          # Application entry point
├── tests/
│   ├── test_api/        # Integration tests
│   └── test_services/   # Unit tests
├── migrations/          # Alembic migrations
├── docs/                # Additional documentation
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml       # Poetry dependencies
└── Makefile
```

## API Endpoints

### Exercises
- `GET /exercises/` - List all exercises (with filtering by category, equipment)
- `POST /exercises/` - Create exercise
- `GET /exercises/{id}` - Get exercise details
- `PUT /exercises/{id}` - Update exercise
- `DELETE /exercises/{id}` - Delete exercise
- `GET /exercises/{id}/history` - Get exercise history with PR and suggestions

### Sessions
- `GET /sessions/` - List all sessions (with filtering by user)
- `POST /sessions/` - Create session with nested exercises and sets
- `GET /sessions/{id}` - Get session details
- `PUT /sessions/{id}` - Update session
- `DELETE /sessions/{id}` - Delete session
- `GET /sessions/from-session/{id}` - Copy session for progressive overload
- `GET /sessions/from-template/{id}` - Create session from template
- `PATCH /sessions/{id}/reorder` - Reorder exercises and sets

### Templates
- `GET /templates/` - List all templates (with filtering by user)
- `POST /templates/` - Create template
- `GET /templates/{id}` - Get template details
- `PUT /templates/{id}` - Update template with exercises
- `DELETE /templates/{id}` - Delete template
- `POST /templates/from-session/{id}` - Create template from session

### Users
- `GET /users/` - List all users
- `POST /users/` - Create user
- `GET /users/{id}` - Get user details
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

## Environment Variables

The `.env` file is used by both local development and Docker Compose. Create it from the example:

```bash
cp .env.example .env
```

**For Docker (default values):**
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/progressive_overload
```

**For Local Development:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/progressive_overload
```

Docker Compose automatically reads the `.env` file from the project root.

## Documentation

- [API Documentation](docs/API.md) - Detailed API endpoint documentation
- [Database Schema](docs/DATABASE.md) - Database structure and relationships
- [Development Guide](docs/DEVELOPMENT.md) - Development workflow and best practices
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment instructions

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Progressive overload calculations based on the Brzycki formula
- Inspired by the need for intelligent workout tracking
