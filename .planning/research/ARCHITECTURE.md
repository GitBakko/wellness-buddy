# Architecture Research — Wellness Buddy

**Domain:** Self-hosted nutrition tracking PWA, multi-user family sync, offline-first
**Researched:** 2026-05-01
**Confidence:** HIGH (stack decisions are pre-locked in PROJECT.md/PROMPT_CONTRACT; research validates patterns and surfaces concrete integration choices)

---

## 0. Executive Summary

Wellness Buddy is a **3-tier offline-first PWA** with a clear separation:

1. **Frontend** (React 19 + Vite 7 PWA) — runs on user's device, fully functional offline against IndexedDB cache via Dexie.js, syncs through TanStack Query when online.
2. **Backend** (FastAPI + SQLAlchemy 2 async) — single-process Uvicorn worker on Windows Server 2019 behind IIS reverse proxy, owns durable state in PostgreSQL.
3. **AI sidecar** (provider pattern) — pluggable abstract `AIProvider` injected via FastAPI `Depends`, swappable at app-startup via `AI_PROVIDER` env var. Sprint 1 ships `NullProvider`; Sprint 5 adds Ollama/OpenAI/Anthropic without business-logic changes.

**Critical architectural moves:**
- **Server is source of truth, IndexedDB is the offline-tolerant cache.** No CRDT, no peer-to-peer sync. Conflict policy = "last-write-wins per resource" + mutation queue replay on reconnect.
- **Multi-user family sync via `Group` entity, not direct user-to-user FKs.** Shared meals are scoped by `group_id` + visibility flag; Stefano and Marta join the same group and see each other's "shared" meal entries via `GET /api/weekly/{week}?include=group_shared`.
- **AI provider selection happens once at app startup** (factory wired into the DI container), then resolved per-request via `Depends(get_ai_provider)`. No per-request runtime switching.
- **Mutation queue lives in Dexie**, not in TanStack Query's persisted state. This is the only durable place between sessions; TanStack Query's persistence is a perf optimization, not correctness.

---

## 1. System Overview

```
+---------------------------------------------------------------------------+
|                     CLIENT (iPhone/Android/Desktop browser)              |
|                                                                           |
|   +-------------------+    +--------------------+    +---------------+    |
|   |  React 19 UI      |    |   Service Worker   |    |  Push API     |    |
|   |  (Vite 7 + Tailw) |    |   (Workbox-gen'd)  |    |  (VAPID sub)  |    |
|   +---------+---------+    +---------+----------+    +-------+-------+    |
|             |                        |                       |            |
|   +---------+--------+   +-----------+-----------+   +-------+--------+   |
|   |   Zustand        |   | TanStack Query v5     |   | Web Push       |   |
|   |   (UI state,     |   | (server cache,        |   | (sub stored    |   |
|   |    current user, |<->| optimistic mutations, |   |  in backend)   |   |
|   |    theme, draft) |   | retries, refetch)     |   +----------------+   |
|   +------------------+   +-----------+-----------+                        |
|                                      |                                    |
|                          +-----------+----------+                         |
|                          |   Dexie.js v4        |                         |
|                          |   (IndexedDB)        |                         |
|                          |   - cached server    |                         |
|                          |     resources        |                         |
|                          |   - mutation queue   |                         |
|                          |   - drafts           |                         |
|                          +-----------+----------+                         |
+---------------------------------------+-----------------------------------+
                                        |
                                        | HTTPS (JWT bearer)
                                        |
+---------------------------------------+-----------------------------------+
|                       IIS (Windows Server 2019)                          |
|   - Reverse proxy /api/* -> 127.0.0.1:8000                               |
|   - Static serve /* -> frontend/dist/                                    |
|   - SSL termination (Let's Encrypt via win-acme)                         |
+---------------------------------------+-----------------------------------+
                                        |
                                        | localhost:8000 (HTTP)
                                        |
+---------------------------------------+-----------------------------------+
|              FastAPI Application (Uvicorn via NSSM service)              |
|                                                                           |
|   +-------------+  +-------------+  +-------------+  +-------------+      |
|   | api/        |  | services/   |  | parsers/    |  | ai/         |      |
|   | (routes)    |->| (biz logic) |->| (MD->JSON)  |  | (provider   |      |
|   |             |  |             |  |             |  |  abstract)  |      |
|   +------+------+  +------+------+  +-------------+  +------+------+      |
|          |                |                                  |             |
|   +------+------+  +------+------+                    +------+------+      |
|   | core/       |  | models/     |                    | NullProvider|      |
|   | (auth, DI,  |  | (SQLAlch.   |                    | (S1)        |      |
|   |  config)    |  |  ORM)       |                    | Ollama (S5) |      |
|   +-------------+  +------+------+                    +-------------+      |
|                           |                                                 |
+---------------------------+-------------------------------------------------+
                            |
                            | asyncpg (SQLAlchemy 2 async)
                            |
+---------------------------+-------------------------------------------------+
|                  PostgreSQL (already installed on server)                  |
|   Database: WellnessBuddy                                                  |
|   Schemas: public (managed by Alembic)                                     |
+----------------------------------------------------------------------------+
```

---

## 2. Component Responsibilities

### 2.1 Frontend Components

| Component | Responsibility | Implementation |
|-----------|----------------|----------------|
| **React 19 UI** | Render views, capture user input, optimistic state display | Functional components, hooks, Tailwind 3 styling |
| **Service Worker** | Cache static assets, intercept API calls when offline, push handler | Workbox via `vite-plugin-pwa` (generateSW strategy initially, upgrade to injectManifest if needed for fine-grain control) |
| **Zustand** | UI state, current user identity, theme, transient drafts not yet persisted | One store per concern: `authStore`, `uiStore`, `draftStore` |
| **TanStack Query v5** | Server data fetching, caching, optimistic mutations, retry/replay on reconnect | One query key per resource family (`['plans']`, `['weekly', weekStart]`, `['weight']`) |
| **Dexie.js v4** | Durable offline cache, mutation queue, draft storage | Tables: `cache_*` (mirrors of server resources by query key), `mutation_queue`, `drafts` |
| **Push API client** | Subscribe to push, send subscription to backend | `navigator.serviceWorker.pushManager.subscribe({ applicationServerKey: VAPID_PUB })` |

### 2.2 Backend Components

| Component | Responsibility | Implementation |
|-----------|----------------|----------------|
| **api/** routes | HTTP boundary: validate input, call services, format response | FastAPI `APIRouter`, Pydantic v2 request/response schemas |
| **core/** | Cross-cutting: config (Pydantic settings), JWT auth, DI providers, exception handlers | `core/auth.py`, `core/deps.py`, `core/config.py`, `core/security.py` |
| **services/** | Business logic, orchestrate models + parsers + AI; transaction boundaries | One service module per domain: `plans_service.py`, `weekly_service.py`, `shopping_service.py`, `tracking_service.py` |
| **models/** | SQLAlchemy 2 async ORM, table definitions, relationships | `User`, `Group`, `NutritionPlan`, `WeeklyPlanVariant`, `WorkoutLog`, `WeightLog`, `ShoppingListState`, `InviteToken`, `PushSubscription` |
| **parsers/** | Markdown plan tolerant parser, Pydantic v2 schemas for `parsed_json` | `md_parser.py` (regex + python-markdown AST), `schemas/plan_parsed.py` |
| **ai/** | `AIProvider` ABC + concrete implementations | `provider.py` (ABC), `null_provider.py`, `ollama_provider.py` (stub), `factory.py` |

### 2.3 Cross-cutting Components

| Component | Responsibility | Implementation |
|-----------|----------------|----------------|
| **PDF service** | Generate shopping list PDF | Backend-only, ReportLab in `run_in_threadpool` |
| **Push dispatcher** | Send Web Push notifications (Monday weigh-in reminder) | Backend scheduled task (APScheduler in-process) + `pywebpush` |
| **Alembic migrations** | DDL versioning | `alembic/versions/`, run on deploy |

---

## 3. Recommended Project Structure

```
wellness-buddy/                                  # monorepo root
├── package.json                                 # pnpm workspace root
├── pnpm-workspace.yaml                          # workspaces: ['frontend']
├── turbo.json                                   # OPTIONAL — only if dev workflow needs it
├── docker-compose.yml                           # OPTIONAL local dev
├── README.md
├── CLAUDE.md
├── .env.example
├── plans/                                       # MD plans (Stefano, Marta) — source of truth, version-controlled
│   ├── stefano.md
│   └── marta.md
│
├── frontend/                                    # React 19 PWA
│   ├── package.json
│   ├── vite.config.ts                           # vite-plugin-pwa registered here
│   ├── tsconfig.json
│   ├── public/
│   │   ├── icons/                               # 192/512 PWA icons
│   │   └── manifest.webmanifest                 # auto-generated by plugin OR hand-written
│   └── src/
│       ├── main.tsx                             # entry, registers SW via virtual:pwa-register/react
│       ├── App.tsx                              # router shell
│       ├── routes/                              # route components (one per page in section 5)
│       │   ├── today/
│       │   ├── week/
│       │   ├── shopping/
│       │   ├── progress/
│       │   ├── plans/
│       │   ├── settings/
│       │   ├── admin/
│       │   └── ai/
│       ├── features/                            # FEATURE-BASED co-location (see decision below)
│       │   ├── auth/
│       │   │   ├── components/
│       │   │   ├── hooks/use-login.ts
│       │   │   ├── api/auth-api.ts              # raw fetch wrappers
│       │   │   ├── queries/use-me.ts            # TanStack Query hooks
│       │   │   └── store/auth-store.ts          # Zustand
│       │   ├── plans/
│       │   ├── weekly/
│       │   ├── shopping/
│       │   ├── tracking-weight/
│       │   ├── tracking-workout/
│       │   ├── dashboard/
│       │   ├── ai-chat/                         # locked widget S1
│       │   └── push-notifications/
│       ├── components/                          # ONLY truly shared, design-system primitives
│       │   ├── ui/                              # Button, Card, Modal, Input — domain-free
│       │   └── layout/                          # AppShell, BottomNav, TopBar
│       ├── lib/                                 # cross-cutting infrastructure
│       │   ├── api-client.ts                    # axios/fetch wrapper, JWT injection, refresh logic
│       │   ├── dexie-db.ts                      # Dexie schema definition
│       │   ├── query-client.ts                  # TanStack QueryClient + persistence
│       │   ├── mutation-queue.ts                # offline queue helpers
│       │   └── sw-register.ts
│       ├── stores/                              # cross-feature Zustand stores (theme, ui)
│       ├── hooks/                               # cross-cutting hooks (useOnline, useMediaQuery)
│       └── styles/
│           └── globals.css
│
├── backend/                                     # FastAPI
│   ├── pyproject.toml                           # poetry/uv-managed
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   ├── main.py                                  # uvicorn entry, app factory
│   └── app/
│       ├── api/
│       │   ├── __init__.py
│       │   ├── deps.py                          # auth dep (get_current_user), pagination
│       │   ├── auth.py
│       │   ├── plans.py
│       │   ├── weekly.py
│       │   ├── shopping.py
│       │   ├── workout.py
│       │   ├── weight.py
│       │   ├── dashboard.py
│       │   ├── ai.py
│       │   ├── admin.py
│       │   └── push.py                          # subscription mgmt
│       ├── core/
│       │   ├── config.py                        # Pydantic settings (BaseSettings)
│       │   ├── security.py                      # password hash, JWT encode/decode
│       │   ├── deps.py                          # DI providers (db session, AI provider)
│       │   ├── exceptions.py                    # custom exception types -> HTTP errors
│       │   └── logging.py
│       ├── models/                              # SQLAlchemy 2 declarative
│       │   ├── base.py                          # Base, common columns
│       │   ├── user.py
│       │   ├── group.py
│       │   ├── plan.py
│       │   ├── weekly.py
│       │   ├── tracking.py                      # WorkoutLog, WeightLog
│       │   ├── shopping.py
│       │   ├── invite.py
│       │   └── push.py
│       ├── schemas/                             # Pydantic v2 request/response + parsed_json schema
│       │   ├── auth.py
│       │   ├── plan.py
│       │   ├── plan_parsed.py                   # canonical shape of parsed_json
│       │   ├── weekly.py
│       │   ├── shopping.py
│       │   ├── tracking.py
│       │   └── ai.py
│       ├── services/                            # business logic
│       │   ├── auth_service.py
│       │   ├── plan_service.py
│       │   ├── weekly_service.py
│       │   ├── shopping_service.py              # variant-aware aggregation
│       │   ├── tracking_service.py
│       │   ├── pdf_service.py                   # ReportLab in threadpool
│       │   └── push_service.py                  # pywebpush dispatcher
│       ├── parsers/
│       │   ├── md_parser.py                     # tolerant section parser
│       │   └── md_sections.py                   # individual section parsers
│       ├── ai/
│       │   ├── provider.py                      # AIProvider ABC
│       │   ├── factory.py                       # get_provider_from_env()
│       │   ├── null_provider.py                 # S1 default
│       │   ├── ollama_provider.py               # S5
│       │   ├── openai_provider.py               # S5
│       │   └── anthropic_provider.py            # S5
│       ├── db/
│       │   ├── session.py                       # async engine + sessionmaker
│       │   └── init_db.py                       # bootstrap admin user
│       └── tasks/
│           └── scheduler.py                     # APScheduler: Monday push reminder
│
├── deploy/                                      # ops scripts/configs
│   ├── nssm/
│   │   └── install-service.ps1
│   ├── iis/
│   │   └── web.config                           # reverse proxy rules
│   └── win-acme/
│       └── README.md
│
└── .planning/                                   # GSD project planning artifacts
```

### 3.1 Structure Rationale

- **Monorepo with `frontend/` + `backend/` siblings:** matches PROMPT_CONTRACT lock-in. Use **pnpm workspaces** for the frontend (single package today, but cheap to extend) and **leave Python out of the JS workspace entirely** — `backend/` is managed by `uv` or `poetry` independently. This avoids shoehorning Python into a Node tooling pattern that gives nothing in return.
- **Turborepo is NOT recommended for this project.** It would add caching value only if there were multiple JS packages or shared libs. With one frontend package, it's overhead. Revisit only if a second JS package emerges (e.g., shared types package or admin app).
- **Frontend uses feature-based folders** (`features/auth/`, `features/weekly/`, etc.) with co-located queries, components, hooks. Layer-based folders (`components/`, `hooks/`, `services/`) become unfindable past ~10 features. Dan Abramov-style co-location is the consensus 2026 default for medium apps. Pure UI primitives stay in `components/ui/` because they're domain-free.
- **Backend keeps the layered structure from PROMPT_CONTRACT** (`api/`, `services/`, `models/`, etc.) because FastAPI projects are read along those axes (someone debugging "why does this endpoint 500?" navigates `api/ → services/ → models/`). Feature-folders in Python add little since module count stays small (~10 domains).
- **`schemas/plan_parsed.py` is the canonical Pydantic shape of `parsed_json`** stored on the `NutritionPlan` model — see section 6 for parser/validation split.

---

## 4. Architectural Patterns

### Pattern 1: Offline-First Mutation Queue (Dexie + TanStack Query)

**What:** Every write goes through a single `mutate()` helper that (a) optimistically updates TanStack Query cache, (b) appends an entry to a Dexie `mutation_queue` table, (c) attempts the network call. On success, the queue entry is dequeued. On failure (offline), it stays in queue. A `flushQueue()` runs on `online` event and on app start.

**When to use:** All user writes (weight log, workout log, shopping checkbox, variant selection). Reads use TanStack Query directly with Dexie as cache backing.

**Trade-offs:**
- Pro: durable across browser restarts, supports true offline writes, replay is deterministic.
- Pro: server stays simple — no CRDT, no merge logic. Conflict resolution is "last-write-wins per row".
- Con: collisions are possible (Marta and Stefano edit same shared meal offline at the same time). Mitigation: shared meals use `updated_at` on the server; client sends `If-Unmodified-Since` style version on PATCH; server returns 409 → client surfaces toast "Marta ha modificato questo pasto, ricarica".
- Con: doesn't handle "two devices, same user, both offline". Acceptable for 100-user family app.

**Code sketch:**
```typescript
// frontend/src/lib/mutation-queue.ts
type QueuedMutation = {
  id: string;            // uuid
  endpoint: string;      // '/api/weight/log'
  method: 'POST' | 'PATCH' | 'DELETE';
  body: unknown;
  createdAt: number;
  retries: number;
};

export const db = new Dexie('wellness-buddy');
db.version(1).stores({
  mutation_queue: 'id, createdAt',
  cache_weekly: '[userId+weekStart]',
  cache_plans: 'id',
  drafts: 'key',
});

export async function enqueueMutation(m: Omit<QueuedMutation,'id'|'createdAt'|'retries'>) {
  await db.table('mutation_queue').add({
    id: crypto.randomUUID(), createdAt: Date.now(), retries: 0, ...m,
  });
}

export async function flushQueue(apiClient) {
  const items = await db.table('mutation_queue').orderBy('createdAt').toArray();
  for (const item of items) {
    try {
      await apiClient.request(item);
      await db.table('mutation_queue').delete(item.id);
    } catch (e) {
      if (isConflict(e)) await handleConflict(item, e);  // surface toast, drop
      else if (item.retries > 5) await moveToDeadLetter(item);
      else await db.table('mutation_queue').update(item.id, { retries: item.retries + 1 });
      break;  // stop on first failure to preserve order
    }
  }
}

window.addEventListener('online', () => flushQueue(apiClient));
```

```typescript
// frontend/src/features/tracking-weight/queries/use-log-weight.ts
export function useLogWeight() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (entry) => apiClient.post('/api/weight/log', entry),
    onMutate: async (entry) => {
      await qc.cancelQueries({ queryKey: ['weight'] });
      const previous = qc.getQueryData(['weight']);
      qc.setQueryData(['weight'], (old) => [...(old ?? []), { ...entry, _optimistic: true }]);
      await enqueueMutation({ endpoint: '/api/weight/log', method: 'POST', body: entry });
      return { previous };
    },
    onError: (_e, _v, ctx) => qc.setQueryData(['weight'], ctx?.previous),
    onSettled: () => qc.invalidateQueries({ queryKey: ['weight'] }),
  });
}
```

### Pattern 2: AI Provider Abstraction via FastAPI Depends

**What:** `AIProvider` ABC declares all AI capabilities. A factory reads `AI_PROVIDER` env var **once at app startup** and instantiates the concrete provider (held as a singleton on `app.state`). Endpoints declare `provider: AIProvider = Depends(get_ai_provider)` — never import concrete classes.

**When to use:** All AI-touching endpoints (Sprint 5 and onward). Sprint 1 already wires the dependency so endpoints return 501 via `NullProvider` without code changes when the provider list activates.

**Trade-offs:**
- Pro: zero runtime cost (provider is a singleton, no per-request construction).
- Pro: tests inject `MockProvider` via `app.dependency_overrides[get_ai_provider]`.
- Con: cannot swap provider per request (e.g., user-selected model). If that becomes a requirement, change to per-request lookup `Depends(lambda req: get_provider_for_user(req.user))`.

**Code sketch:**
```python
# backend/app/ai/provider.py
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

# backend/app/ai/factory.py
from app.core.config import settings
from app.ai.provider import AIProvider
from app.ai.null_provider import NullProvider

def build_provider() -> AIProvider:
    name = settings.AI_PROVIDER
    if name == "null":
        return NullProvider()
    if name == "ollama":
        from app.ai.ollama_provider import OllamaProvider
        return OllamaProvider(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)
    if name == "openai":
        from app.ai.openai_provider import OpenAIProvider
        return OpenAIProvider(api_key=settings.OPENAI_API_KEY)
    if name == "anthropic":
        from app.ai.anthropic_provider import AnthropicProvider
        return AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY)
    raise ValueError(f"unknown AI_PROVIDER: {name}")

# backend/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.ai.factory import build_provider

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ai_provider = build_provider()
    yield

app = FastAPI(lifespan=lifespan)

# backend/app/core/deps.py
from fastapi import Request, Depends
from app.ai.provider import AIProvider

def get_ai_provider(request: Request) -> AIProvider:
    return request.app.state.ai_provider

# backend/app/api/ai.py
@router.post("/api/ai/meal-suggestion")
async def meal_suggestion(
    body: MealSuggestionRequest,
    user: User = Depends(get_current_user),
    ai: AIProvider = Depends(get_ai_provider),
):
    if not ai.is_available:
        raise HTTPException(501, detail={"detail": "AI non disponibile", "code": "ai_unavailable"})
    text = await ai.generate_meal_suggestion(...)
    return {"suggestion": text}
```

### Pattern 3: Tolerant MD Parser → Pydantic Validation Split

**What:** Two-stage parsing. **Stage 1 (parser, tolerant):** `md_parser.py` walks the markdown AST, normalizes headings (case-insensitive, strips emoji/dashes), extracts each section into a `dict[str, Any]`, logs unrecognized sections without raising. **Stage 2 (validation, strict):** the dict is passed to `PlanParsedSchema(**raw_dict)` — a Pydantic v2 model with sensible defaults — which produces the canonical `parsed_json` written to DB. API layer only sees the strict, post-validation shape.

**When to use:** Any time MD is uploaded. Validation **belongs in the parser package**, not in the API layer — endpoints should never see raw dicts. The API endpoint receives `UploadFile`, calls `parse_and_validate(md_bytes) -> PlanParsedSchema`, then persists.

**Trade-offs:**
- Pro: separation of concerns. Parser is forgiving (matches real-world markdown variation). Validation is strict (downstream code can rely on shape).
- Pro: Pydantic v2's `model_validate_json` + `jiter` is fast enough that this isn't a perf concern.
- Con: two failure modes (parser warnings vs. validation errors). Mitigation: parser collects warnings into a `ParseReport` returned alongside the schema; admin UI displays warnings.

**Code sketch:**
```python
# backend/app/schemas/plan_parsed.py
from pydantic import BaseModel, Field

class PersonalData(BaseModel):
    name: str
    age: int | None = None
    current_weight_kg: float | None = None
    target_weight_kg: float | None = None

class MealOption(BaseModel):
    key: str           # "A" | "B" | "pasta"
    title: str
    ingredients: list["Ingredient"]
    macros: "Macros"

class Ingredient(BaseModel):
    name: str
    quantity: float | None = None
    unit: str | None = None
    category: str | None = None  # for shopping list grouping

class Macros(BaseModel):
    kcal: int = 0
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0

class PlanParsedSchema(BaseModel):
    personal_data: PersonalData
    macro_target: Macros
    daily_structure: list[dict] = Field(default_factory=list)
    breakfast: MealOption | None = None
    lunches: dict[str, list[MealOption]] = Field(default_factory=dict)  # "monday" -> [A, B, pasta]
    dinners: dict[str, list[MealOption]] = Field(default_factory=dict)
    snacks: list[MealOption] = Field(default_factory=list)
    supplements: list[dict] = Field(default_factory=list)
    weight_projection: list[dict] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)

# backend/app/parsers/md_parser.py
@dataclass
class ParseReport:
    warnings: list[str]

def parse_and_validate(md_text: str) -> tuple[PlanParsedSchema, ParseReport]:
    raw = _walk_sections(md_text)        # tolerant
    schema = PlanParsedSchema.model_validate(raw)  # strict
    return schema, ParseReport(warnings=raw.pop("_warnings", []))
```

### Pattern 4: Multi-User Family Sync via Group + Visibility

**What:** Users belong to one `Group` (`User.group_id` FK, nullable for solo users). Resources that can be shared (cena, pranzo) carry a `visibility` enum field: `private` | `group_shared`. Queries that fetch shared resources do `WHERE user_id = :me OR (group_id = :my_group AND visibility = 'group_shared')`.

**When to use:** Cene and pranzi by default `group_shared`; colazione/spuntini `private`. Variants selection per-meal-per-user remains private. Weight/workout logs always private.

**Trade-offs:**
- Pro: simple, single-table queries with one extra JOIN to `groups`. No cross-user FK.
- Pro: easy to add a third user (kid) to the group later.
- Con: doesn't model "I want to share THIS meal with Marta only this week". If needed later, switch from boolean visibility to a `meal_shares` association table.

**Data model:**
```python
# backend/app/models/group.py
class Group(Base):
    __tablename__ = "groups"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    users: Mapped[list["User"]] = relationship(back_populates="group")

# backend/app/models/user.py
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    role: Mapped[str] = mapped_column(default="user")  # admin | user
    group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"), nullable=True)
    group: Mapped[Group | None] = relationship(back_populates="users")

# backend/app/models/weekly.py
from enum import Enum
class Visibility(str, Enum):
    PRIVATE = "private"
    GROUP_SHARED = "group_shared"

class WeeklyPlanVariant(Base):
    __tablename__ = "weekly_plan_variants"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("nutrition_plans.id"))
    week_start: Mapped[date] = mapped_column(index=True)
    day_of_week: Mapped[int]  # 0=Mon..6=Sun
    meal_type: Mapped[str]    # breakfast | lunch | dinner | snack
    variant_key: Mapped[str]  # "A" | "B" | "pasta"
    visibility: Mapped[Visibility] = mapped_column(default=Visibility.PRIVATE)
    completed: Mapped[bool] = mapped_column(default=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (
        Index("ix_weekly_user_week", "user_id", "week_start"),
        Index("ix_weekly_group_share", "week_start", "visibility"),
    )
```

```python
# backend/app/services/weekly_service.py
async def get_week(session, user: User, week_start: date) -> dict:
    # own variants
    own = await session.scalars(
        select(WeeklyPlanVariant).where(
            WeeklyPlanVariant.user_id == user.id,
            WeeklyPlanVariant.week_start == week_start,
        )
    )
    # shared variants from group members (excluding self)
    shared = []
    if user.group_id:
        member_ids = await session.scalars(
            select(User.id).where(User.group_id == user.group_id, User.id != user.id)
        )
        shared = await session.scalars(
            select(WeeklyPlanVariant)
            .where(
                WeeklyPlanVariant.user_id.in_(member_ids.all()),
                WeeklyPlanVariant.week_start == week_start,
                WeeklyPlanVariant.visibility == Visibility.GROUP_SHARED,
                WeeklyPlanVariant.meal_type.in_(["lunch", "dinner"]),
            )
        )
    return {"own": own.all(), "shared": shared.all()}
```

### Pattern 5: JWT Refresh Token Rotation in HttpOnly Cookie

**What:** Access token (15 min) returned in JSON response body, stored **in memory** (Zustand `authStore`). Refresh token (7 days) issued as **HttpOnly + Secure + SameSite=Lax cookie** on `/api/auth/login` and `/api/auth/refresh`. On refresh, server **rotates** (issues new refresh, invalidates old via `jti` denylist in DB). Reuse detection: if a previously-rotated `jti` is presented again, revoke the entire session family.

**When to use:** All authenticated requests. Access token sent as `Authorization: Bearer ...` header; refresh cookie sent automatically by browser to `/api/auth/refresh` only (cookie path scoped).

**Trade-offs:**
- Pro: refresh token never visible to JavaScript → XSS can't steal long-lived credentials.
- Pro: rotation + family-revocation detects token theft.
- Con: requires `withCredentials: true` on axios + CORS `Access-Control-Allow-Credentials: true` + non-wildcard `Access-Control-Allow-Origin`. Same-origin (IIS reverse proxy serving both `/` and `/api/*`) eliminates this complication entirely.
- Con: needs server-side `refresh_tokens` table (id, user_id, jti, family_id, issued_at, revoked, replaced_by) to enforce rotation.

**Code sketch:**
```python
# backend/app/api/auth.py
@router.post("/api/auth/login")
async def login(creds, response: Response, session = Depends(get_session)):
    user = await authenticate(session, creds.email, creds.password)
    access = create_access_token(user.id, expires_in=timedelta(minutes=15))
    refresh, family_id = await issue_refresh(session, user.id)
    response.set_cookie(
        "wb_refresh", refresh,
        httponly=True, secure=True, samesite="lax",
        path="/api/auth", max_age=7 * 24 * 3600,
    )
    return {"access_token": access, "user": UserOut.model_validate(user)}

@router.post("/api/auth/refresh")
async def refresh(request: Request, response: Response, session = Depends(get_session)):
    cookie = request.cookies.get("wb_refresh")
    if not cookie: raise HTTPException(401)
    user_id, family_id, old_jti = await rotate_refresh(session, cookie)  # raises if reused
    access = create_access_token(user_id, expires_in=timedelta(minutes=15))
    new_refresh = await issue_refresh_in_family(session, user_id, family_id)
    response.set_cookie("wb_refresh", new_refresh, httponly=True, secure=True, samesite="lax", path="/api/auth", max_age=7*24*3600)
    return {"access_token": access}
```

```typescript
// frontend/src/lib/api-client.ts
let accessToken: string | null = null;
export const setAccessToken = (t: string | null) => (accessToken = t);

const client = axios.create({ baseURL: '/', withCredentials: true });
client.interceptors.request.use((cfg) => {
  if (accessToken) cfg.headers.Authorization = `Bearer ${accessToken}`;
  return cfg;
});
client.interceptors.response.use(
  (r) => r,
  async (err) => {
    if (err.response?.status === 401 && !err.config._retried) {
      err.config._retried = true;
      const { data } = await axios.post('/api/auth/refresh', null, { withCredentials: true });
      setAccessToken(data.access_token);
      err.config.headers.Authorization = `Bearer ${data.access_token}`;
      return client(err.config);
    }
    return Promise.reject(err);
  },
);
```

### Pattern 6: Service Worker Cache Strategy Per Resource Type

**What:** Workbox `runtimeCaching` configures different strategies for different URL patterns.

| Resource pattern | Strategy | Cache name | Rationale |
|------------------|----------|------------|-----------|
| `/assets/*` (JS/CSS hashed) | `CacheFirst` | `static-assets` | content-hashed, immutable |
| `/icons/*`, fonts, images | `CacheFirst` (+ expiration 30d) | `static-images` | rarely change |
| `/api/plans/*` (read), `/api/weekly/*` | `NetworkFirst` w/ 3s timeout | `api-plans`, `api-weekly` | want fresh, fall back to cache offline |
| `/api/dashboard/*` | `StaleWhileRevalidate` | `api-dashboard` | tolerable staleness, instant load |
| `/api/auth/*`, `/api/*` writes | `NetworkOnly` | — | auth must always hit network; writes go via mutation queue, not SW |
| App shell (`/`, `/today`, etc.) | `NetworkFirst` w/ navigateFallback | `app-shell` | must reach SPA shell offline |

**When to use:** Configured once in `vite.config.ts` via `VitePWA({ workbox: { runtimeCaching: [...] } })` using **generateSW strategy** initially. Switch to **injectManifest** only if we need custom logic (e.g., share-target handler).

**Trade-offs:**
- Pro: declarative, no custom SW code in Sprint 1.
- Con: generateSW can't do background sync queue replay — we use Dexie + window `online` event instead, which is fine because writes go through `apiClient`, not via fetch in SW.

---

## 5. Data Flow

### 5.1 Request Flow — Online (Read)

```
[User taps /today]
    ↓
[<TodayPage>] -> useQuery(['weekly', monday]) (TanStack Query)
    ↓
[QueryClient] -> apiClient.get('/api/weekly/2026-04-27')
    ↓
[axios interceptor] adds Authorization: Bearer <accessToken>
    ↓
[Service Worker] runtimeCaching NetworkFirst -> network attempt (3s timeout)
    ↓
[IIS] /api/* -> reverse proxy to localhost:8000
    ↓
[FastAPI router] api/weekly.py -> Depends(get_current_user) decodes JWT
    ↓
[services/weekly_service.py] queries WeeklyPlanVariant (own + group_shared)
    ↓
[SQLAlchemy async session] -> asyncpg -> PostgreSQL
    ↓
[Response] Pydantic v2 schema serialized to JSON
    ↓
[Service Worker] writes to api-weekly cache + returns to TanStack Query
    ↓
[TanStack Query] updates cache, persists to Dexie via persistQueryClient
    ↓
[<TodayPage>] re-renders with data
```

### 5.2 Request Flow — Offline (Write)

```
[User logs weight 78.5kg, offline]
    ↓
[<WeightTracker>] -> useLogWeight().mutate({ date, weight_kg })
    ↓
[onMutate] qc.setQueryData(['weight'], optimistic + entry)  # UI updates instantly
    ↓
[enqueueMutation] Dexie.mutation_queue.add({ endpoint: '/api/weight/log', body, ... })
    ↓
[apiClient.post] -> SW NetworkOnly -> network fails -> rejection
    ↓
[onError] (no rollback because offline is expected, queue persists)
    ↓
[User reconnects: window 'online' fires]
    ↓
[flushQueue] iterates Dexie queue, replays each via apiClient
    ↓
[Server accepts, returns 201] -> Dexie.mutation_queue.delete(id)
    ↓
[onSettled] qc.invalidateQueries(['weight']) -> refetch -> server is source of truth
```

### 5.3 Conflict Flow — Two Users Edit Same Shared Meal

```
[Stefano offline marks dinner Mon variant=A, completed=true]    [Marta online marks variant=B, completed=true]
    ↓                                                              ↓
[Dexie queues PATCH]                                              [Server commits B, updated_at = T1]
    ↓ (Stefano comes online)                                       ↓
[flushQueue replays PATCH with If-Unmodified-Since: T0]
    ↓
[Server: T0 < T1] -> 409 Conflict, body {current: {variant: 'B', updated_at: T1}}
    ↓
[Client] mutation_queue.delete(id) + show toast "Marta ha modificato cena: variante B"
    ↓
[Optionally] qc.invalidateQueries(['weekly']) to pull fresh state
```

### 5.4 State Management Split (decision summary)

| State | Lives in | Why |
|-------|----------|-----|
| Current user, JWT access token, role | **Zustand** (`authStore`) | small, synchronous, must be reactive across app |
| Theme, layout prefs, week-picker selection | **Zustand** (`uiStore`) | UI-only, ephemeral OK |
| Drafts (in-progress workout note before save) | **Dexie** (`drafts` table) | needs to survive refresh |
| Server resources (plans, weekly, weight log, workout log) | **TanStack Query cache** (memory) + **Dexie** (persisted via `persistQueryClient` to `cache_*` tables) | server is source of truth; Dexie persists between sessions |
| Mutation queue | **Dexie** (`mutation_queue`) | durable across sessions/restarts; correctness depends on it |
| Service worker caches | **CacheStorage** (managed by Workbox) | for HTTP responses + assets, distinct from app data |

**Rule:** Anything coming from `/api/*` lives in TanStack Query (mirrored to Dexie). Anything client-only (user picked Italian theme) lives in Zustand. Anything that needs to survive a power loss lives in Dexie. Never duplicate.

---

## 6. Build Order / Phase Dependency Graph

```
                          [P1: Monorepo + Tooling]
                                   ↓
                ┌──────────────────┼──────────────────┐
                ↓                  ↓                  ↓
       [P2: Backend Skel]  [P3: Frontend Skel]  [P4: PostgreSQL DB]
       (FastAPI + Alembic) (Vite + Tailwind +    (CREATE DATABASE,
                            React Router)         Alembic init)
                ↓                  ↓                  ↑
                └──────────┬───────┘                  │
                           ↓                           │
                  [P5: Auth + JWT + Refresh] ────────┤
                           ↓                           │
                  [P6: Models + Migrations]──────────-┘
                           ↓
              ┌────────────┼────────────┐
              ↓            ↓            ↓
     [P7: MD Parser] [P8: PWA Shell] [P9: AI ABC + NullProvider]
                           ↓
              ┌────────────┼────────────┐
              ↓            ↓            ↓
     [P10: Plans     [P11: Weight    [P12: Workout
      upload+activate] Tracker]       Tracker]
              ↓            ↓            ↓
              └────────────┼────────────┘
                           ↓
                [P13: /today landing page]
                           ↓
              ┌──────── Sprint 1 PAUSE GATE ────────┐
              │  Deploy verified on Win Server      │
              └──────────────────┬──────────────────┘
                                 ↓
                  [P14: Weekly variants API + UI]
                                 ↓
              ┌──────────────────┼──────────────────┐
              ↓                  ↓                  ↓
      [P15: Shopping List]  [P16: PDF export]  [P17: Multi-user
       (depends on variants)  (ReportLab)        family sync)
                                 ↓
              ┌──────── Sprint 2 PAUSE GATE ────────┐
                                 ↓
                  [P18: Dashboard KPI + Progress]
                                 ↓
                  [P19: VAPID setup + Push API]
                                 ↓
                  [P20: Monday push reminder]
                                 ↓
              ┌──────── Sprint 3 PAUSE GATE ────────┐
                                 ↓
                       [P21: Plan diff view]
                                 ↓
                       [P22: Admin panel]
                                 ↓
              ┌──────── Sprint 4 PAUSE GATE ────────┐
                                 ↓
                  [P23: Ollama/OpenAI/Anthropic providers]
                                 ↓
                       [P24: AI chat UI unlocked]
                                 ↓
                          [Sprint 5 GATE]
```

### 6.1 Hard Dependencies

- **Models + Migrations (P6) before any feature** — schema must exist before services.
- **Auth (P5) before anything user-scoped** — every protected endpoint needs `Depends(get_current_user)`.
- **MD Parser (P7) before Plans upload (P10)** — endpoint can't function without parser.
- **PWA Shell (P8) before deploy gate** — installability is a Sprint 1 acceptance criterion.
- **AI ABC (P9) before any AI endpoint** — even stub endpoints need the type.
- **Variants API (P14) before Shopping List (P15)** — list aggregates from selected variants.
- **Group entity (in P6) before family sync (P17)** — already in schema from day one to avoid migration churn.
- **VAPID keys (P19) before push reminders (P20)** — server can't sign push without keys.

### 6.2 Soft Dependencies (build-order preferences, not blockers)

- Service worker / Dexie integration can land in P8 (PWA Shell) **as scaffolding only** (online-first reads cached); the full mutation-queue offline flow can land any time before a "real offline" use case appears (early Sprint 2 ideal).
- TanStack Query persistence (`persistQueryClient` + Dexie adapter) is also a Sprint 2 thing — Sprint 1 can use in-memory cache only; data is small.
- Refresh token rotation (full family-revocation) can ship as **basic** in P5 (single refresh + 7-day expiry) and harden later if attack surface concerns rise.

---

## 7. Decision Points That Sprint Planning Must Lock

Before Sprint 1 kickoff, lock these:

| # | Decision | Recommendation | Cost of changing later |
|---|----------|----------------|-------------------------|
| D1 | Monorepo workspace tool | **pnpm workspaces only** (no Turborepo S1) | Low — adding Turborepo later is incremental |
| D2 | Refresh token storage | **HttpOnly cookie with rotation** | High — changes auth flow on every endpoint |
| D3 | SW strategy | **generateSW** initially | Low — switchable via vite-pwa config |
| D4 | PDF generator | **ReportLab** in `run_in_threadpool` | Medium — invoice templates would need rewrite |
| D5 | State split (Zustand vs Query vs Dexie) | per Section 5.4 table | High — touches every feature |
| D6 | Conflict policy on shared meals | **Last-write-wins + 409 on stale `updated_at`** | Medium — toast UX changes |
| D7 | Group entity schema (Sprint 1 even if unused) | **Yes, ship in P6** | High — late migration of FK |
| D8 | AI provider DI (singleton at startup) | per Pattern 2 | Low — DI scope refactor |
| D9 | MD parser strict-vs-tolerant boundary | tolerant parser → strict Pydantic | Low |
| D10 | Uvicorn worker count | **1 worker** for 100 users (see Section 8) | Trivial — env var |
| D11 | SSL termination | **IIS terminates, Uvicorn HTTP localhost** | Low — IIS reconfig |
| D12 | VAPID keys | generated once, stored in `.env` server-side, public key embedded in frontend build | Trivial unless rotated |

Defer to Sprint 2+:
- Whether to add a shared types package (`@wb/types`) between frontend and backend (could autogenerate from OpenAPI). Probably **no** for 100-user app — manual sync is fine and simpler.
- WebSocket vs polling for real-time family sync — start with polling (TanStack Query refetch on focus), add WS only if Stefano/Marta complain about latency.

---

## 8. Deployment Topology

```
Internet
    ↓ HTTPS:443 (Let's Encrypt cert via win-acme)
[Windows Server 2019]
    ↓
[IIS]
    │  Site: wellness-buddy.epartner.it
    │  - SSL termination here
    │  - Static rewrite: /* -> D:\Develop\Wellness Buddy\frontend\dist\
    │  - Reverse proxy: /api/* -> http://127.0.0.1:8000 (URL Rewrite + ARR)
    │
    └→ HTTP:8000 [Uvicorn (NSSM Windows Service "WellnessBuddyAPI")]
       - 1 worker (--workers 1)
       - Reasoning: 100 users, mostly idle; async I/O handles concurrency
         within one event loop. Multi-worker on Windows requires gunicorn
         which doesn't run natively on Windows; uvicorn's built-in
         multi-process is workable but adds complexity for no benefit at
         this scale.
       - Bind to 127.0.0.1 only (never expose 8000 publicly)
       ↓
[PostgreSQL :5432]
    DATABASE: WellnessBuddy
    pool_size=10, max_overflow=10, pool_pre_ping=True, pool_recycle=1800
    Reasoning: 1 uvicorn worker × ~10-20 concurrent requests = ample
    headroom under PG default max_connections=100.
```

### 8.1 SSL Decision: Termination at IIS, Not Pass-through

- **Recommendation:** SSL termination at IIS, plain HTTP localhost between IIS and Uvicorn.
- **Why:** Stefano already runs win-acme for cert renewal. Uvicorn supports SSL but has no automated cert renewal on Windows. Termination at the edge is the standard pattern.
- **Security note:** ensure IIS binds to localhost-only on port 8000 (firewall rule blocking external 8000).

### 8.2 Static Asset Serving: IIS Native

- **Frontend `dist/`** served directly by IIS (static handler is faster than going through Uvicorn).
- Apply `Cache-Control: public, max-age=31536000, immutable` to `/assets/*` (hashed filenames) via IIS response headers.
- `index.html` should be `Cache-Control: no-cache` to allow PWA update detection.

### 8.3 NSSM Service Configuration

```powershell
nssm install WellnessBuddyAPI "C:\Python312\python.exe" `
  "-m uvicorn main:app --host 127.0.0.1 --port 8000"
nssm set WellnessBuddyAPI AppDirectory "D:\Develop\Wellness Buddy\backend"
nssm set WellnessBuddyAPI AppEnvironmentExtra "PYTHONUNBUFFERED=1"
nssm set WellnessBuddyAPI Start SERVICE_AUTO_START
nssm set WellnessBuddyAPI AppStdout "D:\logs\wb-stdout.log"
nssm set WellnessBuddyAPI AppStderr "D:\logs\wb-stderr.log"
```

---

## 9. Database Concerns

### 9.1 Connection Pool Tuning (SQLAlchemy 2 async)

```python
# backend/app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    settings.DATABASE_URL,           # postgresql+asyncpg://...
    pool_size=10,
    max_overflow=10,                 # burst to 20 connections
    pool_timeout=30,
    pool_recycle=1800,               # recycle every 30 min
    pool_pre_ping=True,              # validate connection before checkout
    echo=False,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
```

For 100 users, expected concurrent active = ~5-15 (most users idle). 10/10 pool covers comfortably.

### 9.2 Indexing Strategy

| Query pattern | Required index |
|---------------|----------------|
| `WHERE user_id = ? AND week_start = ?` (weekly) | `(user_id, week_start)` composite |
| `WHERE user_id = ? AND date BETWEEN ? AND ?` (workout, weight time series) | `(user_id, date DESC)` |
| `WHERE group_id = ? AND visibility = 'group_shared' AND week_start = ?` (family sync) | `(week_start, visibility)` partial-style; PG can use bitmap with the (user_id, week_start) one |
| `WHERE token = ?` (invite lookup) | unique index on `token` |
| Unique constraint: 1 active plan per user | partial unique index `WHERE is_active = true` on `(user_id)` |

```python
__table_args__ = (
    Index("ix_workout_user_date", "user_id", "date"),
    Index("ix_weight_user_date", "user_id", "date"),
    Index("ix_weekly_user_week", "user_id", "week_start"),
    Index("ix_active_plan_per_user", "user_id", unique=True,
          postgresql_where=text("is_active = true")),
)
```

---

## 10. Push Notifications Architecture

```
[Frontend]                                           [Backend]                          [Browser Push Service]
    │                                                    │                                     │
    │ (1) navigator.serviceWorker.register()              │                                     │
    │ (2) reg.pushManager.subscribe({                     │                                     │
    │     applicationServerKey: VAPID_PUBLIC })           │                                     │
    │       ─────────────────────────────────────────────→│                                     │
    │ (3) POST /api/push/subscribe                        │                                     │
    │     { endpoint, keys: { p256dh, auth } }            │                                     │
    │       ─────────────────────────────────────────────→│ store in PushSubscription table     │
    │                                                    │                                     │
    │                                                    │ (4) APScheduler weekly job (Mon 7am):│
    │                                                    │     pywebpush(sub, data, vapid_priv)│
    │                                                    │       ─────────────────────────────→│
    │                                                    │                                     │
    │ (5) SW push event fires                            │                                     │
    │     event.waitUntil(showNotification(...))         │                                     │
    │←────────────────────────────────────────────────────────────────────────────────────────│
```

**VAPID setup:**
- `vapid` Python package generates keypair once: `vapid --gen` produces `private_key.pem` + `public_key.pem`.
- Public key (base64url) embedded in frontend build via `VITE_VAPID_PUBLIC_KEY` env var.
- Private key stored in backend `.env` `VAPID_PRIVATE_KEY` (file path or PEM contents).
- Sub claim: `mailto:stefano@nxtlink.it` (admin email).

**Fallback when user blocks notifications:**
- App still functional. Settings page shows "Notifiche disattivate dal browser" with link to OS-level instructions.
- Monday weigh-in reminder degrades gracefully to: when user opens app on a Monday, show a one-off in-app banner "È lunedì! Ricordati di pesarti."

**iOS PWA notifications gotcha:**
- Push notifications work on iOS Safari **only when PWA is installed to home screen** (since iOS 16.4).
- Settings page should detect non-installed state (`window.matchMedia('(display-mode: standalone)').matches`) and prompt "Installa l'app per ricevere notifiche".

---

## 11. Scaling Considerations

| Scale | Architecture adjustments |
|-------|--------------------------|
| **100 users (target)** | Current architecture. 1 uvicorn worker, 10/10 PG pool. No caching layer. |
| **1,000 users** | Bump uvicorn to 2-4 workers (need gunicorn-on-Linux or accept Windows multi-process via uvicorn `--workers 4`). PG pool 20/20. Add Redis for rate limiting and JWT denylist. |
| **10,000+ users** | Out of scope (PROJECT.md "Scaling oltre 100 utenti — nessuna ottimizzazione"). |

### 11.1 First Bottleneck (when it would happen)

PostgreSQL connection saturation under burst (e.g., everyone refreshing dashboard at 8am). Mitigation order: (1) raise pool size, (2) add `LISTEN/NOTIFY` or Redis if real-time, (3) read replicas. **None needed at 100 users.**

### 11.2 Second Bottleneck

Frontend bundle size as features accumulate. Mitigation: route-level `React.lazy()` for `/admin`, `/ai`, `/progress` (charts library is heavy). Apply when bundle > 500KB gzipped.

---

## 12. Anti-Patterns

### Anti-Pattern 1: Direct AI SDK calls in services
**What people do:** `from openai import AsyncOpenAI` inside `services/dashboard_service.py` for "quick" AI summary.
**Why wrong:** breaks the abstract pattern, causes lock-in, tests need OpenAI credentials, can't swap to Ollama without refactoring multiple modules.
**Do instead:** every AI call goes through `provider: AIProvider = Depends(get_ai_provider)` injected into the route, then passed to the service.

### Anti-Pattern 2: Storing JWT in localStorage
**What people do:** `localStorage.setItem('token', accessToken)` because it's "easy".
**Why wrong:** any XSS in any dependency steals the credential. localStorage has no expiration. No way to invalidate on logout server-side without effort.
**Do instead:** access token in memory (Zustand), refresh in HttpOnly cookie. On page reload, hit `/api/auth/refresh` to get a fresh access.

### Anti-Pattern 3: Treating IndexedDB as ground truth
**What people do:** Write to Dexie directly from UI; sync "later".
**Why wrong:** divergent state across devices, no audit, no admin visibility, conflicts unrecoverable.
**Do instead:** server is ground truth. IndexedDB is (a) cache and (b) outbox queue. Read paths use TanStack Query → cache fallback. Write paths optimistic update + queue + replay.

### Anti-Pattern 4: Per-request AI provider construction
**What people do:** `provider = OllamaProvider(...)` inside the endpoint function.
**Why wrong:** opens HTTP connection on every request, no connection reuse, no startup-time validation that env is configured correctly.
**Do instead:** factory at app startup (lifespan handler) → singleton on `app.state` → DI lookup per request.

### Anti-Pattern 5: Coupling Stefano/Marta with bidirectional FKs
**What people do:** `User.partner_id` FK to enable "show me my partner's meals".
**Why wrong:** doesn't extend to 3 family members; pairing logic gets tangled; deletion cascades become dangerous.
**Do instead:** `Group` entity. Users belong to a group. Visibility flag on shareable resources. See Pattern 4.

### Anti-Pattern 6: Validating MD in the API endpoint
**What people do:** Endpoint receives raw text, validates structure inline, throws specific HTTPException for each missing section.
**Why wrong:** mixes transport concerns with parsing. Hard to test parser separately. Hard to reuse parser (e.g., for CLI import).
**Do instead:** `parse_and_validate(md_text) -> (PlanParsedSchema, ParseReport)` in `parsers/`. Endpoint catches `ValidationError` → 422; logs `ParseReport.warnings`.

### Anti-Pattern 7: Worker count cargo-cult
**What people do:** "(2 × CPU) + 1" formula → set `--workers 9` on a 4-core server.
**Why wrong:** for async I/O-bound apps, one event loop per core is enough. Multiple workers multiply DB connections (10 pool × 9 workers = 90 → close to PG default 100). Memory bloat.
**Do instead:** start with 1 worker, monitor, scale up only if event loop becomes the bottleneck. At 100 users, never.

---

## 13. Integration Points

### 13.1 External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| **PostgreSQL** | SQLAlchemy 2 async + asyncpg, pool=10/10 | Already installed; create `WellnessBuddy` DB manually before first deploy. |
| **Web Push (FCM/APNs)** | `pywebpush` POST to subscription endpoint with VAPID JWT | iOS requires PWA installed to home screen. |
| **Ollama (Sprint 5)** | HTTP POST to `${OLLAMA_BASE_URL}/api/chat`, model `gemma3:27b` | GX10 ARM64 in LAN, no auth. Connection should reuse `httpx.AsyncClient`. |
| **OpenAI / Anthropic (Sprint 5)** | Official SDKs (`openai`, `anthropic`) | API keys via `.env`; rate-limit handling in provider. |
| **Let's Encrypt** | win-acme triggered by Stefano on schedule | Cert renewal independent of app deploy. |

### 13.2 Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Frontend ↔ Backend | HTTPS REST + JSON | Same origin via IIS reverse proxy → no CORS. WebSocket reserved for Sprint 5 AI chat. |
| Backend services ↔ Database | SQLAlchemy 2 async sessions | Transaction per request; explicit `async with session.begin():` in services. |
| API layer ↔ Services | Direct function calls; services accept `session` as first arg | No service container — FastAPI's `Depends` is sufficient. |
| Services ↔ Parsers | Pure function calls; parsers are stateless | `parse_and_validate(text)` returns dataclass + Pydantic schema. |
| Services ↔ AI Provider | DI'd `AIProvider` instance | Provider abstracts away network/transport details. |
| Backend ↔ Push Service | `pywebpush(sub, data, vapid_priv)` from APScheduler job | Errors logged; subscription marked stale on 410 Gone. |
| Frontend ↔ Service Worker | `virtual:pwa-register/react` `useRegisterSW` | App receives updates via prompt callback; user clicks "Update" to apply. |
| TanStack Query ↔ Dexie | `persistQueryClient` plugin with custom Dexie persister | One `cache_*` table per query family for clarity. |

---

## 14. Confidence Assessment & Open Questions

| Area | Confidence | Notes |
|------|------------|-------|
| Frontend stack patterns | HIGH | Vite PWA + TanStack Query + Dexie is well-documented 2026 default; pattern verified across multiple sources. |
| AI provider DI | HIGH | Standard FastAPI pattern; lifespan + `app.state` is canonical. |
| JWT refresh rotation | HIGH | 2026 consensus: HttpOnly cookie + rotation + family revocation. |
| Multi-user Group model | MEDIUM | Pattern is sound; "what to share" flagging is project-specific — concrete Stefano/Marta use case validates "cene + pranzi shared by default". |
| Conflict resolution policy | MEDIUM | Last-write-wins + 409 is good enough for 2 users; would need stronger guarantees for higher-collision domains. |
| Worker count on Windows | MEDIUM | 1 worker is right for 100 users, but exact behavior under burst should be validated post-Sprint 1. |
| MD parser tolerance | MEDIUM | Approach is correct; specific edge cases will surface during P7 implementation against real Stefano/Marta MD. |

### Open Questions for Sprint Planning to Resolve

1. **Shared meals: opt-in vs opt-out per family?** Recommendation: cene + pranzi `group_shared` by default, breakfast/snacks `private`. UI lets user toggle. Confirm with Marta.
2. **Push permission UX:** prompt at app install, after first successful weight log, or in settings only? Recommendation: settings only — never auto-prompt (annoying).
3. **Bundle size budget:** when does `/progress` (Recharts) get lazy-loaded? Recommendation: from day 1; charts are heavy.
4. **Backup strategy for PostgreSQL:** out of architecture scope but worth confirming with Stefano (existing NXTLink backup tooling probably covers it).

---

## 15. Sources

### Stack & Patterns
- [Vite PWA Plugin (vite-pwa-org.netlify.app)](https://vite-pwa-org.netlify.app/) — Workbox config, generateSW vs injectManifest
- [TanStack Query v5 Optimistic Updates docs](https://tanstack.com/query/v5/docs/framework/react/guides/optimistic-updates)
- [TanStack Query v5 Mutations docs](https://tanstack.com/query/v5/docs/framework/react/guides/mutations)
- [tanstack-dexie-db-collection](https://github.com/HimanshuKumarDutt094/tanstack-dexie-db-collection) — reference impl for Dexie + TanStack Query offline-first
- [Dexie Cloud Consistency](https://dexie.org/docs/cloud/consistency) — conflict resolution patterns
- [pnpm Workspaces](https://pnpm.io/workspaces) — official docs
- [Monorepo Tools 2026 Comparison](https://viadreams.cc/en/blog/monorepo-tools-2026/) — pnpm vs Turborepo vs Nx
- [React Folder Structure 2025 (Robin Wieruch)](https://www.robinwieruch.de/react-folder-structure/) — feature-based co-location
- [Layered Architecture & DI in FastAPI (dev.to)](https://dev.to/markoulis/layered-architecture-dependency-injection-a-recipe-for-clean-and-testable-fastapi-code-3ioo)
- [FastAPI Dependencies docs](https://fastapi.tiangolo.com/tutorial/dependencies/)

### Auth & Security
- [JWT Security Best Practices 2026 (DevToolKit)](https://www.devtoolkit.cloud/blog/jwt-security-best-practices-2026) — HttpOnly cookie + rotation
- [JWT Best Practices 2026 (jsmanifest)](https://jsmanifest.com/jwt-security-best-practices-2026)
- [Auth0 Refresh Tokens guide](https://auth0.com/blog/refresh-tokens-what-are-they-and-when-to-use-them/) — rotation + family revocation

### Backend & DB
- [SQLAlchemy 2.0 Connection Pooling docs](https://docs.sqlalchemy.org/en/20/core/pooling.html)
- [FastAPI Server Workers docs](https://fastapi.tiangolo.com/deployment/server-workers/) — uvicorn worker count
- [Uvicorn Deployment docs](https://uvicorn.dev/deployment/)
- [Pydantic v2 JSON docs](https://docs.pydantic.dev/latest/concepts/json/) — jiter parser, tolerant validation

### PDF & Push
- [pywebpush GitHub](https://github.com/web-push-libs/pywebpush) — VAPID push from Python
- [MDN Web Push Notifications guide](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Tutorials/js13kGames/Re-engageable_Notifications_Push)
- [Top 10 Python PDF generators 2026 (Nutrient)](https://www.nutrient.io/blog/top-10-ways-to-generate-pdfs-in-python/) — ReportLab vs WeasyPrint
- [ReportLab + FastAPI async pattern](https://woteq.com/using-reportlab-with-fastapi-for-asynchronous-pdf-generation-in-python) — `run_in_threadpool`

### Project Inputs
- `d:/Develop/AI/WellnessBuddy/.planning/PROJECT.md`
- `d:/Develop/AI/WellnessBuddy/docs/PROMPT_CONTRACT_WELLNESS_BUDDY.md` v1.0 (27/04/2026)

---

*Architecture research for: Wellness Buddy (self-hosted nutrition tracking PWA)*
*Researched: 2026-05-01*
