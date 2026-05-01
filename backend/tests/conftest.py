"""Pytest fixtures: env defaults + ephemeral postgres + Alembic upgrade + async client.

Source: D-11, D-13, RESEARCH "Test Infrastructure".

Boot-order: this conftest runs BEFORE any `app.*` import (because pytest collects fixtures
first). We set required env vars here so importing `app.core.config` does not fail-fast on
missing SECRET_KEY/DATABASE_URL/etc.

The `test_engine` fixture creates/drops the `WellnessBuddy_test` DB and applies Alembic
migrations to head. Integration tests that need the schema depend on `test_engine`.

If Postgres is not reachable on localhost:5434 (developer running `pytest -k unit` without
docker compose up), the engine fixture raises a clear error — only integration tests using
`test_engine` are affected. Port 5434 is set by `docker-compose.override.yml` to avoid clash
with another local Postgres container on 5432.

The pytest-postgresql plugin (transitive via dev deps) is disabled in pyproject.toml
(`-p no:postgresql`) because it requires libpq/psycopg which we do not install.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator, Iterator
from typing import Any

# IMPORTANT: env defaults must be set BEFORE any `app.*` import below.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://wnbd:WnBd4321%40@localhost:5434/WellnessBuddy_test",
)
os.environ.setdefault(
    "SECRET_KEY",
    "test-secret-key-32-bytes-minimum-padding-padding",
)
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
os.environ.setdefault("ADMIN_EMAIL", "admin@test.example.com")
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
    """Drop+create `WellnessBuddy_test`, run `alembic upgrade head`, yield engine.

    Alembic env.py calls `asyncio.run(...)` which conflicts with pytest-asyncio's running loop.
    We run `alembic upgrade head` in a subprocess (clean loop context) instead of via
    `command.upgrade(...)`.
    """
    import subprocess

    import asyncpg

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

    # Run alembic in a subprocess to avoid nested-event-loop with pytest-asyncio.
    env = {**os.environ, "DATABASE_URL": TEST_DATABASE_URL}
    result = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"alembic upgrade failed (rc={result.returncode}): "
            f"stdout={result.stdout!r} stderr={result.stderr!r}"
        )

    engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    try:
        yield engine
    finally:
        await engine.dispose()


# Tables truncated between every integration test that touches user-scoped data.
# Order matters: child tables before parent (FK cascade-aware list sufficient — we use
# `TRUNCATE ... CASCADE` which the DB resolves in dependency order anyway).
_TRUNCATE_TABLES = (
    "audit_log",
    "refresh_tokens",
    "invite_tokens",
    "weight_log",
    "workout_log",
    "shopping_list_state",
    "weekly_plan_variants",
    "nutrition_plans",
    "users",
    "groups",
)


async def _truncate_all(engine: AsyncEngine) -> None:
    """TRUNCATE the per-test mutable tables. Cascades clear FK refs."""
    from sqlalchemy import text

    table_list = ", ".join(f'"{t}"' for t in _TRUNCATE_TABLES)
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE TABLE {table_list} RESTART IDENTITY CASCADE"))


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Per-test async session.

    Tests that commit (e.g. seed users via fixtures) need isolation. We TRUNCATE the
    mutable tables BEFORE each test so committed state from a previous test is erased.
    """
    await _truncate_all(test_engine)
    SessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)  # noqa: N806
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest_asyncio.fixture
async def async_client(test_engine: AsyncEngine) -> AsyncIterator[AsyncClient]:
    """Async HTTPX client mounted directly on the FastAPI ASGI app — no real network.

    Depends on `test_engine` to ensure the alembic migration has been applied before any
    request. Tables are NOT truncated here because tests that need both `db_session`
    fixtures + `async_client` get truncation via `db_session`.
    """
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
