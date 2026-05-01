# Wellness Buddy

Self-hosted PWA per nutrition + wellness tracking, multi-user famiglia, AI pluggabile.

## Stack

Frontend: React 19 + Vite 7 + TailwindCSS 4 + shadcn/ui + Geist + Motion v12
Backend: FastAPI 0.136 + SQLAlchemy 2 async + asyncpg + PostgreSQL
Infra: Windows Server 2019 + IIS reverse proxy + win-acme + NSSM

## Dev Setup

Prerequisites: Node.js 20+, pnpm 9+, Python 3.12, uv (Astral), Docker Desktop, PostgreSQL client (`psql`).

Verify env:

```bash
# POSIX
bash scripts/check-env.sh
# Windows PowerShell
pwsh scripts/check-env.ps1
```

Install + first run:

```bash
# 1. Frontend deps (pnpm workspace)
pnpm install

# 2. Backend deps (uv — separate from pnpm)
cd backend && uv sync && cd ..

# 3. Dev postgres
docker compose up -d postgres

# 4. Create database (one-time, manual per D-28)
docker exec -it wellness-buddy-postgres-dev psql -U wnbd -d postgres -c "CREATE DATABASE \"WellnessBuddy\";"
# If already exists this fails harmlessly.

# 5. Run migrations baseline
cd backend && uv run alembic upgrade head && cd ..

# 6. Start both stacks (concurrently)
pnpm dev
```

Frontend: http://localhost:5173
Backend: http://localhost:8000/docs (OpenAPI Swagger UI)

## Architecture

Frontend uses **pnpm workspace**, backend uses **uv** — they are separate (D-01).
Plans MD files live in `/plans/` (gitignored per D-04). `/plans/EXAMPLE.md` shows format.

See `CLAUDE.md` for conventions and `.planning/ROADMAP.md` for phase plan.

## Conventions

Italian-only Sprint 1 — UI strings in `frontend/src/i18n/copy.it.ts`.
JWT access in memory + refresh HttpOnly cookie + rotation + 10s grace window.
MD parser tolerant + Pydantic v2 strict.
Server is canonical truth, Dexie is cache + outbox queue.

## Deploy

See `DEPLOY.md` for Windows Server 2019 step-by-step.
