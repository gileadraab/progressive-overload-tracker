Progressive Overload Tracker FastAPI Application: Step-by-Step Guide

This document provides a detailed walkthrough for setting up and building a FastAPI application for tracking progressive overload, including database configuration, API development, testing, and deployment setup. Each section includes code snippets and instructions on how to verify your progress.

## Table of Contents

1.  [Step 1: Project Setup (Initial Structure)](#step-1-project-setup-initial-structure)
2.  [Step 2: Database Configuration and SQLAlchemy Models](#step-2-database-configuration-and-sqlalchemy-models)
3.  [Step 3: Alembic Migrations](#step-3-alembic-migrations)
4.  [Step 4: Pydantic Schemas](#step-4-pydantic-schemas)
5.  [Step 5: Service Layer](#step-5-service-layer)
6.  [Step 6: FastAPI Routers](#step-6-fastapi-routers)
7.  [Step 7: Testing Infrastructure](#step-7-testing-infrastructure)
8.  [Step 8: Unit Tests for Services](#step-8-unit-tests-for-services)
9.  [Step 9: Integration Tests for API Endpoints](#step-9-integration-tests-for-api-endpoints)
10. [Step 10: Docker Configuration](#step-10-docker-configuration)
11. [Step 11: Development Tools and Configuration](#step-11-development-tools-and-configuration)
12. [Step 12: Project Documentation](#step-12-project-documentation)
13. [Final Steps to Run and Test](#final-steps-to-run-and-test)

---

## Step 1: Project Setup (Initial Structure)

This step creates the foundational directory structure and essential configuration files for your FastAPI project.

### 1.1. Create the Project Root Directory

Start by creating the main directory for your project and navigating into it.

```bash
mkdir progressive-overload-tracker
cd progressive-overload-tracker
```

### 1.2. Define the Core Project Structure

We'll establish the main application (`src`), testing (`tests`), and database migration (`migrations`) directories. We also include `__init__.py` files within Python packages to mark them as such.

```bash
mkdir -p src src/models src/schemas src/services src/routers src/database tests migrations
touch src/__init__.py src/models/__init__.py src/schemas/__init__.py src/services/__init__.py src/routers/__init__.py tests/__init__.py
touch src/database/.gitkeep src/models/.gitkeep src/schemas/.gitkeep src/services/.gitkeep src/routers/.gitkeep tests/.gitkeep migrations/.gitkeep
```

### 1.3. Create `requirements.txt`

This file will list all the Python packages your project depends on.

```requirements.txt
fastapi
uvicorn[standard]
sqlalchemy>=2.0
psycopg2-binary
alembic
pydantic
pytest
pytest-asyncio
httpx
python-dotenv
pydantic-settings
black
isort
flake8
mypy
pre-commit
```

### 1.4. Create `.env.example`

This file serves as a template for environment variables, especially for sensitive data like database connection strings.

```.env.example
# This file is used as a template for your .env file.
# Copy this file to .env and fill in the values.
#
# The .env file is used to configure the application, especially for local development.
# It is ignored by git, so it's a safe place for secrets.

# Database URL for the application.
# Used by the application and alembic for migrations.
DATABASE_URL="postgresql://user:password@localhost:5432/progresstracker_db"

# PostgreSQL connection settings used by Docker Compose.
# These are used to initialize the database container.
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=progresstracker_db
```

### 1.5. Create `src/main.py`

This will be the entry point for your FastAPI application, with a minimal setup.

```src/main.py
from fastapi import FastAPI

app = FastAPI(
    title="Progressive Overload Tracker",
    description="API for tracking workouts and progressive overload.",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Progressive Overload Tracker API"}
```

### 1.6. Create `.gitignore`

This file tells Git which files and directories to ignore.

```.gitignore
.aider*
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*.so

# Distribution / packaging
build/
dist/
*.egg-info/

# Environments
.env
.venv
env/
venv/
ENV/

# Unit test / coverage reports
.pytest_cache/
.coverage
.mypy_cache/
.pre-commit-cache/
htmlcov/
test.db*

# IDE settings
.idea/
.vscode/

# Docker
postgres_data/
secrets/
```

### 1.7. Initialize a Git Repository (Recommended)

```bash
git init
```

---

### Testing Point: Step 1

After completing Step 1, you can verify the basic project structure and file existence.

```bash
ls -F
```

You should see:
```
alembic.ini*      docker-compose.yml     migrations/  requirements.txt  src/
CONTRIBUTING.md   Dockerfile             Makefile*    secrets/          tests/
.dockerignore     .env                   .gitignore   setup.sh*
```

You can also inspect the contents of `src/` and `tests/` etc.

```bash
ls -F src/
```
Output:
```
__init__.py  config/  database/  main.py  models/  routers/  schemas/  services/
```

---

## Step 2: Database Configuration and SQLAlchemy Models

This step sets up the database connection and defines the SQLAlchemy ORM models.

### 2.1. Configuration Settings (`src/config.py`)

This file manages application configuration.

```src/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    These settings are loaded from environment variables.
    You can create a .env file in the root directory to override them.
    """

    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
```

### 2.2. Database Connection Setup (`src/database/database.py`)

This file contains the SQLAlchemy engine, session maker, and declarative base.

```src/database/database.py
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from src.config import settings

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get a database session.

    Yields:
        A SQLAlchemy database session, which is automatically closed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2.3. Enums (`src/models/enums.py`)

Define Python enums for your models.

```src/models/enums.py
import enum


class UnitEnum(str, enum.Enum):
    kg = "kg"
    stacks = "stacks"
```

### 2.4. Exercise Model (`src/models/exercise.py`)

```src/models/exercise.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.database.database import Base


class Exercise(Base):
    """
    Represents an exercise in the database.

    Attributes:
        id: The primary key.
        name_en: The English name of the exercise.
        name_pt: The Portuguese name of the exercise.
        image_url: A URL to an image or video of the exercise.
        category: The primary muscle group targeted by the exercise.
        subcategory: A secondary muscle group.
        equipment: The equipment required for the exercise.
        exercise_sessions: Relationship to ExerciseSession model.
    """

    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(String, nullable=False, index=True)
    name_pt = Column(String, nullable=False, index=True)
    image_url = Column(String, nullable=True)
    category = Column(String, nullable=False, index=True)
    subcategory = Column(String, nullable=True, index=True)
    equipment = Column(String, nullable=True)

    exercise_sessions = relationship("ExerciseSession", back_populates="exercise")
```

### 2.5. Session Model (`src/models/session.py`)

```src/models/session.py
from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.orm import relationship

from src.database.database import Base


class Session(Base):
    """
    Represents a workout session in the database.

    Attributes:
        id: The primary key.
        date: The date and time of the workout session.
        exercise_sessions: Relationship to the ExerciseSession model.
    """

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=func.utcnow(), index=True)

    exercise_sessions = relationship("ExerciseSession", back_populates="session")
```

### 2.6. Template Model (`src/models/template.py`)

```src/models/template.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.database.database import Base


class Template(Base):
    """
    Represents a workout template in the database.

    Attributes:
        id: The primary key.
        name: The name of the template.
        exercise_sessions: Relationship to the ExerciseSession model.
    """

    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    exercise_sessions = relationship("ExerciseSession", back_populates="template")
```

### 2.7. ExerciseSession Model (`src/models/exercise_session.py`)

```src/models/exercise_session.py
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.database.database import Base


class ExerciseSession(Base):
    """
    Represents an exercise performed within a session or template.

    This is a linking table between exercises and sessions/templates.

    Attributes:
        id: The primary key.
        exercise_id: Foreign key to the Exercise model.
        session_id: Foreign key to the Session model.
        template_id: Foreign key to the Template model.
        exercise: Relationship to the Exercise model.
        session: Relationship to the Session model.
        template: Relationship to the Template model.
        sets: Relationship to the Set model.
    """

    __tablename__ = "exercise_sessions"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)

    exercise = relationship("Exercise", back_populates="exercise_sessions")
    session = relationship("Session", back_populates="exercise_sessions")
    template = relationship("Template", back_populates="exercise_sessions")
    sets = relationship(
        "Set", back_populates="exercise_session", cascade="all, delete-orphan"
    )
```

### 2.8. Set Model (`src/models/set.py`)

```src/models/set.py
from sqlalchemy import Column, Enum, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.database.database import Base
from src.models.enums import UnitEnum


class Set(Base):
    """
    Represents a single set of an exercise in the database.

    Attributes:
        id: The primary key.
        weight: The weight used for the set.
        reps: The number of repetitions performed.
        unit: The unit of weight (e.g., kg, stacks).
        exercise_session_id: Foreign key to the ExerciseSession model.
        exercise_session: Relationship to the ExerciseSession model.
    """

    __tablename__ = "sets"

    id = Column(Integer, primary_key=True, index=True)
    weight = Column(Float, nullable=False)
    reps = Column(Integer, nullable=False)
    unit = Column(Enum(UnitEnum), nullable=False)
    exercise_session_id = Column(
        Integer, ForeignKey("exercise_sessions.id"), nullable=False
    )

    exercise_session = relationship("ExerciseSession", back_populates="sets")
```

### 2.9. Update `src/models/__init__.py`

```src/models/__init__.py
from src.database.database import Base
from src.models.enums import UnitEnum
from src.models.exercise import Exercise
from src.models.exercise_session import ExerciseSession
from src.models.session import Session
from src.models.set import Set
from src.models.template import Template

__all__ = [
    "Base",
    "Exercise",
    "Session",
    "Template",
    "ExerciseSession",
    "Set",
    "UnitEnum",
]
```

---

### Testing Point: Step 2

After defining models, you can perform initial checks:

1.  **Install Python Dependencies**: This is crucial to ensure Python can find and interpret the code.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Verify Model Detection with Alembic**: Alembic can "autogenerate" migration scripts by comparing your models to the current database state. If your models are correctly defined, this command should run without errors (though it will indicate no changes yet, as tables haven't been created).
    ```bash
    alembic revision --autogenerate -m "Initial schema"
    ```
    You should see output similar to: `INFO  [alembic.runtime.migration] Context complete.` followed by a new migration file being created in `migrations/versions/`. This indicates Alembic successfully read your models.

---

## Step 3: Alembic Migrations

Alembic is used for database migrations.

### 3.1. Initialize Alembic

If you haven't already, initialize Alembic in your project.

```bash
alembic init migrations
```

### 3.2. Configure `alembic.ini`

Ensure `alembic.ini` points to your database URL and source code.

Modify `alembic.ini` at the project root:

```alembic.ini
# A generic Alembic configuration file.
#
# Additional configuration options can be found at:
# https://alembic.sqlalchemy.org/en/latest/usage.html#configuration

[alembic]
# path to migration scripts
script_location = alembic

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# The sqlalchemy.url is configured to use the DATABASE_URL environment variable.
# This is used by alembic to connect to the database.
sqlalchemy.url = ${DATABASE_URL}

# template for new migration files
# file_template = %%(rev)s_%%(slug)s

# timezone for timestamps within the migration file
# timezone =

# title for migration file naming
# migration_title_style = dash

# timezone for create_date in migration file
# create_date_timezone =

# don't use the transactional DDL by default
# transactional_ddl = false

# set to 'true' to run the environment script completely
# even if visualization is being used
# sourceless = false

# revision range for 'alembic history'
# revision_range =

# Set to true if you want to output the full traceback on error
# output_full_stacktrace = false


# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### 3.3. Update `alembic/env.py`

This file is crucial for Alembic to load your models and connect to the database.

Modify `alembic/env.py`:

```alembic/env.py
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from src.config import settings
from src.database.database import Base
from src.models import *  # noqa: F401, F403

target_metadata = Base.metadata


def get_url():
    """
    Return the database URL from the application settings.

    Returns:
        The database URL.
    """
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        configuration = {}
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 3.4. Create Initial Migration

```bash
alembic revision --autogenerate -m "Initial migration"
```
This will create a file in `migrations/versions/` like `xxxxxxxxxxxx_initial_migration.py` with `create_table` commands.

### 3.5. Create Database Seeding Script (`scripts/seed_database.py`)

Create the `scripts` directory if it doesn't exist.

```bash
mkdir -p scripts
```

```scripts/seed_database.py
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.database import SessionLocal
from src.database.seed import seed_exercises


def main():
    """
    Seed the database with initial data.
    """
    db = SessionLocal()
    try:
        print("Seeding database...")
        seed_exercises(db)
        print("Database seeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
```

---

### Testing Point: Step 3

At this point, you can apply your migration and seed the database. Make sure you have a PostgreSQL database running and its connection details set correctly in your `.env` file (which you should copy from `.env.example`).

1.  **Create `.env` and set `DATABASE_URL`**:
    ```bash
    cp .env.example .env
    # Open .env with your editor and adjust DATABASE_URL if needed.
    # E.g., DATABASE_URL="postgresql://user:password@localhost:5432/your_db_name"
    ```

2.  **Apply Migration**:
    ```bash
    alembic upgrade head
    ```
    This command will create all the tables defined in your models.

3.  **Seed Database**:
    ```bash
    python scripts/seed_database.py
    ```
    This will insert initial exercise data.

4.  **Verify Database State (Optional, requires PostgreSQL client)**:
    If you have `psql` installed and your database is running, you can connect to it and inspect the tables and data.
    ```bash
    # Replace user and progresstracker_db with your actual credentials/database name
    psql -U user -d progresstracker_db
    ```
    Inside `psql`, run:
    ```sql
    \dt -- List tables
    SELECT * FROM exercises; -- Verify seeded data
    ```
    You should see your tables (`exercises`, `sessions`, `templates`, `exercise_sessions`, `sets`) and the seeded exercise data.

---

## Step 4: Pydantic Schemas

Pydantic schemas are crucial for data validation and serialization in FastAPI.

### 4.1. Common Schemas (`src/schemas/common.py`)

```src/schemas/common.py
from pydantic import BaseModel


class Message(BaseModel):
    """A generic message schema for responses."""

    message: str
```

### 4.2. Exercise Schemas (`src/schemas/exercise.py`)

```src/schemas/exercise.py
from pydantic import BaseModel, ConfigDict


class ExerciseBase(BaseModel):
    name_en: str
    name_pt: str
    image_url: str | None = None
    category: str
    subcategory: str | None = None
    equipment: str | None = None


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(BaseModel):
    name_en: str | None = None
    name_pt: str | None = None
    image_url: str | None = None
    category: str | None = None
    subcategory: str | None = None
    equipment: str | None = None


class ExerciseRead(ExerciseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
```

### 4.3. Set Schemas (`src/schemas/set.py`)

```src/schemas/set.py
from pydantic import BaseModel, ConfigDict

from src.models.enums import UnitEnum


class SetBase(BaseModel):
    weight: float
    reps: int
    unit: UnitEnum


class SetCreate(SetBase):
    pass


class SetUpdate(BaseModel):
    weight: float | None = None
    reps: int | None = None
    unit: UnitEnum | None = None


class SetRead(SetBase):
    id: int
    exercise_session_id: int

    model_config = ConfigDict(from_attributes=True)
```

### 4.4. ExerciseSession Schemas (`src/schemas/exercise_session.py`)

```src/schemas/exercise_session.py
from pydantic import BaseModel, ConfigDict

from src.schemas.exercise import ExerciseRead
from src.schemas.set import SetCreate, SetRead


class ExerciseSessionBase(BaseModel):
    exercise_id: int


class ExerciseSessionCreate(ExerciseSessionBase):
    sets: list[SetCreate]


class ExerciseSessionRead(ExerciseSessionBase):
    id: int
    session_id: int | None = None
    template_id: int | None = None
    exercise: ExerciseRead
    sets: list[SetRead]

    model_config = ConfigDict(from_attributes=True)
```

### 4.5. Session Schemas (`src/schemas/session.py`)

```src/schemas/session.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.schemas.exercise_session import (
    ExerciseSessionCreate,
    ExerciseSessionRead,
)


class SessionBase(BaseModel):
    pass


class SessionCreate(SessionBase):
    exercise_sessions: list[ExerciseSessionCreate]


class SessionRead(SessionBase):
    id: int
    date: datetime
    exercise_sessions: list[ExerciseSessionRead]

    model_config = ConfigDict(from_attributes=True)
```

### 4.6. Template Schemas (`src/schemas/template.py`)

```src/schemas/template.py
from pydantic import BaseModel, ConfigDict

from src.schemas.exercise_session import (
    ExerciseSessionCreate,
    ExerciseSessionRead,
)


class TemplateBase(BaseModel):
    name: str


class TemplateCreate(TemplateBase):
    exercise_sessions: list[ExerciseSessionCreate]


class TemplateRead(TemplateBase):
    id: int
    exercise_sessions: list[ExerciseSessionRead]

    model_config = ConfigDict(from_attributes=True)
```

### 4.7. Update `src/schemas/__init__.py`

```src/schemas/__init__.py
from .common import Message
from .exercise import ExerciseCreate, ExerciseRead, ExerciseUpdate
from .exercise_session import (
    ExerciseSessionCreate,
    ExerciseSessionRead,
)
from .session import SessionCreate, SessionRead
from .set import SetCreate, SetRead, SetUpdate
from .template import TemplateCreate, TemplateRead

__all__ = [
    "Message",
    "ExerciseCreate",
    "ExerciseRead",
    "ExerciseUpdate",
    "SetCreate",
    "SetRead",
    "SetUpdate",
    "ExerciseSessionCreate",
    "ExerciseSessionRead",
    "SessionCreate",
    "SessionRead",
    "TemplateCreate",
    "TemplateRead",
]
```

---

### Testing Point: Step 4

To test the Pydantic schemas, you can create a temporary Python script that tries to import and instantiate them.

1.  **Create a temporary test file**:
    ```bash
    touch test_schemas.py
    ```

2.  **Add test code to `test_schemas.py`**:
    ```python
    from src.schemas.exercise import ExerciseCreate
    from src.schemas.session import SessionCreate
    from src.schemas.set import SetCreate
    from src.models.enums import UnitEnum # Needed for SetCreate

    print("--- Testing ExerciseCreate ---")
    try:
        exercise_data = ExerciseCreate(
            name_en="Push-up",
            name_pt="Flexão",
            category="Chest",
            equipment="Bodyweight"
        )
        print(f"Success: {exercise_data.model_dump_json(indent=2)}")
    except Exception as e:
        print(f"Failed: {e}")

    print("\n--- Testing SetCreate ---")
    try:
        set_data = SetCreate(
            weight=50.0,
            reps=10,
            unit=UnitEnum.KG
        )
        print(f"Success: {set_data.model_dump_json(indent=2)}")
    except Exception as e:
        print(f"Failed: {e}")

    print("\n--- Testing SessionCreate ---")
    try:
        session_data = SessionCreate(
            exercise_sessions=[] # Can be empty for now
        )
        print(f"Success: {session_data.model_dump_json(indent=2)}")
    except Exception as e:
        print(f"Failed: {e}")
    ```

3.  **Run the test file**:
    ```bash
    python test_schemas.py
    ```
    If successful, you should see "Success" messages with the JSON representation of your instantiated schemas. If there are errors, they will be reported here.

4.  **Clean up the test file**:
    ```bash
    rm test_schemas.py
    ```

---

## Step 5: Service Layer

The service layer encapsulates the business logic.

### 5.1. Exercise Service (`src/services/exercise_service.py`)

```src/services/exercise_service.py
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy import select

from src.models.exercise import Exercise
from src.schemas.exercise import ExerciseCreate, ExerciseRead


async def get_exercises(db: Session) -> List[ExerciseRead]:
    """
    Get all exercises from the database.

    Args:
        db: The database session.

    Returns:
        A list of all exercises.
    """
    result = db.execute(select(Exercise)).scalars().all()
    return result


async def search_exercises(query: str, db: Session) -> List[ExerciseRead]:
    """
    Search exercises by name or category.

    Args:
        query: The search term.
        db: The database session.

    Returns:
        A list of exercises matching the search query.
    """
    search = f"%{query}%"
    result = db.execute(
        select(Exercise).where(
            (Exercise.name_en.ilike(search))
            | (Exercise.name_pt.ilike(search))
            | (Exercise.category.ilike(search))
        )
    ).scalars().all()
    return result


async def get_exercise(exercise_id: int, db: Session) -> ExerciseRead:
    """
    Get a single exercise by its ID.

    Args:
        exercise_id: The ID of the exercise to retrieve.
        db: The database session.

    Raises:
        HTTPException: If the exercise with the given ID is not found.

    Returns:
        The retrieved exercise.
    """
    exercise = db.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found",
        )
    return exercise


async def create_exercise(exercise: ExerciseCreate, db: Session) -> ExerciseRead:
    """
    Create a new exercise in the database.

    Args:
        exercise: The exercise data to create.
        db: The database session.

    Returns:
        The newly created exercise.
    """
    db_exercise = Exercise(**exercise.model_dump())
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


async def delete_exercise(exercise_id: int, db: Session) -> None:
    """
    Delete an exercise from the database.

    Args:
        exercise_id: The ID of the exercise to delete.
        db: The database session.

    Raises:
        HTTPException: If the exercise with the given ID is not found.
    """
    exercise = db.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found",
        )
    db.delete(exercise)
    db.commit()
    return
```

### 5.2. Session Service (`src/services/session_service.py`)

```src/services/session_service.py
from typing import List
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from sqlalchemy import select

from src.models.session import Session as SessionModel
from src.models.exercise_session import ExerciseSession
from src.models.set import Set as SetModel
from src.schemas.session import SessionCreate, SessionRead


async def get_sessions(db: Session) -> List[SessionRead]:
    """
    Get all workout sessions from the database.

    Args:
        db: The database session.

    Returns:
        A list of all sessions.
    """
    result = db.execute(
        select(SessionModel)
        .options(
            joinedload(SessionModel.exercise_sessions).options(
                joinedload(ExerciseSession.exercise), joinedload(ExerciseSession.sets)
            )
        )
    ).scalars().unique().all()
    return result


async def get_session(session_id: int, db: Session) -> SessionRead:
    """
    Get a single session by its ID, including its exercises and sets.

    Args:
        session_id: The ID of the session to retrieve.
        db: The database session.

    Raises:
        HTTPException: If the session with the given ID is not found.

    Returns:
        The retrieved session.
    """
    result = db.execute(
        select(SessionModel)
        .options(
            joinedload(SessionModel.exercise_sessions).options(
                joinedload(ExerciseSession.exercise), joinedload(ExerciseSession.sets)
            )
        )
        .where(SessionModel.id == session_id)
    )
    session = result.scalars().first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found",
        )
    return session


async def create_session(session_data: SessionCreate, db: Session) -> SessionRead:
    """
    Create a new session with nested exercises and sets.

    Args:
        session_data: The session data, including nested exercise sessions and sets.
        db: The database session.

    Returns:
        The newly created session.
    """
    session_dict = session_data.model_dump()

    exercise_sessions_data = session_dict.pop('exercise_sessions', [])

    db_session = SessionModel(**session_dict)

    for es_data in exercise_sessions_data:
        sets_data = es_data.pop('sets', [])
        db_es = ExerciseSession(**es_data)

        for set_data in sets_data:
            db_set = SetModel(**set_data)
            db_es.sets.append(db_set)

        db_session.exercise_sessions.append(db_es)

    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    return await get_session(db_session.id, db)


async def delete_session(session_id: int, db: Session) -> None:
    """
    Delete a session from the database.

    Args:
        session_id: The ID of the session to delete.
        db: The database session.

    Raises:
        HTTPException: If the session with the given ID is not found.
    """
    session = db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found",
        )
    db.delete(session)
    db.commit()
    return
```
5.3. Template Service (`src/services/template_service.py`)

```src/services/template_service.py
from typing import List
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from sqlalchemy import select

from src.models.template import Template as TemplateModel
from src.models.exercise import Exercise
from src.models.exercise_session import ExerciseSession
from src.schemas.template import TemplateCreate, TemplateRead


async def get_templates(db: Session) -> List[TemplateRead]:
    """
    Get all workout templates from the database.

    Args:
        db: The database session.

    Returns:
        A list of all templates.
    """
    result = db.execute(
        select(TemplateModel).options(
            joinedload(TemplateModel.exercise_sessions).joinedload(
                ExerciseSession.exercise
            )
        )
    ).scalars().unique().all()
    return result


async def get_template(template_id: int, db: Session) -> TemplateRead:
    """
    Get a single template by its ID, including its exercises.

    Args:
        template_id: The ID of the template to retrieve.
        db: The database session.

    Raises:
        HTTPException: If the template with the given ID is not found.

    Returns:
        The retrieved template.
    """
    result = db.execute(
        select(TemplateModel)
        .options(
            joinedload(TemplateModel.exercise_sessions).joinedload(
                ExerciseSession.exercise
            )
        )
        .where(TemplateModel.id == template_id)
    )
    template = result.scalars().first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id {template_id} not found",
        )
    return template


async def create_template(template_data: TemplateCreate, db: Session) -> TemplateRead:
    """
    Create a new template with associated exercises.

    Args:
        template_data: The template data, including a list of exercise IDs.
        db: The database session.

    Raises:
        HTTPException: If any of the provided exercise IDs are not found.

    Returns:
        The newly created template.
    """
    template_dict = template_data.model_dump()
    exercise_ids = template_dict.pop('exercise_ids', [])

    db_template = TemplateModel(**template_dict)

    if exercise_ids:
        unique_exercise_ids = list(set(exercise_ids))
        exercises = db.execute(select(Exercise).where(Exercise.id.in_(unique_exercise_ids))).scalars().all()
        if len(exercises) != len(unique_exercise_ids):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more exercises not found")

        for exercise in exercises:
            exercise_session = ExerciseSession(exercise_id=exercise.id)
            db_template.exercise_sessions.append(exercise_session)

    db.add(db_template)
    db.commit()
    db.refresh(db_template)

    return await get_template(db_template.id, db)


async def delete_template(template_id: int, db: Session) -> None:
    """
    Delete a template from the database.

    Args:
        template_id: The ID of the template to delete.
        db: The database session.

    Raises:
        HTTPException: If the template with the given ID is not found.
    """
    template = db.get(TemplateModel, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template with id {template_id} not found",
        )
    db.delete(template)
    db.commit()
    return
```

---

### Testing Point: Step 5

To test the service layer, you would typically write unit tests. Since we'll create those later in Step 8, for now, you can perform a very basic manual check by trying to import them and ensure no immediate syntax errors.

```bash
python -c "from src.services import exercise_service, session_service, template_service; print('Service imports successful.')"
```
If successful, you should see `Service imports successful.`

---

## Step 6: FastAPI Routers

FastAPI routers define the API endpoints and link them to the service layer.

### 6.1. Exercises Router (`src/routers/exercises.py`)

```src/routers/exercises.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.schemas.common import Message
from src.schemas.exercise import ExerciseCreate, ExerciseRead
from src.services import exercise_service

router = APIRouter(
    prefix="/exercises",
    tags=["exercises"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[ExerciseRead], summary="Get all exercises")
async def get_all_exercises(
    db: Session = Depends(get_db), skip: int = 0, limit: int = 100
) -> List[ExerciseRead]:
    """
    Retrieve a list of all exercises from the database.

    Args:
        db: The database session.

    Returns:
        A list of all exercises.
    """
    return await exercise_service.get_exercises(db)


@router.get("/search", response_model=List[ExerciseRead], summary="Search for exercises")
async def search_for_exercises(
    query: str, db: Session = Depends(get_db), skip: int = 0, limit: int = 100
) -> List[ExerciseRead]:
    """
    Search for exercises by name.

    Args:
        query: The search query string.
        db: The database session.

    Returns:
        A list of exercises matching the query.
    """
    return await exercise_service.search_exercises(query, db)


@router.get(
    "/{exercise_id}",
    response_model=ExerciseRead,
    summary="Get a specific exercise",
)
async def get_exercise_by_id(
    exercise_id: int, db: Session = Depends(get_db)
) -> ExerciseRead:
    """
    Retrieve a single exercise by its ID.

    Args:
        exercise_id: The ID of the exercise to retrieve.
        db: The database session.

    Raises:
        HTTPException: If the exercise is not found.

    Returns:
        The exercise object.
    """
    exercise = await exercise_service.get_exercise(exercise_id, db)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found"
        )
    return exercise


@router.post(
    "/",
    response_model=ExerciseRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new exercise",
)
async def create_new_exercise(
    exercise: ExerciseCreate, db: Session = Depends(get_db)
) -> ExerciseRead:
    """
    Create a new exercise.

    Args:
        exercise: The data for the new exercise.
        db: The database session.

    Returns:
        The newly created exercise object.
    """
    return await exercise_service.create_exercise(exercise, db)


@router.delete(
    "/{exercise_id}", response_model=Message, summary="Delete an exercise"
)
async def delete_exercise_by_id(
    exercise_id: int, db: Session = Depends(get_db)
) -> Message:
    """
    Delete an exercise by its ID.

    Args:
        exercise_id: The ID of the exercise to delete.
        db: The database session.

    Raises:
        HTTPException: If the exercise is not found.

    Returns:
        A confirmation message.
    """
    exercise = await exercise_service.get_exercise(exercise_id, db)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found"
        )
    await exercise_service.delete_exercise(exercise_id, db)
    return {"message": "Exercise deleted successfully"}
```

### 6.2. Sessions Router (`src/routers/sessions.py`)

```src/routers/sessions.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.schemas.common import Message
from src.schemas.session import SessionCreate, SessionRead
from src.services import session_service

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[SessionRead], summary="Get all sessions")
async def get_all_sessions(
    db: Session = Depends(get_db), skip: int = 0, limit: int = 100
) -> List[SessionRead]:
    """
    Retrieve all workout sessions.

    Args:
        db: The database session.

    Returns:
        A list of all sessions.
    """
    return await session_service.get_sessions(db)


@router.get("/{session_id}", response_model=SessionRead, summary="Get a specific session")
async def get_session_by_id(session_id: int, db: Session = Depends(get_db)) -> SessionRead:
    """
    Retrieve a single session by its ID.

    Args:
        session_id: The ID of the session to retrieve.
        db: The database session.

    Raises:
        HTTPException: If the session is not found.

    Returns:
        The session object.
    """
    session = await session_service.get_session(session_id, db)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return session


@router.post(
    "/",
    response_model=SessionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new session",
)
async def create_new_session(
    session_data: SessionCreate, db: Session = Depends(get_db)
) -> SessionRead:
    """
    Create a new workout session.

    Args:
        session_data: The data for the new session.
        db: The database session.

    Returns:
        The newly created session object.
    """
    return await session_service.create_session(session_data, db)


@router.delete("/{session_id}", response_model=Message, summary="Delete a session")
async def delete_session_by_id(session_id: int, db: Session = Depends(get_db)) -> Message:
    """
    Delete a session by its ID.

    Args:
        session_id: The ID of the session to delete.
        db: The database session.

    Raises:
        HTTPException: If the session is not found.

    Returns:
        A confirmation message.
    """
    session = await session_service.get_session(session_id, db)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    await session_service.delete_session(session_id, db)
    return {"message": "Session deleted successfully"}
```

### 6.3. Templates Router (`src/routers/templates.py`)

```src/routers/templates.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.schemas.common import Message
from src.schemas.template import TemplateCreate, TemplateRead
from src.services import template_service

router = APIRouter(
    prefix="/templates",
    tags=["templates"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[TemplateRead], summary="Get all templates")
async def get_all_templates(
    db: Session = Depends(get_db), skip: int = 0, limit: int = 100
) -> List[TemplateRead]:
    """
    Retrieve all workout templates.

    Args:
        db: The database session.

    Returns:
        A list of all templates.
    """
    return await template_service.get_templates(db)


@router.get(
    "/{template_id}", response_model=TemplateRead, summary="Get a specific template"
)
async def get_template_by_id(
    template_id: int, db: Session = Depends(get_db)
) -> TemplateRead:
    """
    Retrieve a single template by its ID.

    Args:
        template_id: The ID of the template to retrieve.
        db: The database session.

    Raises:
        HTTPException: If the template is not found.

    Returns:
        The template object.
    """
    template = await template_service.get_template(template_id, db)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )
    return template


@router.post(
    "/",
    response_model=TemplateRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new template",
)
async def create_new_template(
    template_data: TemplateCreate, db: Session = Depends(get_db)
) -> TemplateRead:
    """
    Create a new workout template.

    Args:
        template_data: The data for the new template.
        db: The database session.

    Returns:
        The newly created template object.
    """
    return await template_service.create_template(template_data, db)


@router.delete("/{template_id}", response_model=Message, summary="Delete a template")
async def delete_template_by_id(
    template_id: int, db: Session = Depends(get_db)
) -> Message:
    """
    Delete a template by its ID.

    Args:
        template_id: The ID of the template to delete.
        db: The database session.

    Raises:
        HTTPException: If the template is not found.

    Returns:
        A confirmation message.
    """
    template = await template_service.get_template(template_id, db)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )
    await template_service.delete_template(template_id, db)
    return {"message": "Template deleted successfully"}
```

### 6.4. Integrate Routers into `src/main.py`

Modify `src/main.py` to include the newly created routers and add middleware for logging, CORS, and error handling.

```src/main.py
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.database.database import Base, engine
from src.routers import exercises, sessions, templates

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Progressive Overload Tracker API",
    description="""
This API provides endpoints for tracking workout sessions, exercises, and templates.
It's designed to support a client application for progressive overload training.

**Key Features:**
- Manage exercises
- Create and track workout sessions
- Build and reuse workout templates
""",
    version="0.1.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    # In a production environment, you would use Alembic to manage database migrations.
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables checked/created.")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")


# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add request/response logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"method={request.method} path={request.url.path} status_code={response.status_code} duration={process_time:.4f}s"
    )
    return response


# Configure proper error handling
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception for {request.method} {request.url}: {exc}", exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )


# Import and include all routers with /api/v1 prefix
app.include_router(exercises.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")
app.include_router(templates.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Welcome to the Progressive Overload Tracker API"}
```

---

### Testing Point: Step 6

At this stage, you can start your FastAPI application and try to access the root endpoint and the automatically generated API documentation.

1.  **Run the FastAPI Application**:
    ```bash
    uvicorn src.main:app --reload
    ```
    You should see output indicating that the Uvicorn server is running.

2.  **Access the Root Endpoint**:
    Open your web browser or use `curl` to access `http://localhost:8000/`.
    ```bash
    curl http://localhost:8000/
    ```
    You should get a JSON response: `{"message":"Welcome to the Progressive Overload Tracker API"}`.

3.  **Access API Documentation**:
    Open your web browser and navigate to `http://localhost:8000/api/v1/docs`. You should see the Swagger UI with all the defined endpoints for exercises, sessions, and templates. This confirms your routers are correctly integrated and FastAPI is generating documentation.

---

## Step 7: Testing Infrastructure

Set up `pytest` for testing, including an in-memory SQLite database.

### 7.1. Pytest Configuration (`pytest.ini`)

```pytest.ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
pythonpath = . src

[flake8]
max-line-length = 88
extend-ignore = E203

[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
ignore_missing_imports = True
```

### 7.2. Test Fixtures and Setup (`tests/conftest.py`)

```tests/conftest.py
import asyncio
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.database.database import Base, get_db
from src.main import app
from src.models import *  # noqa: F401, F403
from src.schemas.exercise import ExerciseCreate, ExerciseRead
from src.services.exercise_service import create_exercise
from asgi_lifespan import LifespanManager

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    """
    Dependency override for get_db to use the test database.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Apply the dependency override to the app for the duration of the tests
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    Create an instance of the default event loop for each test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Create the database tables before the test session and drop them after.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """
    Fixture to get a database session for a test.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


async def create_test_exercise(
    db: Session, name_en: str, name_pt: str, category: str, image_url: str | None = None, subcategory: str | None = None, equipment: str | None = None
) -> ExerciseRead:
    """
    Helper function to create an exercise for testing.
    """
    exercise_data = ExerciseCreate(name_en=name_en, name_pt=name_pt, category=category, image_url=image_url, subcategory=subcategory, equipment=equipment)
    exercise = await create_exercise(exercise=exercise_data, db=db)
    return exercise


@pytest.fixture
async def sample_exercise(db_session: Session) -> ExerciseRead:
    """
    Fixture to create a sample exercise in the database.
    """
    return await create_test_exercise(
        db=db_session, name_en="Test Exercise", name_pt="Exercício Teste", category="Chest"
    )
```

---

### Testing Point: Step 7

You can run `pytest` with a minimal test to confirm the infrastructure works.

1.  **Create a dummy test file**:
    ```bash
    touch tests/test_async.py
    ```

2.  **Add dummy test to `tests/test_async.py`**:
    ```tests/test_async.py
import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_async_sleep():
    await asyncio.sleep(0.01)
    assert True
    ```

3.  **Run pytest**:
    ```bash
    pytest tests/test_async.py
    ```
    You should see output similar to `=== 1 passed in X.XXs ===`, confirming `pytest` and `pytest-asyncio` are configured.

4.  **Clean up dummy test file**:
    ```bash
    rm tests/test_async.py
    ```

---

##


Step 8: Unit Tests for Services

These tests verify the business logic in your service layer.

### 8.1. Exercise Service Tests (`tests/test_services/test_exercise_service.py`)

Create the directory `tests/test_services/` if it doesn't exist:

```bash
mkdir -p tests/test_services
```

```tests/test_services/test_exercise_service.py
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.exercise import Exercise
from src.schemas.exercise import ExerciseCreate
from src.services.exercise_service import (
    create_exercise,
    delete_exercise,
    get_exercise,
    get_exercises,
    search_exercises,
)


@pytest.mark.asyncio
async def test_create_exercise(db_session: Session):
    """
    Test creating a new exercise.
    """
    exercise_data = ExerciseCreate(name_en="Test Exercise", name_pt="Exercício Teste", category="Chest")
    exercise = await create_exercise(exercise_data, db_session)
    assert exercise.name_en == "Test Exercise"
    assert exercise.name_pt == "Exercício Teste"
    assert exercise.id is not None

    db_exercise = db_session.query(Exercise).filter(Exercise.id == exercise.id).first()
    assert db_exercise is not None
    assert db_exercise.name_en == "Test Exercise"


@pytest.mark.asyncio
async def test_get_exercises(db_session: Session, sample_exercise):
    """
    Test retrieving all exercises.
    """
    exercises = await get_exercises(db_session)
    assert len(exercises) >= 1
    assert sample_exercise.name_en in [e.name_en for e in exercises]


@pytest.mark.asyncio
async def test_get_exercise(db_session: Session, sample_exercise):
    """
    Test retrieving a single exercise by its ID.
    """
    exercise = await get_exercise(sample_exercise.id, db_session)
    assert exercise is not None
    assert exercise.id == sample_exercise.id
    assert exercise.name_en == sample_exercise.name_en


@pytest.mark.asyncio
async def test_get_exercise_not_found(db_session: Session):
    """
    Test retrieving a non-existent exercise.
    """
    with pytest.raises(HTTPException) as exc_info:
        await get_exercise(999, db_session)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_search_exercises(db_session: Session, sample_exercise):
    """
    Test searching for exercises.
    """
    # Test with a query that should find the exercise by English name
    results = await search_exercises("Test Ex", db_session)
    assert len(results) >= 1
    assert sample_exercise.name_en in [e.name_en for e in results]

    # Test with a query that should find the exercise by Portuguese name
    results = await search_exercises("Teste", db_session)
    assert len(results) >= 1
    assert sample_exercise.name_pt in [e.name_pt for e in results]

    # Test with a query that should find the exercise by category
    results = await search_exercises("Chest", db_session)
    assert len(results) >= 1
    assert sample_exercise.category in [e.category for e in results]

    # Test with a query that should not find any exercise
    results = await search_exercises("NonExistentExercise", db_session)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_delete_exercise(db_session: Session, sample_exercise):
    """
    Test deleting an exercise.
    """
    exercise_id = sample_exercise.id
    await delete_exercise(exercise_id, db_session)

    # Verify it's deleted
    with pytest.raises(HTTPException) as exc_info:
        await get_exercise(exercise_id, db_session)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_exercise_not_found(db_session: Session):
    """
    Test deleting a non-existent exercise.
    """
    with pytest.raises(HTTPException) as exc_info:
        await delete_exercise(999, db_session)
    assert exc_info.value.status_code == 404
```

### 8.2. Session Service Tests (`tests/test_services/test_session_service.py`)

```tests/test_services/test_session_service.py
import datetime

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.enums import UnitEnum
from src.schemas.exercise import ExerciseRead
from src.schemas.exercise_session import ExerciseSessionCreate
from src.schemas.session import SessionCreate
from src.schemas.set import SetCreate
from src.services.session_service import (
    create_session,
    delete_session,
    get_session,
    get_sessions,
)


@pytest.mark.asyncio
async def test_create_session(db_session: Session, sample_exercise: ExerciseRead):
    """
    Test creating a new session with nested exercises and sets.
    """
    set_data = SetCreate(reps=10, weight=100, unit=UnitEnum.KG)
    exercise_session_data = ExerciseSessionCreate(
        exercise_id=sample_exercise.id, sets=[set_data]
    )
    session_data = SessionCreate(
        exercise_sessions=[exercise_session_data],
    )

    session = await create_session(session_data, db_session)

    assert session.id is not None
    assert len(session.exercise_sessions) == 1
    assert session.exercise_sessions[0].exercise.id == sample_exercise.id
    assert len(session.exercise_sessions[0].sets) == 1
    assert session.exercise_sessions[0].sets[0].reps == 10
    assert session.exercise_sessions[0].sets[0].weight == 100


@pytest.mark.asyncio
async def test_get_sessions(db_session: Session):
    """
    Test retrieving all sessions.
    """
    # Create a session to ensure there's at least one
    session_data = SessionCreate(
        exercise_sessions=[]
    )
    await create_session(session_data, db_session)

    sessions = await get_sessions(db_session)
    assert len(sessions) >= 1


@pytest.mark.asyncio
async def test_get_session(db_session: Session, sample_exercise: ExerciseRead):
    """
    Test retrieving a single session by its ID.
    """
    set_data = SetCreate(reps=12, weight=50, unit=UnitEnum.STACKS)
    exercise_session_data = ExerciseSessionCreate(
        exercise_id=sample_exercise.id, sets=[set_data]
    )
    session_data = SessionCreate(
        exercise_sessions=[exercise_session_data],
    )
    created_session = await create_session(session_data, db_session)

    retrieved_session = await get_session(created_session.id, db_session)
    assert retrieved_session is not None
    assert retrieved_session.id == created_session.id
    assert len(retrieved_session.exercise_sessions) == 1
    assert retrieved_session.exercise_sessions[0].sets[0].reps == 12


@pytest.mark.asyncio
async def test_get_session_not_found(db_session: Session):
    """
    Test retrieving a non-existent session.
    """
    with pytest.raises(HTTPException) as exc_info:
        await get_session(999, db_session)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_session(db_session: Session):
    """
    Test deleting a session.
    """
    session_data = SessionCreate(
        exercise_sessions=[]
    )
    session_to_delete = await create_session(session_data, db_session)
    session_id = session_to_delete.id

    await delete_session(session_id, db_session)

    with pytest.raises(HTTPException) as exc_info:
        await get_session(session_id, db_session)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_session_not_found(db_session: Session):
    """
    Test deleting a non-existent session.
    """
    with pytest.raises(HTTPException) as exc_info:
        await delete_session(999, db_session)
    assert exc_info.value.status_code == 404
```

### 8.3. Template Service Tests (`tests/test_services/test_template_service.py`)

```tests/test_services/test_template_service.py
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.exercise_session import ExerciseSession
from src.schemas.exercise import ExerciseRead
from src.schemas.exercise_session import ExerciseSessionCreate
from src.schemas.template import TemplateCreate
from src.services.template_service import (
    create_template,
    delete_template,
    get_template,
    get_templates,
)
from tests.conftest import create_test_exercise


@pytest.mark.asyncio
async def test_create_template(db_session: Session, sample_exercise: ExerciseRead):
    """
    Test creating a new template with exercises.
    """
    ex2 = await create_test_exercise(db_session, "Another exercise", "Outro exercício", "Back")
    exercise_session_data = ExerciseSessionCreate(
        exercise_id=sample_exercise.id, sets=[]
    )
    exercise_session_data_2 = ExerciseSessionCreate(
        exercise_id=ex2.id, sets=[]
    )
    template_data = TemplateCreate(
        name="Test Template",
        exercise_sessions=[exercise_session_data, exercise_session_data_2]
    )
    template = await create_template(template_data, db_session)

    assert template.name == "Test Template"
    assert template.id is not None
    assert len(template.exercise_sessions) == 2
    assert sample_exercise.id in [es.exercise_id for es in template.exercise_sessions]
    assert ex2.id in [es.exercise_id for es in template.exercise_sessions]


@pytest.mark.asyncio
async def test_create_template_with_nonexistent_exercise(db_session: Session):
    """
    Test creating a template with a non-existent exercise ID.
    """
    exercise_session_data = ExerciseSessionCreate(
        exercise_id=999, sets=[]
    )
    template_data = TemplateCreate(name="Bad Template", exercise_sessions=[exercise_session_data])
    with pytest.raises(HTTPException) as exc_info:
        await create_template(template_data, db_session)
    assert exc_info.value.status_code == 404
    assert "One or more exercises not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_templates(db_session: Session, sample_exercise: ExerciseRead):
    """
    Test retrieving all templates.
    """
    exercise_session_data = ExerciseSessionCreate(
        exercise_id=sample_exercise.id, sets=[]
    )
    template_data = TemplateCreate(
        name="Template for get all", exercise_sessions=[exercise_session_data]
    )
    await create_template(template_data, db_session)

    templates = await get_templates(db_session)
    assert len(templates) >= 1


@pytest.mark.asyncio
async def test_get_template(db_session: Session, sample_exercise: ExerciseRead):
    """
    Test retrieving a single template by its ID.
    """
    exercise_session_data = ExerciseSessionCreate(
        exercise_id=sample_exercise.id, sets=[]
    )
    template_data = TemplateCreate(
        name="Specific Template", exercise_sessions=[exercise_session_data]
    )
    created_template = await create_template(template_data, db_session)

    retrieved_template = await get_template(created_template.id, db_session)
    assert retrieved_template is not None
    assert retrieved_template.id == created_template.id
    assert retrieved_template.name == "Specific Template"
    assert len(retrieved_template.exercise_sessions) == 1
    assert retrieved_template.exercise_sessions[0].exercise.id == sample_exercise.id


@pytest.mark.asyncio
async def test_get_template_not_found(db_session: Session):
    """
    Test retrieving a non-existent template.
    """
    with pytest.raises(HTTPException) as exc_info:
        await get_template(999, db_session)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_template(db_session: Session, sample_exercise: ExerciseRead):
    """
    Test deleting a template.
    """
    exercise_session_data = ExerciseSessionCreate(
        exercise_id=sample_exercise.id, sets=[]
    )
    template_data = TemplateCreate(
        name="To Be Deleted Template", exercise_sessions=[exercise_session_data]
    )
    template_to_delete = await create_template(template_data, db_session)
    template_id = template_to_delete.id

    await delete_template(template_id, db_session)

    with pytest.raises(HTTPException) as exc_info:
        await get_template(template_id, db_session)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_template_not_found(db_session: Session):
    """
    Test deleting a non-existent template.
    """
    with pytest.raises(HTTPException) as exc_info:
        await delete_template(999, db_session)
    assert exc_info.value.status_code == 404
```

---

### Testing Point: Step 8

After creating the unit tests, you can run them to verify your service layer.

```bash
pytest tests/test_services/
```
You should see output indicating all tests passed. This confirms your service logic is correct in isolation.

---

## Step 9: Integration Tests for API Endpoints

Integration tests verify that the different components of your application (routers, services, database) work correctly together.

### 9.1. Exercises API Tests (`tests/test_api/test_exercises.py`)

Create the directory `tests/test_api/` if it doesn't exist:

```bash
mkdir -p tests/test_api
```

```tests/test_api/test_exercises.py
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from src.models import Exercise
from src.schemas import ExerciseRead

pytestmark = pytest.mark.asyncio


async def test_create_exercise(client: AsyncClient, db_session: Session):
    """Test creating a new exercise."""
    response = await client.post(
        "/api/v1/exercises/",
        json={"name_en": "Test Exercise", "name_pt": "Exercício Teste", "category": "Chest"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name_en"] == "Test Exercise"
    assert data["name_pt"] == "Exercício Teste"
    assert "id" in data

    exercise = db_session.get(Exercise, data["id"])
    assert exercise is not None
    assert exercise.name_en == "Test Exercise"


async def test_get_all_exercises(client: AsyncClient, sample_exercise: ExerciseRead):
    """Test retrieving all exercises."""
    response = await client.get("/api/v1/exercises/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(e["id"] == sample_exercise.id for e in data)


async def test_get_exercise_by_id(client: AsyncClient, sample_exercise: ExerciseRead):
    """Test retrieving a specific exercise by its ID."""
    response = await client.get(f"/api/v1/exercises/{sample_exercise.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_exercise.id
    assert data["name_en"] == sample_exercise.name_en


async def test_get_exercise_not_found(client: AsyncClient):
    """Test that a 404 is returned for a non-existent exercise."""
    response = await client.get("/api/v1/exercises/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Exercise not found"}


async def test_search_exercises(client: AsyncClient, sample_exercise: ExerciseRead):
    """Test searching for exercises."""
    response = await client.get(f"/api/v1/exercises/search?query={sample_exercise.name_en[:5]}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(e["id"] == sample_exercise.id for e in data)


async def test_search_exercises_no_results(client: AsyncClient):
    """Test that search returns an empty list for no matches."""
    response = await client.get("/api/v1/exercises/search?query=nonexistentexercisename")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


async def test_delete_exercise(
    client: AsyncClient, sample_exercise: ExerciseRead, db_session: Session
):
    """Test deleting an exercise."""
    response = await client.delete(f"/api/v1/exercises/{sample_exercise.id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Exercise deleted successfully"}

    exercise = db_session.get(Exercise, sample_exercise.id)
    assert exercise is None

    response = await client.get(f"/api/v1/exercises/{sample_exercise.id}")
    assert response.status_code == 404


async def test_delete_exercise_not_found(client: AsyncClient):
    """Test that deleting a non-existent exercise returns a 404."""
    response = await client.delete("/api/v1/exercises/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Exercise not found"}
```

### 9.2. Sessions API Tests (`tests/test_api/test_sessions.py`)

```tests/test_api/test_sessions.py
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from src.models import Session as SessionModel
from src.models.enums import UnitEnum
from src.schemas import ExerciseRead, ExerciseSessionCreate, SetCreate, SessionCreate

pytestmark = pytest.mark.asyncio


async def test_create_session(
    client: AsyncClient, db_session: Session, sample_exercise: ExerciseRead
):
    """Test creating a session with nested exercises and sets."""
    set_data = SetCreate(reps=10, weight=100, unit=UnitEnum.KG)
    exercise_session_data = ExerciseSessionCreate(
        exercise_id=sample_exercise.id, sets=[set_data]
    )
    session_data = SessionCreate(
        exercise_sessions=[exercise_session_data],
    )
    response = await client.post("/api/v1/sessions/", json=session_data.model_dump())
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert len(data["exercise_sessions"]) == 1
    assert data["exercise_sessions"][0]["exercise"]["id"] == sample_exercise.id
    assert len(data["exercise_sessions"][0]["sets"]) == 1
    assert data["exercise_sessions"][0]["sets"][0]["reps"] == 10

    session = db_session.get(SessionModel, data["id"])
    assert session is not None
    assert len(session.exercise_sessions) == 1
    assert len(session.exercise_sessions[0].sets) == 1


async def test_get_all_sessions(client: AsyncClient, sample_exercise: ExerciseRead):
    """Test retrieving all sessions."""
    session_data = SessionCreate(
        exercise_sessions=[ExerciseSessionCreate(exercise_id=sample_exercise.id, sets=[])]
    )
    await client.post("/api/v1/sessions/", json=session_data.model_dump())

    response = await client.get("/api/v1/sessions/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(s["id"] for s in data) # Check if any session exists and has an ID


async def test_get_session_by_id(client: AsyncClient, sample_exercise: ExerciseRead):
    """Test retrieving a specific session by ID."""
    session_data = SessionCreate(
        exercise_sessions=[ExerciseSessionCreate(exercise_id=sample_exercise.id, sets=[])]
    )
    create_response = await client.post("/api/v1/sessions/", json=session_data.model_dump())
    session_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id


async def test_get_session_not_found(client: AsyncClient):
    """Test that a 404 is returned for a non-existent session."""
    response = await client.get("/api/v1/sessions/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Session not found"}


async def test_delete_session(
    client: AsyncClient, db_session: Session, sample_exercise: ExerciseRead
):
    """Test deleting a session."""
    session_data = SessionCreate(
        exercise_sessions=[ExerciseSessionCreate(exercise_id=sample_exercise.id, sets=[])]
    )
    create_response = await client.post("/api/v1/sessions/", json=session_data.model_dump())
    session_id = create_response.json()["id"]

    delete_response = await client.delete(f"/api/v1/sessions/{session_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Session deleted successfully"}

    session = db_session.get(SessionModel, session_id)
    assert session is None

    get_response = await client.get(f"/api/v1/sessions/{session_id}")
    assert get_response.status_code == 404


async def test_delete_session_not_found(client: AsyncClient):
    """Test that deleting a non-existent session returns a 404."""
    response = await client.delete("/api/v1/sessions/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Session not found"}
```

### 9.3. Templates API Tests (`tests/test_api/test_templates.py`)

```tests/test_api/test_templates.py
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from src.models import Template as TemplateModel
from src.schemas import ExerciseRead, ExerciseSessionCreate, TemplateCreate

pytestmark = pytest.mark.asyncio


async def test_create_template(
    client: AsyncClient, db_session: Session, sample_exercise: ExerciseRead
):
    """Test creating a new template."""
    template_data = TemplateCreate(
        name="Test Template",
        exercise_sessions=[ExerciseSessionCreate(exercise_id=sample_exercise.id, sets=[])],
    )
    response = await client.post("/api/v1/templates/", json=template_data.model_dump())
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Template"
    assert "id" in data
    assert len(data["exercise_sessions"]) == 1
    assert data["exercise_sessions"][0]["exercise"]["id"] == sample_exercise.id

    template = db_session.get(TemplateModel, data["id"])
    assert template is not None
    assert template.name == "Test Template"
    assert len(template.exercise_sessions) == 1
    assert template.exercise_sessions[0].exercise.id == sample_exercise.id


async def test_create_template_with_nonexistent_exercise(client: AsyncClient):
    """Test creating a template with an exercise that does not exist."""
    template_data = TemplateCreate(
        name="Bad Template",
        exercise_sessions=[ExerciseSessionCreate(exercise_id=9999, sets=[])],
    )
    response = await client.post("/api/v1/templates/", json=template_data.model_dump())
    assert response.status_code == 404
    assert "One or more exercises not found" in response.json()["detail"]


async def test_get_all_templates(client: AsyncClient, sample_exercise: ExerciseRead):
    """Test retrieving all templates."""
    template_data = TemplateCreate(
        name="Template for GET",
        exercise_sessions=[ExerciseSessionCreate(exercise_id=sample_exercise.id, sets=[])],
    )
    await client.post("/api/v1/templates/", json=template_data.model_dump())

    response = await client.get("/api/v1/templates/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(t["name"] == "Template for GET" for t in data)


async def test_get_template_by_id(client: AsyncClient, sample_exercise: ExerciseRead):
    """Test retrieving a specific template by ID."""
    template_data = TemplateCreate(
        name="Template to Get",
        exercise_sessions=[ExerciseSessionCreate(exercise_id=sample_exercise.id, sets=[])],
    )
    create_response = await client.post("/api/v1/templates/", json=template_data.model_dump())
    template_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/templates/{template_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == template_id
    assert data["name"] == "Template to Get"


async def test_get_template_not_found(client: AsyncClient):
    """Test that a 404 is returned for a non-existent template."""
    response = await client.get("/api/v1/templates/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Template not found"}


async def test_delete_template(
    client: AsyncClient, db_session: Session, sample_exercise: ExerciseRead
):
    """Test deleting a template."""
    template_data = TemplateCreate(
        name="To Be Deleted Template", exercise_sessions=[ExerciseSessionCreate(exercise_id=sample_exercise.id, sets=[])]
    )
    create_response = await client.post("/api/v1/templates/", json=template_data.model_dump())
    template_id = create_response.json()["id"]

    delete_response = await client.delete(f"/api/v1/templates/{template_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Template deleted successfully"}

    template = db_session.get(TemplateModel, template_id)
    assert template is None

    get_response = await client.get(f"/api/v1/templates/{template_id}")
    assert get_response.status_code == 404


async def test_delete_template_not_found(client: AsyncClient):
    """Test that deleting a non-existent template returns a 404."""
    response = await client.delete("/api/v1/templates/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Template not found"}


async def test_template_usage_workflow(
    client: AsyncClient, sample_exercise: ExerciseRead
):
    """Test a typical workflow of using a template to create a session."""
    # 1. Create a template
    template_data = TemplateCreate(
        name="Workflow Template",
        exercise_sessions=[ExerciseSessionCreate(exercise_id=sample_exercise.id, sets=[])],
    )
    create_template_response = await client.post("/api/v1/templates/", json=template_data.model_dump())
    assert create_template_response.status_code == 201
    template = create_template_response.json()
    template_id = template["id"]

    # 2. Get the template to get exercise details
    get_template_response = await client.get(f"/api/v1/templates/{template_id}")
    assert get_template_response.status_code == 200
    template_details = get_template_response.json()

    # 3. Use template to create a new session
    session_exercises = [
        {
            "exercise_id": exercise_session["exercise"]["id"],
            "sets": [{"reps": 5, "weight": 50, "unit": "kg"}],
        }
        for exercise_session in template_details["exercise_sessions"]
    ]

    session_data = SessionCreate(
        exercise_sessions=session_exercises,
    )
    create_session_response = await client.post("/api/v1/sessions/", json=session_data.model_dump())
    assert create_session_response.status_code == 201
    session = create_session_response.json()
    assert len(session["exercise_sessions"]) == 1
    assert session["exercise_sessions"][0]["exercise"]["id"] == sample_exercise.id
```

---

### Testing Point: Step 9

After creating the integration tests, run them to verify your API endpoints.

```bash
pytest tests/test_api/
```
You should see output indicating all tests passed. This confirms your API is functioning as expected end-to-end.

---

## Step 10: Docker Configuration

Dockerize your application for consistent development and production environments.

### 10.1. Dockerfile

```Dockerfile
# Stage 1: Builder - Installs dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Create and activate a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runner - Creates the final image
FROM python:3.11-slim as runner

WORKDIR /app

# Create a non-root user for security
RUN addgroup --system app && adduser --system --ingroup app app

# Copy virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code and alembic configuration
COPY ./src ./src
COPY alembic.ini .
COPY alembic ./alembic

# Set correct ownership for the app directory
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Add the virtual environment to the PATH
ENV PATH="/opt/venv/bin:$PATH"

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 10.2. `.dockerignore`

```.dockerignore
# Git and Docker files
.git
.gitignore
.dockerignore
Dockerfile
docker-compose.yml
docker-compose.prod.yml

# Environment files
.env
.env.example
secrets/

# Python caches
__pycache__/
*.py[cod]
*.so

# Virtual environments
.venv
env/
venv/
ENV/

# Test and coverage reports
.pytest_cache/
.coverage
htmlcov/
test.db*

# IDE settings
.idea/
.vscode/

# Build artifacts
build/
dist/
*.egg-info/
```

### 10.3. `docker-compose.yml` (Development)

```docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./src:/app/src
      - ./alembic:/app/alembic
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
    env_file:
      - .env
    depends_on:
      - db
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    env_file:
      - .env
    ports:
      - "5432:5432"
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```

### 10.4. `docker-compose.prod.yml` (Production)

```docker-compose.prod.yml
version: '3.8'

# This Docker Compose file is intended for production deployments.
# It uses Docker secrets for managing sensitive information like database credentials.

services:
  # The API service, running the FastAPI application.
  api:
    build:
      context: .
      dockerfile: Dockerfile
    command: >
      sh -c "
      export DATABASE_URL=\"postgresql://$(cat /run/secrets/postgres_user):$(cat /run/secrets/postgres_password)@db:5432/$(cat /run/secrets/postgres_db)\" &&
      alembic upgrade head &&
      uvicorn src.main:app --host 0.0.0.0 --port 8000
      "
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    networks:
      - app-network
    secrets:
      - postgres_user
      - postgres_password
      - postgres_db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  # The PostgreSQL database service.
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      POSTGRES_USER_FILE: /run/secrets/postgres_user
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
      POSTGRES_DB_FILE: /run/secrets/postgres_db
    ports:
      - "5432:5432"
    networks:
      - app-network
    secrets:
      - postgres_user
      - postgres_password
      - postgres_db
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$(cat /run/secrets/postgres_user) -d $$(cat /run/secrets/postgres_db)"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  # Persistent volume for PostgreSQL data.
  postgres_data:

networks:
  # Shared network for services to communicate.
  app-network:
    driver: bridge

secrets:
  # Docker secrets for database credentials.
  # These files should be created on the host machine before deploying.
  postgres_user:
    file: ./secrets/postgres_user.txt
  postgres_password:
    file: ./secrets/postgres_password.txt
  postgres_db:
    file: ./secrets/postgres_db.txt
```

---

### Testing Point: Step 10

1.  **Create secrets files**: Docker Compose uses these for the production environment.
    ```bash
    mkdir -p secrets
    echo "user" > secrets/postgres_user.txt
    echo "password" > secrets/postgres_password.txt
    echo "progresstracker_db" > secrets/postgres_db.txt
    ```

2.  **Build and Run Development Containers**:
    ```bash
    docker-compose up --build -d
    ```
    This command will build your Docker images and start the `api` and `db` services in detached mode.

3.  **Verify Containers are Running**:
    ```bash
    docker ps
    ```
    You should see output indicating your `api` and `db` containers are up.

4.  **Test Endpoint with Curl (from host machine)**:
    ```bash
    curl http://localhost:8000/
    ```
    You should receive the welcome message: `{"message":"Welcome to the Progressive Overload Tracker API"}`. This confirms your FastAPI app is running inside Docker.

5.  **Stop Containers (Optional)**:
    ```bash
    docker-compose down
    ```

---

## Step 11: Development Tools and Configuration

Add a `Makefile` for common development commands and `pre-commit` hooks for code quality.

### 11.1. `Makefile`

```Makefile
.PHONY: help install test run migrate seed-db lint format type-check

help:
	@echo "Commands:"
	@echo "  install      : Install dependencies and pre-commit hooks."
	@echo "  test         : Run tests."
	@echo "  run          : Run the FastAPI application."
	@echo "  migrate      : Apply database migrations."
	@echo "  seed-db      : Seed the database with initial data."
	@echo "  lint         : Run linters via pre-commit."
	@echo "  format       : Format code with black and isort."
	@echo "  type-check   : Run mypy for type checking."

install:
	pip install -r requirements.txt
	pre-commit install

test:
	pytest

run:
	uvicorn src.main:app --reload

migrate:
	alembic upgrade head

seed-db:
	python scripts/seed_database.py

lint:
	pre-commit run --all-files

format:
	black .
	isort .

type-check:
	mypy src
```

### 11.2. `pre-commit-config.yaml`

```.pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]
  - repo: https://github.com/pycqa/flake8
    rev: 7.1.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-bugbear]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        args: [--ignore-missing-imports]
        additional_dependencies: [pydantic]
```

### 11.3. `setup.sh` (Initial Development Setup Script)

```setup.sh
#!/bin/bash
set -e

echo "This script will set up the development environment."

# Check for python3 and venv
if ! command -v python3 &> /dev/null
then
    echo "python3 could not be found. Please install Python 3."
    exit 1
fi

if ! python3 -m venv -h &> /dev/null
then
    echo "The 'venv' module is not available. Please install it."
    exit 1
fi

VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists."
fi

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Installing pre-commit hooks..."
pre-commit install

if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "NOTE: .env file created. Please review and update it with your local settings."
fi

echo ""
echo "Setup complete!"
echo "To activate the virtual environment, run: source $VENV_DIR/bin/activate"
```

---

### Testing Point: Step 11

You can test your development tools using the `Makefile` commands. Make sure you are in your activated virtual environment.

1.  **Run linters**:
    ```bash
    make lint
    ```
    This will run `flake8`. If there are no issues, it will exit silently (or with "All clear!" depending on pre-commit output). If there are linting errors, they will be displayed.

2.  **Run formatter**:
    ```bash
    make format
    ```
    This will run `black` and `isort`. If your code is not formatted, these tools will reformat it. Run `git status` afterward; you should see modified files if reformatting occurred.

3.  **Run type checker**:
    ```bash
    make type-check
    ```
    This will run `mypy`. If there are no type errors, it will exit silently.

---

## Step 12: Project Documentation

Add documentation files for your project.

### 12.1. Update `README.md`

```README.md
# Progressive Overload Tracker API

This is the backend API for the Progressive Overload Tracker application. It's built with FastAPI and provides endpoints for managing exercises, workout sessions, and templates.

## Quick Start

The easiest way to get the application running is with Docker.

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Set up environment variables:**
    Copy the example environment file and fill in your details.
    ```bash
    cp .env.example .env
    ```

3.  **Build and run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```

The API will be available at `http://localhost:8000`.

## API Documentation

The API documentation is automatically generated and available at:

-   **Swagger UI:** [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
-   **ReDoc:** [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)

For more detailed documentation, see the `docs/` directory:
-   [API Endpoints](./docs/api.md)
-   [Database Schema](./docs/database.md)

## Development Setup

For local development without Docker:

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up pre-commit hooks:**
    ```bash
    pre-commit install
    ```

4.  **Run the application:**
    ```bash
    uvicorn src.main:app --reload
    ```

See [Development Workflow](./docs/development.md) for more details.

## Testing

To run the test suite:

```bash
pytest
```

This will run all tests using an in-memory SQLite database.

## Deployment

A `Dockerfile` and `docker-compose.prod.yml` are provided for production deployments. You should adjust these files to suit your production environment, especially concerning database connections, secret management, and networking.
```

### 12.2. `CONTRIBUTING.md`

```CONTRIBUTING.md
# Contributing to Progressive Overload Tracker

We welcome contributions to the Progressive Overload Tracker! Please follow these guidelines to ensure a smooth collaboration process.

## Development Setup

1.  Fork the repository and clone it locally.
2.  Set up your local development environment as described in the [Development Setup](./README.md#development-setup) section of the README.
3.  Create a new branch for your feature or bug fix: `git checkout -b feature/your-feature-name` or `bugfix/your-bug-fix`.

## Code Style

This project uses `black` for code formatting and `ruff` for linting, managed via `pre-commit`. Please ensure you have `pre-commit` installed and set up:

```bash
pip install pre-commit
pre-commit install
```

Before you commit, `pre-commit` will automatically format and lint your code.

## Pull Request Process

1.  Ensure that all tests pass by running `pytest`.
2.  Update the `README.md` or other documentation if your changes affect them.
3.  Push your changes to your fork and submit a pull request to the `main` branch of the upstream repository.
4.  Provide a clear title and description for your pull request, explaining the changes and why they are needed.
5.  Your pull request will be reviewed, and you may be asked to make changes before it is merged.

Thank you for your contributions!
```

### 12.3. `docs/` Folder

```bash
mkdir -p docs
```

```docs/api.md
# API Endpoint Documentation

This document provides a high-level overview of the API endpoints. For interactive documentation, please visit the [Swagger UI](/api/v1/docs) or [ReDoc](/api/v1/redoc).

All endpoints are prefixed with `/api/v1`.

## Exercises (`/exercises`)

-   `GET /`: Retrieve all exercises.
-   `POST /`: Create a new exercise.
-   `GET /search`: Search for exercises by name.
-   `GET /{exercise_id}`: Retrieve a specific exercise by its ID.
-   `DELETE /{exercise_id}`: Delete an exercise by its ID.

## Sessions (`/sessions`)

-   `GET /`: Retrieve all workout sessions.
-   `POST /`: Create a new workout session.
-   `GET /{session_id}`: Retrieve a specific session by its ID.
-   `DELETE /{session_id}`: Delete a session by its ID.

## Templates (`/templates`)

-   `GET /`: Retrieve all workout templates.
-   `POST /`: Create a new workout template.
-   `GET /{template_id}`: Retrieve a specific template by its ID.
-   `DELETE /{template_id}`: Delete a template by its ID.
```

```docs/database.md
# Database Schema

This document describes the database schema for the Progressive Overload Tracker. The application uses SQLAlchemy as its ORM.

## Models

### `Exercise`
Represents a single type of exercise (e.g., Bench Press, Squat).

-   `id`: Primary key.
-   `name_en`: English name of the exercise.
-   `name_pt`: Portuguese name of the exercise.
-   `image_url`: URL to an image or video of the exercise.
-   `category`: Main muscle group (e.g., Chest, Back, Legs).
-   `subcategory`: More specific muscle group (e.g., Triceps, Biceps).
-   `equipment`: Equipment needed (e.g., Barbell, Dumbbell).

### `Session`
Represents a single workout session on a specific date.

-   `id`: Primary key.
-   `date`: The date and time of the workout session.

### `Template`
Represents a reusable workout template.

-   `id`: Primary key.
-   `name`: Name of the template (e.g., "Push Day").

### `ExerciseSession`
A linking table that represents an exercise performed within a `Session` or defined in a `Template`.

-   `id`: Primary key.
-   `exercise_id`: Foreign key to the `Exercise`.
-   `session_id`: Foreign key to the `Session` (nullable).
-   `template_id`: Foreign key to the `Template` (nullable).

### `Set`
Represents a single set of an exercise within an `ExerciseSession`.

-   `id`: Primary key.
-   `weight`: Weight used for the set.
-   `reps`: Number of repetitions performed.
-   `unit`: Unit of weight (`kg`, `lbs`, `stacks`).
-   `exercise_session_id`: Foreign key to the `ExerciseSession`.

## Migrations

Database migrations are managed using [Alembic](https://alembic.sqlalchemy.org/). To create a new migration after changing a model, run:

```bash
alembic revision --autogenerate -m "Your migration message"
```

To apply migrations:

```bash
alembic upgrade head
```
```

```docs/development.md
# Development Workflow

This guide provides details for setting up and working on the project locally.

## Initial Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file by copying the example file:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and set `DATABASE_URL`. For local development, you can use SQLite:
    ```
    DATABASE_URL="sqlite:///./test.db"
    ```

5.  **Set up pre-commit hooks:**
    This will ensure your code is formatted and linted before each commit.
    ```bash
    pre-commit install
    ```

## Running the Application

To run the FastAPI server with live reloading:

```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Database Migrations

We use Alembic to manage database schema changes.

-   **To generate a new migration script after model changes:**
    ```bash
    alembic revision --autogenerate -m "A descriptive message about the changes"
    ```
    Review the generated script in `alembic/versions/` before committing.

-   **To apply migrations to your database:**
    ```bash
    alembic upgrade head
    ```

-   **To downgrade:**
    ```bash
    alembic downgrade -1
    ```

## Seeding the Database

A script is provided to seed the database with initial exercise data.

```bash
python scripts/seed_database.py
```

This is useful for setting up a new development environment.
```

```docs/troubleshooting.md
# Troubleshooting Guide

This guide lists common problems and their solutions.

## Docker Issues

### `docker-compose up` fails with a network error
-   **Problem:** Docker may have issues with networking, or another service might be using the required ports.
-   **Solution:**
    1.  Ensure no other service is running on port 8000 (or the port configured for the app).
    2.  Try restarting the Docker daemon.
    3.  Run `docker-compose down -v` to remove volumes and networks, then try `docker-compose up` again.

## Local Development Issues

### `ModuleNotFoundError`
-   **Problem:** A required Python package is not installed.
-   **Solution:**
    1.  Make sure your virtual environment is activated.
    2.  Run `pip install -r requirements.txt` to install all dependencies.

### Database connection errors
-   **Problem:** The application cannot connect to the database specified in `DATABASE_URL`.
-   **Solution:**
    1.  Check that your `.env` file exists and the `DATABASE_URL` is correct.
    2.  If using a database server like PostgreSQL, ensure it is running and accessible.
    3.  For SQLite, ensure the path to the database file is correct and the directory is writable.

### `pre-commit` hook fails
-   **Problem:** `black` or `ruff` fails, preventing a commit.
-   **Solution:**
    -   This is expected behavior. The tools have modified your files.
    -   Run `git add .` to stage the changes made by the hooks, then try committing again.

## Alembic Migration Errors

### `Target database is not up to date`
-   **Problem:** You are trying to generate a new migration, but the database schema does not match the latest migration file.
-   **Solution:**
    -   Run `alembic upgrade head` to apply all pending migrations to your database.
```

---

### Testing Point: Step 12

This step focuses on documentation. There's no executable code to test here. Your primary verification will be to visually inspect the created and modified files to ensure the content is as expected and the markdown renders correctly.

---

## Final Steps to Run and Test

You now have a complete, well-structured FastAPI application. Here's a summary of the remaining steps to get it fully running and verify its functionality:

1.  **Run `setup.sh`**:
    This script will create a virtual environment, install dependencies, and set up pre-commit hooks.
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```
    Follow the prompts. It will create a `.env` file for you based on `.env.example`.

2.  **Apply Database Migrations**:
    This creates the tables defined by your models in the database.
    ```bash
    alembic upgrade head
    ```

3.  **Seed the Database**:
    Populate your database with initial exercise data.
    ```bash
    python scripts/seed_database.py
    ```

4.  **Run Tests (Unit and Integration)**:
    You can run all tests or specific groups of tests.
    *   To run all unit tests for services:
        ```bash
        pytest tests/test_services/
        ```
    *   To run all integration tests for API endpoints:
        ```bash
        pytest tests/test_api/
        ```
    *   To run all tests:
        ```bash
        pytest
        ```

5.  **Run the Application (Local Development)**:
    Start the FastAPI development server.
    ```bash
    uvicorn src.main:app --reload
    ```
    Your API will be accessible at `http://localhost:8000`. You can visit `http://localhost:8000/api/v1/docs` in your browser to see the interactive API documentation (Swagger UI).

6.  **Test Backend is Working (Using a helper script)**:
    We've also created a small script to quickly check if your backend is responsive.

    Create the file `scripts/test_backend.sh`:
    ```scripts/test_backend.sh
    #!/bin/bash
    # A simple script to test if the backend is running.

    # The script will exit immediately if a command exits with a non-zero status.
    set -e

    echo "Pinging the root endpoint..."
    # We assume the server is running on localhost:8000 as per docker-compose.yml
    response=$(curl --silent --write-out "%{http_code}" --output /dev/null http://localhost:8000/)

    if [ "$response" -eq 200 ]; then
      echo "Backend is up and running. Received HTTP 200 OK."
      exit 0
    else
      echo "Backend is not responding correctly. Received HTTP $response."
      exit 1
    fi
    ```
    Make it executable and run it:
    ```bash
    chmod +x scripts/test_backend.sh
    ./scripts/test_backend.sh
