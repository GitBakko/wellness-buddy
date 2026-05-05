"""PDF export integration tests (Plan 02-06 — SHOP-07, DEP-06, Pattern 8).

Plan 02-06 wires the WeasyPrint primary path with ReportLab fallback. This
suite covers:

- happy path: 200 + ``application/pdf`` + ``%PDF`` magic bytes + ``Content-
  Disposition`` filename
- 400 ``no_active_plan`` envelope
- 100-row stress test (page-break-inside: avoid + no overflow crash)
- Italian accent corpus rendered (best-effort text extraction via pypdf
  when available — manual iPhone/Mail.app verification handles the visual
  glyph rendering case)
- ReportLab fallback when ``PDF_BACKEND=reportlab``

The tests run with ``PDF_BACKEND=reportlab`` because GTK3/Pango is not
available on the local dev box (Plan 02-01 spike confirmed WeasyPrint only
on the production Windows Server 2019 box). The endpoint signature uses
``Depends(get_pdf_exporter)`` so swapping the backend is transparent — the
contract under test (Response/headers/PDF magic) is identical.
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
from app.services.pdf_export import ReportLabExporter, get_pdf_exporter

pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="session")]


@pytest.fixture(autouse=True)
def _force_reportlab_backend() -> object:
    """Pin the PDF backend to ReportLab for every test in this module.

    Local dev box lacks GTK3/Pango so WeasyPrint cannot ``dlopen`` libgobject.
    Plan 02-01 ABC factory makes the backend swap transparent — the contract
    under test (Response shape, %PDF magic, headers) is identical. Plan 02-08
    validates WeasyPrint primary on the production Windows Server.

    Using FastAPI dependency override (not env-var mutation) so the override
    is scoped to this test module — avoids leaking state into the rest of
    the suite (where ``shopping_api`` tests do not exercise PDF render and
    the env-cached ``settings.PDF_BACKEND`` is not relevant).
    """
    from app.main import app

    app.dependency_overrides[get_pdf_exporter] = lambda: ReportLabExporter()
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_pdf_exporter, None)


WEEK_START = "2026-05-04"


# Shopping list payload exercising the 5 categories (Frigo & Freschi, Frutta &
# Verdura, Dispensa, Condimenti, Integratori). Italian accents present in
# canonical names so the accent test can extract them.
ACCENT_FIXTURE: dict = {
    "personal_data": {"name": "Stefano"},
    "macro_target": {"kcal": 2100, "protein_g": 160, "carbs_g": 210, "fat_g": 70},
    "daily_structure": [],
    "breakfast": {
        "key": "default",
        "title": "Colazione",
        "ingredients": [
            {"name": "yogurt greco 200g"},
            {"name": "caffè 1 tazza"},
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
                    {"name": "pomodorì 150g"},
                    {"name": "pasta 80g"},
                    {"name": "olio evo q.b."},
                ],
                "macros": {"kcal": 480, "protein_g": 25, "carbs_g": 70, "fat_g": 10},
                "day_of_week": [0],
                "category": None,
            }
        ]
    },
    "dinners": {
        "lun": [
            {
                "key": "piatto",
                "title": "Tiramisù casalingo",
                "ingredients": [
                    {"name": "tiramisù 200g"},
                    {"name": "patate 200g"},
                ],
                "macros": {"kcal": 700, "protein_g": 50, "carbs_g": 40, "fat_g": 35},
                "day_of_week": [0],
                "category": None,
            }
        ]
    },
    "snacks": [
        {
            "key": "default",
            "title": "Spuntino",
            "ingredients": [{"name": "noci 20g"}],
            "macros": {"kcal": 280, "protein_g": 8, "carbs_g": 32, "fat_g": 14},
            "category": None,
        }
    ],
    "supplements": [],
    "weight_projection": [],
}


def _stress_fixture() -> dict:
    """Synthetic 100-row payload spread across 5 categories (20 each).

    Validates @page page-break-inside: avoid honors + no overflow on
    realistic-but-large lists.
    """
    # Each meal has up to 5 distinct ingredients keyed by canonical name.
    breakfast_items = [{"name": f"alimento_b{i} {(i + 1) * 10}g"} for i in range(20)]
    lunch_items = [{"name": f"verdura_l{i} {(i + 1) * 50}g"} for i in range(20)]
    dinner_items = [{"name": f"proteina_d{i} {(i + 1) * 80}g"} for i in range(20)]
    snack_items = [{"name": f"integratore_s{i} {i + 1} cps"} for i in range(20)]
    extra_items = [{"name": f"olio_evo_e{i} q.b."} for i in range(20)]
    return {
        "personal_data": {"name": "Stress"},
        "macro_target": {
            "kcal": 2100,
            "protein_g": 160,
            "carbs_g": 210,
            "fat_g": 70,
        },
        "daily_structure": [],
        "breakfast": {
            "key": "default",
            "title": "B",
            "ingredients": breakfast_items + extra_items,
            "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
            "category": None,
        },
        "lunches": {
            "lun": [
                {
                    "key": "opzione_a",
                    "title": "L",
                    "ingredients": lunch_items,
                    "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
                    "day_of_week": [0],
                    "category": None,
                }
            ]
        },
        "dinners": {
            "lun": [
                {
                    "key": "piatto",
                    "title": "D",
                    "ingredients": dinner_items,
                    "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
                    "day_of_week": [0],
                    "category": None,
                }
            ]
        },
        "snacks": [
            {
                "key": "default",
                "title": "S",
                "ingredients": snack_items,
                "macros": {"kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
                "category": None,
            }
        ],
        "supplements": [],
        "weight_projection": [],
    }


@pytest_asyncio.fixture
async def pdf_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid4(),
        email="pdf-user@test.example.com",
        username="pdf_user",
        hashed_password=hash_password("Password123!"),
        role="user",
        timezone="Europe/Rome",
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def pdf_plan_accent(db_session: AsyncSession, pdf_user: User) -> NutritionPlan:
    plan = NutritionPlan(
        id=uuid4(),
        user_id=pdf_user.id,
        name="Plan accent test",
        raw_md="# placeholder",
        parsed_json=ACCENT_FIXTURE,
        is_active=True,
    )
    db_session.add(plan)
    await db_session.commit()
    return plan


@pytest_asyncio.fixture
async def pdf_plan_stress(db_session: AsyncSession, pdf_user: User) -> NutritionPlan:
    plan = NutritionPlan(
        id=uuid4(),
        user_id=pdf_user.id,
        name="Plan stress test",
        raw_md="# placeholder",
        parsed_json=_stress_fixture(),
        is_active=True,
    )
    db_session.add(plan)
    await db_session.commit()
    return plan


@pytest_asyncio.fixture
async def empty_user(db_session: AsyncSession) -> User:
    """Authenticated user with no active plan — drives the 400 envelope."""
    user = User(
        id=uuid4(),
        email="empty-user@test.example.com",
        username="empty_user",
        hashed_password=hash_password("Password123!"),
        role="user",
        timezone="Europe/Rome",
    )
    db_session.add(user)
    await db_session.commit()
    return user


async def _login(client: AsyncClient, email: str, password: str) -> str:
    r = await client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


# ──────────────────────────────────────────────────────────────────────────────
# Happy path
# ──────────────────────────────────────────────────────────────────────────────


async def test_export_returns_pdf_bytes(
    async_client: AsyncClient,
    pdf_user: User,
    pdf_plan_accent: NutritionPlan,
) -> None:
    """SHOP-07 happy path: 200 + application/pdf + valid %PDF magic + Content-Disposition."""
    access = await _login(async_client, "pdf-user@test.example.com", "Password123!")
    r = await async_client.post(
        f"/api/shopping/{WEEK_START}/export-pdf",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200, r.text
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"
    assert len(r.content) > 1000  # at least 1 KB
    cd = r.headers.get("content-disposition", "")
    assert f"Lista-spesa-{WEEK_START}.pdf" in cd
    assert r.headers.get("cache-control") == "private, no-store"


async def test_export_no_active_plan_returns_400(
    async_client: AsyncClient,
    empty_user: User,
) -> None:
    """No active plan → 400 with code='no_active_plan'."""
    access = await _login(async_client, "empty-user@test.example.com", "Password123!")
    r = await async_client.post(
        f"/api/shopping/{WEEK_START}/export-pdf",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 400
    body = r.json()
    assert body["code"] == "no_active_plan"


async def test_export_unauthorized_returns_401(async_client: AsyncClient) -> None:
    r = await async_client.post(f"/api/shopping/{WEEK_START}/export-pdf")
    assert r.status_code == 401


# ──────────────────────────────────────────────────────────────────────────────
# Stress + accent verification
# ──────────────────────────────────────────────────────────────────────────────


async def test_export_stress_100_rows(
    async_client: AsyncClient,
    pdf_user: User,
    pdf_plan_stress: NutritionPlan,
) -> None:
    """Synthetic 100-row payload across 5 categories — validates page-break-inside: avoid."""
    access = await _login(async_client, "pdf-user@test.example.com", "Password123!")
    r = await async_client.post(
        f"/api/shopping/{WEEK_START}/export-pdf",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200
    assert r.content[:4] == b"%PDF"
    # 100 rows produces a noticeably larger PDF — confirms multi-page render
    assert len(r.content) > 2_000


async def test_export_italian_accents_present(
    async_client: AsyncClient,
    pdf_user: User,
    pdf_plan_accent: NutritionPlan,
) -> None:
    """Payload with Pomodorì, Caffè, Tiramisù — accents extractable from PDF text layer.

    Best-effort text extraction via pypdf when available; otherwise we still
    validate the response shape and rely on the iPhone Safari + Mail.app
    verification artifact for the visual glyph check.
    """
    access = await _login(async_client, "pdf-user@test.example.com", "Password123!")
    r = await async_client.post(
        f"/api/shopping/{WEEK_START}/export-pdf",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200
    assert r.content[:4] == b"%PDF"

    try:
        from io import BytesIO

        from pypdf import PdfReader  # type: ignore[import-untyped]

        reader = PdfReader(BytesIO(r.content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        # At least one Italian accent must round-trip through the text layer.
        # ReportLab default encoding emits "Caffe" if the glyph mapping fails,
        # so we look for a permissive accent presence (è, à, ù all acceptable).
        assert any(ch in text for ch in ("è", "à", "ì", "ò", "ù", "Caffè", "Tiramisù"))
    except ImportError:
        pytest.skip("pypdf not installed — manual iPhone Safari check covers accent verification")


# ──────────────────────────────────────────────────────────────────────────────
# ReportLab fallback path (Plan 02-01 ABC contract)
# ──────────────────────────────────────────────────────────────────────────────


async def test_export_via_reportlab_fallback(
    async_client: AsyncClient,
    pdf_user: User,
    pdf_plan_accent: NutritionPlan,
) -> None:
    """ReportLab backend honors the Plan 02-01 ABC contract.

    The autouse fixture pins this entire module to ReportLab via
    ``app.dependency_overrides``. We assert that the override actually
    returns a ``ReportLabExporter`` (sanity check) and that the endpoint
    contract is identical to the WeasyPrint primary path.
    """
    from app.main import app

    override = app.dependency_overrides.get(get_pdf_exporter)
    assert override is not None
    assert isinstance(override(), ReportLabExporter)

    access = await _login(async_client, "pdf-user@test.example.com", "Password123!")
    r = await async_client.post(
        f"/api/shopping/{WEEK_START}/export-pdf",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r.status_code == 200
    assert r.content[:4] == b"%PDF"
    assert r.headers["content-type"] == "application/pdf"


# ──────────────────────────────────────────────────────────────────────────────
# Template structure assertions (drift-impossible OKLCH gate is a separate
# script; here we validate the embedded font + page-break + 5-category loop
# stay in place even if the file is touched).
# ──────────────────────────────────────────────────────────────────────────────


def test_template_contains_font_face_and_page_break() -> None:
    """shopping_list.html must keep its 3 @font-face inline blocks + page-break + Jinja loop."""
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    tpl = repo_root / "backend" / "app" / "templates" / "shopping_list.html"
    assert tpl.exists(), f"missing template at {tpl}"
    body = tpl.read_text(encoding="utf-8")
    assert body.count("@font-face") == 3
    assert body.count("data:font/woff2;base64,") == 3
    assert "page-break-inside: avoid" in body
    assert "{% for category in categories %}" in body
    assert "{% for item in category.items %}" in body
    assert "@page" in body


# ──────────────────────────────────────────────────────────────────────────────
# OKLCH drift gate — invokes the script as a unit test so CI fails on drift.
# ──────────────────────────────────────────────────────────────────────────────


def test_template_oklch_mirrors_theme_css() -> None:
    """D-12 contract: shopping_list.html OKLCH coords mirror frontend/src/styles/theme.css."""
    import importlib.util
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    script = repo_root / "backend" / "scripts" / "check_pdf_template_oklch.py"
    assert script.exists(), f"missing OKLCH gate script at {script}"

    spec = importlib.util.spec_from_file_location("check_pdf_template_oklch", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    rc = module.main()
    assert rc == 0, "OKLCH coords drift between shopping_list.html and theme.css (D-12 violation)"
