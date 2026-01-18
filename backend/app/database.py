"""Database configuration with SQLAlchemy and PostGIS support."""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# Create async engine with improved concurrency settings
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    future=True,
    pool_size=20,        # Active connection pool
    max_overflow=10,     # Allow 10 extra temporary connections during spikes (prevents crashes)
    pool_timeout=30,     # Wait 30s for a connection before failing
    pool_pre_ping=True,  # Verify connections before using them
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create declarative base
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency for getting async database session.

    Usage in FastAPI endpoints:
        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database - create all tables."""
    from sqlalchemy import text
    async with engine.begin() as conn:
        # Enable PostgreSQL extensions (no PostGIS needed)
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto;"))

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
