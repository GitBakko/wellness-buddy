"""SQLAlchemy 2 async engine + session factory.

Pool sized 15/10 per D-29 (research SUMMARY); re-evaluated Phase 4 with k6.
Source: RESEARCH Pattern 7, SQLAlchemy 2 async docs.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=15,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=settings.SQL_ECHO,
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: yields an async session and ensures cleanup."""
    async with SessionLocal() as session:
        yield session
