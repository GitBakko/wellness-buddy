"""Pytest fixtures for Wellness Buddy backend tests.

Provides ephemeral postgres via pytest-postgresql + async client + Alembic upgrade.
Source: D-11, D-13, RESEARCH.md "Test Infrastructure".
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

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
