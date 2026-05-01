# Wellness Buddy — Backend

FastAPI 0.136 + SQLAlchemy 2 async + asyncpg + Alembic + Pydantic v2.

Managed with **uv** (Astral) — separate from the frontend pnpm workspace (D-01, D-02).

## Setup

```bash
cd backend
uv sync
```

## Dev server

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

The `app.main:app` ASGI module is created by Plan 02a (backend-core). Until then,
this command will fail with ImportError — expected during Plan 01 scaffolding.

## Tests

```bash
cd backend
uv run pytest --cov=app --cov-report=term-missing
```

Coverage gate: ≥80% on `services/`, `parsers/`, `auth/` (D-11).

## Migrations

```bash
cd backend
uv run alembic upgrade head
```
