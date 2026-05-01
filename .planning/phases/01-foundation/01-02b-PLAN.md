---
phase: 01-foundation
plan: 02b
type: execute
wave: 2
depends_on: [01]
files_modified:
  - backend/app/ai/__init__.py
  - backend/app/ai/base.py
  - backend/app/ai/null_provider.py
  - backend/app/ai/factory.py
  - backend/app/parsers/__init__.py
  - backend/app/schemas/auth.py
  - backend/app/schemas/today.py
  - backend/app/schemas/workout.py
  - backend/app/schemas/weight.py
  - backend/app/schemas/invite.py
  - backend/app/schemas/ai.py
  - backend/app/api/auth.py
  - backend/app/api/plans.py
  - backend/app/api/today.py
  - backend/app/api/weekly.py
  - backend/app/api/workout.py
  - backend/app/api/weight.py
  - backend/app/api/shopping.py
  - backend/app/api/ai.py
  - backend/app/api/admin.py
  - backend/app/main.py
  - backend/tests/integration/test_ai_api.py
  - backend/tests/integration/test_stub_endpoints.py
  - backend/tests/unit/test_ai_provider.py
autonomous: true
requirements: [AI-01, AI-02, AI-03, AI-04, AI-07]
must_haves:
  truths:
    - "AIProvider ABC declares generate_meal_suggestion + analyze_week_progress + generate_shopping_tips + chat + is_available"
    - "NullProvider raises HTTPException(501) with body {detail: 'AI non disponibile', code: 'ai_unavailable'} (Italian)"
    - "build_provider() reads settings.AI_PROVIDER, returns NullProvider for 'null', raises ValueError for unknown values"
    - "Lifespan extension binds NullProvider to app.state.ai_provider at boot (AI-03, D-32)"
    - "All stub routers (auth/plans/today/weekly/workout/weight/shopping/admin) return 501 with envelope {detail, code} per AUTH-12"
    - "AI endpoints (/api/ai/meal-suggestion, /week-analysis, /shopping-tips, /chat) wire through Depends(get_ai_provider) and bubble 501 from NullProvider"
    - "Test-only /api/ai/_provider_probe (no auth) returns {provider: 'NullProvider', is_available: false}"
  artifacts:
    - path: "backend/app/ai/base.py"
      provides: "AIProvider ABC contract"
      contains: "class AIProvider(ABC)"
    - path: "backend/app/ai/null_provider.py"
      provides: "NullProvider raises HTTPException 501 Italian"
      contains: "AI non disponibile"
    - path: "backend/app/ai/factory.py"
      provides: "build_provider() reads AI_PROVIDER env, returns NullProvider for 'null'"
      contains: "build_provider"
    - path: "backend/app/api/ai.py"
      provides: "AI endpoints + provider probe (test-only)"
      contains: "_provider_probe"
  key_links:
    - from: "backend/app/main.py"
      to: "backend/app/ai/factory.py"
      via: "lifespan startup binds app.state.ai_provider"
      pattern: "build_provider"
    - from: "backend/app/api/ai.py"
      to: "backend/app/core/deps.py::get_ai_provider"
      via: "Depends injection"
      pattern: 'Depends\(get_ai_provider\)'
---

<objective>
Build the AI layer (split 2 of 2) on top of Plan 02a's backbone: AIProvider ABC + NullProvider + factory (D-31, D-32, AI-01..AI-07), DI lifespan extension that binds NullProvider to `app.state.ai_provider` at boot, stub routers (auth/plans/today/weekly/workout/weight/shopping/admin) returning 501 with AUTH-12 envelope so app boots cleanly with all expected paths registered, real AI endpoints (`/api/ai/meal-suggestion`, `/week-analysis`, `/shopping-tips`, `/chat`) wired through `Depends(get_ai_provider)`, test-only `/api/ai/_provider_probe` confirming the active provider class, schemas/ai.py + auth.py/today.py/workout.py/weight.py/invite.py request/response shapes (Plans 03/04/07 fill real implementations).

Purpose: Plan 02a delivered the FastAPI backbone + models + Alembic. This plan completes the Wave 2 backend foundation by wiring the AI factory + stubs so downstream plans see a fully-import-able `app.main:app`.

**Co-modified file with Plan 02a:** `backend/app/main.py`. Plan 02a created the file with a lifespan stub. This plan extends it (a) adds `_app.state.ai_provider = build_provider()` inside the lifespan and (b) includes all stub routers (auth, plans, today, weekly, workout, weight, shopping, ai, admin). Locked ordering: 02a lands first within Wave 2; 02b extends.

Output: `cd backend && uv run uvicorn app.main:app` boots with NullProvider bound, `GET /api/ai/_provider_probe` returns `{provider: "NullProvider", is_available: false}`, all stub endpoints return 501 with `{detail, code}` envelope, all 02b tests green.
</objective>

<execution_context>
@C:/Users/bakko/.claude/plugins/cache/gsd-plugin/gsd/2.38.8/workflows/execute-plan.md
@C:/Users/bakko/.claude/plugins/cache/gsd-plugin/gsd/2.38.8/templates/summary.md
</execution_context>

<context>
@d:/Develop/AI/WellnessBuddy/.planning/phases/01-foundation/01-CONTEXT.md
@d:/Develop/AI/WellnessBuddy/.planning/phases/01-foundation/01-RESEARCH.md
@d:/Develop/AI/WellnessBuddy/.planning/phases/01-foundation/01-VALIDATION.md
@d:/Develop/AI/WellnessBuddy/.planning/REQUIREMENTS.md
@d:/Develop/AI/WellnessBuddy/.planning/phases/01-foundation/01-02a-PLAN.md
</context>

<interfaces>
<!-- Plan 02b consumes Plan 02a's core (config, deps, exceptions, models) and extends main.py. -->
<!-- Plans 03/04/07 will replace stub routers with real implementations. -->

From `app/ai/base.py` (this plan creates):
```python
class AIProvider(ABC):
    @abstractmethod async def generate_meal_suggestion(self, **kwargs) -> str: ...
    @abstractmethod async def analyze_week_progress(self, **kwargs) -> str: ...
    @abstractmethod async def generate_shopping_tips(self, **kwargs) -> str: ...
    @abstractmethod async def chat(self, **kwargs) -> str: ...
    @property @abstractmethod def is_available(self) -> bool: ...
```

From `app/ai/factory.py`:
```python
def build_provider() -> AIProvider: ...  # reads settings.AI_PROVIDER, returns NullProvider for 'null'
```

Stub routers signature (each router file):
```python
router = APIRouter(prefix="/api/{name}", tags=["{name}"])
@router.post("/{path}") async def {name}() -> dict:
    raise HTTPException(501, {"detail": "Plan {N} implementa", "code": "not_implemented"})
```
</interfaces>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: AI ABC + NullProvider + factory + schemas + lifespan extension in main.py + stub routers + AI endpoints</name>
  <files>backend/app/ai/__init__.py, backend/app/ai/base.py, backend/app/ai/null_provider.py, backend/app/ai/factory.py, backend/app/parsers/__init__.py, backend/app/schemas/auth.py, backend/app/schemas/today.py, backend/app/schemas/workout.py, backend/app/schemas/weight.py, backend/app/schemas/invite.py, backend/app/schemas/ai.py, backend/app/api/auth.py, backend/app/api/plans.py, backend/app/api/today.py, backend/app/api/weekly.py, backend/app/api/workout.py, backend/app/api/weight.py, backend/app/api/shopping.py, backend/app/api/ai.py, backend/app/api/admin.py, backend/app/main.py</files>
  <read_first>
    - .planning/phases/01-foundation/01-RESEARCH.md (Pattern 11 AI Provider DI, Pattern 12 Italian copy contract)
    - .planning/phases/01-foundation/01-CONTEXT.md (D-31, D-32, D-33, AI-01..AI-07)
    - .planning/phases/01-foundation/01-VALIDATION.md (T-AI-01, T-API-01, AUTH-12 envelope)
    - .planning/phases/01-foundation/01-02a-PLAN.md (main.py lifespan stub to extend)
    - backend/app/core/deps.py (get_ai_provider already declared by Plan 02a)
  </read_first>
  <action>
    1. **`backend/app/ai/__init__.py`** — empty
    2. **`backend/app/ai/base.py`** — verbatim from RESEARCH Pattern 11:
       ```python
       """AIProvider ABC. Source: AI-01, RESEARCH Pattern 11."""
       from __future__ import annotations
       from abc import ABC, abstractmethod

       class AIProvider(ABC):
           @abstractmethod
           async def generate_meal_suggestion(self, **kwargs) -> str: ...
           @abstractmethod
           async def analyze_week_progress(self, **kwargs) -> str: ...
           @abstractmethod
           async def generate_shopping_tips(self, **kwargs) -> str: ...
           @abstractmethod
           async def chat(self, **kwargs) -> str: ...
           @property
           @abstractmethod
           def is_available(self) -> bool: ...
       ```

    3. **`backend/app/ai/null_provider.py`** — verbatim from RESEARCH Pattern 11:
       ```python
       """NullProvider — raises HTTPException 501 Italian. Source: AI-04, AI-07, RESEARCH Pattern 11."""
       from __future__ import annotations
       from fastapi import HTTPException
       from app.ai.base import AIProvider

       _DETAIL = {"detail": "AI non disponibile", "code": "ai_unavailable"}

       class NullProvider(AIProvider):
           async def generate_meal_suggestion(self, **kwargs) -> str:
               raise HTTPException(status_code=501, detail=_DETAIL)
           async def analyze_week_progress(self, **kwargs) -> str:
               raise HTTPException(status_code=501, detail=_DETAIL)
           async def generate_shopping_tips(self, **kwargs) -> str:
               raise HTTPException(status_code=501, detail=_DETAIL)
           async def chat(self, **kwargs) -> str:
               raise HTTPException(status_code=501, detail=_DETAIL)
           @property
           def is_available(self) -> bool:
               return False
       ```

    4. **`backend/app/ai/factory.py`** — verbatim from RESEARCH Pattern 11:
       ```python
       """build_provider() reads settings.AI_PROVIDER. Source: D-31, D-32."""
       from __future__ import annotations
       from app.ai.base import AIProvider
       from app.ai.null_provider import NullProvider
       from app.core.config import settings

       def build_provider() -> AIProvider:
           kind = settings.AI_PROVIDER
           if kind == "null":
               return NullProvider()
           # Phase 5 adds: ollama / openai / anthropic
           raise ValueError(f"Unknown AI_PROVIDER={kind!r}; only 'null' supported in Phase 1")
       ```

    5. **`backend/app/parsers/__init__.py`** — empty (Plan 04 fills).

    6. **Schema files** (Plans 03/04/07 own real impls; we ship request/response types so routers can be typed cleanly):
       - **`backend/app/schemas/auth.py`** — LoginRequest / TokenResponse / MeResponse (Plan 03 owns full impl).
       - **`backend/app/schemas/today.py`** — TodayResponse minimal placeholder.
       - **`backend/app/schemas/workout.py`** — WorkoutLogIn / WorkoutLogOut.
       - **`backend/app/schemas/weight.py`** — WeightLogIn / WeightLogOut.
       - **`backend/app/schemas/invite.py`** — InviteCreateRequest / InviteResponse.
       - **`backend/app/schemas/ai.py`** — AIRequest / AIResponse.

       Use Pydantic v2 `BaseModel` (these are minimal so they don't need strict `extra='forbid'` — Plans 03/04/07 use `StrictModel` from `app/schemas/common.py`). Sample:
       ```python
       # backend/app/schemas/auth.py
       from pydantic import BaseModel, EmailStr

       class LoginRequest(BaseModel):
           email: EmailStr
           password: str

       class TokenResponse(BaseModel):
           access_token: str
           token_type: str = "bearer"

       class MeResponse(BaseModel):
           id: str
           email: EmailStr
           username: str
           role: str
           group_id: str | None = None
           timezone: str
       ```

    7. **Stub routers** — files exist with `router = APIRouter(...)` + endpoints raising 501:
       Each non-AI router follows this template:
       ```python
       """{Name} router - stub Plan 02b; full implementation Plan {NN}."""
       from fastapi import APIRouter, HTTPException

       router = APIRouter(prefix="/api/{name}", tags=["{name}"])

       @router.{method}("/{path}")
       async def {handler}() -> dict:
           raise HTTPException(501, {"detail": "Plan {NN} implementa", "code": "not_implemented"})
       ```

       Specifically:
       - **`auth.py`** — prefix `/api/auth`, endpoints: POST /login, POST /logout, POST /refresh, GET /me, POST /invite, POST /register (Plan 03 implements)
       - **`plans.py`** — prefix `/api/plans`, endpoints: POST /upload, GET "", POST /{plan_id}/activate, GET /{plan_id}/diff (Plan 04 implements)
       - **`today.py`** — prefix `/api/today`, endpoints: GET "", POST /meal/{meal_type}/complete (Plan 07 implements)
       - **`weekly.py`** — prefix `/api/weekly`, endpoint: GET /{week_start} (deferred Phase 2)
       - **`workout.py`** — prefix `/api/workout`, endpoints: POST "", GET "", PATCH /{id}, DELETE /{id} (Plan 07 implements)
       - **`weight.py`** — prefix `/api/weight`, endpoints: POST "", GET "", PATCH /{id}, DELETE /{id} (Plan 07 implements)
       - **`shopping.py`** — prefix `/api/shopping`, endpoint: GET /{week_start} (deferred Phase 2)
       - **`admin.py`** — prefix `/api/admin`, endpoint: POST /users/{user_id}/assign-plan (Plan 04 implements)

    8. **`backend/app/api/ai.py`** — verbatim from RESEARCH Pattern 11 + test-only `/api/ai/_provider_probe` route that does NOT require auth (so test_ai_api can verify NullProvider is wired in):
       ```python
       """AI router - endpoints exist Phase 1, return 501 via NullProvider (AI-04, AI-07)."""
       from fastapi import APIRouter, Depends, Request
       from app.ai.base import AIProvider
       from app.core.deps import get_ai_provider, get_current_user

       router = APIRouter(prefix="/api/ai", tags=["ai"])

       # Test-only probe (no auth) - confirms NullProvider wired via lifespan.
       # Will be removed in Phase 5 once auth gates AI endpoints normally.
       @router.get("/_provider_probe", include_in_schema=False)
       async def _provider_probe(request: Request) -> dict:
           ai: AIProvider = get_ai_provider(request)
           return {"provider": type(ai).__name__, "is_available": ai.is_available}

       @router.post("/meal-suggestion")
       async def meal_suggestion(
           user=Depends(get_current_user),
           ai: AIProvider = Depends(get_ai_provider),
       ) -> dict:
           return {"suggestion": await ai.generate_meal_suggestion()}

       @router.post("/week-analysis")
       async def week_analysis(
           user=Depends(get_current_user),
           ai: AIProvider = Depends(get_ai_provider),
       ) -> dict:
           return {"analysis": await ai.analyze_week_progress()}

       @router.post("/shopping-tips")
       async def shopping_tips(
           user=Depends(get_current_user),
           ai: AIProvider = Depends(get_ai_provider),
       ) -> dict:
           return {"tips": await ai.generate_shopping_tips()}

       @router.post("/chat")
       async def chat(
           user=Depends(get_current_user),
           ai: AIProvider = Depends(get_ai_provider),
       ) -> dict:
           return {"response": await ai.chat()}
       ```

    9. **Extend `backend/app/main.py`** (the file Plan 02a created):
       - Replace lifespan body so it BINDS the AI provider:
         ```python
         @asynccontextmanager
         async def lifespan(app: FastAPI) -> AsyncIterator[None]:
             configure_logging()
             app.state.ai_provider = build_provider()
             yield
         ```
       - Add new imports: `from app.ai.factory import build_provider` and `from app.api import auth, plans, today, weekly, workout, weight, shopping, ai, admin`
       - Add the new routers to the include loop:
         ```python
         for r in (
             health.router, version.router, errors.router,
             auth.router, plans.router, today.router, weekly.router,
             workout.router, weight.router, shopping.router, ai.router, admin.router,
         ):
             app.include_router(r)
         ```

       Final main.py shape after this plan's edits is identical to the version that lived in the original (pre-split) Plan 02 Task 1.
  </action>
  <verify>
    <automated>cd backend &amp;&amp; uv run python -c "from app.main import app; print('routes:', len(app.routes))" &amp;&amp; uv run ruff check app/ai app/api/ai.py app/main.py</automated>
  </verify>
  <acceptance_criteria>
    - File exists: `backend/app/ai/base.py` containing literal `class AIProvider(ABC)`
    - File exists: `backend/app/ai/null_provider.py` containing literal `"AI non disponibile"` AND `"ai_unavailable"`
    - File exists: `backend/app/ai/factory.py` containing literal `def build_provider`
    - File exists: `backend/app/api/ai.py` containing literal `Depends(get_ai_provider)` AND `_provider_probe`
    - All 9 stub router files exist: `auth.py plans.py today.py weekly.py workout.py weight.py shopping.py admin.py` (errors.py from 02a)
    - Each non-AI router contains literal `APIRouter(prefix="/api/`
    - All schema files exist: `auth.py today.py workout.py weight.py invite.py ai.py`
    - File `backend/app/main.py` (modified by both 02a and 02b — 02b adds these literals): `app.state.ai_provider = build_provider()` AND `from app.ai.factory import build_provider` AND includes for `auth.router`, `plans.router`, `today.router`, `weekly.router`, `workout.router`, `weight.router`, `shopping.router`, `ai.router`, `admin.router`
    - Command `cd backend && uv run python -c "from app.main import app"` exits 0 (full app import)
  </acceptance_criteria>
  <done>AI ABC + NullProvider + factory wired via lifespan to `app.state.ai_provider`. AI endpoints exist returning 501 envelope per AUTH-12. All 9 stub routers ship so app boots cleanly with full route table. Plans 03/04/07 will replace stubs with real implementations.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: Integration + unit tests for AI provider + stub endpoints (test_ai_api + test_stub_endpoints + test_ai_provider)</name>
  <files>backend/tests/integration/test_ai_api.py, backend/tests/integration/test_stub_endpoints.py, backend/tests/unit/test_ai_provider.py</files>
  <read_first>
    - .planning/phases/01-foundation/01-RESEARCH.md (Pattern 11 AI Provider DI)
    - .planning/phases/01-foundation/01-CONTEXT.md (AI-01..AI-07)
    - .planning/phases/01-foundation/01-VALIDATION.md (T-AI-01, AUTH-12 envelope)
    - backend/app/api/ai.py (Task 1 — provider_probe + endpoints)
    - backend/tests/conftest.py (Plan 02a — async_client + test_engine fixtures)
  </read_first>
  <action>
    1. **`backend/tests/integration/test_ai_api.py`** (T-AI-01 + AI-04 + AUTH-12 envelope):
       ```python
       from fastapi.testclient import TestClient
       from app.main import app

       def test_provider_probe_returns_null_provider() -> None:
           with TestClient(app) as client:
               r = client.get("/api/ai/_provider_probe")
               assert r.status_code == 200
               body = r.json()
               assert body["provider"] == "NullProvider"
               assert body["is_available"] is False

       def test_meal_suggestion_returns_envelope() -> None:
           """Endpoint exists; without auth Plan 02 stub get_current_user returns 501.
           After Plan 03, this 501 will move from auth_not_implemented to ai_unavailable.
           Either way, error envelope shape MUST match AUTH-12 contract."""
           with TestClient(app) as client:
               r = client.post("/api/ai/meal-suggestion")
               assert r.status_code == 501
               body = r.json()
               assert "detail" in body and "code" in body

       def test_week_analysis_returns_envelope() -> None:
           with TestClient(app) as client:
               r = client.post("/api/ai/week-analysis")
               assert r.status_code == 501
               body = r.json()
               assert "detail" in body and "code" in body

       def test_shopping_tips_returns_envelope() -> None:
           with TestClient(app) as client:
               r = client.post("/api/ai/shopping-tips")
               assert r.status_code == 501
               body = r.json()
               assert "detail" in body and "code" in body

       def test_chat_returns_envelope() -> None:
           with TestClient(app) as client:
               r = client.post("/api/ai/chat")
               assert r.status_code == 501
               body = r.json()
               assert "detail" in body and "code" in body
       ```

    2. **`backend/tests/integration/test_stub_endpoints.py`** — verify each stub router returns 501 + envelope (not full coverage of all stubs, but representative samples to lock the AUTH-12 contract while Plans 03/04/07 are still pending):
       ```python
       from fastapi.testclient import TestClient
       from app.main import app

       client = TestClient(app)

       def test_auth_login_stub_returns_envelope() -> None:
           r = client.post("/api/auth/login")
           assert r.status_code == 501
           assert "detail" in r.json() and "code" in r.json()

       def test_plans_upload_stub_returns_envelope() -> None:
           r = client.post("/api/plans/upload")
           assert r.status_code == 501
           assert "detail" in r.json() and "code" in r.json()

       def test_today_get_stub_returns_envelope() -> None:
           r = client.get("/api/today")
           assert r.status_code == 501
           assert "detail" in r.json() and "code" in r.json()

       def test_weight_post_stub_returns_envelope() -> None:
           r = client.post("/api/weight")
           assert r.status_code == 501
           assert "detail" in r.json() and "code" in r.json()

       def test_workout_post_stub_returns_envelope() -> None:
           r = client.post("/api/workout")
           assert r.status_code == 501
           assert "detail" in r.json() and "code" in r.json()

       def test_admin_assign_stub_returns_envelope() -> None:
           r = client.post("/api/admin/users/00000000-0000-0000-0000-000000000000/assign-plan")
           assert r.status_code == 501
           assert "detail" in r.json() and "code" in r.json()
       ```

    3. **`backend/tests/unit/test_ai_provider.py`** (verbatim from original Plan 02 Task 3):
       ```python
       import pytest
       from fastapi import HTTPException
       from app.ai.null_provider import NullProvider
       from app.ai.factory import build_provider
       from app.ai.base import AIProvider

       def test_null_provider_is_aiprovider() -> None:
           assert issubclass(NullProvider, AIProvider)

       def test_null_provider_not_available() -> None:
           assert NullProvider().is_available is False

       @pytest.mark.asyncio
       async def test_null_provider_meal_suggestion_raises_501_italian() -> None:
           with pytest.raises(HTTPException) as exc:
               await NullProvider().generate_meal_suggestion()
           assert exc.value.status_code == 501
           assert exc.value.detail == {"detail": "AI non disponibile", "code": "ai_unavailable"}

       def test_factory_returns_null_provider_when_env_null(monkeypatch) -> None:
           monkeypatch.setenv("AI_PROVIDER", "null")
           from importlib import reload
           from app.core import config as cfg
           reload(cfg)
           from app.ai import factory as fac
           reload(fac)
           assert type(fac.build_provider()).__name__ == "NullProvider"

       def test_factory_raises_for_unknown_provider(monkeypatch) -> None:
           # Direct test bypassing settings reload (settings is loaded at import)
           from app.ai import factory as fac
           monkeypatch.setattr(fac.settings, "AI_PROVIDER", "weird-unknown")
           with pytest.raises(ValueError, match="Unknown AI_PROVIDER"):
               fac.build_provider()
       ```
  </action>
  <verify>
    <automated>cd backend &amp;&amp; uv run pytest tests/unit/test_ai_provider.py tests/integration/test_ai_api.py tests/integration/test_stub_endpoints.py -x -q</automated>
  </verify>
  <acceptance_criteria>
    - File exists: `backend/tests/integration/test_ai_api.py` containing literal `test_provider_probe_returns_null_provider`
    - File exists: `backend/tests/integration/test_stub_endpoints.py` containing literal `test_auth_login_stub_returns_envelope`
    - File exists: `backend/tests/unit/test_ai_provider.py` containing literal `test_null_provider_is_aiprovider` AND `test_factory_raises_for_unknown_provider`
    - Command `cd backend && uv run pytest tests/unit/test_ai_provider.py -x` exits 0
    - Command `cd backend && uv run pytest tests/integration/test_ai_api.py -x` exits 0
    - Command `cd backend && uv run pytest tests/integration/test_stub_endpoints.py -x` exits 0
  </acceptance_criteria>
  <done>AI provider tests confirm NullProvider class + Italian 501 envelope. Stub endpoint tests verify AUTH-12 envelope contract is upheld across all router stubs (representative sample). Plans 03/04/07 will replace stubs and re-target these tests at real behavior.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Lifespan startup -> app.state | AI provider singleton; `build_provider` rejects unknown values at boot |
| Client -> /api/ai/* | Untrusted JSON (Pydantic v2 validates); auth gate (Plan 03 owns) |

## STRIDE Threat Register (Plan 02b scope)

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-AI-01 | Information disclosure / Tampering | AI placeholder leakage of sensitive context | mitigate | NullProvider raises HTTPException(501) with hardcoded Italian Phase 1 — zero context interpolation, zero data emission. AI factory rejects unknown `AI_PROVIDER` values at boot (Phase 5 adds concrete providers). `_provider_probe` route confirms NullProvider is the active class in CI |

</threat_model>

<verification>
End-of-plan checks:

```bash
cd backend
uv run python -c "from app.main import app; print(f'Routes registered: {len(app.routes)}')"

# Run tests
uv run pytest tests/unit/test_ai_provider.py tests/integration/test_ai_api.py tests/integration/test_stub_endpoints.py -x -q

# Boot uvicorn briefly and probe
uv run uvicorn app.main:app --host 127.0.0.1 --port 8001 &
SERVER_PID=$!
sleep 2
curl -s http://127.0.0.1:8001/api/ai/_provider_probe | grep -q "NullProvider"
kill $SERVER_PID
```
</verification>

<success_criteria>
- All Task 1 + Task 2 acceptance criteria met
- `cd backend && uv run uvicorn app.main:app --port 8001` boots in <2s without errors
- `GET /api/ai/_provider_probe` returns 200 `{provider: "NullProvider", is_available: false}`
- `POST /api/ai/meal-suggestion` returns 501 with envelope `{detail, code}`
- All stub routers return 501 with envelope shape
- All Plan 02b tests green
</success_criteria>

<output>
After completion, create `.planning/phases/01-foundation/01-02b-SUMMARY.md` capturing:
- Final list of routes registered (`app.routes` count + grouping by tag)
- Confirmation that AI lifespan binding works (`provider_probe` response)
- Stub endpoint envelope coverage (which paths, which status codes)
- Any deviations from RESEARCH Pattern 11
</output>
