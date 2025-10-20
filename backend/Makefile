.PHONY: help install dev test test-cov lint format type-check migrate migrate-create docker-up docker-down docker-logs clean

help:
	@echo "Progressive Overload Tracker - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install dependencies with Poetry"
	@echo ""
	@echo "Development:"
	@echo "  make dev              Start development server"
	@echo "  make test             Run tests"
	@echo "  make test-cov         Run tests with coverage report"
	@echo "  make lint             Run linting (flake8)"
	@echo "  make format           Format code (black + isort)"
	@echo "  make type-check       Run type checking (mypy)"
	@echo ""
	@echo "Database:"
	@echo "  make migrate          Run database migrations"
	@echo "  make migrate-create   Create new migration (use MSG='description')"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up        Start Docker services"
	@echo "  make docker-down      Stop Docker services"
	@echo "  make docker-logs      View Docker logs"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean            Clean up generated files"

install:
	poetry install

dev:
	poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test:
	poetry run pytest -v

test-cov:
	poetry run pytest -v --cov=src --cov-report=term-missing --cov-report=html

lint:
	poetry run flake8 src/ tests/

format:
	poetry run black .
	poetry run isort .

type-check:
	poetry run mypy src/

migrate:
	poetry run alembic upgrade head

migrate-create:
	@if [ -z "$(MSG)" ]; then \
		echo "Error: MSG variable is required. Usage: make migrate-create MSG='your migration description'"; \
		exit 1; \
	fi
	poetry run alembic revision --autogenerate -m "$(MSG)"

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	rm -f .coverage
