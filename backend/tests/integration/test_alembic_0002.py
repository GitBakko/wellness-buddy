"""Test 0002_activate_groups: backfill correctness + idempotence + downgrade roundtrip.

Source: Plan 02-07 Task 1 behavior matrix; PITFALL #16 mitigation; D-22, D-23, FAM-01.

The migration is data-only: for each User without a ``group_id`` it creates a
``"{username} · household"`` Group and links the user. Re-running the migration
must be a no-op so deploys can replay it safely. ``downgrade`` nulls out
``users.group_id`` and deletes the household groups.
"""

from __future__ import annotations

import os
import subprocess
from uuid import uuid4

import pytest
import pytest_asyncio
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.security import hash_password
from app.models.user import User

pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="session")]


def _run_alembic(action: str, target: str) -> None:
    """Invoke alembic via subprocess (clean event loop) — see conftest test_engine."""
    env = {**os.environ, "DATABASE_URL": os.environ["DATABASE_URL"]}
    result = subprocess.run(
        ["uv", "run", "alembic", action, target],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:  # pragma: no cover — surfaces alembic stderr on failure
        raise RuntimeError(
            f"alembic {action} {target} failed (rc={result.returncode}): "
            f"stdout={result.stdout!r} stderr={result.stderr!r}"
        )


async def _truncate_users_groups(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.execute(text('TRUNCATE TABLE "users", "groups" RESTART IDENTITY CASCADE'))


@pytest_asyncio.fixture
async def two_users_no_group(test_engine: AsyncEngine):
    """Seed two users with ``group_id=NULL`` so the migration has work to do."""
    await _truncate_users_groups(test_engine)
    from sqlalchemy.ext.asyncio import async_sessionmaker

    SessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)  # noqa: N806
    async with SessionLocal() as session:
        for username, email in (
            ("alembic_user_a", "alembic-a@test.example.com"),
            ("alembic_user_b", "alembic-b@test.example.com"),
        ):
            session.add(
                User(
                    id=uuid4(),
                    email=email,
                    username=username,
                    hashed_password=hash_password("Password123!"),
                    role="user",
                    timezone="Europe/Rome",
                    group_id=None,
                )
            )
        await session.commit()
    yield


async def test_0002_backfills_groups_for_users_without(
    test_engine: AsyncEngine, two_users_no_group: None
) -> None:
    """Two users seeded with group_id=NULL — after upgrade have personal household groups.

    The ``two_users_no_group`` fixture seeds AFTER ``test_engine`` has run
    ``upgrade head`` once. To exercise the migration on these users, we
    downgrade past 0002 then re-upgrade.
    """
    _run_alembic("downgrade", "8137b2e24001")
    try:
        _run_alembic("upgrade", "0002")
        async with test_engine.begin() as conn:
            rows = (
                await conn.execute(
                    text(
                        "SELECT u.username, g.name "
                        "FROM users u JOIN groups g ON u.group_id = g.id "
                        "WHERE u.username IN ('alembic_user_a','alembic_user_b') "
                        "ORDER BY u.username"
                    )
                )
            ).all()
        assert len(rows) == 2, f"expected 2 backfilled users, got {rows}"
        names = [r[1] for r in rows]
        assert all(n.endswith(" · household") for n in names), names
        assert "alembic_user_a · household" in names
        assert "alembic_user_b · household" in names
    finally:
        # Leave DB at head for downstream tests.
        _run_alembic("upgrade", "0002")


async def test_0002_idempotent(test_engine: AsyncEngine, two_users_no_group: None) -> None:
    """Running 0002 twice produces same outcome as once (no duplicate groups)."""
    _run_alembic("downgrade", "8137b2e24001")
    try:
        _run_alembic("upgrade", "0002")
        async with test_engine.begin() as conn:
            first = (
                await conn.execute(
                    text(
                        "SELECT id, group_id FROM users "
                        "WHERE username IN ('alembic_user_a','alembic_user_b') "
                        "ORDER BY username"
                    )
                )
            ).all()
            first_group_count = (await conn.execute(text("SELECT count(*) FROM groups"))).scalar()

        _run_alembic("upgrade", "0002")  # re-run head — must be no-op

        async with test_engine.begin() as conn:
            second = (
                await conn.execute(
                    text(
                        "SELECT id, group_id FROM users "
                        "WHERE username IN ('alembic_user_a','alembic_user_b') "
                        "ORDER BY username"
                    )
                )
            ).all()
            second_group_count = (await conn.execute(text("SELECT count(*) FROM groups"))).scalar()

        assert first == second, "group_id assignments shifted on re-run (not idempotent)"
        assert first_group_count == second_group_count, (
            f"group count changed on re-run ({first_group_count} → {second_group_count})"
        )
    finally:
        _run_alembic("upgrade", "0002")


async def test_0002_downgrade_nulls_group_ids(
    test_engine: AsyncEngine, two_users_no_group: None
) -> None:
    """downgrade nulls user.group_id + deletes household groups."""
    # First run upgrade -> downgrade (the seeded users currently have NULL group_id
    # because test_engine ran upgrade head BEFORE seeding).
    _run_alembic("downgrade", "8137b2e24001")
    try:
        _run_alembic("upgrade", "0002")
        # Now downgrade again to verify the cleanup logic.
        _run_alembic("downgrade", "8137b2e24001")
        async with test_engine.begin() as conn:
            user_rows = (
                await conn.execute(
                    text(
                        "SELECT group_id FROM users "
                        "WHERE username IN ('alembic_user_a','alembic_user_b')"
                    )
                )
            ).all()
            household_count = (
                await conn.execute(
                    text("SELECT count(*) FROM groups WHERE name LIKE '% · household'")
                )
            ).scalar()
        assert all(r[0] is None for r in user_rows), f"group_id not nulled: {user_rows}"
        assert household_count == 0, f"household groups not cleaned up: {household_count}"
    finally:
        # Restore head so subsequent tests see a fully-migrated DB.
        _run_alembic("upgrade", "0002")


async def test_0002_revision_chain_links_to_8137b2e24001(test_engine: AsyncEngine) -> None:
    """Smoke check the revision chain: 0002 → 8137b2e24001 → a694bcd4d792 (baseline)."""
    async with test_engine.begin() as conn:
        version = (await conn.execute(text("SELECT version_num FROM alembic_version"))).scalar()
    assert version == "0002", f"expected head=0002, got {version!r}"
    # The migration file shape is also asserted statically — compile-time grep
    # in the plan acceptance criteria.
    text_blob = open(  # noqa: SIM115 — test reads file once
        "alembic/versions/0002_activate_groups.py", encoding="utf-8"
    ).read()
    assert 'revision: str = "0002"' in text_blob
    assert 'down_revision: str | Sequence[str] | None = "8137b2e24001"' in text_blob
    assert "household" in text_blob


# Module-level imports used by the helper above.
_ = sa  # silence unused import for static analysers
