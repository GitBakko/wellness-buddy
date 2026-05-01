# Phase 1: Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-01
**Phase:** 01-foundation
**Mode:** discuss (auto-mode runtime, condensed gray-area selection)
**Areas discussed:** Domain DNS, MD Plans Test Corpus, Deploy Strategy, CI/CD Platform

---

## Domain DNS

| Option | Description | Selected |
|--------|-------------|----------|
| wellness-buddy.epartner.it | Default contract, sotto-dominio epartner.it esistente | ✓ |
| wellness.nxtlink.it | Sottodominio NXTLink alternativo | |
| Altro | Specifica custom | |

**User's choice:** wellness-buddy.epartner.it
**Notes:** Conferma del default del prompt contract. Win-acme cert flow noto, CORS_ORIGINS = `https://wellness-buddy.epartner.it`.

---

## MD Plans Test Corpus

| Option | Description | Selected |
|--------|-------------|----------|
| /plans dir nel repo | Versionati con repo, gitignored (privacy) | ✓ |
| Esterni a repo | Path esterno, copiati in CI come fixture | |
| Sintetici Sprint 1 | Genero piani sintetici, reali post-deploy | |

**User's choice:** /plans dir nel repo
**Notes:** Plans reali Stefano+Marta in `/plans/` con `.gitignore` voce. Fixture sintetici in `backend/tests/fixtures/plans/` (versionati, evil-corpus + canonical happy path).

---

## Deploy Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Continuous da PR #1 | GH Actions → Win Server ogni merge a main | |
| End of Phase 1 | Deploy single-shot a foundation completa | |
| Mid-phase milestone | Deploy primo dopo auth+models+/today | |
| Other (custom) | Alla fine, quando app strutturata e completa | ✓ |

**User's choice:** Custom — "Alla fine, quando abbiamo una app strutturata e completa"
**Notes:** Più conservativo di "End of Phase 1" stretto. Deploy SOLO quando login + auth + plan upload + /today + weight/workout log tutti funzionanti localmente. Sviluppo locale-first via Docker Compose. CI deploy automation deferred Sprint 4.

---

## CI/CD Platform

| Option | Description | Selected |
|--------|-------------|----------|
| GitHub Actions | Free repo privati piccoli, Windows runners disponibili | ✓ |
| Self-hosted runner | Su Windows Server, più controllo, more maintenance | |
| Solo CI locale Sprint 1 | Pre-commit + manual, GH setup deferred | |

**User's choice:** GitHub Actions
**Notes:** Pipelines Sprint 1: pr.yml (lint+type+test+build), axe-a11y.yml, dark-mode-screenshot.yml. Pre-commit hooks via Husky+lint-staged. Deploy automation deferred Sprint 4.

---

## Pre-locked (research-derived defaults, not asked)

| Decision | Default |
|----------|---------|
| Repo structure | pnpm workspaces (frontend/+backend/), backend Python via uv |
| Python tooling | uv (Astral) — fastest 2026, deterministic lockfile |
| .env management | `.env` gitignored, `.env.example` versionato |
| Testing backend | pytest + pytest-asyncio + httpx + pytest-postgresql Docker |
| Testing frontend | Vitest + Playwright + axe-core/playwright |
| Test DB | Docker postgres ephemeral, no sqlite (JSONB/TIMESTAMPTZ divergence) |
| Persist storage prompt | After successful first login (full-screen welcome CTA) |
| PWA install prompt | After 2nd visit, no auto-prompt; iOS bottom sheet |
| Error boundaries | Global ErrorBoundary + per-route Suspense fallback |
| Backend logging | structlog JSON, request ID middleware |
| Frontend observability | NONE Sprint 1, Sentry deferred Sprint 4 |
| SECRET_KEY | `secrets.token_hex(32)`, gitignored |
| DB password | `openssl rand -base64 32`, Windows DPAPI cifrato |
| VAPID | Phase 3 only |
| Connection pool | 15/10 (per research SUMMARY.md) |
| Alembic baseline | Single migration `0000_baseline.py` con full Phase 1 schema |
| Group entity | Created Sprint 1 schema (visibility enum included) anche se family sync arriva Phase 2 |

---

## Claude's Discretion

- Esatti SQLAlchemy model file paths
- Alembic env.py boilerplate
- FastAPI folder layout dettagliato (api/ vs routers/)
- Workbox runtime caching config per asset type
- Dexie schema versioning + upgrade hooks
- shadcn/ui CLI install order (17 components from UI-SPEC §14)
- Lottie animations Sprint 1 specifiche
- Storyset/Open Doodles selection for empty states + login hero

---

## Deferred Ideas

- WebSocket vs SSE vs polling per condiviso badge → Phase 2 research
- WeasyPrint GTK3 Windows spike → Phase 2
- VAPID + push notifications → Phase 3
- Mascot final + Lottie/Rive integration → Phase 3
- PostgreSQL RLS defense-in-depth → Phase 4
- k6 load test → Phase 4
- Vite 7→8 upgrade → Phase 4
- Sentry observability → Phase 4
- Automated deploy CI/CD → Phase 4
- AI providers concreti → Phase 5
- AI prompt-injection corpus → Phase 5
- Recharts performance optimization → Phase 3+
- i18n refactor → v2 (post-Sprint 5)
