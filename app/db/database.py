"""Database connection and session management."""

import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# Support SQLite for local dev / testing when no PostgreSQL is available
_db_url = os.environ.get("DATABASE_URL", settings.database_url)

if _db_url.startswith("sqlite"):
    engine = create_async_engine(_db_url, echo=False)
else:
    engine = create_async_engine(
        _db_url,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:  # type: ignore[misc]
    async with async_session() as session:
        yield session


async def init_db() -> None:
    from app.db.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
