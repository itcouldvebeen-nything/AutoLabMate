"""
Database session management
Async SQLAlchemy session handling
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

# Database URL - SQLite for mock mode, PostgreSQL for production
DATABASE_URL = os.getenv(
    "POSTGRES_URL",
    "sqlite+aiosqlite:///./autolabmate.db"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("LOG_LEVEL") == "DEBUG",
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Declarative base (for models)
Base = declarative_base()


# ✅ Option 1: Use in FastAPI routes (dependency injection)
async def get_db_session_dep():
    """
    Dependency version for FastAPI.
    Usage:
        async def some_route(session: AsyncSession = Depends(get_db_session_dep)):
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


# ✅ Option 2: Direct use in app logic (context manager)
def get_db_session():
    """
    Direct-use version for scripts, agents, or manual DB access.
    Usage:
        async with get_db_session() as session:
            ...
    """
    return AsyncSessionLocal()


# Initialize and cleanup functions
async def init_db():
    """Initialize database tables"""
    from database.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections"""
    await engine.dispose()
