"""Integration tests for /api/weekly per-day variant resolution (Plan 02-04).

Covers the contract where lunches/dinners parsed_json is keyed by day_slug
(`{lun: [...], mar: [...], ...}`) and each day's payload surfaces the lunch
title from THAT day, not generic "first option" across the week.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.plan import NutritionPlan
from app.models.user import User

pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="session")]


# Plan parsed_json fixture in Plan 02-04 grid format — different lunch per day.
GRID_PARSED_FIXTURE: dict = {
    "personal_data": {"name": "GridUser"},
    "macro_target": {"kcal": 2100, "protein_g": 160, "carbs_g": 210, "fat_g": 70},
    "daily_structure": [],
    "breakfast": {
        "key": "default",
        "title": "Yogurt + frutta",
        "ingredients": [],
        "macros": {"kcal": 380, "protein_g": 25, "carbs_g": 40, "fat_g": 12},
    },
    "lunches": {
        "lun": [
            {
                "key": "opzione_a",
                "title": "Pasta al pomodoro",
                "ingredients": [],
                "macros": {"kcal": 480, "protein_g": 25, "carbs_g": 70, "fat_g": 10},
                "day_of_week": [0],
            },
            {
                "key": "opzione_b",
                "title": "Bresaola + pane integrale",
                "ingredients": [],
                "macros": {"kcal": 460, "protein_g": 38, "carbs_g": 60, "fat_g": 9},
                "day_of_week": [0],
            },
        ],
        "mer": [
            {
                "key": "opzione_a",
                "title": "Petto di pollo + riso",
                "ingredients": [],
                "macros": {"kcal": 470, "protein_g": 42, "carbs_g": 55, "fat_g": 8},
                "day_of_week": [2],
            }
        ],
    },
    "dinners": {
        "lun": [
            {
                "key": "piatto",
                "title": "Salmone al forno",
                "ingredients": [],
                "macros": {"kcal": 700, "protein_g": 50, "carbs_g": 40, "fat_g": 35},
                "day_of_week": [0],
            }
        ],
        "mer": [
            {
                "key": "piatto",
                "title": "Lenticchie + uovo in camicia",
                "ingredients": [],
                "macros": {"kcal": 650, "protein_g": 40, "carbs_g": 70, "fat_g": 18},
                "day_of_week": [2],
            }
        ],
    },
    "snacks": [
        {
            "key": "afternoon",
            "title": "Yogurt soia + noci",
            "ingredients": [],
            "macros": {"kcal": 280, "protein_g": 8, "carbs_g": 32, "fat_g": 14},
        }
    ],
    "supplements": [],
    "weight_projection": [],
}


WEEK_START = "2026-05-04"  # Monday


@pytest_asyncio.fixture
async def grid_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid4(),
        email="grid-user@test.example.com",
        username="grid_user",
        hashed_password=hash_password("Password123!"),
        role="user",
        timezone="Europe/Rome",
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def grid_active_plan(db_session: AsyncSession, grid_user: User) -> NutritionPlan:
    plan = NutritionPlan(
        id=uuid4(),
        user_id=grid_user.id,
        name="Grid plan",
        raw_md="# placeholder",
        parsed_json=GRID_PARSED_FIXTURE,
        is_active=True,
    )
    db_session.add(plan)
    await db_session.commit()
    return plan


async def _login(client: AsyncClient, email: str, password: str) -> str:
    r = await client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


# ──────────────────────────────────────────────────────────────────────────────
# GET /api/weekly/{week_start} — per-day lunch/dinner resolution
# ──────────────────────────────────────────────────────────────────────────────


async def test_get_weekly_returns_7_days_with_per_day_lunches(
    async_client: AsyncClient,
    grid_user: User,
    grid_active_plan: NutritionPlan,
) -> None:
    """Each day's lunch slot resolves to the lunch from that day's grid cell."""
    access = await _login(async_client, "grid-user@test.example.com", "Password123!")
    r = await async_client.get(
        f"/api/weekly/{WEEK_START}",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["days"]) == 7

    # Monday (dow=0): lunch from lunches['lun'] → "Pasta al pomodoro"
    monday = body["days"][0]
    monday_lunch = next(m for m in monday["meals"] if m["slot"] == "lunch")
    assert monday_lunch["title"] == "Pasta al pomodoro"

    # Wednesday (dow=2): lunch from lunches['mer'] → "Petto di pollo + riso"
    wednesday = body["days"][2]
    wed_lunch = next(m for m in wednesday["meals"] if m["slot"] == "lunch")
    assert wed_lunch["title"] == "Petto di pollo + riso"

    # Monday dinner: "Salmone al forno"
    monday_dinner = next(m for m in monday["meals"] if m["slot"] == "dinner")
    assert monday_dinner["title"] == "Salmone al forno"


async def test_get_weekly_falls_back_when_day_slug_missing(
    async_client: AsyncClient,
    grid_user: User,
    grid_active_plan: NutritionPlan,
) -> None:
    """A day without its own grid cell falls back to first non-empty list value (defensive)."""
    access = await _login(async_client, "grid-user@test.example.com", "Password123!")
    r = await async_client.get(
        f"/api/weekly/{WEEK_START}",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    # Tuesday (dow=1) — no 'mar' key in fixture lunches → falls back to first non-empty list.
    # The fixture has lunches['lun'] and lunches['mer']; iter order is insertion order →
    # the fallback takes lunches['lun'][0] = "Pasta al pomodoro".
    tuesday = body["days"][1]
    tue_lunch = next(m for m in tuesday["meals"] if m["slot"] == "lunch")
    assert tue_lunch["title"] in ("Pasta al pomodoro", "Petto di pollo + riso")


async def test_patch_variant_for_specific_day_increments_version(
    async_client: AsyncClient,
    grid_user: User,
    grid_active_plan: NutritionPlan,
) -> None:
    """PATCH lunch variant for day 0 then for day 2 → two distinct rows, each version=1."""
    access = await _login(async_client, "grid-user@test.example.com", "Password123!")

    # PATCH Mon lunch
    r1 = await async_client.patch(
        f"/api/weekly/{WEEK_START}/variant",
        json={
            "plan_id": str(grid_active_plan.id),
            "day_of_week": 0,
            "meal_type": "lunch",
            "variant_key": "opzione_b",
        },
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r1.status_code == 200
    assert r1.json()["version"] == 1
    assert r1.json()["day_of_week"] == 0

    # PATCH Wed lunch — separate composite key, separate row
    r2 = await async_client.patch(
        f"/api/weekly/{WEEK_START}/variant",
        json={
            "plan_id": str(grid_active_plan.id),
            "day_of_week": 2,
            "meal_type": "lunch",
            "variant_key": "opzione_a",
        },
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r2.status_code == 200
    assert r2.json()["version"] == 1  # NEW row, version starts at 1
    assert r2.json()["day_of_week"] == 2

    # Update Mon lunch again — same row, version increments
    r3 = await async_client.patch(
        f"/api/weekly/{WEEK_START}/variant",
        json={
            "plan_id": str(grid_active_plan.id),
            "day_of_week": 0,
            "meal_type": "lunch",
            "variant_key": "opzione_a",
        },
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r3.status_code == 200
    assert r3.json()["version"] == 2
    assert r3.json()["day_of_week"] == 0


async def test_patch_variant_invalid_day_of_week_negative_rejected(
    async_client: AsyncClient,
    grid_user: User,
    grid_active_plan: NutritionPlan,
) -> None:
    """day_of_week < 0 → 422 (Pydantic Field(ge=0, le=6))."""
    access = await _login(async_client, "grid-user@test.example.com", "Password123!")
    r = await async_client.patch(
        f"/api/weekly/{WEEK_START}/variant",
        json={
            "plan_id": str(grid_active_plan.id),
            "day_of_week": -1,
            "meal_type": "lunch",
            "variant_key": "opzione_a",
        },
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 422
    assert r.json()["code"] == "validation_error"


async def test_patch_variant_invalid_day_of_week_too_large_rejected(
    async_client: AsyncClient,
    grid_user: User,
    grid_active_plan: NutritionPlan,
) -> None:
    """day_of_week > 6 → 422."""
    access = await _login(async_client, "grid-user@test.example.com", "Password123!")
    r = await async_client.patch(
        f"/api/weekly/{WEEK_START}/variant",
        json={
            "plan_id": str(grid_active_plan.id),
            "day_of_week": 9,
            "meal_type": "lunch",
            "variant_key": "opzione_a",
        },
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 422
    assert r.json()["code"] == "validation_error"


async def test_get_weekly_after_variant_change_reflects_selection(
    async_client: AsyncClient,
    grid_user: User,
    grid_active_plan: NutritionPlan,
) -> None:
    """After PATCH variant=opzione_b on Mon lunch, GET /api/weekly returns it."""
    access = await _login(async_client, "grid-user@test.example.com", "Password123!")
    pr = await async_client.patch(
        f"/api/weekly/{WEEK_START}/variant",
        json={
            "plan_id": str(grid_active_plan.id),
            "day_of_week": 0,
            "meal_type": "lunch",
            "variant_key": "opzione_b",
        },
        headers={"Authorization": f"Bearer {access}"},
    )
    assert pr.status_code == 200

    r = await async_client.get(
        f"/api/weekly/{WEEK_START}",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200
    body = r.json()
    monday = body["days"][0]
    monday_lunch = next(m for m in monday["meals"] if m["slot"] == "lunch")
    # The weekly_service resolves the meal block using variant_key — Bresaola is opzione_b
    assert monday_lunch["variant_key"] == "opzione_b"
    assert monday_lunch["title"] == "Bresaola + pane integrale"
