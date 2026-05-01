---
phase: 01-foundation
plan: 02a
type: execute
wave: 2
depends_on: [01]
files_modified:
  - backend/app/__init__.py
  - backend/app/main.py
  - backend/app/core/__init__.py
  - backend/app/core/config.py
  - backend/app/core/database.py
  - backend/app/core/security.py
  - backend/app/core/deps.py
  - backend/app/core/exceptions.py
  - backend/app/core/logging.py
  - backend/app/core/middleware.py
  - backend/app/models/__init__.py
  - backend/app/models/base.py
  - backend/app/models/user.py
  - backend/app/models/group.py
  - backend/app/models/plan.py
  - backend/app/models/variant.py
  - backend/app/models/workout.py
  - backend/app/models/weight.py
  - backend/app/models/shopping.py
  - backend/app/models/invite.py
  - backend/app/models/refresh.py
  - backend/app/models/audit.py
  - backend/app/schemas/__init__.py
  - backend/app/schemas/user.py
  - backend/app/schemas/group.py
  - backend/app/schemas/plan.py
  - backend/app/schemas/common.py
  - backend/app/services/__init__.py
  - backend/app/services/audit_service.py
  - backend/app/api/__init__.py
  - backend/app/api/health.py
  - backend/app/api/version.py
  - backend/app/api/errors.py
  - backend/alembic/versions/0000_baseline.py
  - backend/tests/conftest.py
  - backend/tests/integration/__init__.py
  - backend/tests/integration/test_app_startup.py
  - backend/tests/integration/test_health.py
  - backend/tests/integration/test_alembic_baseline.py
  - backend/tests/unit/__init__.py
  - backend/tests/unit/test_models.py
autonomous: true
requirements: [FND-03, MOD-01, MOD-02, MOD-03, MOD-04, MOD-05, MOD-06, MOD-07, MOD-08, MOD-09, MOD-10, AUTH-12]
must_haves:
  truths:
    - "FastAPI app starts with lifespan hook (AI provider binding deferred to Plan 02b)"
    - "Alembic baseline 0000_baseline.py creates all 10 tables (users, groups, nutrition_plans, weekly_plan_variants, workout_log, weight_log, shopping_list_state, invite_tokens, refresh_tokens, audit_log) with TIMESTAMPTZ + IANA tz on User"
    - "GET /api/health returns 200 {status: ok, version, build_hash}"
    - "GET /version.json returns 200 {version, build_hash}"
    - "structlog emits JSON with request_id field on every request"
    - "API errors return JSON {detail: string, code: string} (AUTH-12 contract)"
    - "Pydantic v2 base schemas exist for User, Group, NutritionPlan with strict ConfigDict(extra='forbid')"
    - "audit_service.write_audit() persists rows to audit_log table"
  artifacts:
    - path: "backend/app/main.py"
      provides: "FastAPI app factory + lifespan stub + middleware + base router includes"
      contains: "lifespan"
    - path: "backend/app/models/base.py"
      provides: "DeclarativeBase + TimestampTZ alias"
      contains: "DeclarativeBase"
    - path: "backend/app/models/user.py"
      provides: "User model with timezone IANA default Europe/Rome"
      contains: "Europe/Rome"
    - path: "backend/alembic/versions/0000_baseline.py"
      provides: "Schema baseline migration covering all 10 tables"
      contains: "create_table"
    - path: "backend/app/services/audit_service.py"
      provides: "write_audit() helper"
      contains: "write_audit"
  key_links:
    - from: "backend/app/main.py"
      to: "backend/app/core/exceptions.py::register_exception_handlers"
      via: "Exception envelope wired in app factory"
      pattern: "register_exception_handlers"
    - from: "backend/app/models/user.py"
      to: "backend/app/models/group.py"
      via: "ForeignKey users.group_id -> groups.id"
      pattern: 'ForeignKey\("groups\.id"'
    - from: "backend/alembic/versions/0000_baseline.py"
      to: "backend/app/models/*.py"
      via: "Alembic autogenerate from Base.metadata"
      pattern: "users"
---

<objective>
Build the backend backbone (split 1 of 2): FastAPI app factory + core scaffolding (config/database/security/deps/exceptions/logging/middleware), all 10 SQLAlchemy 2 async Mapped models with TIMESTAMPTZ + IANA tz on User, Pydantic v2 base schemas (User/Group/NutritionPlan/common), Alembic baseline migration `0000_baseline.py` covering full Phase 1 schema (D-30), audit_service helper (D-23), structlog JSON config + request ID middleware (D-21), `/api/health` + `/version.json` endpoints (FND-03, FND-06), AUTH-12 error envelope contract enforced via custom exception handler, conftest.py + test_app_startup + test_models + test_health + test_alembic_baseline.

The AI layer (ABC + NullProvider + factory + stub routers + AI endpoints + integration tests) is owned by Plan 02b — it lands in parallel within Wave 2 but 02b's main.py edits extend the lifespan stub created here.

Purpose: Every Wave 3+ plan (auth, parser, /today) depends on this skeleton being importable and the Alembic schema being applied. Per build order locks: Models before features, Group entity in schema Sprint 1, TIMESTAMPTZ + IANA tz Sprint 1.

Output: `cd backend && uv run uvicorn app.main:app --port 8001` boots successfully, `alembic upgrade head` creates all 10 tables on a fresh DB, `pytest tests/integration/test_app_startup.py tests/integration/test_alembic_baseline.py tests/unit/test_models.py` green.
</objective>

<execution_context>
@C:/Users/bakko/.claude/plugins/cache/gsd-plugin/gsd/2.38.8/workflows/execute-plan.md
@C:/Users/bakko/.claude/plugins/cache/gsd-plugin/gsd/2.38.8/templates/summary.md
</execution_context>

<context>
@d:/Develop/AI/WellnessBuddy/.planning/PROJECT.md
@d:/Develop/AI/WellnessBuddy/.planning/ROADMAP.md
@d:/Develop/AI/WellnessBuddy/.planning/STATE.md
@d:/Develop/AI/WellnessBuddy/.planning/REQUIREMENTS.md
@d:/Develop/AI/WellnessBuddy/.planning/phases/01-foundation/01-CONTEXT.md
@d:/Develop/AI/WellnessBuddy/.planning/phases/01-foundation/01-RESEARCH.md
@d:/Develop/AI/WellnessBuddy/.planning/phases/01-foundation/01-VALIDATION.md
@d:/Develop/AI/WellnessBuddy/.planning/research/ARCHITECTURE.md
@d:/Develop/AI/WellnessBuddy/.planning/phases/01-foundation/01-01-PLAN.md
</context>

<interfaces>
<!-- Plans 03 (auth), 04 (parser), 07 (today) consume these models + DI helpers + envelope. -->
<!-- Plan 02b creates app.ai.* and extends main.py lifespan to bind AI provider. -->

From `app/core/config.py`:
```python
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str  # validated len >= 32
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: list[str]
    AI_PROVIDER: Literal["null", "ollama", "openai", "anthropic"] = "null"
    MAX_USERS: int = 100
    ADMIN_EMAIL: str
    LOG_LEVEL: str = "INFO"
    SQL_ECHO: bool = False
    APP_VERSION: str = "0.1.0"
    BUILD_HASH: str = "dev"

settings: Settings
```

From `app/core/database.py`:
```python
engine: AsyncEngine  # pool_size=15, max_overflow=10
SessionLocal: async_sessionmaker[AsyncSession]
async def get_session() -> AsyncIterator[AsyncSession]: ...
```

From `app/core/deps.py`:
```python
async def get_current_user(...) -> User  # STUB raising 501; Plan 03 implements
def get_ai_provider(request: Request) -> AIProvider  # reads request.app.state.ai_provider (bound by Plan 02b)
def require_admin(user=Depends(get_current_user)) -> User
```

From `app/core/exceptions.py`:
```python
class AppException(StarletteHTTPException):
    def __init__(self, status_code: int, detail: str, code: str): ...
def register_exception_handlers(app: FastAPI) -> None: ...
```

From `app/models/base.py`:
```python
class Base(DeclarativeBase): pass
TimestampTZ = Annotated[datetime, mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)]
```

From `app/models/user.py`:
```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID]  # PK PgUUID
    email: Mapped[str]  # unique
    username: Mapped[str]  # unique
    hashed_password: Mapped[str]
    role: Mapped[str]  # 'admin' | 'user'
    group_id: Mapped[UUID | None]  # FK groups.id ondelete=SET NULL
    timezone: Mapped[str]  # IANA, default 'Europe/Rome'
    created_at: Mapped[TimestampTZ]
```
</interfaces>

<tasks>

<task type="auto" tdd="false">
  <name>Task 1: Core scaffolding (config + database + security + deps stubs + exceptions + logging + middleware) + main.py with lifespan stub + health/version/errors endpoints + conftest</name>
  <files>backend/app/__init__.py, backend/app/main.py, backend/app/core/__init__.py, backend/app/core/config.py, backend/app/core/database.py, backend/app/core/security.py, backend/app/core/deps.py, backend/app/core/exceptions.py, backend/app/core/logging.py, backend/app/core/middleware.py, backend/app/api/__init__.py, backend/app/api/health.py, backend/app/api/version.py, backend/app/api/errors.py, backend/tests/conftest.py, backend/tests/integration/__init__.py, backend/tests/integration/test_app_startup.py, backend/tests/integration/test_health.py</files>
  <read_first>
    - .planning/phases/01-foundation/01-RESEARCH.md (Pattern 7 SQLAlchemy async config, Pattern 9 security primitives, "Backend `main.py` skeleton" code, Pattern 4 /version.json backend section)
    - .planning/phases/01-foundation/01-CONTEXT.md (D-21 structlog, D-29 pool 15/10, D-32 lifespan, D-20 error envelope)
    - .planning/research/ARCHITECTURE.md
    - backend/.env.example (env keys to wire into Settings)
  </read_first>
  <action>
    Build the backbone of the FastAPI app. Concrete code per RESEARCH.md.

    1. **`backend/app/__init__.py`** — empty
    2. **`backend/app/core/__init__.py`** — empty

    3. **`backend/app/core/config.py`** — Pydantic settings BaseSettings:
       ```python
       """App settings loaded from backend/.env at boot. Fail-fast on missing required values."""
       from __future__ import annotations
       from typing import Literal
       from pydantic import Field, field_validator
       from pydantic_settings import BaseSettings, SettingsConfigDict

       class Settings(BaseSettings):
           model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

           # Database (D-29)
           DATABASE_URL: str = Field(..., min_length=10)
           SQL_ECHO: bool = False

           # JWT (D-24, AUTH-04, AUTH-05)
           SECRET_KEY: str = Field(..., min_length=32)
           ALGORITHM: str = "HS256"
           ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
           REFRESH_TOKEN_EXPIRE_DAYS: int = 7

           # CORS (validated at boot, never wildcard prod)
           CORS_ORIGINS: list[str] = Field(default_factory=list)

           # AI provider (D-31, D-32, AI-07)
           AI_PROVIDER: Literal["null", "ollama", "openai", "anthropic"] = "null"

           # Operational
           MAX_USERS: int = 100
           ADMIN_EMAIL: str
           LOG_LEVEL: str = "INFO"
           APP_VERSION: str = "0.1.0"
           BUILD_HASH: str = "dev"

           @field_validator("CORS_ORIGINS", mode="before")
           @classmethod
           def split_csv(cls, v: object) -> list[str]:
               if isinstance(v, str):
                   return [s.strip() for s in v.split(",") if s.strip()]
               if isinstance(v, list):
                   return v
               return []

           @field_validator("CORS_ORIGINS")
           @classmethod
           def reject_wildcard(cls, v: list[str]) -> list[str]:
               if "*" in v:
                   raise ValueError("CORS_ORIGINS cannot contain wildcard '*' - set explicit allowlist")
               return v

       settings = Settings()  # type: ignore[call-arg]
       ```

    4. **`backend/app/core/database.py`** — verbatim from RESEARCH Pattern 7:
       ```python
       """SQLAlchemy 2 async engine + session factory. Pool 15/10 per D-29."""
       from __future__ import annotations
       from collections.abc import AsyncIterator
       from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
       from app.core.config import settings

       engine = create_async_engine(
           settings.DATABASE_URL,
           pool_size=15,
           max_overflow=10,
           pool_timeout=30,
           pool_recycle=1800,
           pool_pre_ping=True,
           echo=settings.SQL_ECHO,
       )

       SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

       async def get_session() -> AsyncIterator[AsyncSession]:
           async with SessionLocal() as session:
               yield session
       ```

    5. **`backend/app/core/security.py`** — JWT primitives + bcrypt (Plan 03 extends with rotate logic):
       ```python
       """JWT encode/decode + password hash primitives. Source: RESEARCH Pattern 9, AUTH-04..05."""
       from __future__ import annotations
       from datetime import datetime, timedelta, timezone
       from uuid import UUID
       from jose import jwt
       from passlib.context import CryptContext
       from app.core.config import settings

       pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

       def hash_password(p: str) -> str:
           return pwd_context.hash(p)

       def verify_password(p: str, h: str) -> bool:
           return pwd_context.verify(p, h)

       def create_access_token(user_id: UUID, expires_in: timedelta | None = None) -> str:
           expires_in = expires_in or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
           now = datetime.now(timezone.utc)
           payload = {"sub": str(user_id), "iat": now, "exp": now + expires_in, "type": "access"}
           return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

       def create_refresh_token(user_id: UUID, family_id: UUID, jti: UUID, expires_in: timedelta | None = None) -> str:
           expires_in = expires_in or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
           now = datetime.now(timezone.utc)
           payload = {
               "sub": str(user_id), "family": str(family_id), "jti": str(jti),
               "iat": now, "exp": now + expires_in, "type": "refresh",
           }
           return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

       def decode_token(token: str) -> dict:
           return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
       ```

    6. **`backend/app/core/exceptions.py`** — AUTH-12 envelope (verbatim from original 02 Task 1):
       ```python
       """Custom exceptions ensuring all API errors return JSON {detail: string, code: string}."""
       from __future__ import annotations
       from fastapi import FastAPI, Request
       from fastapi.exceptions import RequestValidationError
       from fastapi.responses import JSONResponse
       from starlette.exceptions import HTTPException as StarletteHTTPException

       class AppException(StarletteHTTPException):
           def __init__(self, status_code: int, detail: str, code: str) -> None:
               super().__init__(status_code=status_code, detail={"detail": detail, "code": code})

       async def _envelope(status: int, detail: str, code: str) -> JSONResponse:
           return JSONResponse(status_code=status, content={"detail": detail, "code": code})

       def register_exception_handlers(app: FastAPI) -> None:
           @app.exception_handler(StarletteHTTPException)
           async def http_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
               if isinstance(exc.detail, dict) and "code" in exc.detail:
                   return JSONResponse(status_code=exc.status_code, content=exc.detail)
               return await _envelope(exc.status_code, str(exc.detail), f"http_{exc.status_code}")

           @app.exception_handler(RequestValidationError)
           async def validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
               return await _envelope(422, "Dati non validi", "validation_error")

           @app.exception_handler(Exception)
           async def fallback_handler(_: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
               return await _envelope(500, "Errore interno del server", "internal_error")
       ```

    7. **`backend/app/core/logging.py`** — structlog JSON config + sensitive-key redaction (D-21). Verbatim from original 02 Task 1.

    8. **`backend/app/core/middleware.py`** — RequestIDMiddleware injecting `request_id` into structlog contextvars + IdempotentGraceMiddleware passthrough (Plan 03 owns grace logic at service layer). Verbatim from original 02 Task 1.

    9. **`backend/app/core/deps.py`** — DI dependencies. `get_current_user` is a 501 STUB (Plan 03 replaces). `get_ai_provider` returns `request.app.state.ai_provider` (bound by Plan 02b's lifespan extension). `require_admin` gates by user.role.

    10. **`backend/app/api/__init__.py`** — empty

    11. **`backend/app/api/health.py`** (FND-03):
        ```python
        from fastapi import APIRouter
        from app.core.config import settings

        router = APIRouter(tags=["health"])

        @router.get("/api/health")
        async def health() -> dict:
            return {"status": "ok", "version": settings.APP_VERSION, "build_hash": settings.BUILD_HASH}
        ```

    12. **`backend/app/api/version.py`** (FND-06):
        ```python
        from fastapi import APIRouter
        from app.core.config import settings

        router = APIRouter(tags=["version"])

        @router.get("/version.json", include_in_schema=False)
        async def version() -> dict:
            return {"version": settings.APP_VERSION, "build_hash": settings.BUILD_HASH}
        ```

    13. **`backend/app/api/errors.py`** (D-18 frontend error log):
        ```python
        from fastapi import APIRouter
        from pydantic import BaseModel
        import structlog

        log = structlog.get_logger()
        router = APIRouter(tags=["errors"])

        class ErrorReport(BaseModel):
            message: str
            stack: str | None = None
            url: str | None = None
            user_agent: str | None = None

        @router.post("/api/errors", status_code=204)
        async def log_error(report: ErrorReport) -> None:
            log.warning("frontend_error", **report.model_dump())
        ```

    14. **`backend/app/main.py`** — FastAPI factory with lifespan that DOES NOT yet bind ai_provider (Plan 02b extends). Includes only health/version/errors routers; stub routers come from Plan 02b.
        ```python
        """FastAPI app factory. Lifespan stub - Plan 02b extends to bind AI provider per AI-03/D-32."""
        from __future__ import annotations
        from contextlib import asynccontextmanager
        from collections.abc import AsyncIterator
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from app.core.config import settings
        from app.core.logging import configure_logging
        from app.core.middleware import RequestIDMiddleware, IdempotentGraceMiddleware
        from app.core.exceptions import register_exception_handlers
        from app.api import health, version, errors

        @asynccontextmanager
        async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
            configure_logging()
            # Plan 02b extends: _app.state.ai_provider = build_provider()
            yield

        app = FastAPI(
            title="Wellness Buddy API",
            version=settings.APP_VERSION,
            lifespan=lifespan,
        )

        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
            allow_headers=["*"],
        )
        app.add_middleware(RequestIDMiddleware)
        app.add_middleware(IdempotentGraceMiddleware)

        register_exception_handlers(app)

        for r in (health.router, version.router, errors.router):
            app.include_router(r)
        ```

    15. **`backend/tests/conftest.py`** — extend Plan 01 skeleton with full pytest-postgresql ephemeral fixture, async client fixture, alembic upgrade fixture (full implementation per RESEARCH Pattern 7 / Plan 03 conftest section adapted to ship here as the foundation):
        ```python
        """Pytest fixtures: ephemeral postgres + Alembic upgrade + async client."""
        from __future__ import annotations
        import asyncio
        import os
        from collections.abc import AsyncIterator

        import pytest
        import pytest_asyncio
        from httpx import AsyncClient, ASGITransport
        from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine, AsyncSession
        from alembic.config import Config
        from alembic import command

        TEST_DATABASE_URL = os.environ.get(
            "TEST_DATABASE_URL",
            "postgresql+asyncpg://wnbd:WnBd4321@@localhost:5432/WellnessBuddy_test",
        )

        @pytest.fixture(scope="session")
        def event_loop():
            loop = asyncio.new_event_loop()
            yield loop
            loop.close()

        @pytest_asyncio.fixture(scope="session")
        async def test_engine() -> AsyncIterator[AsyncEngine]:
            import asyncpg
            sys_dsn = TEST_DATABASE_URL.replace("postgresql+asyncpg", "postgresql").rsplit("/", 1)[0] + "/postgres"
            sys_conn = await asyncpg.connect(sys_dsn)
            await sys_conn.execute('DROP DATABASE IF EXISTS "WellnessBuddy_test"')
            await sys_conn.execute('CREATE DATABASE "WellnessBuddy_test"')
            await sys_conn.close()

            cfg = Config("alembic.ini")
            cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL.replace("+asyncpg", ""))
            os.environ["DATABASE_URL"] = TEST_DATABASE_URL
            command.upgrade(cfg, "head")

            engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
            yield engine
            await engine.dispose()

        @pytest_asyncio.fixture
        async def db_session(test_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
            SessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)
            async with SessionLocal() as session:
                yield session
                await session.rollback()

        @pytest_asyncio.fixture
        async def async_client() -> AsyncIterator[AsyncClient]:
            os.environ["DATABASE_URL"] = TEST_DATABASE_URL
            os.environ.setdefault("SECRET_KEY", "test-secret-key-32-bytes-minimum-padding-padding")
            os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")
            os.environ.setdefault("ADMIN_EMAIL", "admin@test.local")
            os.environ.setdefault("AI_PROVIDER", "null")
            from importlib import reload
            from app.core import config as cfg_mod
            reload(cfg_mod)
            from app.main import app
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://testserver") as client:
                yield client
        ```

    16. **`backend/tests/integration/__init__.py`** — empty

    17. **`backend/tests/integration/test_app_startup.py`** — boot test (lifespan smoke; AI provider check is owned by Plan 02b's test_ai_api):
        ```python
        from fastapi.testclient import TestClient
        from app.main import app

        def test_app_imports_and_routes_registered() -> None:
            assert len(app.routes) >= 3  # health + version + errors
            paths = {route.path for route in app.routes if hasattr(route, "path")}
            assert "/api/health" in paths
            assert "/version.json" in paths
            assert "/api/errors" in paths

        def test_app_boots_with_lifespan() -> None:
            with TestClient(app) as client:
                # Lifespan ran during context enter; configure_logging executed without error
                r = client.get("/api/health")
                assert r.status_code == 200
        ```

    18. **`backend/tests/integration/test_health.py`** — verify health + version endpoints (verbatim from original 02 Task 3):
        ```python
        from fastapi.testclient import TestClient
        from app.main import app

        def test_health_endpoint() -> None:
            with TestClient(app) as client:
                r = client.get("/api/health")
                assert r.status_code == 200
                body = r.json()
                assert body["status"] == "ok"
                assert "version" in body and "build_hash" in body

        def test_version_endpoint() -> None:
            with TestClient(app) as client:
                r = client.get("/version.json")
                assert r.status_code == 200
                body = r.json()
                assert "version" in body and "build_hash" in body
        ```
  </action>
  <verify>
    <automated>cd backend &amp;&amp; uv run python -c "from app.main import app; from app.core.config import settings; assert settings.AI_PROVIDER == 'null'; print('boot OK')" &amp;&amp; uv run pytest tests/integration/test_app_startup.py tests/integration/test_health.py -x -q &amp;&amp; uv run ruff check app/core app/api/health.py app/api/version.py app/api/errors.py app/main.py</automated>
  </verify>
  <acceptance_criteria>
    - File exists: `backend/app/core/config.py` containing literal `class Settings(BaseSettings)` AND `reject_wildcard`
    - File exists: `backend/app/core/database.py` containing literal `pool_size=15` AND `max_overflow=10`
    - File exists: `backend/app/core/security.py` containing literal `bcrypt__rounds=12`
    - File exists: `backend/app/core/exceptions.py` containing literal `register_exception_handlers`
    - File exists: `backend/app/core/logging.py` containing literal `_SENSITIVE_KEYS`
    - File exists: `backend/app/core/middleware.py` containing literal `RequestIDMiddleware` AND `IdempotentGraceMiddleware`
    - File exists: `backend/app/core/deps.py` containing literal `get_ai_provider` AND `require_admin`
    - File exists: `backend/app/api/health.py` containing literal `/api/health`
    - File exists: `backend/app/api/version.py` containing literal `/version.json`
    - File exists: `backend/app/main.py` containing literal `lifespan` AND `register_exception_handlers(app)`
    - File exists: `backend/tests/conftest.py` containing literal `test_engine` AND `async_client`
    - Command `cd backend && uv run python -c "from app.main import app"` exits 0
    - Command `cd backend && uv run pytest tests/integration/test_app_startup.py tests/integration/test_health.py -x` exits 0
    - `ruff check app/core app/main.py` exits 0
  </acceptance_criteria>
  <done>App backbone in place. Config/database/security/logging/middleware/exceptions/deps + main.py with lifespan stub + health/version/errors endpoints exist. Conftest provides ephemeral postgres for integration tests. Lifespan reserves AI provider binding for Plan 02b.</done>
</task>

<task type="auto" tdd="false">
  <name>Task 2: All 10 SQLAlchemy models + Pydantic v2 base schemas + audit_service + Alembic baseline migration covering full Phase 1 schema + test_models + test_alembic_baseline</name>
  <files>backend/app/models/__init__.py, backend/app/models/base.py, backend/app/models/user.py, backend/app/models/group.py, backend/app/models/plan.py, backend/app/models/variant.py, backend/app/models/workout.py, backend/app/models/weight.py, backend/app/models/shopping.py, backend/app/models/invite.py, backend/app/models/refresh.py, backend/app/models/audit.py, backend/app/schemas/__init__.py, backend/app/schemas/user.py, backend/app/schemas/group.py, backend/app/schemas/plan.py, backend/app/schemas/common.py, backend/app/services/__init__.py, backend/app/services/audit_service.py, backend/alembic/versions/0000_baseline.py, backend/tests/unit/__init__.py, backend/tests/unit/test_models.py, backend/tests/integration/test_alembic_baseline.py</files>
  <read_first>
    - .planning/phases/01-foundation/01-RESEARCH.md (Pattern 7 SQLAlchemy 2 Models, Pattern 8 Alembic Baseline)
    - .planning/phases/01-foundation/01-CONTEXT.md (D-30, D-23 audit log, MOD-01..MOD-10)
    - .planning/REQUIREMENTS.md (MOD-01..MOD-10 exact field list)
    - .planning/research/ARCHITECTURE.md
  </read_first>
  <action>
    Build all 10 SQLAlchemy 2 Mapped models per RESEARCH Pattern 7 + REQUIREMENTS.md MOD-01..10. All models inherit from `Base` (declarative). All timestamps are `TIMESTAMPTZ` via `TimestampTZ` alias. UUID primary keys server-generated. Plus Pydantic v2 base schemas with `ConfigDict(extra='forbid')` and the audit_service helper.

    1. **`backend/app/models/__init__.py`** — registry that imports every model so Alembic autogenerate sees all 10:
       ```python
       """Model registry. IMPORT ORDER MATTERS for Alembic autogenerate."""
       from app.models.base import Base
       from app.models.group import Group
       from app.models.user import User
       from app.models.plan import NutritionPlan
       from app.models.variant import WeeklyPlanVariant, Visibility
       from app.models.workout import WorkoutLog
       from app.models.weight import WeightLog
       from app.models.shopping import ShoppingListState
       from app.models.invite import InviteToken
       from app.models.refresh import RefreshToken
       from app.models.audit import AuditLog

       __all__ = [
           "Base", "Group", "User", "NutritionPlan", "WeeklyPlanVariant", "Visibility",
           "WorkoutLog", "WeightLog", "ShoppingListState", "InviteToken", "RefreshToken", "AuditLog",
       ]
       ```

    2. **`backend/app/models/base.py`** — verbatim from RESEARCH Pattern 7 (Base + TimestampTZ alias).

    3. **`backend/app/models/group.py`** — Group entity (MOD-02).

    4. **`backend/app/models/user.py`** — verbatim from RESEARCH Pattern 7 with `timezone` IANA default `'Europe/Rome'` (MOD-01, MOD-09).

    5. **`backend/app/models/plan.py`** — NutritionPlan with partial unique index `WHERE is_active=true` per V11 (MOD-03, MOD-10).

    6. **`backend/app/models/variant.py`** — verbatim from RESEARCH Pattern 7 (MOD-04, Visibility enum).

    7. **`backend/app/models/workout.py`** — WorkoutLog (MOD-05) with `ix_workout_user_date` index.

    8. **`backend/app/models/weight.py`** — WeightLog (MOD-06) with `Numeric(5,2)` + UNIQUE `(user_id, date)` constraint.

    9. **`backend/app/models/shopping.py`** — ShoppingListState (MOD-07).

    10. **`backend/app/models/invite.py`** — InviteToken (MOD-08, AUTH-10).

    11. **`backend/app/models/refresh.py`** — RefreshToken with `family_id`, `revoked`, `replaced_at`, `cached_access`, `cached_refresh` columns (Plan 03 fills the rotate logic; here we ship the table schema so 0000_baseline includes it).

    12. **`backend/app/models/audit.py`** — AuditLog (D-23).

    All model file contents are verbatim from the original Plan 02 Task 2 (now superseded). Refer to git history of the original `01-02-PLAN.md` (deleted in this revision) for verbatim code, or re-derive from RESEARCH Pattern 7.

    13. **`backend/app/schemas/__init__.py`** — empty.

    14. **`backend/app/schemas/common.py`** — base mixin Pydantic v2 with strict ConfigDict:
        ```python
        from pydantic import BaseModel, ConfigDict

        class StrictModel(BaseModel):
            model_config = ConfigDict(extra="forbid")
        ```

    15. **`backend/app/schemas/user.py`** — UserBase / UserOut response shapes:
        ```python
        from pydantic import EmailStr
        from app.schemas.common import StrictModel

        class UserBase(StrictModel):
            email: EmailStr
            username: str
            role: str = "user"
            timezone: str = "Europe/Rome"

        class UserOut(UserBase):
            id: str
            group_id: str | None = None
        ```

    16. **`backend/app/schemas/group.py`**:
        ```python
        from app.schemas.common import StrictModel

        class GroupBase(StrictModel):
            name: str

        class GroupOut(GroupBase):
            id: str
        ```

    17. **`backend/app/schemas/plan.py`** — PlanResponse + PlanListItem placeholders (Plan 04 extends with upload/diff response shapes):
        ```python
        from app.schemas.common import StrictModel

        class PlanResponse(StrictModel):
            id: str
            name: str
            is_active: bool

        class PlanListItem(PlanResponse):
            uploaded_at: str
        ```

    18. **`backend/app/services/__init__.py`** — empty.

    19. **`backend/app/services/audit_service.py`** (D-23):
        ```python
        from __future__ import annotations
        from uuid import UUID
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.models.audit import AuditLog

        async def write_audit(
            session: AsyncSession,
            *,
            actor_id: UUID | None,
            action: str,
            target_type: str,
            target_id: UUID | None,
            payload: dict | None = None,
        ) -> None:
            session.add(AuditLog(
                actor_id=actor_id, action=action, target_type=target_type,
                target_id=target_id, payload=payload or {},
            ))
        ```

    20. **Generate Alembic baseline `0000_baseline.py`**: run from `backend/`:
        ```bash
        docker compose -f ../docker-compose.yml up -d postgres
        until docker compose -f ../docker-compose.yml exec -T postgres pg_isready -U wnbd; do sleep 1; done
        docker compose -f ../docker-compose.yml exec -T postgres psql -U wnbd -d postgres -c "CREATE DATABASE \"WellnessBuddy\";" || true

        uv run alembic revision --autogenerate -m "baseline"
        mv alembic/versions/*_baseline.py alembic/versions/0000_baseline.py 2>/dev/null || true
        ```
        Review and ensure the migration includes:
        - All 10 tables (groups, users, nutrition_plans, weekly_plan_variants, workout_log, weight_log, shopping_list_state, invite_tokens, refresh_tokens, audit_log)
        - All `TIMESTAMPTZ` columns (`sa.DateTime(timezone=True)`)
        - All indexes per MOD-10
        - Partial unique index on `nutrition_plans` `WHERE is_active = true`
        - Visibility enum type creation `visibility_enum`
        - User.timezone default `'Europe/Rome'`

        Then `uv run alembic upgrade head`.

    21. **`backend/tests/unit/__init__.py`** — empty.

    22. **`backend/tests/unit/test_models.py`** — verbatim from original Plan 02 Task 2 (registers all 10 tables, asserts MOD-09 TIMESTAMPTZ on User.created_at, asserts IANA default `Europe/Rome`, asserts indexes per MOD-10):
        ```python
        from app.models import Base, User, Group, NutritionPlan, WeeklyPlanVariant, Visibility
        from app.models import WorkoutLog, WeightLog, ShoppingListState, InviteToken, RefreshToken, AuditLog

        EXPECTED = {
            "groups", "users", "nutrition_plans", "weekly_plan_variants",
            "workout_log", "weight_log", "shopping_list_state",
            "invite_tokens", "refresh_tokens", "audit_log",
        }

        def test_all_tables_registered() -> None:
            assert EXPECTED <= set(Base.metadata.tables.keys())

        def test_user_timezone_iana_default() -> None:
            assert User.__table__.c.timezone.default.arg == "Europe/Rome"

        def test_user_created_at_timestamptz() -> None:
            assert User.__table__.c.created_at.type.timezone is True

        def test_workout_user_date_index() -> None:
            assert any(idx.name == "ix_workout_user_date" for idx in WorkoutLog.__table__.indexes)

        def test_weight_user_date_index() -> None:
            assert any(idx.name == "ix_weight_user_date" for idx in WeightLog.__table__.indexes)

        def test_visibility_enum_values() -> None:
            assert Visibility.PRIVATE.value == "private"
            assert Visibility.GROUP_SHARED.value == "group_shared"
        ```

    23. **`backend/tests/integration/test_alembic_baseline.py`** — verify `alembic upgrade head` applies cleanly on a fresh DB and creates all 10 tables:
        ```python
        import pytest
        from sqlalchemy import inspect
        from sqlalchemy.ext.asyncio import AsyncEngine

        @pytest.mark.asyncio
        async def test_alembic_baseline_creates_all_10_tables(test_engine: AsyncEngine) -> None:
            async with test_engine.begin() as conn:
                tables = await conn.run_sync(lambda c: inspect(c).get_table_names())
            expected = {
                "groups", "users", "nutrition_plans", "weekly_plan_variants",
                "workout_log", "weight_log", "shopping_list_state",
                "invite_tokens", "refresh_tokens", "audit_log",
            }
            assert expected <= set(tables)

        @pytest.mark.asyncio
        async def test_users_created_at_is_timestamptz(test_engine: AsyncEngine) -> None:
            """W2 fix: previously SQL probe via psql; now reads via SQLAlchemy inspect."""
            async with test_engine.begin() as conn:
                cols = await conn.run_sync(lambda c: inspect(c).get_columns("users"))
            created_at = next(c for c in cols if c["name"] == "created_at")
            # SQLAlchemy reports timezone-aware timestamp via type.timezone or 'TIMESTAMP WITH TIME ZONE' in SQL string
            assert "TIME ZONE" in str(created_at["type"]).upper() or getattr(created_at["type"], "timezone", False)
        ```
  </action>
  <verify>
    <automated>cd backend &amp;&amp; uv run pytest tests/unit/test_models.py tests/integration/test_alembic_baseline.py -x -q &amp;&amp; uv run alembic upgrade head &amp;&amp; uv run alembic current</automated>
  </verify>
  <acceptance_criteria>
    - File exists: `backend/app/models/base.py` containing literal `class Base(DeclarativeBase)` AND `TimestampTZ`
    - File exists: `backend/app/models/user.py` containing literal `default="Europe/Rome"`
    - File exists: `backend/app/models/group.py` containing literal `class Group(Base)`
    - File exists: `backend/app/models/plan.py` containing literal `is_active.is_(True)`
    - File exists: `backend/app/models/variant.py` containing literal `class Visibility` AND `GROUP_SHARED = "group_shared"`
    - File exists: `backend/app/models/workout.py` containing literal `ix_workout_user_date`
    - File exists: `backend/app/models/weight.py` containing literal `ix_weight_user_date`
    - File exists: `backend/app/models/shopping.py` containing literal `class ShoppingListState`
    - File exists: `backend/app/models/invite.py` containing literal `class InviteToken`
    - File exists: `backend/app/models/refresh.py` containing literal `family_id` AND `cached_access`
    - File exists: `backend/app/models/audit.py` containing literal `class AuditLog`
    - File exists: `backend/app/schemas/common.py` containing literal `extra="forbid"`
    - File exists: `backend/app/services/audit_service.py` containing literal `def write_audit`
    - File exists: `backend/alembic/versions/0000_baseline.py` containing literal `op.create_table("users"` AND `op.create_table("groups"` AND `op.create_table("refresh_tokens"`
    - Command `cd backend && uv run pytest tests/unit/test_models.py -x` exits 0
    - Command `cd backend && uv run pytest tests/integration/test_alembic_baseline.py -x` exits 0
    - Command `cd backend && uv run alembic upgrade head` exits 0
    - **W2 fix:** `test_users_created_at_is_timestamptz` runs as automated unit test (replacing prior `psql information_schema` probe; SQL probe is manual/optional)
  </acceptance_criteria>
  <done>All 10 models defined with correct types (TIMESTAMPTZ, IANA tz, indexes per MOD-10, partial unique index per V11). Pydantic v2 base schemas (User/Group/Plan/common) ship with `extra='forbid'`. Audit service helper persists rows to audit_log. Alembic 0000_baseline.py applies cleanly creating all tables. Unit + integration tests verify metadata correctness via SQLAlchemy inspect (W2 — no psql probe needed in CI).</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Client -> API | Untrusted JSON body + headers cross here; Pydantic v2 validates at route boundary |
| API -> DB | App-layer authorization (Plan 03 wires); SQLAlchemy parameterized queries prevent SQLi |
| Settings boot -> CORS | Wildcard `*` rejected at boot (Settings validator) |

## STRIDE Threat Register (Plan 02a scope)

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-API-01 | Spoofing / DoS | FastAPI startup failure leaves prod in undefined state | mitigate | Pydantic Settings fail-fast at boot if SECRET_KEY < 32 chars or DATABASE_URL missing or CORS_ORIGINS contains `*` (V14, V9). `test_app_startup.py` integration test verifies lifespan + base routes |
| T-DB-01 | Tampering / Information disclosure | TIMESTAMPTZ handling in DB | mitigate | Docker compose enforces `PGTZ: UTC` + `TZ: UTC`; all model timestamps use `DateTime(timezone=True)` via `TimestampTZ` alias; `test_user_created_at_timestamptz` unit test asserts `timezone is True` (MOD-09); `test_users_created_at_is_timestamptz` integration test verifies via Alembic-applied schema |
| T-DB-02 | Tampering | Schema integrity / partial unique on active plan | mitigate | Alembic baseline ships `Index("ix_nutrition_plans_active_per_user", "user_id", unique=True, postgresql_where=is_active.is_(True))` (V11 — only one active plan per user); ensures invariant at DB layer not just app code |

</threat_model>

<verification>
End-of-plan checks:

```bash
cd backend
uv run python -c "from app.main import app; print(f'Routes registered: {len(app.routes)}')"
uv run alembic upgrade head
uv run pytest tests/unit/test_models.py tests/integration/test_app_startup.py tests/integration/test_health.py tests/integration/test_alembic_baseline.py -x -q
```
</verification>

<success_criteria>
- Both tasks complete with `<acceptance_criteria>` met
- `cd backend && uv run uvicorn app.main:app --port 8001` boots in <2s without errors
- `GET /api/health` returns 200 `{status: "ok", version, build_hash}`
- `GET /version.json` returns 200 `{version, build_hash}`
- `alembic upgrade head` on a fresh DB creates exactly 10 tables
- All 02a tests green: `pytest tests/unit/test_models.py tests/integration/test_app_startup.py tests/integration/test_health.py tests/integration/test_alembic_baseline.py -x`
- Lifespan stub explicitly leaves AI provider binding for Plan 02b (commented placeholder in `main.py::lifespan`)
</success_criteria>

<output>
After completion, create `.planning/phases/01-foundation/01-02a-SUMMARY.md` capturing:
- Final list of routes registered (`app.routes` count, only health/version/errors)
- Alembic baseline file path + line count + table list
- Confirmation that all 10 tables exist after `alembic upgrade head`
- Note: AI provider binding deferred to Plan 02b
</output>
