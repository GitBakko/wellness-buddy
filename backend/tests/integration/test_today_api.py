"""Integration tests for /api/today/* — Plan 01-07 Wave 5.

Coverage matrix per Plan 07 Task 1 <behavior>:
  - GET /api/today: aggregator returns greeting_period + meals + today's weight + workout
  - POST /api/today/meal/{meal_type}/complete: persists to weekly_plan_variant
  - 401 on missing auth
  - cross-user isolation (V13 — User B never sees User A's weight/workout)
  - empty meals when no active plan

Source: TODAY-01..TODAY-08, T-API-02 (information disclosure), T-API-03 (authz),
        UI-SPEC §7.2 (greeting_period server-computed), CONV-09 (TIMESTAMPTZ + IANA tz).
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.plan import NutritionPlan
from app.models.user import User
from app.models.variant import WeeklyPlanVariant
from app.models.weight import WeightLog
from app.models.workout import WorkoutLog

pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="session")]


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid4(),
        email="today-user@test.example.com",
        username="today_user",
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
        email="today-other@test.example.com",
        username="today_other",
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


PLAN_PARSED_FIXTURE: dict = {
    "personal_data": {"name": "Test"},
    "macro_target": {"kcal": 2100, "protein_g": 160, "carbs_g": 210, "fat_g": 70},
    "daily_structure": [],
    "breakfast": {
        "key": "default",
        "title": "Yogurt greco con frutta",
        "ingredients": [],
        "macros": {"kcal": 380, "protein_g": 25, "carbs_g": 40, "fat_g": 12},
    },
    "lunches": {
        "default": [
            {
                "key": "A",
                "title": "Pasta integrale",
                "ingredients": [],
                "macros": {"kcal": 720, "protein_g": 28, "carbs_g": 90, "fat_g": 18},
            }
        ]
    },
    "dinners": {
        "default": [
            {
                "key": "A",
                "title": "Salmone alla griglia",
                "ingredients": [],
                "macros": {"kcal": 620, "protein_g": 45, "carbs_g": 30, "fat_g": 28},
            }
        ]
    },
    "snacks": [
        {
            "key": "afternoon",
            "title": "Frutta + mandorle",
            "ingredients": [],
            "macros": {"kcal": 280, "protein_g": 8, "carbs_g": 32, "fat_g": 14},
        }
    ],
    "supplements": [],
    "weight_projection": [],
    "rules": [],
}


@pytest_asyncio.fixture
async def active_plan(db_session: AsyncSession, test_user: User) -> NutritionPlan:
    plan = NutritionPlan(
        id=uuid4(),
        user_id=test_user.id,
        name="Test plan",
        raw_md="# Plan",
        parsed_json=PLAN_PARSED_FIXTURE,
        is_active=True,
    )
    db_session.add(plan)
    await db_session.commit()
    return plan


# ──────────────────────────────────────────────────────────────────────────────
# /api/today GET
# ──────────────────────────────────────────────────────────────────────────────


async def test_today_unauth_401(async_client: AsyncClient) -> None:
    r = await async_client.get("/api/today")
    assert r.status_code == 401
    body = r.json()
    assert "detail" in body and "code" in body


async def test_today_returns_active_plan_meals_for_today(
    async_client: AsyncClient, test_user: User, active_plan: NutritionPlan
) -> None:
    access = await _login(async_client, "today-user@test.example.com", "Password123!")
    r = await async_client.get(
        "/api/today", headers={"Authorization": f"Bearer {access}"}
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "date" in body
    assert "day_of_week" in body
    assert body["greeting_period"] in {"morning", "afternoon", "evening", "night"}
    assert isinstance(body["meals"], list)
    # 4 meals from fixture: breakfast + lunch + dinner + 1 snack
    meal_types = [m["meal_type"] for m in body["meals"]]
    assert "breakfast" in meal_types
    assert "lunch" in meal_types
    assert "dinner" in meal_types
    assert "snack" in meal_types
    # Meals carry macros + completion flag
    for m in body["meals"]:
        assert "title" in m
        assert "macros" in m
        assert {"kcal", "protein_g", "carbs_g", "fat_g"} <= set(m["macros"].keys())
        assert "completed" in m
        assert m["completed"] is False  # nothing marked yet
    # No weight/workout logged today
    assert body["weight_today"] is None
    assert body["workout_today"] is None


async def test_today_no_active_plan_returns_empty_meals(
    async_client: AsyncClient, test_user: User
) -> None:
    access = await _login(async_client, "today-user@test.example.com", "Password123!")
    r = await async_client.get(
        "/api/today", headers={"Authorization": f"Bearer {access}"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["meals"] == []
    assert body["weight_today"] is None
    assert body["workout_today"] is None


async def test_today_includes_meal_completions(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    active_plan: NutritionPlan,
) -> None:
    access = await _login(async_client, "today-user@test.example.com", "Password123!")
    # Mark lunch completed
    r = await async_client.post(
        "/api/today/meal/lunch/complete",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["completed"] is True

    # GET /api/today reflects the completion
    r = await async_client.get(
        "/api/today", headers={"Authorization": f"Bearer {access}"}
    )
    assert r.status_code == 200
    meals_by_type = {m["meal_type"]: m for m in r.json()["meals"]}
    assert meals_by_type["lunch"]["completed"] is True
    assert meals_by_type["breakfast"]["completed"] is False


async def test_complete_meal_persists_weekly_variant(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    active_plan: NutritionPlan,
) -> None:
    access = await _login(async_client, "today-user@test.example.com", "Password123!")
    r = await async_client.post(
        "/api/today/meal/breakfast/complete",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200

    # Verify DB row
    tz = ZoneInfo(test_user.timezone)
    today = datetime.now(tz).date()
    day_of_week = today.weekday()
    week_start = today - timedelta(days=day_of_week)
    rows = (
        await db_session.scalars(
            select(WeeklyPlanVariant).where(
                WeeklyPlanVariant.user_id == test_user.id,
                WeeklyPlanVariant.week_start == week_start,
                WeeklyPlanVariant.day_of_week == day_of_week,
                WeeklyPlanVariant.meal_type == "breakfast",
            )
        )
    ).all()
    assert len(rows) == 1
    assert rows[0].completed is True


async def test_complete_meal_invalid_type_400(
    async_client: AsyncClient, test_user: User, active_plan: NutritionPlan
) -> None:
    access = await _login(async_client, "today-user@test.example.com", "Password123!")
    r = await async_client.post(
        "/api/today/meal/dessert/complete",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 400
    assert r.json()["code"] == "invalid_meal_type"


async def test_complete_meal_no_active_plan_400(
    async_client: AsyncClient, test_user: User
) -> None:
    access = await _login(async_client, "today-user@test.example.com", "Password123!")
    r = await async_client.post(
        "/api/today/meal/breakfast/complete",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 400
    assert r.json()["code"] == "no_active_plan"


async def test_today_other_user_isolation(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    other_user: User,
    active_plan: NutritionPlan,
) -> None:
    """T-API-02: User B's /today must not leak User A's weight/workout/meals."""
    # User A logs weight
    a_weight = WeightLog(
        user_id=test_user.id,
        date=date.today(),
        weight_kg=Decimal("75.30"),
    )
    db_session.add(a_weight)
    await db_session.commit()

    # User B GET /today — must NOT show User A's weight
    b_access = await _login(
        async_client, "today-other@test.example.com", "Password123!"
    )
    r = await async_client.get(
        "/api/today", headers={"Authorization": f"Bearer {b_access}"}
    )
    assert r.status_code == 200
    body = r.json()
    # User B has no plan + no weight
    assert body["meals"] == []
    assert body["weight_today"] is None
    assert body["workout_today"] is None


async def test_today_includes_today_weight_and_workout(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    active_plan: NutritionPlan,
) -> None:
    """Today's weight + workout are surfaced on GET /api/today."""
    today = date.today()
    db_session.add_all(
        [
            WeightLog(
                user_id=test_user.id,
                date=today,
                weight_kg=Decimal("75.30"),
            ),
            WorkoutLog(
                user_id=test_user.id,
                date=today,
                trained=True,
                duration_min=45,
                workout_type="corsa",
                notes="5 km easy",
            ),
        ]
    )
    await db_session.commit()

    access = await _login(async_client, "today-user@test.example.com", "Password123!")
    r = await async_client.get(
        "/api/today", headers={"Authorization": f"Bearer {access}"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["weight_today"] is not None
    assert float(body["weight_today"]["weight_kg"]) == 75.30
    assert body["workout_today"] is not None
    assert body["workout_today"]["trained"] is True
    assert body["workout_today"]["duration_min"] == 45
    assert body["workout_today"]["workout_type"] == "corsa"


async def test_today_greeting_period_is_one_of_known_buckets(
    async_client: AsyncClient, test_user: User
) -> None:
    """UI-SPEC §7.2 — server computes greeting_period from user.timezone IANA."""
    access = await _login(async_client, "today-user@test.example.com", "Password123!")
    r = await async_client.get(
        "/api/today", headers={"Authorization": f"Bearer {access}"}
    )
    assert r.status_code == 200
    period = r.json()["greeting_period"]
    assert period in {"morning", "afternoon", "evening", "night"}
