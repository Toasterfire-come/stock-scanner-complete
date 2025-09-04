"""
Database connection and session management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://user:password@localhost/stockscanner'
)

# For production, use connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,  # Verify connections before using
    echo=False  # Set to True for SQL query logging in development
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Ensures proper cleanup and error handling.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        db.close()

def init_database():
    """
    Initialize database tables
    """
    from .models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

def get_db_session() -> Session:
    """
    Get a new database session for FastAPI dependency injection
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()