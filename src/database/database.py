from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from src.config import settings

# Connect to the database with connection pooling configuration
# Pool settings optimize for FastAPI async handling and production workloads
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using (detect stale connections)
    pool_size=10,  # Maximum number of permanent connections
    max_overflow=20,  # Maximum number of temporary connections beyond pool_size
    pool_recycle=3600,  # Recycle connections after 1 hour (prevents stale connections)
    echo=False,  # Set to True for SQL query logging (debugging)
)

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
