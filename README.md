# Progressive Overload Tracker

A full-stack fitness tracking application with intelligent workout suggestions and progressive overload tracking.

## Overview

Progressive Overload Tracker helps users systematically improve their strength training by tracking workouts, analyzing performance history, and providing smart recommendations for progressive overload.

### Key Features

- 📊 **Exercise History & PRs** - Track personal records and performance trends
- 💡 **Progressive Overload Logic** - Automatic recommendations for weight/rep progression
- 📝 **Workout Templates** - Create and reuse workout plans
- 🔄 **Session Copying** - "Repeat last workout" with modifications
- 📈 **Volume Tracking** - Monitor total work performed over time
- 🎯 **1RM Calculations** - Brzycki formula for estimated max strength

## Quick Start

### Full Stack (Docker)

```bash
# Clone the repository
git clone https://github.com/gileadraab/progressive-overload-tracker.git
cd progressive-overload-tracker

# Set up environment
cp .env.example .env

# Start all services
docker-compose up -d

# Access the application
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Frontend: http://localhost:3000 (coming soon)
```

### Backend Only

```bash
cd backend

# Install dependencies
poetry install

# Set up environment
cp ../.env.example .env

# Run migrations
poetry run alembic upgrade head

# Start the server
poetry run uvicorn src.main:app --reload

# Backend API: http://localhost:8000
```

## Project Structure

```
progressive-overload-tracker/
├── backend/             # FastAPI backend
│   ├── src/            # Source code
│   ├── tests/          # Test suite
│   ├── docs/           # API & database docs
│   └── migrations/     # Database migrations
├── frontend/           # Frontend (coming soon)
├── docker-compose.yml  # Full stack orchestration
└── DEVELOPMENT.md      # Development guide
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0
- **Testing**: pytest (236 tests, 99% coverage)

### Frontend (Coming Soon)
- Framework TBD (React/Vue/Svelte)
- TypeScript
- Modern build tooling

### Infrastructure
- Docker & Docker Compose
- GitHub Actions CI/CD
- Pre-commit hooks

## Documentation

- [Backend API Documentation](backend/docs/API.md)
- [Database Schema](backend/docs/DATABASE.md)
- [Development Guide](DEVELOPMENT.md)

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup instructions, coding standards, and contribution guidelines.

### Quick Commands

```bash
# Backend development
cd backend
make test          # Run tests
make format        # Format code
make lint          # Run linters

# Docker development
make docker-up     # Start services
make docker-down   # Stop services
```

## Progressive Overload Workflow

1. **Start a workout** - Copy your last session or use a template
2. **Check history** - View PRs and get suggestions for each exercise
3. **Track your sets** - Log weights and reps as you work out
4. **Get feedback** - See updated PRs and progression recommendations

## API Overview

### Core Endpoints

- `GET /exercises/{id}/history` - Exercise performance history with suggestions
- `GET /sessions/from-session/{id}` - Copy previous workout
- `POST /sessions/` - Create new workout session
- `GET /templates/` - List workout templates

See [API Documentation](backend/docs/API.md) for complete endpoint details.

## Current Status

- ✅ Backend API complete (99% test coverage)
- ✅ Docker containerization
- ✅ CI/CD pipeline
- ⏳ Frontend in development
- ⏳ Authentication (planned)
- ⏳ Mobile app (planned)

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Progressive overload calculations based on the Brzycki formula
- Inspired by the need for data-driven strength training
