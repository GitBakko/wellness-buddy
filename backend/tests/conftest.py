"""Pytest fixtures for Wellness Buddy backend tests.

Provides ephemeral postgres via pytest-postgresql + async client + Alembic upgrade.
Source: D-11, D-13, RESEARCH.md "Test Infrastructure".

NOTE (worktree race, Plan 02b): pytest-postgresql is in dev deps but its psycopg
backend is not yet installed (Plan 02a is expected to add `psycopg[binary]`).
We disable the postgresql plugin globally here so unit + integration-without-DB
tests run cleanly. Plan 02a's conftest update will reinstate it once psycopg
binaries are pinned.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Disable pytest-postgresql plugin until Plan 02a adds psycopg[binary].
# Tests that need DB will be added by Plans 03/04/07 and re-enable as needed.
collect_ignore_glob: list[str] = []


def pytest_configure(config: pytest.Config) -> None:
    """Unload pytest-postgresql to avoid libpq import error on Windows worktree."""
    config.pluginmanager.set_blocked("postgresql")


# NOTE: app imports deferred — Plan 02a creates app/main.py + models.
# When fixtures are first used, this conftest will fail with ImportError until Plan 02a lands.
# That is expected and confirms ordering: Plan 01 ships scaffolding only.


@pytest.fixture(scope="session")
def event_loop() -> Any:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_client() -> AsyncIterator[AsyncClient]:
    """Provide an async HTTP client against the FastAPI app.

    Activated once Plan 02a creates `app.main:app`.
    """
    from app.main import app  # noqa: PLC0415  — deferred import per above

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
