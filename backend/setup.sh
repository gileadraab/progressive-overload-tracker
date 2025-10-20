#!/bin/bash

set -e

echo "=================================================="
echo "Progressive Overload Tracker - Environment Setup"
echo "=================================================="
echo ""

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed!"
    echo ""
    echo "Please install Poetry first:"
    echo "  curl -sSL https://install.python-poetry.org | python3 -"
    echo ""
    echo "Or visit: https://python-poetry.org/docs/#installation"
    exit 1
fi

echo "✅ Poetry found: $(poetry --version)"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker is not installed. You'll need it to run the PostgreSQL database."
    echo "   Visit: https://docs.docker.com/get-docker/"
    echo ""
else
    echo "✅ Docker found: $(docker --version)"
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  docker-compose is not installed. You'll need it to run the PostgreSQL database."
    echo "   Visit: https://docs.docker.com/compose/install/"
    echo ""
else
    echo "✅ docker-compose found: $(docker-compose --version)"
fi

echo ""
echo "Step 1: Installing Python dependencies..."
poetry install

echo ""
echo "Step 2: Setting up environment variables..."
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file from .env.example"
        echo "   Please review and update DATABASE_URL if needed"
    else
        echo "⚠️  No .env.example found. Creating basic .env file..."
        cat > .env << EOF
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/progressive_overload_tracker
EOF
        echo "✅ Created basic .env file"
    fi
else
    echo "✅ .env file already exists"
fi

echo ""
echo "Step 3: Starting PostgreSQL database..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
    echo "✅ Database container started"
    echo "   Waiting for database to be ready..."
    sleep 3
else
    echo "⚠️  Skipping database startup (docker-compose not available)"
fi

echo ""
echo "Step 4: Running database migrations..."
if command -v docker-compose &> /dev/null; then
    poetry run alembic upgrade head
    echo "✅ Database migrations complete"
else
    echo "⚠️  Skipping migrations (database not running)"
fi

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Start the development server:"
echo "     make dev"
echo ""
echo "  2. Run tests:"
echo "     make test"
echo ""
echo "  3. View all available commands:"
echo "     make help"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
echo ""
