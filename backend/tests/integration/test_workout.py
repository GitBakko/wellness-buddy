"""Integration tests for /api/workout/* — Plan 01-07 Wave 5.

Coverage matrix per Plan 07 Task 1 <behavior>:
  - POST /api/workout (create with trained=False or trained=True+full payload)
  - GET /api/workout (current user only, optional date range)
  - PATCH /api/workout/{id}
  - DELETE /api/workout/{id}
  - Cross-user 404 (V13 — never reveal existence)

Source: WORK-01, WORK-02, T-API-03, V13.
"""

from __future__ import annotations

from datetime import date, timedelta
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.models.workout import WorkoutLog

pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="session")]


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid4(),
        email="workout-user@test.example.com",
        username="workout_user",
        hashed_password=hash_password("Password123!"),
        role="user",
        timezone="Europe/Rome",
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def other_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid4(),
        email="workout-other@test.example.com",
        username="workout_other",
        hashed_password=hash_password("Password123!"),
        role="user",
        timezone="Europe/Rome",
    )
    db_session.add(user)
    await db_session.commit()
    return user


async def _login(client: AsyncClient, email: str, password: str) -> str:
    r = await client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


# ──────────────────────────────────────────────────────────────────────────────
# POST
# ──────────────────────────────────────────────────────────────────────────────


async def test_post_workout_full_payload_persists(
    async_client: AsyncClient, db_session: AsyncSession, test_user: User
) -> None:
    access = await _login(
        async_client, "workout-user@test.example.com", "Password123!"
    )
    today = date.today().isoformat()
    r = await async_client.post(
        "/api/workout",
        json={
            "date": today,
            "trained": True,
            "duration_min": 45,
            "calories_burned": 380,
            "workout_type": "corsa",
            "notes": "5 km easy",
        },
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["trained"] is True
    assert body["duration_min"] == 45
    assert body["workout_type"] == "corsa"


async def test_post_workout_trained_false_no_other_fields_required(
    async_client: AsyncClient, db_session: AsyncSession, test_user: User
) -> None:
    """User toggles 'no — non ho allenato': minimal payload accepted."""
    access = await _login(
        async_client, "workout-user@test.example.com", "Password123!"
    )
    r = await async_client.post(
        "/api/workout",
        json={"date": date.today().isoformat(), "trained": False},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["trained"] is False
    assert body["duration_min"] is None
    assert body["workout_type"] is None


async def test_post_workout_unauth_401(async_client: AsyncClient) -> None:
    r = await async_client.post(
        "/api/workout",
        json={"date": date.today().isoformat(), "trained": True},
    )
    assert r.status_code == 401


# ──────────────────────────────────────────────────────────────────────────────
# GET list
# ──────────────────────────────────────────────────────────────────────────────


async def test_workout_filter_by_date_range(
    async_client: AsyncClient, db_session: AsyncSession, test_user: User
) -> None:
    today = date.today()
    db_session.add_all(
        [
            WorkoutLog(
                user_id=test_user.id,
                date=today - timedelta(days=10),
                trained=True,
                duration_min=30,
            ),
            WorkoutLog(
                user_id=test_user.id,
                date=today - timedelta(days=2),
                trained=True,
                duration_min=45,
            ),
            WorkoutLog(
                user_id=test_user.id,
                date=today,
                trained=True,
                duration_min=60,
            ),
        ]
    )
    await db_session.commit()
    access = await _login(
        async_client, "workout-user@test.example.com", "Password123!"
    )
    start = (today - timedelta(days=5)).isoformat()
    end = today.isoformat()
    r = await async_client.get(
        f"/api/workout?start={start}&end={end}",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200
    body = r.json()
    # 2 in range (today, -2)
    assert len(body) == 2


async def test_workout_list_excludes_other_users(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    other_user: User,
) -> None:
    db_session.add_all(
        [
            WorkoutLog(
                user_id=test_user.id,
                date=date.today(),
                trained=True,
                duration_min=30,
            ),
            WorkoutLog(
                user_id=other_user.id,
                date=date.today(),
                trained=True,
                duration_min=120,
            ),
        ]
    )
    await db_session.commit()
    b_access = await _login(
        async_client, "workout-other@test.example.com", "Password123!"
    )
    r = await async_client.get(
        "/api/workout", headers={"Authorization": f"Bearer {b_access}"}
    )
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["duration_min"] == 120


# ──────────────────────────────────────────────────────────────────────────────
# PATCH
# ──────────────────────────────────────────────────────────────────────────────


async def test_patch_workout_partial_update(
    async_client: AsyncClient, db_session: AsyncSession, test_user: User
) -> None:
    w = WorkoutLog(
        user_id=test_user.id,
        date=date.today(),
        trained=True,
        duration_min=30,
        workout_type="corsa",
    )
    db_session.add(w)
    await db_session.commit()
    await db_session.refresh(w)

    access = await _login(
        async_client, "workout-user@test.example.com", "Password123!"
    )
    r = await async_client.patch(
        f"/api/workout/{w.id}",
        json={"duration_min": 60, "notes": "ho aggiunto 30 minuti"},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["duration_min"] == 60
    assert body["notes"] == "ho aggiunto 30 minuti"
    # Untouched fields preserved
    assert body["workout_type"] == "corsa"


async def test_workout_patch_other_user_returns_404(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    other_user: User,
) -> None:
    w = WorkoutLog(
        user_id=test_user.id,
        date=date.today(),
        trained=True,
    )
    db_session.add(w)
    await db_session.commit()
    await db_session.refresh(w)

    b_access = await _login(
        async_client, "workout-other@test.example.com", "Password123!"
    )
    r = await async_client.patch(
        f"/api/workout/{w.id}",
        json={"duration_min": 999},
        headers={"Authorization": f"Bearer {b_access}"},
    )
    assert r.status_code == 404
    assert r.json()["code"] == "not_found"


# ──────────────────────────────────────────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────────────────────────────────────────


async def test_delete_workout_removes_row(
    async_client: AsyncClient, db_session: AsyncSession, test_user: User
) -> None:
    w = WorkoutLog(
        user_id=test_user.id, date=date.today(), trained=True, duration_min=30
    )
    db_session.add(w)
    await db_session.commit()
    await db_session.refresh(w)
    workout_id = w.id

    access = await _login(
        async_client, "workout-user@test.example.com", "Password123!"
    )
    r = await async_client.delete(
        f"/api/workout/{workout_id}",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 204

    rows = (
        await db_session.scalars(
            select(WorkoutLog).where(WorkoutLog.id == workout_id)
        )
    ).all()
    assert len(rows) == 0


async def test_workout_delete_other_user_returns_404(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    other_user: User,
) -> None:
    w = WorkoutLog(
        user_id=test_user.id, date=date.today(), trained=True
    )
    db_session.add(w)
    await db_session.commit()
    await db_session.refresh(w)

    b_access = await _login(
        async_client, "workout-other@test.example.com", "Password123!"
    )
    r = await async_client.delete(
        f"/api/workout/{w.id}",
        headers={"Authorization": f"Bearer {b_access}"},
    )
    assert r.status_code == 404
    assert r.json()["code"] == "not_found"
