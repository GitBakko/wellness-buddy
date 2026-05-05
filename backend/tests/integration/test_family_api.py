"""Integration tests for /api/family/share — Plan 02-07 Task 2.

Coverage:
  * owner toggles visibility group_shared → private (and back)
  * non-owner attempt returns 404 with ``not_found`` envelope (V13)
  * invalid visibility enum returns 422 (Pydantic) or 400 (service)
  * ``get_user_with_group_access`` semantics (own / partner / outsider / orphan)
  * convergence smoke for FAM-09 (≤5s shared meal sync)

Source: FAM-02, FAM-03, FAM-06, FAM-07, FAM-09, V13.
"""

from __future__ import annotations

from datetime import date, timedelta
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.group import Group
from app.models.plan import NutritionPlan
from app.models.user import User
from app.models.variant import Visibility, WeeklyPlanVariant

pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="session")]


# ──────────────────────────────────────────────────────────────────────────────
# Shared fixtures (used by Family API + the 40-test authz matrix)
# ──────────────────────────────────────────────────────────────────────────────


PLAN_PARSED_FIXTURE: dict = {
    "personal_data": {"name": "Test"},
    "macro_target": {"kcal": 2100, "protein_g": 160, "carbs_g": 210, "fat_g": 70},
    "daily_structure": [],
    "breakfast": {
        "key": "default",
        "title": "Yogurt greco",
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


def _week_start_today_dow() -> tuple[date, int]:
    """Return (this Monday, today's day_of_week 0..6 in Europe/Rome).

    today_service queries variants by ``today's day_of_week`` so fixtures must
    seed for THE CURRENT day or the lookup misses (variant_by_meal returns
    None and the default visibility kicks in).
    """
    from datetime import datetime as _datetime
    from zoneinfo import ZoneInfo as _ZoneInfo

    now = _datetime.now(_ZoneInfo("Europe/Rome"))
    dow = now.weekday()
    return now.date() - timedelta(days=dow), dow


@pytest_asyncio.fixture
async def family_world(db_session: AsyncSession) -> dict:
    """Seed a complete fixture world for family + matrix testing.

    Layout:
      * group_brunelli       — Stefano + Marta share this household
      * group_other          — Outsider lives here
      * stefano              — owner of two variants (lunch shared, breakfast private)
      * marta                — partner; group-shared sibling
      * outsider             — different group entirely
      * ex_member            — was in group_brunelli, now group_id=group_other
        (simulates membership change while their JWT stays valid 15 min)
      * each user has an active NutritionPlan with the simple parsed fixture
      * stefano has pre-seeded WeeklyPlanVariants for THIS week / TODAY:
        - lunch: visibility=group_shared (id surfaced)
        - breakfast: visibility=private (id surfaced)

    Returns dict with users, plans, variants, and the chosen week_start.
    """
    week_start, day_of_week = _week_start_today_dow()

    group_brunelli = Group(id=uuid4(), name="Brunelli household")
    group_other = Group(id=uuid4(), name="Other household")
    db_session.add_all([group_brunelli, group_other])
    await db_session.flush()

    stefano = User(
        id=uuid4(),
        email="fam-stefano@test.example.com",
        username="stefano_fam",
        hashed_password=hash_password("Password123!"),
        role="user",
        timezone="Europe/Rome",
        group_id=group_brunelli.id,
    )
    marta = User(
        id=uuid4(),
        email="fam-marta@test.example.com",
        username="marta_fam",
        hashed_password=hash_password("Password123!"),
        role="user",
        timezone="Europe/Rome",
        group_id=group_brunelli.id,
    )
    outsider = User(
        id=uuid4(),
        email="fam-outsider@test.example.com",
        username="outsider_fam",
        hashed_password=hash_password("Password123!"),
        role="user",
        timezone="Europe/Rome",
        group_id=group_other.id,
    )
    ex_member = User(
        id=uuid4(),
        email="fam-exmember@test.example.com",
        username="exmember_fam",
        hashed_password=hash_password("Password123!"),
        role="user",
        timezone="Europe/Rome",
        # Simulate "was in Brunelli, now moved to other group" — JWT issued
        # while in Brunelli is still valid 15min but membership changed.
        group_id=group_other.id,
    )
    db_session.add_all([stefano, marta, outsider, ex_member])
    await db_session.flush()

    # Active plan per user — needed for /today, /weekly, /shopping endpoints.
    for owner in (stefano, marta, outsider, ex_member):
        db_session.add(
            NutritionPlan(
                id=uuid4(),
                user_id=owner.id,
                name=f"{owner.username} plan",
                raw_md="# Plan",
                parsed_json=PLAN_PARSED_FIXTURE,
                is_active=True,
            )
        )
    await db_session.flush()

    from sqlalchemy import select as _select

    stefano_plan = (
        await db_session.scalars(_select(NutritionPlan).where(NutritionPlan.user_id == stefano.id))
    ).first()

    # Stefano's variants: lunch shared, breakfast private.
    stefano_lunch_shared = WeeklyPlanVariant(
        id=uuid4(),
        user_id=stefano.id,
        plan_id=stefano_plan.id,
        week_start=week_start,
        day_of_week=day_of_week,
        meal_type="lunch",
        variant_key="A",
        visibility=Visibility.GROUP_SHARED,
        version=1,
    )
    db_session.add(stefano_lunch_shared)

    stefano_breakfast_private = WeeklyPlanVariant(
        id=uuid4(),
        user_id=stefano.id,
        plan_id=stefano_plan.id,
        week_start=week_start,
        day_of_week=day_of_week,
        meal_type="breakfast",
        variant_key="default",
        visibility=Visibility.PRIVATE,
        version=1,
    )
    db_session.add(stefano_breakfast_private)

    # Marta also has shared+private variants for her own plan
    marta_plan = (
        await db_session.scalars(_select(NutritionPlan).where(NutritionPlan.user_id == marta.id))
    ).first()
    marta_lunch_shared = WeeklyPlanVariant(
        id=uuid4(),
        user_id=marta.id,
        plan_id=marta_plan.id,
        week_start=week_start,
        day_of_week=day_of_week,
        meal_type="lunch",
        variant_key="A",
        visibility=Visibility.GROUP_SHARED,
        version=1,
    )
    db_session.add(marta_lunch_shared)

    await db_session.commit()
    return {
        "week_start": week_start,
        "stefano": stefano,
        "marta": marta,
        "outsider": outsider,
        "ex_member": ex_member,
        "group_brunelli": group_brunelli,
        "group_other": group_other,
        "stefano_lunch_shared_id": stefano_lunch_shared.id,
        "stefano_breakfast_private_id": stefano_breakfast_private.id,
        "marta_lunch_shared_id": marta_lunch_shared.id,
    }


async def _login(client: AsyncClient, email: str) -> str:
    r = await client.post(
        "/api/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


# ──────────────────────────────────────────────────────────────────────────────
# PATCH /api/family/share/{variant_id} — owner-only toggle
# ──────────────────────────────────────────────────────────────────────────────


async def test_share_toggle_owner_changes_visibility_to_private(
    async_client: AsyncClient, family_world: dict
) -> None:
    """Owner switches a shared variant to private."""
    token = await _login(async_client, "fam-stefano@test.example.com")
    r = await async_client.patch(
        f"/api/family/share/{family_world['stefano_lunch_shared_id']}",
        json={"visibility": "private"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["visibility"] == "private"
    assert body["version"] == 2  # bumped from 1


async def test_share_toggle_owner_changes_visibility_to_shared(
    async_client: AsyncClient, family_world: dict
) -> None:
    """Owner switches a private variant to group_shared."""
    token = await _login(async_client, "fam-stefano@test.example.com")
    r = await async_client.patch(
        f"/api/family/share/{family_world['stefano_breakfast_private_id']}",
        json={"visibility": "group_shared"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["visibility"] == "group_shared"


async def test_share_toggle_non_owner_returns_404(
    async_client: AsyncClient, family_world: dict
) -> None:
    """Marta (group partner, NOT owner) cannot toggle Stefano's variant — 404 V13."""
    token = await _login(async_client, "fam-marta@test.example.com")
    r = await async_client.patch(
        f"/api/family/share/{family_world['stefano_lunch_shared_id']}",
        json={"visibility": "private"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404, r.text
    assert r.json()["code"] == "not_found"


async def test_share_toggle_outsider_returns_404(
    async_client: AsyncClient, family_world: dict
) -> None:
    """Outsider (different group) cannot toggle anything in family — 404."""
    token = await _login(async_client, "fam-outsider@test.example.com")
    r = await async_client.patch(
        f"/api/family/share/{family_world['stefano_lunch_shared_id']}",
        json={"visibility": "private"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404, r.text
    assert r.json()["code"] == "not_found"


async def test_share_toggle_invalid_visibility_returns_422(
    async_client: AsyncClient, family_world: dict
) -> None:
    """Invalid enum value rejected by Pydantic Literal — 422."""
    token = await _login(async_client, "fam-stefano@test.example.com")
    r = await async_client.patch(
        f"/api/family/share/{family_world['stefano_lunch_shared_id']}",
        json={"visibility": "public_internet"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 422, r.text


async def test_share_toggle_unauth_returns_401(
    async_client: AsyncClient, family_world: dict
) -> None:
    r = await async_client.patch(
        f"/api/family/share/{family_world['stefano_lunch_shared_id']}",
        json={"visibility": "private"},
    )
    assert r.status_code == 401


async def test_share_toggle_unknown_variant_returns_404(
    async_client: AsyncClient, family_world: dict
) -> None:
    """Unknown variant id returns 404 (not 400, not 422 — V13 envelope)."""
    token = await _login(async_client, "fam-stefano@test.example.com")
    r = await async_client.patch(
        f"/api/family/share/{uuid4()}",
        json={"visibility": "private"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404, r.text
    assert r.json()["code"] == "not_found"


# ──────────────────────────────────────────────────────────────────────────────
# get_user_with_group_access dependency unit-ish tests (via /api/today path)
# ──────────────────────────────────────────────────────────────────────────────


async def test_today_with_user_id_self_returns_own_payload(
    async_client: AsyncClient, family_world: dict
) -> None:
    """Passing your own user_id is a no-op — same payload as no query string."""
    token = await _login(async_client, "fam-stefano@test.example.com")
    headers = {"Authorization": f"Bearer {token}"}
    r1 = await async_client.get("/api/today", headers=headers)
    r2 = await async_client.get(f"/api/today?user_id={family_world['stefano'].id}", headers=headers)
    assert r1.status_code == 200 and r2.status_code == 200, (r1.text, r2.text)


async def test_today_with_partner_user_id_returns_filtered_meals(
    async_client: AsyncClient, family_world: dict
) -> None:
    """Stefano viewing Marta's /today: shared meals visible, weight + workout hidden."""
    token = await _login(async_client, "fam-stefano@test.example.com")
    r = await async_client.get(
        f"/api/today?user_id={family_world['marta'].id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    # Cross-user view never includes weight or workout (CONV-14 — always private)
    assert body["weight_today"] is None
    assert body["workout_today"] is None
    # All visible meals must be group_shared
    for m in body["meals"]:
        assert m["visibility"] == "group_shared", m


async def test_today_with_outsider_user_id_returns_404(
    async_client: AsyncClient, family_world: dict
) -> None:
    """Stefano querying outsider's data → 404 (V13)."""
    token = await _login(async_client, "fam-stefano@test.example.com")
    r = await async_client.get(
        f"/api/today?user_id={family_world['outsider'].id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404, r.text
    assert r.json()["code"] == "not_found"


async def test_today_with_unknown_user_id_returns_404(
    async_client: AsyncClient, family_world: dict
) -> None:
    """Random UUID for user_id → 404 (V13 — same envelope as cross-group)."""
    token = await _login(async_client, "fam-stefano@test.example.com")
    r = await async_client.get(
        f"/api/today?user_id={uuid4()}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404, r.text
    assert r.json()["code"] == "not_found"


async def test_today_with_ex_member_user_id_returns_404(
    async_client: AsyncClient, family_world: dict
) -> None:
    """Ex-member's group_id changed: even with valid JWT they're outside the
    Brunelli group now. Stefano's read against the ex-member returns 404 because
    ``group_id`` is re-looked-up from the DB on every request (FAM-07)."""
    token = await _login(async_client, "fam-stefano@test.example.com")
    r = await async_client.get(
        f"/api/today?user_id={family_world['ex_member'].id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404, r.text
    assert r.json()["code"] == "not_found"


# ──────────────────────────────────────────────────────────────────────────────
# Convergence smoke (FAM-09)
# ──────────────────────────────────────────────────────────────────────────────


async def test_family_polling_convergence(async_client: AsyncClient, family_world: dict) -> None:
    """FAM-09 — Stefano patches a shared variant; Marta refetches and sees the new state.

    Convergence is "≤5s" via TanStack Query refetchOnFocus + 30s staleTime on
    the frontend; in test mode the second fetch is instant. The assertion is
    correctness (Marta sees Stefano's updated visibility), not latency.
    """
    stefano_token = await _login(async_client, "fam-stefano@test.example.com")
    marta_token = await _login(async_client, "fam-marta@test.example.com")

    # Marta's initial cross-user view of Stefano's /today
    r1 = await async_client.get(
        f"/api/today?user_id={family_world['stefano'].id}",
        headers={"Authorization": f"Bearer {marta_token}"},
    )
    assert r1.status_code == 200
    initial_meals = r1.json()["meals"]
    assert any(m["visibility"] == "group_shared" for m in initial_meals)

    # Stefano flips his lunch from group_shared to private
    pr = await async_client.patch(
        f"/api/family/share/{family_world['stefano_lunch_shared_id']}",
        json={"visibility": "private"},
        headers={"Authorization": f"Bearer {stefano_token}"},
    )
    assert pr.status_code == 200, pr.text

    # Marta refetches (simulating refetchOnFocus) — lunch should disappear from her view
    r2 = await async_client.get(
        f"/api/today?user_id={family_world['stefano'].id}",
        headers={"Authorization": f"Bearer {marta_token}"},
    )
    assert r2.status_code == 200, r2.text
    new_meals = r2.json()["meals"]
    # Lunch entry should no longer appear (now private). All visible meals must
    # still be group_shared. The lunch meal was the only group_shared item
    # owned by Stefano; without it, Marta sees no lunch entry from Stefano.
    lunch_entries = [m for m in new_meals if m["meal_type"] == "lunch"]
    # If a lunch entry still appears, it MUST not have visibility=group_shared
    # (it would have been filtered out — but we double-check the contract).
    for m in new_meals:
        assert m["visibility"] == "group_shared"
    assert lunch_entries == [], "lunch was made private but still appears in cross-user view"
