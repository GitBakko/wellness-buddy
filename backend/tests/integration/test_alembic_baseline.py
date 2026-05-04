"""Verify `alembic upgrade head` applies cleanly on a fresh DB and creates all 10 tables.

W2 fix: the previous SQL-shell probe via psql is replaced by SQLAlchemy `inspect` so it runs
in CI without psql being on PATH.
"""

from __future__ import annotations

import pytest
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncEngine


@pytest.mark.asyncio
async def test_alembic_baseline_creates_all_10_tables(test_engine: AsyncEngine) -> None:
    async with test_engine.begin() as conn:
        tables = await conn.run_sync(lambda c: inspect(c).get_table_names())
    expected = {
        "groups",
        "users",
        "nutrition_plans",
        "weekly_plan_variants",
        "workout_log",
        "weight_log",
        "shopping_list_state",
        "invite_tokens",
        "refresh_tokens",
        "audit_log",
    }
    assert expected <= set(tables)


@pytest.mark.asyncio
async def test_users_created_at_is_timestamptz(test_engine: AsyncEngine) -> None:
    """W2 fix: previously SQL probe via psql; now reads via SQLAlchemy inspect."""
    async with test_engine.begin() as conn:
        cols = await conn.run_sync(lambda c: inspect(c).get_columns("users"))
    created_at = next(c for c in cols if c["name"] == "created_at")
    # Postgres reports TIMESTAMPTZ either via type.timezone=True or 'TIMESTAMP WITH TIME ZONE' in repr  # noqa: E501
    is_tz = (
        getattr(created_at["type"], "timezone", False)
        or "TIME ZONE" in str(created_at["type"]).upper()
    )
    assert is_tz, f"users.created_at type {created_at['type']!r} is not TIMESTAMPTZ"


@pytest.mark.asyncio
async def test_users_timezone_column_present_and_not_null(test_engine: AsyncEngine) -> None:
    """MOD-01 + MOD-09: users has IANA tz column, NOT NULL.

    Note: the IANA `Europe/Rome` default is enforced at the SQLAlchemy ORM layer
    (see `test_user_timezone_iana_default` in tests/unit/test_models.py), not as a
    SQL-level DEFAULT clause. This integration test only verifies the column shape.
    """
    async with test_engine.begin() as conn:
        cols = await conn.run_sync(lambda c: inspect(c).get_columns("users"))
    tz_col = next(c for c in cols if c["name"] == "timezone")
    assert tz_col["nullable"] is False
    assert "VARCHAR" in str(tz_col["type"]).upper() or "STRING" in str(tz_col["type"]).upper()


@pytest.mark.asyncio
async def test_partial_unique_active_plan_index(test_engine: AsyncEngine) -> None:
    """V11: only one active nutrition plan per user — partial unique index applied."""
    async with test_engine.begin() as conn:
        indexes = await conn.run_sync(lambda c: inspect(c).get_indexes("nutrition_plans"))
    by_name = {i["name"]: i for i in indexes}
    assert "ix_nutrition_plans_active_per_user" in by_name
    idx = by_name["ix_nutrition_plans_active_per_user"]
    assert idx["unique"] is True
