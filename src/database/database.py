from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from src.config import settings

# Connect to the database
engine = create_engine(settings.DATABASE_URL)

# Factory to create database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for model declarations
Base = declarative_base()

# Dependency that FastAPI will use to inject DB sessions
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
