"""Shopping API integration tests (SHOP-01..SHOP-06; PDF endpoint scaffold 501).

Plan 02-05 Task 2 — RED phase.

Covers:
  * GET /api/shopping/{week_start} — 5 categories, fixed order, aggregation
    across (day, slot, variant) tuples.
  * PATCH /api/shopping/{week_start}/check — LWW version increments per call.
  * POST /api/shopping/{week_start}/reset — clears persisted check state.
  * Error envelope shape: ``{detail, code}`` with code='no_active_plan' when
    the user has no is_active=True NutritionPlan.
  * PDF endpoint scaffold returns 501 with code='not_implemented' (Plan 02-06
    will swap the body for the actual exporter).
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
from app.models.variant import WeeklyPlanVariant

pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="session")]


# Stripped-down parsed_json fixture with realistic ingredients from real plans.
# Lunches grid has lun + mar variants; dinners shared across all days; snacks
# flat list. Categories left blank — keyword lookup will buckets them.
SHOPPING_FIXTURE: dict = {
    "personal_data": {"name": "ShopUser"},
    "macro_target": {"kcal": 2100, "protein_g": 160, "carbs_g": 210, "fat_g": 70},
    "daily_structure": [],
    "breakfast": {
        "key": "default",
        "title": "Yogurt + frutta",
        "ingredients": [
            {"name": "yogurt greco 200g"},
            {"name": "frutta secca 30g"},
            {"name": "miele 10g"},
        ],
        "macros": {"kcal": 380, "protein_g": 25, "carbs_g": 40, "fat_g": 12},
        "category": None,
    },
    "lunches": {
        "lun": [
            {
                "key": "opzione_a",
                "title": "Pasta al pomodoro",
                "ingredients": [
                    {"name": "pasta integrale 80g"},
                    {"name": "pomodoro 150g"},
                    {"name": "olio evo q.b."},
                ],
                "macros": {"kcal": 480, "protein_g": 25, "carbs_g": 70, "fat_g": 10},
                "day_of_week": [0],
                "category": None,
            },
        ],
        "mar": [
            {
                "key": "opzione_a",
                "title": "Pollo + riso",
                "ingredients": [
                    {"name": "pollo 150g"},
                    {"name": "riso basmati 80g"},
                    {"name": "zucchine 200g"},
                ],
                "macros": {"kcal": 470, "protein_g": 42, "carbs_g": 55, "fat_g": 8},
                "day_of_week": [1],
                "category": None,
            }
        ],
    },
    "dinners": {
        "lun": [
            {
                "key": "piatto",
                "title": "Salmone al forno",
                "ingredients": [
                    {"name": "salmone 200g"},
                    {"name": "patate 200g"},
                    {"name": "olio evo q.b."},
                ],
                "macros": {"kcal": 700, "protein_g": 50, "carbs_g": 40, "fat_g": 35},
                "day_of_week": [0],
                "category": None,
            }
        ],
    },
    "snacks": [
        {
            "key": "default",
            "title": "Yogurt + noci",
            "ingredients": [
                {"name": "yogurt greco 150g"},
                {"name": "noci 20g"},
            ],
            "macros": {"kcal": 280, "protein_g": 8, "carbs_g": 32, "fat_g": 14},
            "category": None,
        }
    ],
    "supplements": [],
    "weight_projection": [],
}


WEEK_START = "2026-05-04"  # Monday


@pytest_asyncio.fixture
async def shop_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid4(),
        email="shop-user@test.example.com",
        username="shop_user",
        hashed_password=hash_password("Password123!"),
        role="user",
        timezone="Europe/Rome",
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def shop_active_plan(db_session: AsyncSession, shop_user: User) -> NutritionPlan:
    plan = NutritionPlan(
        id=uuid4(),
        user_id=shop_user.id,
        name="Shopping fixture plan",
        raw_md="# placeholder",
        parsed_json=SHOPPING_FIXTURE,
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
# GET /api/shopping/{week_start}
# ──────────────────────────────────────────────────────────────────────────────


async def test_get_shopping_returns_5_categories_in_fixed_order(
    async_client: AsyncClient,
    shop_user: User,
    shop_active_plan: NutritionPlan,
) -> None:
    access = await _login(async_client, "shop-user@test.example.com", "Password123!")
    r = await async_client.get(
        f"/api/shopping/{WEEK_START}",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["week_start"] == WEEK_START
    assert "version" in body
    cat_names = [c["name"] for c in body["categories"]]
    assert cat_names == [
        "Frigo & Freschi",
        "Frutta & Verdura",
        "Dispensa",
        "Condimenti",
        "Integratori",
    ]


async def test_get_shopping_aggregates_yogurt_across_breakfast_and_snack(
    async_client: AsyncClient,
    shop_user: User,
    shop_active_plan: NutritionPlan,
) -> None:
    """Breakfast yogurt + snack yogurt in same week sum into a single row.

    Fixture has yogurt greco 200 g (breakfast every day, 7×) + 150 g (snack
    every day, 7×) → both keyed by ('yogurt greco', 'g'). Single merged row
    in 'Frigo & Freschi'.
    """
    access = await _login(async_client, "shop-user@test.example.com", "Password123!")
    r = await async_client.get(
        f"/api/shopping/{WEEK_START}",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    fridge = next(c for c in body["categories"] if c["name"] == "Frigo & Freschi")
    yogurts = [it for it in fridge["items"] if "yogurt" in it["canonical_name"]]
    assert len(yogurts) == 1
    # 7 days × (200 g breakfast + 150 g snack) = 7 × 350 = 2450 g
    assert yogurts[0]["amount"] == 2450.0
    assert yogurts[0]["unit"] == "g"
    assert yogurts[0]["quantity_it"] == "2450 g"


async def test_get_shopping_qb_olio_count_is_one(
    async_client: AsyncClient,
    shop_user: User,
    shop_active_plan: NutritionPlan,
) -> None:
    """Olio q.b. appears in lunch (Mon) + dinner (Mon) = 2 contributions but a single qb row."""
    access = await _login(async_client, "shop-user@test.example.com", "Password123!")
    r = await async_client.get(
        f"/api/shopping/{WEEK_START}",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    condiments = next(c for c in body["categories"] if c["name"] == "Condimenti")
    olios = [it for it in condiments["items"] if "olio" in it["canonical_name"]]
    assert len(olios) == 1
    assert olios[0]["unit"] == "qb"
    assert olios[0]["quantity_it"] == "q.b."


async def test_get_shopping_no_active_plan_returns_400(
    async_client: AsyncClient,
    shop_user: User,
) -> None:
    """No active plan → 400 with code='no_active_plan'."""
    access = await _login(async_client, "shop-user@test.example.com", "Password123!")
    r = await async_client.get(
        f"/api/shopping/{WEEK_START}",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 400
    body = r.json()
    assert body["code"] == "no_active_plan"


# ──────────────────────────────────────────────────────────────────────────────
# PATCH /api/shopping/{week_start}/check
# ──────────────────────────────────────────────────────────────────────────────


async def test_patch_check_persists_and_increments_version(
    async_client: AsyncClient,
    shop_user: User,
    shop_active_plan: NutritionPlan,
) -> None:
    access = await _login(async_client, "shop-user@test.example.com", "Password123!")

    # Initial GET — version 0
    r0 = await async_client.get(
        f"/api/shopping/{WEEK_START}",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r0.status_code == 200
    assert r0.json()["version"] == 0

    # PATCH check
    r1 = await async_client.patch(
        f"/api/shopping/{WEEK_START}/check",
        json={"canonical_name": "yogurt greco", "unit": "g", "checked": True},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r1.status_code == 200, r1.text
    body1 = r1.json()
    assert body1["version"] == 1
    fridge = next(c for c in body1["categories"] if c["name"] == "Frigo & Freschi")
    yogurt = next(it for it in fridge["items"] if "yogurt" in it["canonical_name"])
    assert yogurt["checked"] is True

    # PATCH uncheck → version=2
    r2 = await async_client.patch(
        f"/api/shopping/{WEEK_START}/check",
        json={"canonical_name": "yogurt greco", "unit": "g", "checked": False},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r2.status_code == 200
    assert r2.json()["version"] == 2


# ──────────────────────────────────────────────────────────────────────────────
# POST /api/shopping/{week_start}/reset
# ──────────────────────────────────────────────────────────────────────────────


async def test_post_reset_clears_check_state(
    async_client: AsyncClient,
    shop_user: User,
    shop_active_plan: NutritionPlan,
) -> None:
    access = await _login(async_client, "shop-user@test.example.com", "Password123!")
    # Check first
    await async_client.patch(
        f"/api/shopping/{WEEK_START}/check",
        json={"canonical_name": "yogurt greco", "unit": "g", "checked": True},
        headers={"Authorization": f"Bearer {access}"},
    )
    # Reset
    r = await async_client.post(
        f"/api/shopping/{WEEK_START}/reset",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["week_start"] == WEEK_START
    assert "reset_at" in body

    # Verify all unchecked
    r2 = await async_client.get(
        f"/api/shopping/{WEEK_START}",
        headers={"Authorization": f"Bearer {access}"},
    )
    body2 = r2.json()
    fridge = next(c for c in body2["categories"] if c["name"] == "Frigo & Freschi")
    yogurt = next(it for it in fridge["items"] if "yogurt" in it["canonical_name"])
    assert yogurt["checked"] is False


# ──────────────────────────────────────────────────────────────────────────────
# PDF endpoint scaffold — Plan 02-06 wires real impl
# ──────────────────────────────────────────────────────────────────────────────


async def test_export_pdf_endpoint_returns_501(
    async_client: AsyncClient,
    shop_user: User,
    shop_active_plan: NutritionPlan,
) -> None:
    access = await _login(async_client, "shop-user@test.example.com", "Password123!")
    r = await async_client.post(
        f"/api/shopping/{WEEK_START}/export-pdf",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 501
    body = r.json()
    assert body["code"] == "not_implemented"


# ──────────────────────────────────────────────────────────────────────────────
# Variants flow into the aggregation
# ──────────────────────────────────────────────────────────────────────────────


async def test_variant_choice_changes_shopping_aggregate(
    async_client: AsyncClient,
    db_session: AsyncSession,
    shop_user: User,
    shop_active_plan: NutritionPlan,
) -> None:
    """When user chooses a non-default variant the shopping list reflects it."""
    # Add an alternative lunch with completely different ingredients
    alt_fixture = dict(SHOPPING_FIXTURE)
    alt_fixture["lunches"] = {
        "lun": [
            {
                "key": "opzione_a",
                "title": "Pasta al pomodoro",
                "ingredients": [{"name": "pasta integrale 80g"}],
                "macros": {"kcal": 480, "protein_g": 25, "carbs_g": 70, "fat_g": 10},
                "day_of_week": [0],
                "category": None,
            },
            {
                "key": "opzione_b",
                "title": "Lenticchie",
                "ingredients": [{"name": "lenticchie 100g"}],
                "macros": {"kcal": 380, "protein_g": 20, "carbs_g": 60, "fat_g": 5},
                "day_of_week": [0],
                "category": None,
            },
        ]
    }
    shop_active_plan.parsed_json = alt_fixture
    await db_session.commit()

    # Without variant row → default (opzione_a) — pasta integrale shows up
    access = await _login(async_client, "shop-user@test.example.com", "Password123!")
    r0 = await async_client.get(
        f"/api/shopping/{WEEK_START}",
        headers={"Authorization": f"Bearer {access}"},
    )
    body0 = r0.json()
    pantry0 = next(c for c in body0["categories"] if c["name"] == "Dispensa")
    pantry_names0 = {it["canonical_name"] for it in pantry0["items"]}
    assert "pasta integrale" in pantry_names0

    # Pick opzione_b for Monday lunch
    variant = WeeklyPlanVariant(
        id=uuid4(),
        user_id=shop_user.id,
        plan_id=shop_active_plan.id,
        week_start=__import__("datetime").date.fromisoformat(WEEK_START),
        day_of_week=0,
        meal_type="lunch",
        variant_key="opzione_b",
    )
    db_session.add(variant)
    await db_session.commit()

    r1 = await async_client.get(
        f"/api/shopping/{WEEK_START}",
        headers={"Authorization": f"Bearer {access}"},
    )
    body1 = r1.json()
    pantry1 = next(c for c in body1["categories"] if c["name"] == "Dispensa")
    pantry_names1 = {it["canonical_name"] for it in pantry1["items"]}
    assert "lenticchie" in pantry_names1
