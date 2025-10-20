# Development Guide

## Quick Setup

### Full Stack (Docker)

```bash
git clone https://github.com/gileadraab/progressive-overload-tracker.git
cd progressive-overload-tracker
cp .env.example .env
docker-compose up -d
```

Access: http://localhost:8000/docs

### Backend Only

```bash
cd backend
poetry install
cp ../.env.example .env
docker-compose -f docker-compose.dev.yml up -d db
poetry run alembic upgrade head
poetry run uvicorn src.main:app --reload
```

### Local (No Docker)

```bash
cd backend
poetry install
cp ../.env.example .env
# Edit .env: DATABASE_URL=postgresql://user:password@localhost/progresstracker_db
poetry run alembic upgrade head
poetry run uvicorn src.main:app --reload
```

## Development Workflow

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

Hooks: black, isort, flake8, mypy, bandit

### Code Quality

```bash
cd backend

# Format code
make format

# Run linters
make lint

# Run tests
make test

# All checks
make format && make lint && make test
```

### Database Migrations

```bash
# Create migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback
poetry run alembic downgrade -1
```

### Testing

```bash
# Run all tests
poetry run pytest

# With coverage
poetry run pytest --cov=src --cov-report=term-missing

# Specific test
poetry run pytest tests/test_models.py::test_user_creation
```

## Project Structure

```
progressive-overload-tracker/
├── backend/
│   ├── src/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── routers/         # API endpoints
│   │   ├── services/        # Business logic
│   │   └── main.py          # FastAPI app
│   ├── tests/               # Test suite (236 tests, 99% coverage)
│   ├── migrations/          # Alembic migrations
│   └── docs/                # API and database docs
├── frontend/                # Coming soon
└── docker-compose.yml       # Full stack
```

## Coding Standards

- **Formatting**: Black (line length 100)
- **Import sorting**: isort (black profile)
- **Linting**: flake8
- **Type checking**: mypy (strict mode)
- **Testing**: pytest (99%+ coverage required)

### Before Committing

```bash
make format    # Auto-fix formatting
make lint      # Check for issues
make test      # Ensure tests pass
```

Pre-commit hooks will enforce these automatically.

## Adding Features

### New Model

1. Create model in `src/models/`
2. Create schemas in `src/schemas/`
3. Generate migration: `alembic revision --autogenerate -m "add model"`
4. Apply migration: `alembic upgrade head`
5. Write tests in `tests/`

### New Endpoint

1. Create router in `src/routers/`
2. Register in `src/main.py`
3. Write tests
4. Test in Swagger UI: http://localhost:8000/docs

## Docker Commands

```bash
# Full stack
docker-compose up -d
docker-compose logs -f backend
docker-compose down

# Backend only
cd backend
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml exec backend poetry run pytest

# Clean slate
docker-compose down -v
```

## Make Commands

```bash
cd backend

make install       # Install dependencies
make run           # Start dev server
make format        # Format code
make lint          # Run linters
make test          # Run tests
make migrate       # Apply migrations
make docker-up     # Start Docker
make clean         # Remove cache
```

## Troubleshooting

**Module not found**: `cd backend && poetry install && poetry shell`

**Pre-commit failing**: `make format` then fix remaining issues

**Database connection refused**: `docker-compose restart db`

**Tests failing**: Clear cache with `rm -rf .pytest_cache && poetry run pytest`

**Docker build fails**: `docker-compose build --no-cache`

## Documentation

- [API Documentation](backend/docs/API.md)
- [Database Schema](backend/docs/DATABASE.md)
- [README](README.md)

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
