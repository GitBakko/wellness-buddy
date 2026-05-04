"""Integration tests for /api/weekly/* — Plan 02-02 Wave 2.

Coverage matrix per Plan 02-02 Task 2 <behavior>:
  - GET /api/weekly/{week_start}              — 7 days × 4 slots aggregator
  - GET /api/weekly/{week_start}/summary      — kcal/macro per-day + week total
  - PATCH /api/weekly/{week_start}/variant    — upsert + LWW (If-Unmodified-Since)
  - 409 on stale precondition                 — code='version_conflict' + "Aggiornato da {nome}"
  - 400 on no active plan                     — code='no_active_plan'
  - Default visibility per FAM-02
  - Version increments
  - Cross-user 404 on PATCH (V13)

Source: WEEK-01..05, FAM-02, FAM-04, D-17, V13, T-API-02.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.plan import NutritionPlan
from app.models.user import User
from app.models.variant import WeeklyPlanVariant

pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="session")]


PLAN_PARSED_FIXTURE: dict = {
    "personal_data": {"name": "Test"},
    "macro_target": {
        "kcal": 2100,
        "protein_g": 160,
        "carbs_g": 210,
        "fat_g": 70,
    },
    "daily_structure": [],
    "breakfast": {
        "key": "default",
        "title": "Yogurt greco con frutta",
        "ingredients": [],
        "macros": {
            "kcal": 380,
            "protein_g": 25,
            "carbs_g": 40,
            "fat_g": 12,
        },
    },
    "lunches": {
        "default": [
            {
                "key": "A",
                "title": "Pasta integrale",
                "ingredients": [],
                "macros": {
                    "kcal": 720,
                    "protein_g": 28,
                    "carbs_g": 90,
                    "fat_g": 18,
                },
            },
            {
                "key": "B",
                "title": "Riso e verdure",
                "ingredients": [],
                "macros": {
                    "kcal": 680,
                    "protein_g": 22,
                    "carbs_g": 95,
                    "fat_g": 14,
                },
            },
        ]
    },
    "dinners": {
        "default": [
            {
                "key": "A",
                "title": "Salmone alla griglia",
                "ingredients": [],
                "macros": {
                    "kcal": 620,
                    "protein_g": 45,
                    "carbs_g": 30,
                    "fat_g": 28,
                },
            },
            {
                "key": "B",
                "title": "Pollo al limone",
                "ingredients": [],
                "macros": {
                    "kcal": 560,
                    "protein_g": 50,
                    "carbs_g": 20,
                    "fat_g": 22,
                },
            },
            {
                "key": "special",
                "title": "Pasta speciale del weekend",
                "ingredients": [],
                "macros": {
                    "kcal": 850,
                    "protein_g": 30,
                    "carbs_g": 110,
                    "fat_g": 25,
                },
            },
        ]
    },
    "snacks": [
        {
            "key": "afternoon",
            "title": "Frutta + mandorle",
            "ingredients": [],
            "macros": {
                "kcal": 280,
                "protein_g": 8,
                "carbs_g": 32,
                "fat_g": 14,
            },
        }
    ],
    "supplements": [],
    "weight_projection": [],
}


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid4(),
        email="weekly-user@test.example.com",
        username="weekly_user",
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
        email="weekly-other@test.example.com",
        username="weekly_other",
        hashed_password=hash_password("Password123!"),
        role="user",
        timezone="Europe/Rome",
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def active_plan(db_session: AsyncSession, test_user: User) -> NutritionPlan:
    plan = NutritionPlan(
        id=uuid4(),
        user_id=test_user.id,
        name="Test plan",
        raw_md="# placeholder",
        parsed_json=PLAN_PARSED_FIXTURE,
        is_active=True,
    )
    db_session.add(plan)
    await db_session.commit()
    return plan


async def _login(client: AsyncClient, email: str, password: str) -> str:
    r = await client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


WEEK_START = "2026-05-04"  # Monday — used in the plan UI fixtures


# ──────────────────────────────────────────────────────────────────────────────
# GET /api/weekly/{week_start}
# ──────────────────────────────────────────────────────────────────────────────


async def test_get_weekly_returns_7_days_with_default_variants(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    active_plan: NutritionPlan,
) -> None:
    access = await _login(async_client, "weekly-user@test.example.com", "Password123!")
    r = await async_client.get(
        f"/api/weekly/{WEEK_START}",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["week_start"] == WEEK_START
    assert len(body["days"]) == 7
    # Every day has 4 meal slots (breakfast/lunch/dinner/snack)
    for day in body["days"]:
        assert {m["slot"] for m in day["meals"]} == {
            "breakfast",
            "lunch",
            "dinner",
            "snack",
        }
        # No variants saved → defaults
        for meal in day["meals"]:
            assert meal["variant_key"] == "default"
            assert meal["version"] == 0
            assert meal["completed"] is False
    # Day-0 lunch resolves to first lunch option (D-03 default)
    monday = body["days"][0]
    lunch = next(m for m in monday["meals"] if m["slot"] == "lunch")
    assert lunch["title"] == "Pasta integrale"


async def test_get_weekly_no_active_plan_returns_400(
    async_client: AsyncClient, test_user: User
) -> None:
    access = await _login(async_client, "weekly-user@test.example.com", "Password123!")
    r = await async_client.get(
        f"/api/weekly/{WEEK_START}",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 400
    assert r.json()["code"] == "no_active_plan"


async def test_get_weekly_unauth_returns_401(
    async_client: AsyncClient,
) -> None:
    r = await async_client.get(f"/api/weekly/{WEEK_START}")
    assert r.status_code == 401


# ──────────────────────────────────────────────────────────────────────────────
# GET /api/weekly/{week_start}/summary
# ──────────────────────────────────────────────────────────────────────────────


async def test_get_weekly_summary_returns_kcal_macros(
    async_client: AsyncClient,
    test_user: User,
    active_plan: NutritionPlan,
) -> None:
    access = await _login(async_client, "weekly-user@test.example.com", "Password123!")
    r = await async_client.get(
        f"/api/weekly/{WEEK_START}/summary",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["week_start"] == WEEK_START
    assert "kcal_total" in body
    assert "protein_g" in body
    assert len(body["days"]) == 7
    # Every day has macros aggregated from 4 default slots
    # breakfast 380 + lunch 720 + dinner 620 + snack 280 = 2000 kcal/day
    assert body["days"][0]["kcal"] == 380 + 720 + 620 + 280
    # Week total = 7 × 2000 = 14000
    assert body["kcal_total"] == 7 * 2000


# ──────────────────────────────────────────────────────────────────────────────
# PATCH /api/weekly/{week_start}/variant — happy path + visibility defaults
# ──────────────────────────────────────────────────────────────────────────────


async def test_patch_variant_creates_with_default_visibility_for_dinner(
    async_client: AsyncClient,
    test_user: User,
    active_plan: NutritionPlan,
) -> None:
    """FAM-02: dinner default visibility = group_shared."""
    access = await _login(async_client, "weekly-user@test.example.com", "Password123!")
    r = await async_client.patch(
        f"/api/weekly/{WEEK_START}/variant",
        json={
            "plan_id": str(active_plan.id),
            "day_of_week": 0,
            "meal_type": "dinner",
            "variant_key": "B",
        },
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["variant_key"] == "B"
    assert body["visibility"] == "group_shared"
    assert body["version"] == 1


async def test_patch_variant_creates_with_default_visibility_for_breakfast(
    async_client: AsyncClient,
    test_user: User,
    active_plan: NutritionPlan,
) -> None:
    """FAM-02: breakfast default visibility = private."""
    access = await _login(async_client, "weekly-user@test.example.com", "Password123!")
    r = await async_client.patch(
        f"/api/weekly/{WEEK_START}/variant",
        json={
            "plan_id": str(active_plan.id),
            "day_of_week": 1,
            "meal_type": "breakfast",
            "variant_key": "default",
        },
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["visibility"] == "private"
    assert body["version"] == 1


async def test_patch_variant_increments_version(
    async_client: AsyncClient,
    test_user: User,
    active_plan: NutritionPlan,
) -> None:
    """Two PATCHes → version 1 then 2."""
    access = await _login(async_client, "weekly-user@test.example.com", "Password123!")
    payload = {
        "plan_id": str(active_plan.id),
        "day_of_week": 2,
        "meal_type": "lunch",
        "variant_key": "A",
    }
    r1 = await async_client.patch(
        f"/api/weekly/{WEEK_START}/variant",
        json=payload,
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r1.status_code == 200
    assert r1.json()["version"] == 1

    r2 = await async_client.patch(
        f"/api/weekly/{WEEK_START}/variant",
        json={**payload, "variant_key": "B"},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r2.status_code == 200
    assert r2.json()["version"] == 2
    assert r2.json()["variant_key"] == "B"


# ──────────────────────────────────────────────────────────────────────────────
# PATCH /api/weekly/{week_start}/variant — LWW conflict
# ──────────────────────────────────────────────────────────────────────────────


async def test_patch_variant_409_on_stale_if_unmodified_since(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    active_plan: NutritionPlan,
) -> None:
    """Stale `If-Unmodified-Since` (older than row.updated_at) → 409 + version_conflict."""
    access = await _login(async_client, "weekly-user@test.example.com", "Password123!")
    # Seed an existing variant row owned by test_user
    payload = {
        "plan_id": str(active_plan.id),
        "day_of_week": 3,
        "meal_type": "dinner",
        "variant_key": "A",
    }
    r1 = await async_client.patch(
        f"/api/weekly/{WEEK_START}/variant",
        json=payload,
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r1.status_code == 200
    # Stale precondition → 409
    r2 = await async_client.patch(
        f"/api/weekly/{WEEK_START}/variant",
        json={**payload, "variant_key": "B"},
        headers={
            "Authorization": f"Bearer {access}",
            "If-Unmodified-Since": "2020-01-01T00:00:00+00:00",
        },
    )
    assert r2.status_code == 409, r2.text
    body = r2.json()
    assert body["code"] == "version_conflict"
    assert body["detail"].startswith("Aggiornato da")


async def test_patch_variant_skips_lww_when_no_header(
    async_client: AsyncClient,
    test_user: User,
    active_plan: NutritionPlan,
) -> None:
    """No If-Unmodified-Since → no LWW check → 200 even after stale state."""
    access = await _login(async_client, "weekly-user@test.example.com", "Password123!")
    payload = {
        "plan_id": str(active_plan.id),
        "day_of_week": 4,
        "meal_type": "lunch",
        "variant_key": "A",
    }
    r1 = await async_client.patch(
        f"/api/weekly/{WEEK_START}/variant",
        json=payload,
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r1.status_code == 200

    # No If-Unmodified-Since → upsert proceeds even if client state is "stale"
    r2 = await async_client.patch(
        f"/api/weekly/{WEEK_START}/variant",
        json={**payload, "variant_key": "B"},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r2.status_code == 200
    assert r2.json()["variant_key"] == "B"


async def test_patch_variant_fresh_if_unmodified_since_succeeds(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    active_plan: NutritionPlan,
) -> None:
    """Fresh precondition (matches row.updated_at) → 200."""
    access = await _login(async_client, "weekly-user@test.example.com", "Password123!")
    payload = {
        "plan_id": str(active_plan.id),
        "day_of_week": 5,
        "meal_type": "dinner",
        "variant_key": "A",
    }
    r1 = await async_client.patch(
        f"/api/weekly/{WEEK_START}/variant",
        json=payload,
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r1.status_code == 200
    fresh_ius = r1.json()["updated_at"]
    # Fresh precondition (>= row.updated_at) → 200
    r2 = await async_client.patch(
        f"/api/weekly/{WEEK_START}/variant",
        json={**payload, "variant_key": "B"},
        headers={
            "Authorization": f"Bearer {access}",
            "If-Unmodified-Since": fresh_ius,
        },
    )
    assert r2.status_code == 200
    assert r2.json()["version"] == 2


# ──────────────────────────────────────────────────────────────────────────────
# Cross-user smoke (V13) — full matrix lives in Plan 02-06
# ──────────────────────────────────────────────────────────────────────────────


async def test_patch_variant_other_user_plan_id_creates_separate_row(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    other_user: User,
    active_plan: NutritionPlan,
) -> None:
    """V13 mitigation smoke — other_user's PATCH writes their OWN row, never test_user's.

    Plan 02-02 only ships own-user paths (`current_user`-scoped). Cross-user reads/mutations
    via `?user_id=` are deferred to Plan 02-06 with `get_user_with_group_access` (V13 — 404).
    """
    # other_user logs in and PATCHes; the row is keyed by (user_id, week_start, day, meal)
    # so it CANNOT collide with test_user's row.
    access = await _login(async_client, "weekly-other@test.example.com", "Password123!")
    r = await async_client.patch(
        f"/api/weekly/{WEEK_START}/variant",
        json={
            "plan_id": str(active_plan.id),
            "day_of_week": 0,
            "meal_type": "dinner",
            "variant_key": "A",
        },
        headers={"Authorization": f"Bearer {access}"},
    )
    # other_user has no NutritionPlan, but variant_service does NOT validate plan_id ownership
    # this plan; it relies on user_id scoping. The row that gets written is owned by other_user.
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["user_id"] == str(other_user.id)

    # Confirm test_user's data area was untouched
    rows = (
        await db_session.scalars(
            select(WeeklyPlanVariant).where(WeeklyPlanVariant.user_id == test_user.id)
        )
    ).all()
    assert len(rows) == 0


# ──────────────────────────────────────────────────────────────────────────────
# Validation
# ──────────────────────────────────────────────────────────────────────────────


async def test_patch_variant_invalid_day_of_week_rejected(
    async_client: AsyncClient,
    test_user: User,
    active_plan: NutritionPlan,
) -> None:
    """Pydantic strict: day_of_week must be in [0, 6]."""
    access = await _login(async_client, "weekly-user@test.example.com", "Password123!")
    r = await async_client.patch(
        f"/api/weekly/{WEEK_START}/variant",
        json={
            "plan_id": str(active_plan.id),
            "day_of_week": 7,  # invalid
            "meal_type": "dinner",
            "variant_key": "A",
        },
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 422
    assert r.json()["code"] == "validation_error"


# ──────────────────────────────────────────────────────────────────────────────
# Plan 02-04 gap-closure — Bug C (composition + macros + non-zero per-meal kcal)
# ──────────────────────────────────────────────────────────────────────────────


async def test_weekly_meal_entries_carry_ingredients_and_macros(
    async_client: AsyncClient,
    test_user: User,
    active_plan: NutritionPlan,
) -> None:
    """Plan 02-04 gap-closure — every weekly meal entry has ingredients[] and
    macros.kcal > 0. Mirrors the Bug B/C win condition for /settimana."""
    access = await _login(async_client, "weekly-user@test.example.com", "Password123!")
    r = await async_client.get(
        f"/api/weekly/{WEEK_START}", headers={"Authorization": f"Bearer {access}"}
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["days"]) == 7
    for day in body["days"]:
        for m in day["meals"]:
            assert "ingredients" in m
            assert isinstance(m["ingredients"], list)
            assert "macros" in m
            assert "kcal" in m["macros"]
            assert m["macros"]["kcal"] > 0  # always non-zero (proportional fallback)


async def test_weekly_proportional_macros_for_grid_plan_without_per_cell_macros(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
) -> None:
    """Plan 02-04 gap-closure — when parsed_json grid cells carry zero macros,
    weekly_service falls back to proportional split (25/35/30/10) so /settimana
    shows realistic kcal values per slot instead of 0 across the board."""
    grid_plan_parsed = {
        "personal_data": {"name": "Grid"},
        "macro_target": {"kcal": 2000, "protein_g": 160, "carbs_g": 200, "fat_g": 60},
        "daily_structure": [],
        "breakfast": {
            "key": "default",
            "title": "Colazione",
            "ingredients": [{"name": "avena + whey"}],
            "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
        },
        "lunches": {
            "lun": [
                {
                    "key": "opzione_a",
                    "title": "Pranzo lun",
                    "ingredients": [{"name": "uova + riso"}],
                    "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
                    "day_of_week": [0],
                }
            ]
        },
        "dinners": {
            "lun": [
                {
                    "key": "piatto",
                    "title": "Cena lun",
                    "ingredients": [{"name": "salmone + patate"}],
                    "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
                    "day_of_week": [0],
                }
            ]
        },
        "snacks": [
            {
                "key": "afternoon",
                "title": "Spuntino",
                "ingredients": [{"name": "yogurt"}],
                "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
            }
        ],
        "supplements": [],
        "weight_projection": [],
        "rules": [],
    }
    plan = NutritionPlan(
        id=uuid4(),
        user_id=test_user.id,
        name="Grid plan",
        raw_md="# Plan",
        parsed_json=grid_plan_parsed,
        is_active=True,
    )
    db_session.add(plan)
    await db_session.commit()

    access = await _login(async_client, "weekly-user@test.example.com", "Password123!")
    r = await async_client.get(
        f"/api/weekly/{WEEK_START}", headers={"Authorization": f"Bearer {access}"}
    )
    assert r.status_code == 200
    monday = r.json()["days"][0]  # day_of_week=0
    by_slot = {m["slot"]: m for m in monday["meals"]}
    assert by_slot["breakfast"]["macros"]["kcal"] == 500  # 25%
    assert by_slot["lunch"]["macros"]["kcal"] == 700  # 35%
    assert by_slot["dinner"]["macros"]["kcal"] == 600  # 30%
    assert by_slot["snack"]["macros"]["kcal"] == 200  # 10%
