"""Pytest fixtures: env defaults + ephemeral postgres + Alembic upgrade + async client.

Source: D-11, D-13, RESEARCH "Test Infrastructure".

Boot-order: this conftest runs BEFORE any `app.*` import (because pytest collects fixtures
first). We set required env vars here so importing `app.core.config` does not fail-fast on
missing SECRET_KEY/DATABASE_URL/etc.

The `test_engine` fixture creates/drops the `WellnessBuddy_test` DB and applies Alembic
migrations to head. Integration tests that need the schema depend on `test_engine`.

If Postgres is not reachable on localhost:5432 (developer running `pytest -k unit` without
docker compose up), the engine fixture raises a clear error — only integration tests using
`test_engine` are affected.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator, Iterator
from typing import Any

# IMPORTANT: env defaults must be set BEFORE any `app.*` import below.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://wnbd:WnBd4321%40@localhost:5432/WellnessBuddy_test",
)
os.environ.setdefault(
    "SECRET_KEY",
    "test-secret-key-32-bytes-minimum-padding-padding",
)
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
os.environ.setdefault("ADMIN_EMAIL", "admin@test.local")
os.environ.setdefault("AI_PROVIDER", "null")
os.environ.setdefault("LOG_LEVEL", "WARNING")
os.environ.setdefault("APP_VERSION", "0.1.0-test")
os.environ.setdefault("BUILD_HASH", "testhash")

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

TEST_DATABASE_URL = os.environ["DATABASE_URL"]


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """Single asyncio loop for the session — required by pytest-asyncio + session-scoped engine."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncIterator[AsyncEngine]:
    """Drop+create `WellnessBuddy_test`, run `alembic upgrade head`, yield engine."""
    import asyncpg
    from alembic import command
    from alembic.config import Config

    # Connect to default 'postgres' DB to create/drop the test DB.
    sys_dsn_async = TEST_DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
    base, _, _ = sys_dsn_async.rpartition("/")
    sys_dsn = f"{base}/postgres"

    sys_conn = await asyncpg.connect(sys_dsn)
    try:
        await sys_conn.execute('DROP DATABASE IF EXISTS "WellnessBuddy_test"')
        await sys_conn.execute('CREATE DATABASE "WellnessBuddy_test"')
    finally:
        await sys_conn.close()

    # Alembic uses sync driver — strip +asyncpg for the migration command.
    sync_url = TEST_DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2") \
        if False else TEST_DATABASE_URL.replace("+asyncpg", "")
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", sync_url)
    # env.py reads settings.DATABASE_URL — async variant is fine since alembic env uses async_engine_from_config
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    command.upgrade(cfg, "head")

    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Per-test session that rolls back after use to keep DB clean between tests."""
    SessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest_asyncio.fixture
async def async_client() -> AsyncIterator[AsyncClient]:
    """Async HTTPX client mounted directly on the FastAPI ASGI app — no real network."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


# Helper for non-async tests that just need the imported app
@pytest.fixture
def app_instance() -> Any:
    """Return the FastAPI app instance (re-imports each test for isolation if config changed)."""
    from app.main import app

    return app
