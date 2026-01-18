"""Database connection for scraper (synchronous)."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from scraper.config import settings

# Create sync engine (scraper doesn't need async)
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=0,
)

# Create session factory
SessionLocal = sessionmaker(
    engine,
    autocommit=False,
    autoflush=False,
)


@contextmanager
def get_db() -> Session:
    """Get database session context manager."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
