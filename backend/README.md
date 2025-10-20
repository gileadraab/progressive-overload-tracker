# Progressive Overload Tracker - Backend

FastAPI backend for the Progressive Overload Tracker application.

## Quick Start

### With Docker

```bash
# From backend directory
docker-compose -f docker-compose.dev.yml up -d

# Access API
http://localhost:8000/docs
```

### Local Development

```bash
poetry install
cp ../.env.example .env
poetry run alembic upgrade head
poetry run uvicorn src.main:app --reload
```

## Project Structure

```
backend/
├── src/
│   ├── models/          # SQLAlchemy database models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── routers/         # FastAPI route handlers
│   ├── services/        # Business logic layer
│   ├── database/        # Database configuration
│   └── main.py          # FastAPI application
├── tests/               # Test suite (236 tests, 99% coverage)
├── migrations/          # Alembic database migrations
└── docs/                # Backend documentation
```

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **Testing**: pytest
- **Type Checking**: mypy

## Development Commands

```bash
# Install dependencies
poetry install

# Run development server
poetry run uvicorn src.main:app --reload

# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run isort .

# Lint and type check
poetry run flake8 .
poetry run mypy src/

# Database migrations
poetry run alembic upgrade head
poetry run alembic revision --autogenerate -m "description"
```

## Using Make

```bash
make install       # Install dependencies
make run           # Start dev server
make test          # Run tests with coverage
make format        # Format code (black + isort)
make lint          # Run linters (flake8 + mypy)
make migrate       # Apply migrations
```

## API Documentation

Interactive API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

See [docs/API.md](docs/API.md) for detailed endpoint documentation.

## Database

PostgreSQL 16 with SQLAlchemy 2.0 ORM.

**Connection pooling** (configured in `src/database/database.py`):
- Pool size: 10
- Max overflow: 20
- Pre-ping: enabled
- Pool recycle: 3600s

See [docs/DATABASE.md](docs/DATABASE.md) for complete schema documentation.

## Testing

```bash
# Run all tests
make test

# Run specific test
poetry run pytest tests/test_models.py

# Generate coverage report
poetry run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

**Current coverage**: 99% (236 tests)

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
DATABASE_URL=postgresql://user:password@localhost/progresstracker_db
APP_ENV=development
LOG_LEVEL=INFO
```

## Progressive Overload Logic

The backend implements progressive overload calculations:

- **1RM Calculation**: Brzycki formula `weight / (1.0278 - 0.0278 * reps)`
- **Volume Tracking**: Total sets × reps × weight
- **Progression Suggestions**: Based on performance history and rep ranges

## Docker

**Backend + Database**:
```bash
docker-compose -f docker-compose.dev.yml up -d
```

**Backend only** (use external database):
```bash
docker build -t progressive-overload-backend .
docker run -p 8000:8000 --env-file .env progressive-overload-backend
```

## Documentation

- [API Documentation](docs/API.md) - Complete endpoint reference
- [Database Schema](docs/DATABASE.md) - Database structure and relationships
- [Development Guide](../DEVELOPMENT.md) - Full development workflow

## License

Personal use and learning purposes.
