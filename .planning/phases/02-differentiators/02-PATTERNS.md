# Phase 02: Differentiators — Pattern Map

**Mapped:** 2026-05-02
**Files analyzed:** ~70 (40 backend + 30 frontend + 1 PDF template + supporting fixtures/migration/docs)
**Analogs found:** 38 strong matches / 6 no-analog (PDF template, scheduler, BroadcastChannel lib, group_service, ingredient_parser, category_mapper)

## File Classification

### Backend services
| New/Modified file | Role | Data flow | Closest analog | Match Quality |
|---|---|---|---|---|
| `backend/app/services/weekly_service.py` | service | request-response (read) + CRUD | `backend/app/services/today_service.py` | exact (aggregator + tz + variant rows) |
| `backend/app/services/variant_service.py` | service | CRUD + LWW | `backend/app/services/today_service.py::complete_meal` (lines 224-281) + `weight_service.upsert_weight` | exact (variant upsert exists in stub form) |
| `backend/app/services/shopping_service.py` | service | CRUD + transform (aggregation) | `backend/app/services/today_service.py::build_today_payload` + `plan_service.diff_against_active` | role-match (aggregator across plan parsed_json) |
| `backend/app/services/ingredient_parser.py` | service (pure utility) | transform | `backend/app/parsers/normalizer.py` + `backend/app/parsers/plan_sections.py::_parse_macros` | role-match (regex + heuristic dictionary) |
| `backend/app/services/category_mapper.py` | service (pure utility) | transform (lookup) | `backend/app/parsers/plan_parser.py::SECTION_STEMS` (dict-based prefix mapping) | role-match (italian-keyword → category dict) |
| `backend/app/services/pdf_export.py` (ABC + WeasyPrint + ReportLab) | service (strategy) | transform (in-memory render) | `backend/app/ai/factory.py` + `app.state.ai_provider` ABC pattern | role-match (provider ABC, env-keyed factory) |
| `backend/app/services/group_service.py` | service | CRUD | `backend/app/services/plan_service.py::admin_assign_plan` (lines 227-263) | role-match (cross-user admin write + audit) |
| `backend/app/core/scheduler.py` | core/service | event-driven (cron) | none (NEW PATTERN — APScheduler factory) | no analog; Pattern 5 of RESEARCH is canonical |

### Backend API routes
| New/Modified file | Role | Data flow | Closest analog | Match Quality |
|---|---|---|---|---|
| `backend/app/api/weekly.py` (extend stub) | controller | request-response | `backend/app/api/today.py` + `backend/app/api/weight.py` | exact |
| `backend/app/api/shopping.py` (extend stub) | controller + file-I/O (PDF stream) | request-response + binary stream | `backend/app/api/plans.py::upload` (file response) + `today.py` | exact for JSON; `Response(content=..., media_type=application/pdf)` is new |
| `backend/app/api/family.py` (NEW) | controller | request-response | `backend/app/api/weight.py` (PATCH + 404 v13 pattern) | exact |
| `backend/app/api/today.py` (extend `?user_id=`) | controller | request-response (cross-user read) | `backend/app/api/today.py` lines 26-32 (current GET) + `app/core/deps.py::get_current_user` | exact (extend with new dep) |
| `backend/app/main.py` (extend lifespan) | config/bootstrap | request-response | `backend/app/main.py` lines 47-56 (existing lifespan + ai_provider binding) | exact (add scheduler.start/shutdown) |
| `backend/app/core/deps.py` (add `get_user_with_group_access`) | middleware/DI | request-response | `backend/app/core/deps.py::get_current_user` (lines 30-55) + `require_admin` (lines 69-73) | exact |

### Backend schemas (Pydantic v2)
| New/Modified file | Role | Data flow | Closest analog | Match Quality |
|---|---|---|---|---|
| `backend/app/schemas/weekly.py` (NEW) | schema | request-response | `backend/app/schemas/today.py` | exact |
| `backend/app/schemas/shopping.py` (NEW) | schema | request-response | `backend/app/schemas/today.py` + `backend/app/schemas/plan.py` | exact |
| `backend/app/schemas/family.py` (NEW) | schema | request-response | `backend/app/schemas/plan.py::AssignPlanRequest` | exact |
| `backend/app/schemas/plan_parsed.py` (extend `Categoria`) | schema | transform/validation | `backend/app/schemas/plan_parsed.py::Ingredient` (line 37-45 — `category` field already present) | exact (extend `Ingredient` model only) |

### Backend parsers
| New/Modified file | Role | Data flow | Closest analog | Match Quality |
|---|---|---|---|---|
| `backend/app/parsers/plan_sections.py` (extend `**Categoria:**`) | parser | transform | `backend/app/parsers/plan_sections.py::_extract_photo_url` (lines 31-43) | exact (twin regex helper) |

### Backend tests
| New/Modified file | Role | Data flow | Closest analog | Match Quality |
|---|---|---|---|---|
| `backend/tests/integration/test_weekly_api.py` | test | request-response | `backend/tests/integration/test_weight.py` + `test_today_api.py` | exact (CRUD matrix + cross-user 404) |
| `backend/tests/integration/test_shopping_api.py` | test | request-response | `backend/tests/integration/test_weight.py` | exact |
| `backend/tests/integration/test_family_api.py` | test | request-response | `backend/tests/integration/test_plans_api.py::test_activate_other_user_plan_403` (lines 382-407) | exact |
| `backend/tests/integration/test_family_authz_matrix.py` (40 tests) | test | request-response | `backend/tests/integration/test_plans_api.py` (8 fixtures + parametrize approach) + `test_weight.py` | role-match — extend with parametrize of (endpoint × scenario) |
| `backend/tests/integration/test_pdf_export.py` | test | binary I/O | `backend/tests/integration/test_plans_api.py::test_upload_*` (multipart pattern) | role-match |
| `backend/tests/integration/test_alembic_0001.py` | test | DB | `backend/tests/integration/test_alembic_baseline.py` | exact |
| `backend/tests/integration/test_scheduler.py` | test | event-driven | none (NEW — APScheduler+DST) | no analog |
| `backend/tests/unit/test_ingredient_parser.py` | test | unit (parametrize evil-corpus) | `backend/tests/unit/test_parser_evil.py` (lines 108-120 parametrize) | exact |
| `backend/tests/unit/test_category_mapper.py` | test | unit | `backend/tests/unit/test_normalizer.py` (small unit table) | role-match |
| `backend/tests/unit/test_variant_service.py` | test | unit | `backend/tests/integration/test_today_api.py` (variant model usage) | role-match |
| `backend/tests/unit/test_shopping_service.py` | test | unit | none direct; mirrors structure of unit/test_plan_schema.py | role-match |

### Backend migration
| New file | Role | Data flow | Closest analog | Match Quality |
|---|---|---|---|---|
| `backend/alembic/versions/0001_activate_groups.py` | migration | DB-batch | `backend/alembic/versions/0000_baseline.py` (Alembic op shape) | role-match (data-only — baseline is schema-only) |

### Backend templates / static
| New file | Role | Data flow | Closest analog | Match Quality |
|---|---|---|---|---|
| `backend/app/templates/shopping_list.html` | template | transform (Jinja2 → HTML → PDF) | none — first Jinja2 template in repo | **no analog** — UI-SPEC §6.4 is canonical |
| `backend/app/static/fonts/*.woff2` | asset | static | none | no analog |

### Frontend services (TanStack Query)
| New/Modified file | Role | Data flow | Closest analog | Match Quality |
|---|---|---|---|---|
| `frontend/src/services/weekly.ts` (NEW) | service hook | request-response | `frontend/src/services/today.ts` | exact |
| `frontend/src/services/shopping.ts` (NEW) | service hook | CRUD + offline mutations | `frontend/src/services/weight.ts` (full CRUD + mutationQueue) | exact |
| `frontend/src/services/family.ts` (NEW) | service hook | CRUD (mutation only) | `frontend/src/services/weight.ts::useUpdateWeight` (lines 84-99) | exact |

### Frontend components
| New/Modified file | Role | Data flow | Closest analog | Match Quality |
|---|---|---|---|---|
| `frontend/src/components/today/MealCard.tsx` (extend) | component | request-response | self (lines 44-140) — extend with badge slot + ⋯ menu slot | exact |
| `frontend/src/components/week/WeeklyMacroRing.tsx` | component | display | `frontend/src/components/today/MacroRing.tsx` | **exact** (same SVG anatomy, +caption variant) |
| `frontend/src/components/week/WeekPicker.tsx` | component | event-driven (chip + popover) | `frontend/src/components/today/WeightQuickLog.tsx` (popover) — none ideal | role-match |
| `frontend/src/components/week/DayCompletionStrip.tsx` | component | display | `frontend/src/components/today/MacroDisplay.tsx` (compact metric strip) | role-match |
| `frontend/src/components/week/VariantSelector.tsx` | component | event-driven (Radix DropdownMenu) | `frontend/src/components/today/MealCard.tsx` (Phosphor + tap) | role-match |
| `frontend/src/components/family/SharedBadge.tsx` | component | display + tooltip | `frontend/src/components/today/DayStatusIndicator.tsx` | role-match |
| `frontend/src/components/family/ShareToggleMenu.tsx` | component | event-driven (DropdownMenu + Switch) | none | no analog |
| `frontend/src/components/family/ConflictToast.tsx` | component | event-driven (sonner) | `frontend/src/lib/mutationQueue.ts` lines 53-57 (existing 409 toast) | role-match |
| `frontend/src/components/shopping/ShoppingCategorySection.tsx` | component | display + collapse | none | partial match (re-uses Phosphor + tokens) |
| `frontend/src/components/shopping/ShoppingItemRow.tsx` | component | event-driven (checkbox + swipe) | `frontend/src/components/today/MealCard.tsx` (44×44 button + tokens) | role-match |
| `frontend/src/components/shopping/ShoppingViewToggle.tsx` | component | event-driven (Radix ToggleGroup) | none | no analog |
| `frontend/src/components/icons/index.ts` (extend) | facade | static | self | exact (add 11 named exports) |

### Frontend pages
| New/Modified file | Role | Data flow | Closest analog | Match Quality |
|---|---|---|---|---|
| `frontend/src/pages/Week.tsx` | page | request-response | `frontend/src/pages/Today.tsx` | exact (loading/empty/error/main shell) |
| `frontend/src/pages/Shopping.tsx` (`/spesa`) | page | request-response | `frontend/src/pages/Today.tsx` + `History.tsx` | exact |

### Frontend i18n + Dexie + lib
| New/Modified file | Role | Data flow | Closest analog | Match Quality |
|---|---|---|---|---|
| `frontend/src/i18n/copy.it.ts` (extend namespaces `week.*`, `shopping.*`, `family.*`, `sync.*`, `pwa.*`) | i18n | static | self (lines 13-92, existing `today.*` namespace) | exact |
| `frontend/src/db/dexie.ts` (v1 → v2 with cache_weekly + cache_shopping) | db schema | local cache | self (lines 36-47, `version(1).stores({...})`) | exact (add `version(2).stores({...})`) |
| `frontend/src/db/schema.ts` (add `CachedWeekly`, `CachedShopping`) | types | static | self (`CachedToday` lines 29-34, `CachedWeightLog` lines 48-54) | exact |
| `frontend/src/lib/ifUnmodifiedSince.ts` | utility | transform | `frontend/src/lib/format.ts` (utility module shape) | role-match |
| `frontend/src/lib/broadcastChannel.ts` | utility | event-driven (multi-tab) | none | no analog |

### Frontend tests
| New file | Role | Data flow | Closest analog | Match Quality |
|---|---|---|---|---|
| `frontend/src/components/week/*.test.tsx` | test | unit | `frontend/src/components/today/MealCard.test.tsx` + `MacroRing.test.tsx` | exact |
| `frontend/src/components/shopping/*.test.tsx` | test | unit | `frontend/src/components/today/MealCard.test.tsx` | exact |
| `frontend/tests/visual/light.spec.ts` (extend ROUTES, regen baselines) | test | visual | self lines 15-27 | exact |
| `frontend/tests/e2e/today.spec.ts` clone → `week.spec.ts` / `spesa.spec.ts` | test | e2e | self | exact |

### Phase docs (planning artifacts)
| New file | Role | Closest analog |
|---|---|---|
| `.planning/phases/02-differentiators/02-01-GTK3-SPIKE.md` | doc | `.planning/phases/01-foundation/01-08-tone-calibration-checklist.md` |
| `.planning/phases/02-differentiators/02-03-DEPLOY-CHECKLIST.md` | doc | `01-08-tone-calibration-checklist.md` (sign-off matrix shape) |
| `.planning/phases/02-differentiators/VERIFICATION.md` | doc | `.planning/phases/01-foundation/VERIFICATION.md` |

---

## Pattern Assignments

### `backend/app/services/weekly_service.py` (service, request-response/CRUD)

**Analog:** `backend/app/services/today_service.py`

**Imports + module-doc pattern** (today_service.py lines 1-32):
```python
"""Weekly aggregator service — Phase 2.

Computes /weekly/{week_start} payload: 7 days × 4 meal slots, each with chosen variant
(default 'Opzione A'), aggregated macros per day, plus weekly totals + completion strip.

Source: WEEK-01..WEEK-05, T-API-02 cross-user via get_user_with_group_access.
"""

from __future__ import annotations

from datetime import date as date_t, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.plan import NutritionPlan
from app.models.user import User
from app.models.variant import Visibility, WeeklyPlanVariant
```

**Aggregator entry-point pattern** (today_service.py lines 141-176 — copy week-keyed instead of day-keyed):
```python
async def build_weekly_payload(
    session: AsyncSession, *, user: User, week_start: date_t
) -> WeeklyResponse:
    """Aggregate 7 days starting at `week_start` (a Monday). Scoped to `user.id` only."""
    plan = (
        await session.scalars(
            select(NutritionPlan).where(
                NutritionPlan.user_id == user.id,
                NutritionPlan.is_active.is_(True),
            )
        )
    ).first()

    variants = (
        await session.scalars(
            select(WeeklyPlanVariant).where(
                WeeklyPlanVariant.user_id == user.id,
                WeeklyPlanVariant.week_start == week_start,
            )
        )
    ).all()
    # ... build day-by-day from plan.parsed_json + apply variant.variant_key + completion
```

**Defensive coercion pattern from parsed_json** (today_service.py lines 49-73 — reuse `_coerce_macros`, `_coerce_photo_url`).

---

### `backend/app/services/variant_service.py` (service, CRUD + LWW)

**Analog:** `backend/app/services/today_service.py::complete_meal` (lines 224-281) + `weight_service.upsert_weight` (lines 30-72)

**Upsert + version bump pattern** (today_service.py lines 248-281):
```python
variant = (
    await session.scalars(
        select(WeeklyPlanVariant).where(
            WeeklyPlanVariant.user_id == user.id,
            WeeklyPlanVariant.week_start == week_start,
            WeeklyPlanVariant.day_of_week == day_of_week,
            WeeklyPlanVariant.meal_type == meal_type,
        )
    )
).first()

if not variant:
    variant = WeeklyPlanVariant(
        user_id=user.id, plan_id=plan.id,
        week_start=week_start, day_of_week=day_of_week,
        meal_type=meal_type, variant_key="default",
        visibility=(Visibility.GROUP_SHARED if meal_type in ("lunch", "dinner") else Visibility.PRIVATE),
        completed=True,
    )
    session.add(variant)
else:
    variant.completed = True
    variant.version = variant.version + 1   # ← LWW version bump pattern
```

**LWW conflict detection pattern** (RESEARCH.md Pattern 4 — verbatim — lines 786-867):
```python
# Conflict detection — only when row exists AND client sent a precondition.
if row is not None and if_unmodified_since is not None:
    if row.updated_at > if_unmodified_since:
        partner = await _conflict_partner_name(session, row=row, current_user=user)
        raise AppException(
            409,
            _MSG_CONFLICT.format(nome=partner or "un familiare"),
            "version_conflict",
        )
```

**Audit log pattern** (plan_service.py lines 73-83 — call before commit):
```python
await write_audit(
    session, actor_id=user.id, action="variant_update",
    target_type="weekly_plan_variant", target_id=variant.id,
    payload={"week_start": str(week_start), "meal_type": meal_type, "variant_key": variant_key},
)
await session.commit()
await session.refresh(variant)
```

---

### `backend/app/services/shopping_service.py` (service, CRUD + transform)

**Analog:** `backend/app/services/today_service.py::build_today_payload` + `plan_service.diff_against_active`

**Aggregation entry-point pattern** (today_service.py lines 141-176):
```python
async def aggregate_for_week(
    session: AsyncSession, *, user_id: UUID, week_start: date_t
) -> ShoppingListResponse:
    """Generate categorized shopping list from variants chosen for week."""
    plan = (await session.scalars(select(NutritionPlan).where(
        NutritionPlan.user_id == user_id, NutritionPlan.is_active.is_(True)
    ))).first()
    if not plan:
        raise AppException(400, "Nessun piano attivo.", "no_active_plan")

    variants = (await session.scalars(select(WeeklyPlanVariant).where(
        WeeklyPlanVariant.user_id == user_id, WeeklyPlanVariant.week_start == week_start
    ))).all()
    # ... iterate plan.parsed_json["lunches"]["default"] / ["dinners"]["default"]
    # ... explode each meal's ingredients via ingredient_parser.parse(line)
    # ... merge by (canonical_name, unit) — sum amounts when units match
    # ... categorize via category_mapper.lookup(name) (or `**Categoria:**` annotation)
```

**Checkbox state persistence** (mirror `weight_service.upsert_weight` lines 30-72):
```python
existing = (await session.scalars(
    select(ShoppingListState).where(
        ShoppingListState.user_id == user_id,
        ShoppingListState.week_start == week_start,
    )
)).first()
if existing:
    existing.items_json = patched_items_json
    existing.version = existing.version + 1
    await session.commit()
    await session.refresh(existing)
    return existing
```

---

### `backend/app/services/ingredient_parser.py` (utility, transform)

**Analog:** `backend/app/parsers/normalizer.py` (regex + NFC) + `backend/app/parsers/plan_sections.py::_parse_macros`

**Regex constants pattern** (plan_sections.py lines 27-34):
```python
_NUMBER_RE = re.compile(r"(\d+(?:[.,]\d+)?)")
_PHOTO_RE = re.compile(
    r"^\s*\*\*\s*foto\s*:\s*\*\*\s+(\S{1,500})\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)
```

**Normalize pipeline pattern** (normalizer.py lines 37-54 — copy NFC + lowercase + collapse-whitespace shape):
```python
def normalize(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s
```

**Full ingredient parser body** — verbatim from RESEARCH.md Pattern 3 (lines 581-731). Use the `ParsedIngredient` dataclass + `_UNITS_LONG_FIRST` ordered tuple + `_UNIT_CANON` dict + `parse()` entry-point.

**Evil-corpus seed table** — RESEARCH.md lines 733-751 — must pass.

---

### `backend/app/services/category_mapper.py` (utility, lookup)

**Analog:** `backend/app/parsers/plan_parser.py::SECTION_STEMS` (lines 30-43)

**Ordered-dict prefix-lookup pattern** (plan_parser.py lines 30-43, 94-101):
```python
# Order matters — longer/more specific keywords first
_KEYWORD_TO_CATEGORY: dict[str, str] = {
    "yogurt": "Frigo & Freschi",
    "latte": "Frigo & Freschi",
    "uova": "Frigo & Freschi",
    "salmone": "Frigo & Freschi",
    "pomodoro": "Frutta & Verdura",
    "mela": "Frutta & Verdura",
    "pasta": "Dispensa",
    "olio evo": "Condimenti",
    "vitamina": "Integratori",
    # ... etc.
}

def lookup(name: str) -> str:
    """Resolve canonical name to category. Default 'Dispensa' if no match."""
    norm = name.lower().strip()
    for keyword, category in _KEYWORD_TO_CATEGORY.items():
        if keyword in norm:
            return category
    return "Dispensa"
```

---

### `backend/app/services/pdf_export.py` (strategy ABC)

**Analog:** AI provider ABC (`backend/app/ai/factory.py` + `app.state.ai_provider` binding). Note: full code in RESEARCH.md Pattern 2 (lines 469-558) — use verbatim.

**Factory entry-point pattern** (RESEARCH.md lines 552-558):
```python
def get_pdf_exporter() -> PdfExporter:
    """FastAPI Depends() factory. Returns active backend per env."""
    backend = (settings.PDF_BACKEND or "weasyprint").lower()
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    if backend == "reportlab":
        return ReportLabExporter()
    return WeasyPrintExporter(template_dir=template_dir)
```

**Lazy import pattern** (so test envs without GTK3 can still import the module):
```python
def __init__(self, template_dir: Path) -> None:
    from jinja2 import Environment, FileSystemLoader  # lazy
    self._env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)

async def render_shopping_list(self, ...) -> bytes:
    from weasyprint import HTML  # lazy — keeps test envs without GTK3 healthy
    ...
```

---

### `backend/app/core/scheduler.py` (NEW pattern)

**Analog:** none — first APScheduler use in repo.

**Canonical reference:** RESEARCH.md Pattern 5 (lines 937-1000). Use verbatim.

**Lifespan integration pattern** (extend `backend/app/main.py` lines 47-56):
```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging(settings.LOG_LEVEL)
    app.state.ai_provider = build_provider()
    # Phase 2 additions
    from app.core.scheduler import build_scheduler, register_user_jobs
    scheduler = build_scheduler()
    await register_user_jobs(scheduler, session_factory=app.state.session_factory)
    scheduler.start()
    app.state.scheduler = scheduler
    yield
    scheduler.shutdown(wait=False)
```

---

### `backend/app/core/deps.py` (extend with `get_user_with_group_access`)

**Analog:** self — `get_current_user` (lines 30-55) + `require_admin` (lines 69-73)

**New dependency pattern** (mirrors get_current_user shape):
```python
async def get_user_with_group_access(
    target_user_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Allow access to target_user data ONLY when same group_id (re-look-up from DB).

    Source: D-19, D-20 — group_id NEVER in JWT.
    Returns 404 (not 403) on cross-group to mitigate info disclosure (V13 inherited).
    """
    if target_user_id == user.id:
        return user  # own data
    target = (await session.scalars(select(User).where(User.id == target_user_id))).first()
    if not target or target.group_id is None or target.group_id != user.group_id:
        raise AppException(404, "Risorsa non trovata.", "not_found")
    return target
```

---

### `backend/app/api/weekly.py` (extend stub)

**Analog:** `backend/app/api/today.py` (full file, lines 1-50)

**Router prefix + auth pattern** (today.py lines 23-32):
```python
router = APIRouter(prefix="/api/weekly", tags=["weekly"])

@router.get("/{week_start}", response_model=WeeklyResponse)
async def get_weekly(
    week_start: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> WeeklyResponse:
    return await weekly_service.build_weekly_payload(
        session, user=user, week_start=date.fromisoformat(week_start),
    )
```

**PATCH with If-Unmodified-Since header pattern** — RESEARCH.md Pattern 4 lines 873-892 (verbatim).

**Cross-user GET pattern** (extend with new dep):
```python
@router.get("/{week_start}", response_model=WeeklyResponse)
async def get_weekly(
    week_start: str,
    user_id: UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> WeeklyResponse:
    target_user = current_user
    if user_id and user_id != current_user.id:
        target_user = await get_user_with_group_access(user_id, current_user, session)
    return await weekly_service.build_weekly_payload(session, user=target_user, week_start=...)
```

---

### `backend/app/api/shopping.py` (extend stub)

**Analog:** `backend/app/api/today.py` for JSON endpoints; `backend/app/api/plans.py::upload` for multipart-style binary handling.

**Binary stream response pattern** (RESEARCH.md lines 564-579):
```python
from fastapi import Response

@router.post("/{week_start}/export-pdf")
async def export_pdf(
    week_start: str,
    user: User = Depends(get_current_user),
    exporter: PdfExporter = Depends(get_pdf_exporter),
    session: AsyncSession = Depends(get_session),
) -> Response:
    payload = await shopping_service.build_pdf_payload(
        session, user_id=user.id, week_start=week_start,
    )
    pdf_bytes = await exporter.render_shopping_list(**payload)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="spesa-{week_start}.pdf"'},
    )
```

---

### `backend/app/api/family.py` (NEW)

**Analog:** `backend/app/api/weight.py` (PATCH semantics + cross-user 404)

**Mutating endpoint pattern** (weight.py lines 53-68 — PATCH variant visibility):
```python
@router.patch("/share/{variant_id}", response_model=VariantResponse)
async def patch_share(
    variant_id: UUID,
    body: ShareTogglePayload,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> VariantResponse:
    row = await family_service.toggle_share(
        session, user_id=user.id, variant_id=variant_id, visibility=body.visibility,
    )
    return VariantResponse.model_validate(row)
```

---

### `backend/app/schemas/weekly.py` (NEW)

**Analog:** `backend/app/schemas/today.py` (full file)

**StrictModel + ConfigDict pattern** (today.py lines 16-30):
```python
from pydantic import BaseModel, ConfigDict, Field

class VariantResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    user_id: str
    week_start: str
    day_of_week: int
    meal_type: str
    variant_key: str
    visibility: str   # 'private' | 'group_shared'
    version: int
    updated_at: str   # ISO-8601 — used for If-Unmodified-Since echo
    completed: bool

class PatchVariantPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: str
    day_of_week: int
    meal_type: str
    variant_key: str
    visibility: str | None = None
```

---

### `backend/app/schemas/plan_parsed.py` (extend `Categoria` annotation)

**Analog:** self — `Ingredient` model (lines 37-45) ALREADY has `category: str | None = None`. The Phase 2 work is wiring the parser to populate it. No schema change needed; only `plan_sections.py` extension.

**Existing `Ingredient` model** (verbatim, lines 37-45):
```python
class Ingredient(BaseModel):
    """Phase 1 unused — placeholder for Phase 2 deeper meal parsing."""
    model_config = ConfigDict(extra="forbid")

    name: str
    quantity: float | None = None
    unit: str | None = None
    category: str | None = None
```

---

### `backend/app/parsers/plan_sections.py` (extend `**Categoria:**` extraction)

**Analog:** self — `_extract_photo_url` (lines 31-43) is the exact twin pattern.

**Photo URL helper pattern (copy verbatim, swap regex)** (lines 28-43):
```python
_CATEGORY_RE = re.compile(
    r"^\s*\*\*\s*categoria\s*:\s*\*\*\s+(.{1,50}?)\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)

def _extract_category(body: str) -> str | None:
    """Phase 2 — sniff `**Categoria:** <name>` line. Returns None when absent (default 'Dispensa')."""
    m = _CATEGORY_RE.search(body)
    if not m:
        return None
    return m.group(1).strip() or None
```

Then thread into `_parse_meal_options` and `_parse_breakfast` exactly like `_extract_photo_url` (lines 156-165).

---

### `backend/alembic/versions/0001_activate_groups.py` (data-only migration)

**Analog:** `backend/alembic/versions/0000_baseline.py` (lines 1-19 — Alembic revision shape)

**Revision header pattern** (0000_baseline.py lines 1-19):
```python
"""activate groups (data-only — D-22, D-23)

Phase 1 baseline 0000_baseline.py created the `groups` table + `users.group_id` FK.
Phase 2 backfills: for each User without a group_id, create a personal household.

Revision ID: 0001_activate_groups
Revises: a694bcd4d792
Create Date: 2026-05-XX
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_activate_groups'
down_revision: Union[str, Sequence[str], None] = 'a694bcd4d792'
branch_labels = None
depends_on = None
```

**Body pattern** — full code in RESEARCH.md Pattern 6 (lines 1040-1126). Use verbatim. Key: reflective `sa.table()` (NOT `app.models.User`) for migration stability.

---

### `backend/tests/integration/test_weekly_api.py` (CRUD + cross-user)

**Analog:** `backend/tests/integration/test_weight.py` (full file)

**Fixture pattern** (test_weight.py lines 32-59):
```python
pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="session")]

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

async def _login(client: AsyncClient, email: str, password: str) -> str:
    r = await client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]
```

**Cross-user 404 test pattern** (test_weight.py lines 248-272):
```python
async def test_weekly_patch_other_user_returns_404(
    async_client, db_session, test_user, other_user,
) -> None:
    """V13 + D-19: cross-user mutation returns 404, not 403."""
    # ... seed variant for test_user, login as other_user, PATCH it ...
    assert r.status_code == 404
    assert r.json()["code"] == "not_found"
```

**409 conflict test pattern** (NEW for Phase 2 — model after the cross-user test shape):
```python
async def test_patch_variant_409_on_stale_if_unmodified_since(...) -> None:
    # PATCH with stale If-Unmodified-Since header → 409 + version_conflict code
    r = await async_client.patch(
        f"/api/weekly/{week_start}/variant",
        json=payload,
        headers={
            "Authorization": f"Bearer {access}",
            "If-Unmodified-Since": "2020-01-01T00:00:00+00:00",  # ancient
        },
    )
    assert r.status_code == 409
    assert r.json()["code"] == "version_conflict"
```

---

### `backend/tests/integration/test_family_authz_matrix.py` (40 tests)

**Analog:** `backend/tests/integration/test_plans_api.py::test_activate_other_user_plan_403` (lines 382-407) + 8-fixture matrix shape from `test_weight.py`

**Parametrize endpoint × scenario pattern** (extend `test_parser_evil.py` parametrize style — lines 108-120):
```python
ENDPOINTS = [
    ("GET", "/api/today?user_id={target}"),
    ("GET", "/api/weekly/{week}?user_id={target}"),
    ("PATCH", "/api/weekly/{week}/variant"),
    # ... 8 endpoints total per FAM-08
]

SCENARIOS = ["S1_own", "S2_shared_via_group", "S3_private_other_user",
             "S4_non_family", "S5_ex_member"]
EXPECTED = {  # (endpoint, scenario) → status code
    ("GET", "S1_own"): 200,
    ("GET", "S3_private_other_user"): 404,  # info-disclosure mitigation
    # ... 40 total cells
}

@pytest.mark.parametrize("endpoint", ENDPOINTS, ids=lambda e: f"{e[0]} {e[1]}")
@pytest.mark.parametrize("scenario", SCENARIOS)
async def test_authz_matrix(endpoint, scenario, ...) -> None:
    method, path = endpoint
    expected_status = EXPECTED[(method, scenario)]
    # ... invoke + assert
```

---

### `backend/tests/integration/test_alembic_0001.py` (idempotence)

**Analog:** `backend/tests/integration/test_alembic_baseline.py`

**Idempotence test pattern** — RESEARCH.md Pattern 6 lines 1130-1143 (verbatim):
```python
async def test_0001_idempotent(alembic_engine, db_session):
    """Running 0001 twice produces the same outcome as once."""
    from alembic.config import Config
    from alembic import command

    cfg = Config("alembic.ini")
    command.upgrade(cfg, "0001")
    first = (await db_session.execute(sa.text("SELECT id, group_id FROM users"))).all()
    command.upgrade(cfg, "0001")  # Re-run — should be no-op
    second = (await db_session.execute(sa.text("SELECT id, group_id FROM users"))).all()
    assert first == second
```

---

### `backend/tests/unit/test_ingredient_parser.py` (parametrize evil-corpus)

**Analog:** `backend/tests/unit/test_parser_evil.py` (lines 108-120)

**Parametrize pattern** (test_parser_evil.py lines 108-120):
```python
EVIL_CASES = [
    ("Yogurt greco 200g + frutta secca 30g + miele 10g",
     [("yogurt greco", 200, "g"), ("frutta secca", 30, "g"), ("miele", 10, "g")]),
    ("Olio EVO q.b.", [("olio evo", None, "qb")]),
    ("Un pizzico di sale", [("di sale", 1, "pizzico")]),
    ("1,5 kg pomodori", [("pomodori", 1.5, "kg")]),
    # ... 15 cases verbatim from RESEARCH.md lines 733-751
]

@pytest.mark.parametrize("line,expected", EVIL_CASES, ids=lambda c: c[0] if isinstance(c, str) else "")
def test_evil_corpus_quantities(line: str, expected: list) -> None:
    result = parse(line)
    assert [(p.name, p.amount, p.unit) for p in result] == expected
```

---

### `backend/app/templates/shopping_list.html` (NO ANALOG — first Jinja2 in repo)

**Canonical reference:** UI-SPEC §6.4 (lines 262-411). Use the full HTML+CSS body verbatim.

**Key contracts:**
- `@page` for A4 portrait + 20mm margins + page counter footer
- `@font-face` woff2 base64 inline (PITFALLS #13 italian accents)
- OKLCH color values MUST match `frontend/src/styles/theme.css` (CI grep gate per UI-SPEC §6.4 contract)
- Body: `<header>` with `<h1 class="title">`, `<p class="subtitle">` (Instrument Serif italic — escape hatch reused from §3.2), `<div class="wordmark">`
- `<main>` loops `{% for category in categories %}` → `<section class="category"><h2>{{ category.name }}</h2><ul class="items">{% for item ... %}</ul></section>`
- Checkbox glyph `☐` (U+2610 BALLOT BOX) Geist Mono — NOT image
- Quantity right-aligned tabular Geist Mono

---

### `frontend/src/services/weekly.ts` (NEW)

**Analog:** `frontend/src/services/today.ts` (full file)

**Module-doc + types pattern** (today.ts lines 1-50):
```typescript
// frontend/src/services/weekly.ts
// TanStack Query bindings for /api/weekly + variant mutations.
// Source: WEEK-01..WEEK-05, RESEARCH Pattern 4 (LWW + If-Unmodified-Since).

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { db } from '@/db/dexie';
import { useAuthStore } from '@/stores/auth';

export interface WeeklyDay { /* ... */ }
export interface WeeklyResponse {
  week_start: string;
  days: WeeklyDay[];
  totals: { kcal: number; protein_g: number; carbs_g: number; fat_g: number };
}

export const weeklyQueryKey = (userId: string, weekStart: string) =>
  ['weekly', userId, weekStart] as const;
```

**useQuery + Dexie mirror pattern** (today.ts lines 54-78):
```typescript
export function useWeekly(weekStart: string, userId?: string) {
  const id = userId ?? useAuthStore.getState().user?.id ?? '';
  return useQuery<WeeklyResponse>({
    queryKey: weeklyQueryKey(id, weekStart),
    queryFn: async () => {
      const url = userId
        ? `/api/weekly/${weekStart}?user_id=${userId}`
        : `/api/weekly/${weekStart}`;
      const resp = await apiClient.request<WeeklyResponse>({ url });
      try {
        await db.cache_weekly.put({
          user_id: id,
          week_start: weekStart,
          payload: resp,
          fetched_at: new Date().toISOString(),
        });
      } catch { /* Dexie unavailable */ }
      return resp;
    },
    staleTime: 30_000,
    refetchOnWindowFocus: true,  // D-16: real-time strategy = polling on focus
  });
}
```

**Mutation with optimistic update + 409 toast** — RESEARCH.md Pattern 4 lines 896-933 (verbatim).

---

### `frontend/src/services/shopping.ts` (NEW)

**Analog:** `frontend/src/services/weight.ts` (full file — has the full CRUD + offline mutationQueue pattern)

**useMutation + offline queue pattern** (weight.ts lines 50-82):
```typescript
export function useToggleItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: { week_start: string; item_id: string; checked: boolean }) => {
      try {
        return await apiClient.request<ShoppingResponse>({
          url: `/api/shopping/${input.week_start}/check`,
          method: 'PATCH',
          data: { item_id: input.item_id, checked: input.checked },
        });
      } catch (e: unknown) {
        if (typeof navigator !== 'undefined' && navigator.onLine === false) {
          await enqueueMutation({
            endpoint: `/api/shopping/${input.week_start}/check`,
            method: 'PATCH',
            body: input,
          });
          // Optimistic local row...
        }
        throw e instanceof Error ? e : new Error(String(e));
      }
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['shopping'] });
    },
  });
}
```

---

### `frontend/src/components/today/MealCard.tsx` (extend with badge slot + ⋯ menu slot)

**Analog:** self (lines 1-140)

**Existing layout to extend** (MealCard.tsx lines 53-110 — preserve flex container, add slot in info-column caption row):
```tsx
{/* Info column — extend caption row with SharedBadge */}
<div className="flex-1 min-w-0 flex flex-col gap-[var(--spacing-1)]">
  <div className="text-[var(--text-caption)] font-bold uppercase tracking-[0.08em] text-[color:var(--color-text-muted)] flex items-center gap-[var(--spacing-1)]">
    {slotLabel}
    {meal.visibility === 'group_shared' && meal.owner_user_id !== currentUserId && (
      <SharedBadge partnerName={partnerLookup[meal.owner_user_id]} updatedAt={meal.updated_at} />
    )}
  </div>
  <h3 className="text-[var(--text-base)] font-semibold leading-tight ...">
    {meal.title}
    {meal.owner_user_id === currentUserId && (
      <ShareToggleMenu meal={meal} />  {/* DotsThreeOutline + Switch */}
    )}
  </h3>
  {/* macros chips unchanged */}
</div>
```

---

### `frontend/src/components/week/WeeklyMacroRing.tsx`

**Analog:** `frontend/src/components/today/MacroRing.tsx` (full file — exact match)

**Reuse SVG anatomy verbatim** (MacroRing.tsx lines 75-170 — same 4-concentric-rings, same colors). Differences for Phase 2:
- Center text: `consumedLabel` is weekly kcal sum (× 7 days), `subtitle` uses `copy.week.weeklyTotalSubtitle` ("su 15.400")
- Below SVG: 7-day completion strip `<DayCompletionStrip>` — NEW component
- ARIA label uses `copy.week.weeklyMacroRingAria`

**Helper functions** (MacroRing.tsx lines 38-50 — `clamp()` and `dasharray()` copy verbatim).

---

### `frontend/src/pages/Week.tsx` (`/settimana` route)

**Analog:** `frontend/src/pages/Today.tsx` (full file — exact loading/error/empty/main shell)

**Page shell pattern** (Today.tsx lines 119-142):
```tsx
export default function Week(): React.ReactElement {
  const { weekStart } = useParams<{ weekStart: string }>();
  const userId = useAuthStore((s) => s.user?.id) ?? '';
  const { data, isLoading, isError } = useWeekly(weekStart!, userId);

  if (isLoading) {
    return (
      <main className="p-[var(--spacing-4)] flex flex-col gap-[var(--spacing-4)] max-w-3xl mx-auto">
        <Skeleton className="h-9 w-2/3" />
        <Skeleton className="h-56 w-full" />
        <Skeleton className="h-24 w-full" />
      </main>
    );
  }
  if (isError || !data) {
    return (
      <main role="alert" className="p-[var(--spacing-6)] ...">
        <p className="text-[color:var(--color-text-muted)] text-center">{copy.errors.generic500}</p>
      </main>
    );
  }
  if (data.days.every(d => d.meals.length === 0)) {
    return <EmptyStateWeek />;
  }
  // ... main render
}
```

**Header/section/grid pattern** (Today.tsx lines 183-241 — preserve `max-w-3xl mx-auto`, `gap-[var(--spacing-5)]`, sectioned articles).

---

### `frontend/src/pages/Shopping.tsx` (`/spesa` route)

**Analog:** `frontend/src/pages/Today.tsx` for shell + `History.tsx` for list-view structure.

**ShoppingViewToggle integration** (UI-SPEC §6.3 layout map). Page shell same as Today.tsx; body alternates between category-sections vs day-sections based on `viewMode` state.

---

### `frontend/src/db/dexie.ts` (v1 → v2)

**Analog:** self (lines 36-47)

**Versioning pattern** (dexie.ts lines 36-47 — append `version(2)`, do NOT modify v1):
```typescript
constructor() {
  super('wellness-buddy');
  this.version(1).stores({
    cache_users: 'id, email',
    cache_plans: 'id, user_id, is_active',
    cache_today: 'date, user_id',
    cache_workout_log: 'id, [user_id+date]',
    cache_weight_log: 'id, [user_id+date]',
    mutation_queue: 'id, created_at',
    drafts: 'key, updated_at',
  });
  // Phase 2 (FND-07 + PITFALLS#5: schema bumps DROP + re-fetch, no in-place migration)
  this.version(2).stores({
    cache_weekly: '[user_id+week_start], user_id',
    cache_shopping: '[user_id+week_start], user_id',
  });
}
```

**Type addition pattern** (`schema.ts` — append matching the `CachedToday` shape, lines 29-34):
```typescript
export interface CachedWeekly {
  user_id: string;
  week_start: string;
  payload: unknown;  // PITFALLS#5 — opaque mirror; bumps DROP + re-fetch
  fetched_at: string;
}

export interface CachedShopping {
  user_id: string;
  week_start: string;
  payload: unknown;
  fetched_at: string;
}
```

---

### `frontend/src/i18n/copy.it.ts` (extend namespaces)

**Analog:** self (lines 13-92 — existing `today.*`, `auth.*`, `invite.*` namespace structure)

**Namespace extension pattern** — append after existing namespaces, BEFORE the trailing `} as const;`:
```typescript
  // ───── /week (Phase 2 — vista settimanale + variant selector) ─────
  week: {
    heading: 'La settimana',
    // ... full block from UI-SPEC §7.1 lines 548-583 (verbatim)
  },

  // ───── /spesa ─────
  shopping: { /* UI-SPEC §7.1 lines 585-629 verbatim */ },

  // ───── Family sync ─────
  family: { /* UI-SPEC §7.1 lines 631+ verbatim */ },

  // ───── Sync conflict toast ─────
  sync: {
    conflictToast: "Aggiornato da {nome}. Ricarica per vedere l'ultima versione.",
    conflictReloadCta: 'Ricarica',
  },

  // ───── PWA install follow-up (post Plan 02-03 deploy) ─────
  pwa: {
    installFollowUp: '...',  // verbatim from UI-SPEC
  },
```

---

## Shared Patterns (cross-cutting — apply to multiple Phase 2 files)

### Authentication / Authorization
**Source:** `backend/app/core/deps.py::get_current_user` (lines 30-55) + new `get_user_with_group_access`
**Apply to:** ALL Phase 2 backend route handlers (weekly.py, shopping.py, family.py, today.py extensions)
```python
@router.get("/...")
async def handler(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Response: ...
```
For cross-user reads, swap to: `user: User = Depends(get_user_with_group_access)` (taking `target_user_id` query/path param).

### Error envelope `{detail, code}`
**Source:** `backend/app/core/exceptions.py::AppException` (lines 17-25)
**Apply to:** ALL Phase 2 backend service modules
```python
from app.core.exceptions import AppException

raise AppException(404, "Risorsa non trovata.", "not_found")
raise AppException(409, "Aggiornato da {nome}. ...", "version_conflict")
raise AppException(400, "Nessun piano attivo.", "no_active_plan")
```
Frontend `apiClient` decodes `error.code` and maps via `copy.errors.*` / `copy.sync.*`.

### Cross-user read returns 404 (not 403) — V13 mitigation
**Source:** `backend/app/services/weight_service.py::update_weight` (lines 89-110), `plan_service.activate_plan` (lines 119-127)
**Apply to:** ALL Phase 2 cross-user-eligible queries (variants, shopping list, family share)
```python
row = (await session.scalars(
    select(Model).where(Model.id == row_id, Model.user_id == user_id)
)).first()
if not row:
    raise AppException(404, _MSG_NOT_FOUND, "not_found")  # NEVER 403
```

### Italian copy single source (FND-09)
**Source:** `frontend/src/i18n/copy.it.ts` (full file)
**Apply to:** ALL Phase 2 frontend components
- Never inline italian strings in components — always `copy.<namespace>.<key>`
- Tokens substituted via `.replace('{name}', value)` (existing pattern, today.ts uses this)
- New namespaces: `week.*`, `shopping.*`, `family.*`, `sync.*`, `pwa.*`

### Tailwind 4 `@theme` tokens — zero hex
**Source:** `frontend/src/components/today/MealCard.tsx` (lines 53-138 — every color via `var(--color-*)`)
**Apply to:** ALL Phase 2 frontend components — CI ESLint hex-ban inherited
```tsx
className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-[var(--radius-md)]"
style={{ background: 'var(--color-leaf-500)' }}
```

### Phosphor facade — single import surface
**Source:** `frontend/src/components/icons/index.ts`
**Apply to:** ALL Phase 2 frontend components
```typescript
import { UsersThree, Snowflake, Carrot, DotsThreeOutline /* etc. */ } from '@/components/icons';
// NEVER: import { ... } from '@phosphor-icons/react'  ← CI grep gate fails
```

### Offline-first contract (PITFALLS#5)
**Source:** `frontend/src/services/today.ts` lines 60-72 + `frontend/src/lib/mutationQueue.ts`
**Apply to:** Phase 2 weekly.ts + shopping.ts (NOT family.ts share toggle — see D-17 conflict UX)
- Mirror server response to `db.cache_*` inside `queryFn` after success
- For mutations: try network, on `navigator.onLine === false` → `enqueueMutation({ endpoint, method, body })`
- mutation_queue stores OPAQUE HTTP — never domain shapes
- Dexie schema bumps DROP + re-fetch (NEVER in-place migrate cache_*)

### TanStack Query 30s + refetchOnFocus (D-16 real-time strategy)
**Source:** `frontend/src/services/today.ts` line 76 (`staleTime: 30_000`)
**Apply to:** weekly.ts, shopping.ts, family.ts queries
```typescript
return useQuery({
  queryKey: ['weekly', userId, weekStart],
  queryFn: async () => { /* ... */ },
  staleTime: 30_000,
  refetchOnWindowFocus: true,   // D-16: NO WebSocket Phase 2 — polling on focus only
});
```

### Test fixtures (integration)
**Source:** `backend/tests/integration/test_weight.py` lines 32-68
**Apply to:** ALL Phase 2 integration tests
```python
pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="session")]

@pytest_asyncio.fixture
async def test_user(db_session): ...
@pytest_asyncio.fixture
async def other_user(db_session): ...
async def _login(client, email, password) -> str: ...
```

### Visual regression baselines (D-31)
**Source:** `frontend/tests/visual/light.spec.ts` lines 13-27
**Apply to:** Phase 2 — extend `ROUTES` array with `/settimana`, `/spesa`. First Plan 02-02 action: `pnpm test:visual --update-snapshots` to absorb post-Plan-09 Lifesum Pure baseline drift.

### Phase doc / sign-off matrix
**Source:** `.planning/phases/01-foundation/01-08-tone-calibration-checklist.md` (sign-off table shape)
**Apply to:** `02-01-GTK3-SPIKE.md`, `02-03-DEPLOY-CHECKLIST.md`
```markdown
| Reviewer | Initial | Date | Time | Verdict (PASS/CONCERNS/BLOCK) | Notes |
|----------|---------|------|------|-------------------------------|-------|
| Stefano  |         |      |      |                               |       |
| Marta    |         |      |      |                               |       |
```

---

## No Analog Found

Files with no close existing match — planner should use RESEARCH.md / UI-SPEC.md as canonical references:

| File | Role | Data Flow | Reason | Canonical Reference |
|------|------|-----------|--------|---------------------|
| `backend/app/templates/shopping_list.html` | Jinja2 PDF template | transform | First Jinja2 template in repo; first PDF rendering surface | UI-SPEC §6.4 (lines 262-411) |
| `backend/app/core/scheduler.py` | APScheduler bootstrap | event-driven (cron) | First scheduler in repo (Phase 3 push reuses) | RESEARCH.md Pattern 5 (lines 937-1000) |
| `backend/app/services/group_service.py` (group meta + cross-user authz helpers) | service | CRUD | New domain (group not yet activated as logic, only schema) | RESEARCH.md Pattern 7 (FAM-08 matrix) |
| `frontend/src/lib/broadcastChannel.ts` | utility | event-driven (multi-tab) | New cross-tab sync; iOS Safari fallback | RESEARCH.md Pattern 10 (lines 1342-1400) |
| `frontend/src/components/family/ShareToggleMenu.tsx` | component | event-driven (DropdownMenu+Switch) | First Radix Switch + DropdownMenu combo in app | UI-SPEC §6.2 (line 206) |
| `frontend/src/components/shopping/ShoppingViewToggle.tsx` | component | event-driven (ToggleGroup) | First Radix ToggleGroup in app | UI-SPEC §6.2 (line 209) |

For these, plans should embed RESEARCH.md / UI-SPEC.md excerpts directly rather than reference an existing analog file.

---

## Metadata

**Analog search scope:**
- `backend/app/services/`, `backend/app/api/`, `backend/app/schemas/`, `backend/app/parsers/`, `backend/app/core/`, `backend/app/models/`, `backend/alembic/versions/`
- `backend/tests/integration/`, `backend/tests/unit/`
- `frontend/src/services/`, `frontend/src/components/today/`, `frontend/src/pages/`, `frontend/src/db/`, `frontend/src/i18n/`, `frontend/src/lib/`
- `frontend/tests/visual/`, `frontend/tests/e2e/`

**Files scanned (read in full):**
- `backend/app/services/today_service.py` (282 lines), `plan_service.py` (264 lines), `weight_service.py` (126 lines), `audit_service.py` (36 lines)
- `backend/app/api/today.py`, `plans.py`, `weight.py`, `weekly.py` (stub), `shopping.py` (stub), `main.py`
- `backend/app/schemas/today.py`, `plan.py`, `plan_parsed.py`
- `backend/app/parsers/plan_parser.py` (130 lines), `plan_sections.py` (228 lines), `normalizer.py` (54 lines)
- `backend/app/core/deps.py`, `exceptions.py`
- `backend/app/models/variant.py`, `shopping.py`, `user.py`, `group.py`
- `backend/alembic/versions/0000_baseline.py` (185 lines)
- `backend/tests/integration/test_weight.py` (330 lines), `test_plans_api.py` (530 lines), `test_today_api.py` (head 80 lines), `conftest.py` (head 80 lines)
- `backend/tests/unit/test_parser_evil.py` (head 120 lines)
- `frontend/src/services/today.ts`, `weight.ts`
- `frontend/src/components/today/MealCard.tsx`, `MacroRing.tsx`, `MealCard.test.tsx` (head 60 lines)
- `frontend/src/pages/Today.tsx` (243 lines)
- `frontend/src/db/dexie.ts`, `schema.ts`
- `frontend/src/lib/mutationQueue.ts` (head 80 lines)
- `frontend/src/i18n/copy.it.ts` (head 100 lines)
- `frontend/tests/visual/light.spec.ts`
- `.planning/phases/02-differentiators/02-CONTEXT.md` (full), `02-RESEARCH.md` (sections via index + Patterns 1-6 in detail), `02-UI-SPEC.md` (§6 component anatomy + §7.1 copy keys)

**Pattern extraction date:** 2026-05-02
**Mapper:** gsd pattern mapper (Phase 2 differentiators)
