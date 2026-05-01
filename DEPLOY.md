# Wellness Buddy — Deploy Guide (Windows Server 2019)

> **Status:** Skeleton (Plan 01). Full step-by-step finalized in Plan 08 (end of Phase 1).
> Per CONTEXT D-06: deploy is deferred to end of Phase 1, sviluppo locale-first via Docker Compose.

## Prerequisites (server-side, verified Plan 08)

- PostgreSQL (already installed on Windows Server 2019 per CONTEXT.md)
- IIS with URL Rewrite + ARR modules (likely already configured for other epartner.it sites)
- NSSM (https://nssm.cc/) for wrapping Uvicorn as Windows service
- win-acme (https://www.win-acme.com/) for Let's Encrypt SSL
- Python 3.12 (server)
- GTK3 Runtime — **NOT NEEDED Phase 1** (Phase 2 WeasyPrint spike)

## Phase 1 Deploy Steps (filled in Plan 08)

TBD — Plan 08 ships full procedure:

- Step 1: Verify env via `scripts/check-env.ps1` on server
- Step 2: PostgreSQL `CREATE DATABASE WellnessBuddy;` (D-28)
- Step 3: Backend deploy: clone, `uv sync`, `alembic upgrade head`, NSSM service install
- Step 4: Frontend deploy: `pnpm build` -> IIS site root -> `frontend/dist/`
- Step 5: IIS reverse proxy `web.config` `/api/* -> localhost:8000`, `/* -> dist/`
- Step 6: win-acme cert request for `wellness-buddy.epartner.it`
- Step 7: Smoke tests (login + plan upload + /today + weight log)

## Secret Generation (D-24, D-25)

```powershell
# SECRET_KEY (32-byte hex)
python -c "import secrets; Write-Host (secrets.token_hex(32))"

# Database password
# Use openssl on dev box, copy to server .env (DPAPI cifrato)
openssl rand -base64 32
```

## Domain & SSL

Domain: `wellness-buddy.epartner.it` (D-05) — sottodominio epartner.it esistente, win-acme flow noto.

## Rollback Plan

TBD Plan 08 — Stefano known pattern from MANTIS/ePartner.

---

*Skeleton committed: Plan 01. Finalized: Plan 08.*
