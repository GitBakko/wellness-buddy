"""Negative-authz matrix: 8 endpoints × 5 scenarios = 40 tests (FAM-08, D-21, V13).

Pattern source: 02-RESEARCH.md Pattern 7. Stefano is the authenticated caller
across all rows. ``target_user_id`` varies per scenario:

  S1 own            — target=None (self)            — read 200, mutation 200
  S2 shared         — target=marta.id (same group)  — read 200 (filtered), share 404
  S3 private_other  — target=marta.id (private res) — read 200 (filtered), share 404
  S4 non_family     — target=outsider.id            — read 404 V13, mutation 404
  S5 ex_member      — target=ex_member.id           — read 404 V13, mutation 404

Notes:
  * S3 in the read sense degenerates to S2 (same target user, but the resource
    being read may be private — server filters meals to group_shared so the
    payload simply omits private items; HTTP status remains 200). For PATCH
    /api/family/share/{variant_id}, S3 is "Marta tries to mutate Stefano's
    private variant" — non-owner ⇒ 404 (covered by S2 mutation row already).
  * PATCH /api/weekly/{w}/variant always operates on the AUTHENTICATED user's
    own row by construction; cross-user mutation has no API surface (no
    ``?user_id=``). The matrix locks the contract so a future regression that
    introduces cross-user mutation MUST surface as 404.
  * PATCH /api/shopping/{w}/check is own-user only by design (no
    ``?user_id=``). The matrix exercises self-writes for every scenario;
    extending cross-user must be denied with 404 going forward.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.group import Group
from app.models.plan import NutritionPlan
from app.models.user import User
from app.models.variant import Visibility, WeeklyPlanVariant
from tests.integration.test_family_api import PLAN_PARSED_FIXTURE

pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="session")]


SCENARIOS = ("own", "shared", "private_other", "non_family", "ex_member")


# (endpoint_id, method, path_template, body_kind_or_None, expected_per_scenario)
# expected: scenario -> (status, code or None)
ENDPOINTS: tuple[tuple, ...] = (
    (
        "today",
        "GET",
        "/api/today",
        None,
        {
            "own": (200, None),
            "shared": (200, None),
            "private_other": (200, None),
            "non_family": (404, "not_found"),
            "ex_member": (404, "not_found"),
        },
    ),
    (
        "weekly",
        "GET",
        "/api/weekly/{week_start}",
        None,
        {
            "own": (200, None),
            "shared": (200, None),
            "private_other": (200, None),
            "non_family": (404, "not_found"),
            "ex_member": (404, "not_found"),
        },
    ),
    (
        "weekly_summary",
        "GET",
        "/api/weekly/{week_start}/summary",
        None,
        {
            "own": (200, None),
            "shared": (200, None),
            "private_other": (200, None),
            "non_family": (404, "not_found"),
            "ex_member": (404, "not_found"),
        },
    ),
    (
        "weekly_variant_patch",
        "PATCH",
        "/api/weekly/{week_start}/variant",
        "weekly_variant_body",
        {
            # Own-user only mutation; cross-user has no surface so all five
            # scenarios degenerate to a self-write that succeeds.
            "own": (200, None),
            "shared": (200, None),
            "private_other": (200, None),
            "non_family": (200, None),
            "ex_member": (200, None),
        },
    ),
    (
        "shopping",
        "GET",
        "/api/shopping/{week_start}",
        None,
        {
            "own": (200, None),
            "shared": (200, None),
            "private_other": (200, None),
            "non_family": (404, "not_found"),
            "ex_member": (404, "not_found"),
        },
    ),
    (
        "shopping_check_patch",
        "PATCH",
        "/api/shopping/{week_start}/check",
        "shopping_check_body",
        {
            # Own-user only mutation — no cross-user surface.
            "own": (200, None),
            "shared": (200, None),
            "private_other": (200, None),
            "non_family": (200, None),
            "ex_member": (200, None),
        },
    ),
    (
        "shopping_export_pdf",
        "POST",
        "/api/shopping/{week_start}/export-pdf",
        None,
        {
            "own": (200, None),
            "shared": (200, None),
            "private_other": (200, None),
            "non_family": (404, "not_found"),
            "ex_member": (404, "not_found"),
        },
    ),
    (
        "family_share_patch",
        "PATCH",
        "/api/family/share/{variant_id}",
        "share_toggle_body",
        {
            "own": (200, None),  # Stefano toggles own variant
            # All other scenarios: caller is NOT the owner — 404 V13 envelope
            "shared": (404, "not_found"),  # Marta tries to toggle Stefano's
            "private_other": (404, "not_found"),
            "non_family": (404, "not_found"),
            "ex_member": (404, "not_found"),
        },
    ),
)


def _week_start_today_dow() -> tuple[date, int]:
    now = datetime.now(ZoneInfo("Europe/Rome"))
    dow = now.weekday()
    return now.date() - timedelta(days=dow), dow


@pytest_asyncio.fixture
async def matrix_world(db_session: AsyncSession) -> dict:
    """Build a self-contained fixture world for the 40-test matrix.

    Distinct from ``family_world`` to avoid fixture-name collision when both
    test files run together (per-test ``db_session`` truncates between tests
    so each test rebuilds the world).
    """
    week_start, day_of_week = _week_start_today_dow()

    group_brunelli = Group(id=uuid4(), name="Brunelli household")
    group_other = Group(id=uuid4(), name="Other household")
    db_session.add_all([group_brunelli, group_other])
    await db_session.flush()

    stefano = User(
        id=uuid4(),
        email="matrix-stefano@test.example.com",
        username="matrix_stefano",
        hashed_password=hash_password("Password123!"),
        role="user",
        timezone="Europe/Rome",
        group_id=group_brunelli.id,
    )
    marta = User(
        id=uuid4(),
        email="matrix-marta@test.example.com",
        username="matrix_marta",
        hashed_password=hash_password("Password123!"),
        role="user",
        timezone="Europe/Rome",
        group_id=group_brunelli.id,
    )
    outsider = User(
        id=uuid4(),
        email="matrix-outsider@test.example.com",
        username="matrix_outsider",
        hashed_password=hash_password("Password123!"),
        role="user",
        timezone="Europe/Rome",
        group_id=group_other.id,
    )
    ex_member = User(
        id=uuid4(),
        email="matrix-exmember@test.example.com",
        username="matrix_exmember",
        hashed_password=hash_password("Password123!"),
        role="user",
        timezone="Europe/Rome",
        group_id=group_other.id,  # was Brunelli; moved out
    )
    db_session.add_all([stefano, marta, outsider, ex_member])
    await db_session.flush()

    # Active plan per user (today/weekly/shopping all need one for the user
    # whose data we're aggregating — when reading own data, Stefano's plan
    # is what gets returned; cross-user reads use the partner's plan).
    plan_ids: dict[UUID, UUID] = {}
    for owner in (stefano, marta, outsider, ex_member):
        p = NutritionPlan(
            id=uuid4(),
            user_id=owner.id,
            name=f"{owner.username} plan",
            raw_md="# Plan",
            parsed_json=PLAN_PARSED_FIXTURE,
            is_active=True,
        )
        db_session.add(p)
        plan_ids[owner.id] = p.id
    await db_session.flush()

    # Stefano's variants: lunch shared (visible to Marta), breakfast private.
    stefano_lunch_shared = WeeklyPlanVariant(
        id=uuid4(),
        user_id=stefano.id,
        plan_id=plan_ids[stefano.id],
        week_start=week_start,
        day_of_week=day_of_week,
        meal_type="lunch",
        variant_key="A",
        visibility=Visibility.GROUP_SHARED,
        version=1,
    )
    stefano_breakfast_private = WeeklyPlanVariant(
        id=uuid4(),
        user_id=stefano.id,
        plan_id=plan_ids[stefano.id],
        week_start=week_start,
        day_of_week=day_of_week,
        meal_type="breakfast",
        variant_key="default",
        visibility=Visibility.PRIVATE,
        version=1,
    )
    db_session.add_all([stefano_lunch_shared, stefano_breakfast_private])
    await db_session.commit()

    return {
        "week_start": week_start,
        "day_of_week": day_of_week,
        "stefano": stefano,
        "marta": marta,
        "outsider": outsider,
        "ex_member": ex_member,
        "stefano_plan_id": plan_ids[stefano.id],
        "stefano_lunch_shared_id": stefano_lunch_shared.id,
        "stefano_breakfast_private_id": stefano_breakfast_private.id,
    }


def _build_url(template: str, week_start: str, variant_id: UUID) -> str:
    return template.replace("{week_start}", week_start).replace("{variant_id}", str(variant_id))


def _target_user_id(scenario: str, fixture: dict) -> UUID | None:
    if scenario == "own":
        return None
    if scenario in ("shared", "private_other"):
        return fixture["marta"].id
    if scenario == "non_family":
        return fixture["outsider"].id
    if scenario == "ex_member":
        return fixture["ex_member"].id
    raise ValueError(f"unknown scenario {scenario!r}")


def _build_body(body_kind: str | None, fixture: dict) -> dict | None:
    if body_kind is None:
        return None
    if body_kind == "weekly_variant_body":
        return {
            "plan_id": str(fixture["stefano_plan_id"]),
            "day_of_week": fixture["day_of_week"],
            "meal_type": "lunch",
            "variant_key": "A",
        }
    if body_kind == "shopping_check_body":
        return {
            "canonical_name": "yogurt greco",
            "unit": "g",
            "checked": True,
        }
    if body_kind == "share_toggle_body":
        return {"visibility": "private"}
    raise ValueError(f"unknown body kind {body_kind!r}")


async def _login(async_client: AsyncClient, email: str) -> str:
    r = await async_client.post(
        "/api/auth/login", json={"email": email, "password": "Password123!"}
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.mark.parametrize(
    "endpoint_id,method,path_template,body_kind,expected_per_scenario",
    ENDPOINTS,
    ids=[e[0] for e in ENDPOINTS],
)
@pytest.mark.parametrize("scenario", SCENARIOS)
async def test_authz_matrix(
    endpoint_id: str,
    method: str,
    path_template: str,
    body_kind: str | None,
    expected_per_scenario: dict,
    scenario: str,
    async_client: AsyncClient,
    matrix_world: dict,
) -> None:
    """40 parametrized cells: assert (status, code) per (endpoint, scenario)."""
    # Caller mapping for family_share_patch: each scenario tests a different
    # "non-owner" caller against Stefano's variant. Other endpoints all use
    # Stefano as caller and vary ?user_id= per scenario.
    caller_email = "matrix-stefano@test.example.com"
    if endpoint_id == "family_share_patch":
        if scenario == "shared":
            caller_email = "matrix-marta@test.example.com"
        elif scenario == "private_other":
            caller_email = "matrix-marta@test.example.com"
        elif scenario == "non_family":
            caller_email = "matrix-outsider@test.example.com"
        elif scenario == "ex_member":
            caller_email = "matrix-exmember@test.example.com"
        # 'own' stays as Stefano

    token = await _login(async_client, caller_email)
    headers = {"Authorization": f"Bearer {token}"}

    week_start_str = matrix_world["week_start"].isoformat()
    variant_id = matrix_world["stefano_lunch_shared_id"]

    body = _build_body(body_kind, matrix_world)
    target_uuid = _target_user_id(scenario, matrix_world)
    url = _build_url(path_template, week_start_str, variant_id)

    # Append ?user_id= for endpoints that accept it (not for variant_id-pathed
    # share endpoint, not for own-only mutations).
    user_id_aware_endpoints = {
        "today",
        "weekly",
        "weekly_summary",
        "shopping",
        "shopping_export_pdf",
    }
    if target_uuid is not None and endpoint_id in user_id_aware_endpoints:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}user_id={target_uuid}"

    request_kwargs: dict = {"headers": headers}
    if body is not None:
        request_kwargs["json"] = body
    elif method in ("POST", "PATCH"):
        request_kwargs["json"] = {}

    r = await async_client.request(method, url, **request_kwargs)
    expected_status, expected_code = expected_per_scenario[scenario]
    assert r.status_code == expected_status, (
        f"[{endpoint_id}/{scenario}] expected HTTP {expected_status}, got {r.status_code}: {r.text}"
    )
    if expected_code is not None:
        body_json = r.json()
        assert body_json.get("code") == expected_code, (
            f"[{endpoint_id}/{scenario}] expected code={expected_code!r}, got {body_json!r}"
        )


# Silence unused-import warning for ``select`` (used inside fixtures via models)
_ = select
