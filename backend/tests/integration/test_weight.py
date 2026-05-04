"""Integration tests for /api/weight/* — Plan 01-07 Wave 5.

Coverage matrix per Plan 07 Task 1 <behavior>:
  - POST /api/weight (upsert per date)
  - GET /api/weight (current user only, desc)
  - PATCH /api/weight/{id}
  - DELETE /api/weight/{id}
  - Cross-user 404 (V13 — never reveal existence)

Source: WEIGHT-01, WEIGHT-02, T-API-03, V13.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.models.weight import WeightLog

pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="session")]


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid4(),
        email="weight-user@test.example.com",
        username="weight_user",
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
        email="weight-other@test.example.com",
        username="weight_other",
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


async def test_post_weight_persists_with_2decimal_precision(
    async_client: AsyncClient, db_session: AsyncSession, test_user: User
) -> None:
    access = await _login(async_client, "weight-user@test.example.com", "Password123!")
    today = date.today().isoformat()
    r = await async_client.post(
        "/api/weight",
        json={"date": today, "weight_kg": 75.30},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert "id" in body
    assert body["date"] == today
    assert float(body["weight_kg"]) == 75.30

    # DB has exact Decimal 75.30
    rows = (
        await db_session.scalars(select(WeightLog).where(WeightLog.user_id == test_user.id))
    ).all()
    assert len(rows) == 1
    assert rows[0].weight_kg == Decimal("75.30")


async def test_post_weight_unique_per_day_upserts(
    async_client: AsyncClient, db_session: AsyncSession, test_user: User
) -> None:
    access = await _login(async_client, "weight-user@test.example.com", "Password123!")
    today = date.today().isoformat()
    # First POST
    r1 = await async_client.post(
        "/api/weight",
        json={"date": today, "weight_kg": 75.30},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r1.status_code == 201
    # Second POST same date → upsert
    r2 = await async_client.post(
        "/api/weight",
        json={"date": today, "weight_kg": 75.50},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r2.status_code == 201
    # DB has single row, latest value
    rows = (
        await db_session.scalars(select(WeightLog).where(WeightLog.user_id == test_user.id))
    ).all()
    assert len(rows) == 1
    assert rows[0].weight_kg == Decimal("75.50")


async def test_post_weight_unauth_401(async_client: AsyncClient) -> None:
    r = await async_client.post(
        "/api/weight",
        json={"date": date.today().isoformat(), "weight_kg": 75.0},
    )
    assert r.status_code == 401


# ──────────────────────────────────────────────────────────────────────────────
# GET list
# ──────────────────────────────────────────────────────────────────────────────


async def test_get_weight_list_orderby_date_desc(
    async_client: AsyncClient, db_session: AsyncSession, test_user: User
) -> None:
    today = date.today()
    db_session.add_all(
        [
            WeightLog(
                user_id=test_user.id,
                date=today - timedelta(days=2),
                weight_kg=Decimal("76.00"),
            ),
            WeightLog(
                user_id=test_user.id,
                date=today,
                weight_kg=Decimal("75.30"),
            ),
            WeightLog(
                user_id=test_user.id,
                date=today - timedelta(days=1),
                weight_kg=Decimal("75.70"),
            ),
        ]
    )
    await db_session.commit()
    access = await _login(async_client, "weight-user@test.example.com", "Password123!")
    r = await async_client.get("/api/weight", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 3
    # Desc by date — today first
    assert body[0]["date"] == today.isoformat()
    assert body[1]["date"] == (today - timedelta(days=1)).isoformat()
    assert body[2]["date"] == (today - timedelta(days=2)).isoformat()


async def test_get_weight_list_excludes_other_users(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    other_user: User,
) -> None:
    """T-API-03: User B's GET excludes User A's rows."""
    db_session.add_all(
        [
            WeightLog(
                user_id=test_user.id,
                date=date.today(),
                weight_kg=Decimal("75.30"),
            ),
            WeightLog(
                user_id=other_user.id,
                date=date.today(),
                weight_kg=Decimal("60.10"),
            ),
        ]
    )
    await db_session.commit()
    b_access = await _login(async_client, "weight-other@test.example.com", "Password123!")
    r = await async_client.get("/api/weight", headers={"Authorization": f"Bearer {b_access}"})
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert float(body[0]["weight_kg"]) == 60.10


# ──────────────────────────────────────────────────────────────────────────────
# PATCH
# ──────────────────────────────────────────────────────────────────────────────


async def test_patch_weight_updates_value(
    async_client: AsyncClient, db_session: AsyncSession, test_user: User
) -> None:
    w = WeightLog(user_id=test_user.id, date=date.today(), weight_kg=Decimal("75.30"))
    db_session.add(w)
    await db_session.commit()
    await db_session.refresh(w)

    access = await _login(async_client, "weight-user@test.example.com", "Password123!")
    r = await async_client.patch(
        f"/api/weight/{w.id}",
        json={"date": date.today().isoformat(), "weight_kg": 75.50},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200, r.text
    assert float(r.json()["weight_kg"]) == 75.50


async def test_weight_patch_other_user_returns_404(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    other_user: User,
) -> None:
    """V13: scrub existence — return 404 (not 403) on cross-user."""
    w = WeightLog(user_id=test_user.id, date=date.today(), weight_kg=Decimal("75.30"))
    db_session.add(w)
    await db_session.commit()
    await db_session.refresh(w)

    b_access = await _login(async_client, "weight-other@test.example.com", "Password123!")
    r = await async_client.patch(
        f"/api/weight/{w.id}",
        json={"date": date.today().isoformat(), "weight_kg": 99.99},
        headers={"Authorization": f"Bearer {b_access}"},
    )
    assert r.status_code == 404
    assert r.json()["code"] == "not_found"


# ──────────────────────────────────────────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────────────────────────────────────────


async def test_delete_weight_removes_row(
    async_client: AsyncClient, db_session: AsyncSession, test_user: User
) -> None:
    w = WeightLog(user_id=test_user.id, date=date.today(), weight_kg=Decimal("75.30"))
    db_session.add(w)
    await db_session.commit()
    await db_session.refresh(w)
    weight_id = w.id

    access = await _login(async_client, "weight-user@test.example.com", "Password123!")
    r = await async_client.delete(
        f"/api/weight/{weight_id}",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 204

    # Row gone — fresh session to avoid identity-map confusion
    rows = (await db_session.scalars(select(WeightLog).where(WeightLog.id == weight_id))).all()
    assert len(rows) == 0


async def test_weight_delete_other_user_returns_404(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    other_user: User,
) -> None:
    w = WeightLog(user_id=test_user.id, date=date.today(), weight_kg=Decimal("75.30"))
    db_session.add(w)
    await db_session.commit()
    await db_session.refresh(w)

    b_access = await _login(async_client, "weight-other@test.example.com", "Password123!")
    r = await async_client.delete(
        f"/api/weight/{w.id}",
        headers={"Authorization": f"Bearer {b_access}"},
    )
    assert r.status_code == 404
    assert r.json()["code"] == "not_found"
