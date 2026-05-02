# Phase 2: Differentiators - Research

**Researched:** 2026-05-02
**Domain:** Weekly variants + shopping list aggregation + family sync (multi-user) + WeasyPrint Windows Server PDF + Plan 08 T3 production deploy absorption
**Confidence:** HIGH for code/architecture patterns (Phase 1 inheritance + locked CONTEXT.md decisions); MEDIUM for WeasyPrint Windows Server 2019 stability (production verdict belongs to the 7-day spike); MEDIUM for BroadcastChannel iOS Safari edge cases (caniuse confirms support, private mode + standalone PWA quirks need device verification).

## Summary

Phase 2 turns Wellness Buddy into a real weekly tool for the Brunelli family. The phase is fully scoped by **34 locked CONTEXT.md decisions** (D-01..D-34) and an **APPROVED 6/6 UI-SPEC.md (revision 2)** that inherits Phase 1 §1-§5 verbatim. Research role here is therefore **prescriptive, not exploratory** — every architectural primitive is already decided. Open territory lives in:

1. **WeasyPrint on Windows Server 2019** — install path verified against authoritative WeasyPrint docs (MSYS2 Pango install or GTK3 runtime portable bundle). 7-day spike (Plan 02-01) gates the rest of Phase 2 PDF work. ReportLab fallback scaffolded behind `PdfExporter` ABC.
2. **Italian quantity parser** — heuristic dictionary in `backend/app/services/ingredient_parser.py`. No NLP library exists for Italian recipe quantities; we ship a tightly-scoped regex + lookup parser tuned to the 6 fixture plans + future evil corpus.
3. **WeeklyPlanVariant LWW + If-Unmodified-Since** — schema already ships `version int` + `updated_at TIMESTAMPTZ` from Plan 02b baseline. Pattern: client sends `If-Unmodified-Since: <updated_at ISO>` header, server compares to row, mismatch → 409 with `{detail, code: "version_conflict", conflicting_user: "Marta"}` envelope. NOT 412 (semantics align with FAM-05 Italian copy contract).
4. **Group migration data backfill** — Alembic data-only migration `0001_activate_groups.py` is idempotent: skip if `user.group_id IS NOT NULL`. Async session pattern via `op.get_bind()` + plain SQLAlchemy Core (no model imports — migrations stable across model evolution).
5. **APScheduler + IANA tz** — APScheduler 3.x already pulls `zoneinfo` (Python 3.12 native). `AsyncIOScheduler` is the FastAPI pairing. Per-user cron jobs registered at lifespan startup + on user creation event. DST-correctness comes from `CronTrigger(timezone=ZoneInfo(user.timezone))` — APScheduler computes next-fire each run, NOT additive arithmetic.
6. **TanStack Query refetchOnFocus + 30s staleTime** — already wired Phase 1. Extension to `/week` + `/spesa` + condiviso badge: standard query keys `['weekly', userId, weekStart]` + `['shopping', userId, weekStart]`. Convergence ≤5s validated in two-client integration test (T-FAM-04).
7. **PostgreSQL partial unique index per visibility** — NOT introduced Phase 2 (D-23: no schema changes). Existing `(user_id, week_start, day_of_week, meal_type)` natural key + version column suffices. Visibility enum already in baseline.
8. **Negative-authz test matrix** — extend Plan 04 + Plan 07 cross-user 404 pattern to 8 endpoints × 5 scenarios = 40 tests in `backend/tests/integration/test_family_authz_matrix.py`.
9. **WeasyPrint Italian font embedding** — `@font-face` with woff2 base64 inline (NOT URL-referenced — WeasyPrint runs offline at PDF-gen time, no network access at print). Validated end-to-end on iPhone Safari + Mail.app at end of Phase 2 (T-PDF-02).
10. **Visual regression baseline regen** — Playwright `--update-snapshots` flow committed in Plan 02-02 first-task action. Phase 1 left TODO comments in `frontend/tests/visual/{light,dark}.spec.ts`.

**Primary recommendation:** Plan 02-01 (GTK3 spike) is a **HARD GATE** — no other Phase 2 work depending on PDF (Plan 02-05) starts before the 7-day stability run produces a verdict. Wave 2 (Plan 02-02 `/week` + variant selector) and Wave 4 (Plan 02-04 shopping list backend without PDF export) can proceed in parallel during the spike window.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Variant selection (mutate user choice) | API / Backend | Browser / Client (optimistic UI) | Server canonical truth; client overlays optimistic state per CONV-7 |
| Weekly summary aggregation (kcal/macros over 7 days) | API / Backend | — | Pure server-side computation reading variants + plan parsed_json |
| Variant version conflict detection | API / Backend (LWW + If-Unmodified-Since) | — | DB-level serialization; client only renders 409 toast |
| Shopping list aggregation from variants | API / Backend | — | Reads server canonical variants + plan ingredient parser; cached as `ShoppingListState` |
| Italian quantity parsing | API / Backend | — | Server-side heuristic dictionary; runs at plan parse + on-demand for shopping list |
| Shopping checkbox state | API / Backend (canonical) | Browser / Client (Dexie cache + outbox) | Cross-device sync requires server canonical; client offline-tolerant via mutation queue |
| Shopping list weekly reset (cron) | API / Backend (APScheduler) | — | Server-side IANA tz cron; client never schedules |
| PDF generation (WeasyPrint) | API / Backend | — | Backend-only; binary GTK3 dep; never client |
| `condiviso` badge live update | Browser / Client (TanStack Query refetchOnFocus + 30s staleTime) | API / Backend (DB read) | Polling pattern locked D-16; no WebSocket Phase 2 |
| Cross-user authz (group_shared resources) | API / Backend (`get_user_with_group_access` dep) | — | Authz NEVER trusted to client per FAM-07 + Pitfall #3 |
| Group entity activation backfill | API / Backend (Alembic data migration) | — | One-time DB operation; idempotent |
| Variant pill UI + meal share toggle | Browser / Client (React + Radix) | — | Component layer per UI-SPEC §6.2 |
| iOS install instructions banner | Browser / Client (PWA detection) | — | Standard iOS PWA pattern (UI-SPEC §10) |
| Production deploy walkthrough (Plan 02-03) | Human-verified runbook | — | DEPLOY.md script exists; checkpoint validates end-to-end on real iPhone |

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Variant model:**
- **D-01:** Variant naming verbatim REQ WEEK-03: "Opzione A" / "Opzione B" / "Pasta speciale". No free-text varianti Phase 2.
- **D-02:** Variant override granularity = **per-meal-day** (`(week_start, day, meal_slot)`). Default = "Opzione A".
- **D-03:** Default variant inheritance: nuova settimana mai visitata → tutti pasti default "Opzione A". Persistenza server-side `WeeklyPlanVariant` keyed `(user_id, week_start, day, meal_slot)`.
- **D-04:** Endpoint summary ritorna `{kcal_total, protein_g, carbs_g, fat_g, days: [...]}` (WEEK-05).

**Shopping list aggregation:**
- **D-05:** Italian quantity parser heuristic dictionary in `backend/app/services/ingredient_parser.py`. Tuple `(amount, unit)`. NOT NLP.
- **D-06:** NO fuzzy matching Phase 2. Exact match dopo lowercase + NFC + trim. Synonyms deferred Phase 5.
- **D-07:** Categorie locked: Frigo & Freschi / Frutta & Verdura / Dispensa / Condimenti / Integratori. Plan parser estende grammar opzionale `**Categoria:** <nome>`. Mapping fallback in `backend/app/services/category_mapper.py`.
- **D-08:** Week start = lunedì. `startOfWeek({ weekStartsOn: 1 })`.
- **D-09:** Reset settimanale lunedì 00:00 IANA tz user via APScheduler `reset_shopping_lists_at_user_midnight`.
- **D-10:** `ShoppingListState` server-canonical, Dexie cache + mutation queue (Plan 06 pattern).

**PDF export (WeasyPrint):**
- **D-11:** Plan 02-01 = GTK3 spike PRIMA di shopping list code dipendente. 7-day stability. Soglia fallback 5xx >2% in 7d → ReportLab branch. Spike report `02-01-GTK3-SPIKE.md`.
- **D-12:** PDF brand template `backend/app/templates/shopping_list.html` consuma stessa palette `@theme` Lifesum Pure (mirror via OKLCH coords). Drift impossibile.
- **D-13:** Plus Jakarta Sans woff2 embedded HTML; verifica iPhone Safari + Mail.app fine Phase 2.
- **D-14:** ReportLab fallback wiring scaffolded Plan 02-01, attivato SOLO se spike fallisce. Branching dietro `PdfExporter` ABC.

**Family sync:**
- **D-15:** Visibility defaults: cene + pranzi `group_shared`, colazione + spuntini `private`. User per-meal toggle in MealCard `⋯` menu (`DotsThreeOutline` → "Condividi con la famiglia" Switch).
- **D-16:** Real-time strategy: TanStack Query `refetchOnFocus: true` + `staleTime: 30_000`. NO WebSocket. NO SSE Phase 2. Convergence ≤5s test.
- **D-17:** Conflict UX: PATCH accepts `If-Unmodified-Since` header from `WeeklyPlanVariant.updated_at` (FAM-04). Mismatch → 409 `{detail, code: "version_conflict", conflicting_user: "Marta"}`. Toast key `copy.sync.conflictToast`.
- **D-18:** Condiviso badge UI: Phosphor `UsersThree` 14px + caption nome partner inline accanto al meal title. Tap → Tooltip Radix con timestamp.

**Authz extension:**
- **D-19:** Cross-user reads via `get_user_with_group_access(target_user_id)` dependency. Endpoints estesi: `GET /api/today?user_id=...`, `GET /api/weekly/{week_start}?user_id=...`, `GET /api/shopping/{week_start}?user_id=...`.
- **D-20:** `group_id` MAI in JWT. Re-look-up DB ogni request.
- **D-21:** Negative-authz matrix CI: 8 endpoints × 5 scenari = 40 test minimum. File `backend/tests/integration/test_family_authz_matrix.py`. Cross-user reads non autorizzati = 404 (info-disclosure).

**Migration strategy:**
- **D-22:** Alembic data-only `0001_activate_groups.py`: per ogni User esistente crea `Group(name=user.full_name + " · household")` + `user.group_id = group.id`. Idempotente.
- **D-23:** No schema changes — Group + visibility enum + WeeklyPlanVariant.version già nel baseline Plan 02. Solo data backfill.
- **D-24:** Admin merge gruppi → deferred Phase 4.

**iOS Safari quirks:**
- **D-25:** Multi-tab sync shopping list checkbox via BroadcastChannel API. Fallback `window.addEventListener('focus', refetch)` se assente. Detection `'BroadcastChannel' in window`.

**Plan 08 T3 deferred — production deploy mid-phase:**
- **D-26:** **Plan 02-03 = production deploy CHECKPOINT** mid-phase (DOPO `/week` + variant selector ship Plan 02-02; PRIMA Plan 02-04 shopping list). Stefano DEPLOY.md su Windows Server 2019.
- **D-27:** Stefano + Marta validation iPhone install + offline `/today` + variant selector. Sign-off `02-03-DEPLOY-CHECKLIST.md`.
- **D-28:** Lighthouse PWA ≥95 + a11y ≥95 su `https://wellness-buddy.epartner.it/today`.

**Performance:**
- **D-29:** Shopping list ~336 righe: NO virtualization Phase 2. Threshold >500 → Phase 4.
- **D-30:** Weekly view pre-fetch ±1 week con `useWeeklyQuery`.

**Visual regression:**
- **D-31:** Rigeneration `pnpm test:visual --update-snapshots` come prima azione Plan 02-02.

**AI widget:**
- **D-32:** AI widget invariato (locked placeholder Phase 1). NO surface change.

**Italian copy:**
- **D-33:** ~95 new strings (UI-SPEC §7.1 leaf-counted) sotto namespaces `week.*`, `shopping.*`, `family.*`, `sync.conflictToast`, `pwa.installFollowUp`.

**Wave structure (suggested):**
- **D-34:** W1 02-01 GTK3 spike → W2 02-02 `/week` + variant + visual baseline → W3 02-03 deploy CHECKPOINT → W4 02-04 shopping list aggregation → W5 02-05 PDF export → W6 02-06 family sync activation + authz matrix → W7 02-07 closure.

### Claude's Discretion

- Exact `WeeklyPlanVariant.version` increment strategy (auto-increment SQL trigger vs explicit service)
- TanStack Query key shape (`['weekly', userId, weekStart]` vs flat)
- Phosphor icon choice per shopping category (Snowflake/Carrot/Package/Wine/Pill — designer call within token system; UI-SPEC §6.5 already locked these)
- Exact 5xx threshold timing in 7-day spike (project owner decides if mid-spike trip OR end-of-spike summary)

### Deferred Ideas (OUT OF SCOPE)

**To Phase 3 (Engagement):**
- Mascot custom (water-droplet o scale-spirit, NON avocado)
- Lottie celebrations weekly streak
- Dashboard KPI con adherence ring (Phase 3 calcola da Phase 2 variant data)
- Push notification lunedì pesata + DST handling

**To Phase 4 (Admin & Hardening):**
- Admin panel per merge gruppi famiglia
- Row-Level Security PostgreSQL defense-in-depth
- Stress test mattina lunedì simultaneo
- Shopping list virtualization se >500 righe

**To Phase 5 (AI):**
- Fuzzy ingredient matching synonym dictionary
- AI shopping suggestions
- Plan editor con AI-assisted variant generation
- Streaming chat AI widget activation

**Out of scope (mai):**
- Mobile native iOS/Android app
- Wearable integration
- Barcode scanner alimenti
- USDA food database
- Sistema billing/subscription

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| WEEK-01 | Vista settimanale `/week` navigabile con week picker | §Standard Stack (date-fns startOfWeek), §Code Examples (WeekPicker + chip-row), UI-SPEC §6.2 |
| WEEK-02 | Per ogni giorno colazione/pranzo/cena/spuntini con macro target | §Architecture Patterns (server aggregator pattern, today_service.py reuse) |
| WEEK-03 | Variant selector per ogni pasto: Opzione A / Opzione B / Pasta speciale | §Code Examples (VariantSelector dropdown), UI-SPEC §6.2 (Trigger pill anatomy) |
| WEEK-04 | Selezioni varianti settimanali persistenti | §Architecture Patterns (PATCH /api/weekly/.../variant + LWW If-Unmodified-Since) |
| WEEK-05 | Endpoint `GET /api/weekly/{week_start}/summary` ritorna riepilogo macro | §Architecture Patterns (summary endpoint reads variants + parsed_json) |
| SHOP-01 | Lista spesa auto-generata da varianti settimana | §Architecture Patterns (ShoppingAggregator service composes parsed_json + variant choices) |
| SHOP-02 | Aggregazione intelligente: ingredienti uguali sommati tra colazione/pranzo/cena | §Code Examples (Italian quantity parser + group-by name+unit) |
| SHOP-03 | Checkbox interattivi con stato persistente (Dexie + sync server) | §Architecture Patterns (ShoppingListState + mutation_queue offline-first) |
| SHOP-04 | Divisione per categoria italiana (5 categorie locked) | §Code Examples (category_mapper keyword fallback dictionary) |
| SHOP-05 | Vista alternativa "lista per giorno" | §Architecture Patterns (ShoppingViewToggle, server returns same payload, client groups) |
| SHOP-06 | Esportazione lista come testo semplice (copia/condividi) | §Code Examples (text export composition pure-frontend) |
| SHOP-07 | Esportazione lista come PDF via WeasyPrint con brand Tailwind tokens | §Code Examples (PdfExporter ABC + WeasyPrintExporter + ReportLabExporter) |
| SHOP-08 | Reset settimanale automatico lunedì 00:00 user IANA tz | §Code Examples (APScheduler AsyncIOScheduler CronTrigger ZoneInfo) |
| FAM-01 | User può appartenere a un gruppo (`Group`) | §Code Examples (Alembic 0001_activate_groups data-only migration) |
| FAM-02 | Cene e pranzi default `visibility=group_shared`; colazione+spuntini `private` | §Architecture Patterns (visibility defaulting in variant_service) |
| FAM-03 | Badge "condiviso con [nome]" per pasti group_shared di altri membri | §Code Examples (SharedBadge + UsersThree icon), UI-SPEC §6.2 |
| FAM-04 | Conflict resolution last-write-wins con `If-Unmodified-Since` | §Code Examples (PATCH header + version compare + 409) |
| FAM-05 | Conflitto 409 → toast UX italiano | §Code Examples (sonner ConflictToast + copy.sync.conflictToast key) |
| FAM-06 | `get_user_with_group_access(target_user_id)` dependency | §Code Examples (FastAPI dependency factory pattern) |
| FAM-07 | `group_id` MAI in JWT — re-look-up da DB | §Architecture Patterns (Pitfall #3 inheritance — group lookup per request) |
| FAM-08 | Negative-authz matrix in CI: 8 endpoints × 5 scenari | §Code Examples (test_family_authz_matrix.py shape) |
| FAM-09 | Polling TanStack Query refetchOnFocus + 30s staleTime | §Architecture Patterns (no WebSocket Phase 2 — convergence test) |
| DEP-06 | WeasyPrint GTK3 Runtime MSI installato + spike validation | §Code Examples (Windows install steps + verification + 7-day spike checklist) |
| UI-01..UI-20 | Cross-cutting WIN REQUISITE | UI-SPEC §1-§5 inherited; Phase 2 §6 components only |

</phase_requirements>

## Standard Stack

### Core (Phase 2 net additions; Phase 1 stack inherited verbatim)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| weasyprint | `^62.x` | HTML+CSS → PDF rendering | Locked Phase 1 STACK.md decision; CSS reuse pays dividends for branded shopping list PDF [VERIFIED: STACK.md L196 + L204-224] |
| reportlab | `^4.x` | Imperative canvas PDF (fallback only) | Activated only if Plan 02-01 GTK3 spike fails 5xx>2% threshold (D-11); kept behind `PdfExporter` ABC [CITED: STACK.md L222 fallback condition] |
| jinja2 | `^3.x` (transitive via FastAPI) | HTML template rendering for `shopping_list.html` | Already pulled by FastAPI; explicit dep makes intent clear [VERIFIED: pyproject.toml] |
| apscheduler | `^3.11` | Async cron jobs for weekly shopping list reset | Standard Python scheduler; AsyncIOScheduler integrates with FastAPI lifespan [VERIFIED: apscheduler.readthedocs.io 3.11.2.post1] |

**Verification:**
```bash
# WeasyPrint (after MSYS2 + GTK3 setup — see §Code Examples)
python -m pip show weasyprint
python -m weasyprint --info        # Authoritative install verification command per official docs

# APScheduler
python -m pip show apscheduler

# ReportLab (fallback)
python -m pip show reportlab
```

**Version verification command for each:**
```bash
uv pip install "weasyprint>=62" "apscheduler>=3.11" "reportlab>=4"
uv pip freeze | grep -iE 'weasyprint|apscheduler|reportlab'
```

### Supporting (already in Phase 1 stack — used unchanged)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `motion` | `^12.38` | VariantSelector dropdown 250ms ease-out-soft, swipe-to-delete shopping row | UI-SPEC §5 |
| `@radix-ui/react-popover` | `^1.1.15` | WeekPicker jump-to-date popover | UI-SPEC §6.2 |
| `@radix-ui/react-dropdown-menu` | `^2.1.16` | VariantSelector + ShareToggleMenu | UI-SPEC §6.2 |
| `@radix-ui/react-tooltip` | `^1.x` (NEW shadcn block) | SharedBadge tooltip on tap | UI-SPEC §6.2 + §14 net-new shadcn block |
| `@radix-ui/react-alert-dialog` | `^1.x` (NEW shadcn block) | Shopping list row delete confirmation | UI-SPEC §6.2 |
| `@radix-ui/react-collapsible` | `^1.x` (NEW shadcn block) | ShoppingCategorySection expand/collapse | UI-SPEC §6.2 |
| `@radix-ui/react-toggle-group` | `^1.x` (NEW shadcn block) | ShoppingViewToggle Per categoria/Per giorno | UI-SPEC §6.2 |
| `dexie` | `^4.4.2` | Schema bump v1 → v2 with `cache_weekly` + `cache_shopping` | Plan 06 mutation_queue invariant: opaque HTTP requests survive bump |
| `date-fns` | `^4.1.0` | `startOfWeek({ weekStartsOn: 1 })`, `format` Italian locale | Already used by Phase 1 |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| WeasyPrint | ReportLab (primary) | Imperative canvas → harder brand consistency, kept as fallback only |
| WeasyPrint | wkhtmltopdf | Project unmaintained + security concerns [CITED: STACK.md L356] |
| WeasyPrint | Browserless/Puppeteer PDF | Adds Node sidecar process to Windows Server install; more brittle than GTK3 |
| APScheduler | Windows Task Scheduler call into FastAPI | Adds OS-level orchestration; APScheduler in-process is simpler for a single-worker NSSM service |
| APScheduler | Celery + Redis | Massively over-scoped for a once-per-week-per-user job for ≤100 users |
| Italian quantity parser (heuristic) | `ingredient-parser-nlp` PyPI | English-trained, no Italian unit support (q.b., pizzico, confezione) [VERIFIED: WebSearch — no Italian-targeted parser exists 2026] |
| Italian quantity parser (heuristic) | LLM provider call | Adds AI dependency to a deterministic data path; conflicts with D-32 "AI widget invariato" |
| BroadcastChannel | localStorage `storage` event | iOS Safari less reliable for cross-tab; BroadcastChannel is the modern primitive when available |
| BroadcastChannel | Service Worker `postMessage` | More plumbing for the same effect; SW already bound to update flow (FND-06) |

**Installation:**
```bash
# Backend (uv)
cd backend
uv add weasyprint reportlab apscheduler

# Frontend (pnpm) — net-new shadcn blocks (UI-SPEC §14 fix flag 4)
cd frontend
pnpm dlx shadcn@latest add popover tooltip alert-dialog collapsible toggle-group
```

**Version verification:** `apscheduler>=3.11` is current as of 2026; `weasyprint>=62` matches Phase 1 STACK.md. ReportLab 4.x is the API surface used by the fallback.

## Architecture Patterns

### System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│ CLIENT (iPhone PWA / desktop browser)                                    │
│                                                                           │
│ User taps variant pill ──► Optimistic UI update (TanStack Query)         │
│                              │                                            │
│                              ▼                                            │
│                     PATCH /api/weekly/{week}/variant                      │
│                     Header: If-Unmodified-Since: <updated_at ISO>        │
│                     ┌─────────────────────────┐                           │
│                     │ navigator.onLine ?      │                           │
│                     └─────────────────────────┘                           │
│                          │ no                │ yes                        │
│                          ▼                   ▼                            │
│                  Dexie mutation_queue   ─► Server                         │
│                  (opaque HTTP req)         │                              │
│                          │                 │                              │
│                  Network resume            │ 200 OK / 409 Conflict        │
│                          │                 │                              │
│                          ▼                 ▼                              │
│                  Replay queued ─────► Update cache + sonner toast         │
└──────────────────────────────────────────────────────────────────────────┘
                                                │
                                                │ HTTPS
                                                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ FastAPI Backend (Uvicorn 1 worker via NSSM, Windows Server 2019)         │
│                                                                           │
│ Routes (api/)                                                             │
│   weekly.py     ─┐                                                        │
│   shopping.py   ─┼──► Services (services/)                                │
│   today.py      ─┘     ├── variant_service.py    (LWW + 409)              │
│   family.py (new) ─────┤── shopping_service.py   (aggregator)             │
│                        ├── ingredient_parser.py  (Italian quantity)       │
│                        ├── category_mapper.py    (keyword fallback)       │
│                        ├── pdf_export.py         (PdfExporter ABC)        │
│                        │     ├── WeasyPrintExporter (primary)             │
│                        │     └── ReportLabExporter  (fallback)            │
│                        └── group_service.py      (cross-user authz)       │
│                                                                           │
│ Lifespan startup ──► AsyncIOScheduler ──► CronTrigger per User            │
│                       (`reset_shopping_lists_at_user_midnight`)           │
│                                                                           │
│ Dependencies (core/deps.py)                                               │
│   get_current_user                                                        │
│   get_user_with_group_access(target_user_id) ◄── re-lookup from DB       │
└──────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ PostgreSQL (canonical truth)                                             │
│   weekly_plan_variants (already in baseline) — version int, updated_at   │
│   shopping_list_state  (already in baseline) — items_json, version       │
│   groups               (already in baseline) — populated by 0001_*.py    │
│   visibility_enum      (already in baseline) — private | group_shared    │
└──────────────────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure (Phase 2 additions only)

```
backend/app/
├── services/
│   ├── variant_service.py        # NEW Phase 2 — LWW + 409
│   ├── shopping_service.py       # NEW Phase 2 — aggregator
│   ├── ingredient_parser.py      # NEW Phase 2 — Italian quantity parser
│   ├── category_mapper.py        # NEW Phase 2 — keyword fallback
│   ├── pdf_export.py             # NEW Phase 2 — ABC + WeasyPrint + ReportLab
│   ├── group_service.py          # NEW Phase 2 — group + cross-user authz
│   └── weekly_service.py         # NEW Phase 2 — summary aggregation
├── api/
│   ├── weekly.py                 # EXTEND (existing 501 stub) — GET week, GET summary, PATCH variant
│   ├── shopping.py               # EXTEND (existing 501 stub) — GET, PATCH check, POST export-pdf
│   ├── family.py                 # NEW Phase 2 — share toggle + group meta
│   └── today.py                  # EXTEND — accept ?user_id= via get_user_with_group_access
├── templates/
│   └── shopping_list.html        # NEW Phase 2 — Jinja2 template for WeasyPrint
├── static/
│   └── fonts/                    # NEW Phase 2 — woff2 sources for PDF embedding
│       ├── plus-jakarta-sans-variable.woff2
│       ├── geist-mono-variable.woff2
│       └── instrument-serif-italic.woff2
├── core/
│   ├── deps.py                   # EXTEND — add get_user_with_group_access
│   └── scheduler.py              # NEW Phase 2 — AsyncIOScheduler factory + lifespan hook
└── main.py                       # EXTEND — lifespan adds scheduler.start() / .shutdown()

backend/alembic/versions/
└── 0001_activate_groups.py       # NEW Phase 2 — data-only migration (D-22)

backend/tests/
├── unit/
│   ├── test_ingredient_parser.py # NEW — evil-corpus Italian quantities
│   ├── test_category_mapper.py   # NEW — keyword fallback table
│   ├── test_variant_service.py   # NEW — LWW unit tests
│   └── test_shopping_service.py  # NEW — aggregation edge cases
├── integration/
│   ├── test_weekly_api.py        # NEW — variant CRUD + 409 conflict
│   ├── test_shopping_api.py      # NEW — list + checkbox + export
│   ├── test_family_api.py        # NEW — share toggle + group + cross-user
│   ├── test_family_authz_matrix.py # NEW — 8×5=40 negative authz tests (FAM-08)
│   ├── test_pdf_export.py        # NEW — WeasyPrint smoke + accent verification
│   ├── test_alembic_0001.py      # NEW — migration idempotence + backfill correctness
│   └── test_scheduler.py         # NEW — APScheduler IANA tz + DST boundary

frontend/src/
├── pages/
│   ├── Week.tsx                  # NEW — `/settimana` route
│   └── Shopping.tsx              # NEW — `/spesa` route
├── components/
│   ├── week/                     # NEW — WeekPicker, WeeklyMacroRing, DayCompletionStrip
│   ├── shopping/                 # NEW — ShoppingCategorySection, ShoppingItemRow, ShoppingViewToggle
│   ├── family/                   # NEW — SharedBadge, ShareToggleMenu, ConflictToast
│   └── today/MealCard.tsx        # EXTEND — Condiviso badge slot + ⋯ menu
├── services/
│   ├── weekly.ts                 # NEW — TanStack Query hooks
│   ├── shopping.ts               # NEW — TanStack Query hooks + Dexie cache
│   └── family.ts                 # NEW — share toggle mutation
├── db/
│   └── dexie.ts                  # EXTEND — v2 schema with cache_weekly + cache_shopping
└── lib/
    ├── ifUnmodifiedSince.ts      # NEW — header builder + 409 detector
    └── broadcastChannel.ts       # NEW — feature detect + fallback
```

### Pattern 1: WeasyPrint Setup on Windows Server 2019

**What:** Install GTK3/Pango runtime + WeasyPrint Python package on Windows Server 2019 production host.
**When to use:** Plan 02-01 spike + production deploy (DEPLOY.md addendum).

**Step 1 — Install MSYS2 + Pango (recommended path per official docs):**
```powershell
# Run as Administrator on Windows Server 2019
# 1. Download MSYS2 from https://www.msys2.org/ (one-time, ~150 MB)
# 2. Run installer with default options (installs to C:\msys64)
# 3. Open "MSYS2 MINGW64" shell from Start menu
pacman -Syu                                        # Update package DB; close shell when prompted
pacman -S mingw-w64-x86_64-pango                   # Install Pango (pulls Cairo, GLib, GDK-PixBuf, GObject)
exit
```

**Step 2 — Add MSYS2 to PATH (system-wide for NSSM service):**
```powershell
# Append C:\msys64\mingw64\bin to PATH (System variables, NOT User)
# This is what loads gobject-2.0-0.dll, libpango-1.0-0.dll, libcairo-2.dll at runtime.
# NSSM service inherits System PATH at install time — set BEFORE `nssm install` if not done.
[Environment]::SetEnvironmentVariable(
  "Path",
  $env:Path + ";C:\msys64\mingw64\bin",
  [EnvironmentVariableTarget]::Machine
)
# Restart NSSM service to pick up new PATH
nssm restart WellnessBuddyAPI
```

**Step 3 — Install WeasyPrint in backend venv:**
```powershell
cd D:\Develop\AI\WellnessBuddy\backend
.\venv\Scripts\Activate.ps1
uv add weasyprint
```

**Step 4 — Verify (authoritative test command per WeasyPrint docs):**
```powershell
python -m weasyprint --info
# Expected output:
#   WeasyPrint version: 62.x.x
#   Python: 3.12.x
#   Pango: 1.x.x
#   Cairo: 1.x.x
# If you see "OSError: cannot load library 'gobject-2.0-0'" → PATH not propagated.
```

**Step 5 — Smoke test PDF generation:**
```powershell
python -c "from weasyprint import HTML; HTML(string='<h1>Test à è ì ò ù</h1>').write_pdf('test.pdf')"
# Open test.pdf in Adobe Reader. Italian accents must render. If they don't, font fallback failed —
# embed woff2 fonts inline (D-13).
```

**Common Windows-specific failures (from WebSearch + community gist):**

| Symptom | Cause | Fix |
|---------|-------|-----|
| `OSError: cannot load library 'gobject-2.0-0'` | PATH does not include `C:\msys64\mingw64\bin` | Add to System PATH, restart NSSM service |
| `cannot load library 'libpango-1.0-0'` | Pango not installed | `pacman -S mingw-w64-x86_64-pango` in MSYS2 MINGW64 |
| Italian accents render as `?` or boxes | Font fallback failed; OS lacks fonts WeasyPrint expects | Embed woff2 base64 inline in `@font-face` (see Pattern 9) |
| Antivirus quarantines `weasyprint.exe` | Known false positive (per official docs) | Whitelist in Defender; report to AV vendor |
| 32-bit Python | GTK3 runtime is 64-bit only | Use Python 3.12 64-bit (verify `python -c "import platform; print(platform.architecture())"`) |
| Service runs but `--info` works in shell | NSSM AppDirectory not set or PATH not at service level | Set NSSM AppDirectory + restart service |

**Plan 02-01 GTK3 spike checklist (7 days, written into `02-01-GTK3-SPIKE.md`):**

```markdown
## GTK3 WeasyPrint 7-Day Spike

| Check | Pass criterion | Cadence |
|-------|----------------|---------|
| `python -m weasyprint --info` | Returns version info | Day 0 |
| 50 sample PDFs generated locally | All open in Adobe Reader, accents correct | Day 0 |
| Endpoint `POST /api/shopping/{week}/export-pdf` | Returns 200 + valid PDF byte stream | Day 0 |
| iPhone Safari opens PDF | Renders, accents intact | Day 0 |
| Mail.app preview | Renders, accents intact | Day 0 |
| 5xx rate during 7-day window | <2% (D-11 threshold) | Continuous (logging) |
| NSSM service PATH stable through reboot | `--info` survives reboot | Day 1 + Day 4 |
| Memory leak check (continuous PDF gen) | RSS stable over 100 PDFs | Day 3 |
| Cold-start time (post-reboot first PDF) | <10s | Day 1 |
| Pango version pinned (no auto-update breakage) | `pacman -Q mingw-w64-x86_64-pango` matches Day 0 | Day 7 |

**Verdict:**
- ✅ PASS → lock WeasyPrint, document install in DEPLOY.md
- ❌ FAIL (any check) → activate ReportLab branch via `PdfExporter` ABC; spike report records reason
```

### Pattern 2: PdfExporter ABC + WeasyPrintExporter + ReportLabExporter (Fallback)

**What:** Strategy interface that hides the GTK3 dependency from `shopping_service`. Spike outcome flips the active implementation via env var.

```python
# backend/app/services/pdf_export.py
"""PDF export ABC + WeasyPrint primary + ReportLab fallback (D-11..D-14).

The `PdfExporter` ABC isolates the rendering backend from `shopping_service`.
Plan 02-01 spike outcome → `PDF_BACKEND=weasyprint` (default) or `PDF_BACKEND=reportlab`.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from app.core.config import settings


class PdfExporter(ABC):
    """Renders a structured shopping list payload to PDF bytes."""

    @abstractmethod
    async def render_shopping_list(
        self,
        *,
        week_start: str,           # YYYY-MM-DD
        week_start_long_it: str,   # "5 maggio 2026"
        domain: str,               # "wellness-buddy.epartner.it" — footer
        categories: list[dict[str, Any]],  # [{name, items: [{name, quantity_it}]}]
    ) -> bytes:
        """Return PDF bytes. Caller streams to client via FileResponse."""


class WeasyPrintExporter(PdfExporter):
    """Primary backend (D-11 lock). Renders Jinja2 template with embedded woff2 fonts."""

    def __init__(self, template_dir: Path) -> None:
        # Lazy-import WeasyPrint so test environments without GTK3 can still import this module.
        from jinja2 import Environment, FileSystemLoader
        self._env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)

    async def render_shopping_list(
        self, *, week_start, week_start_long_it, domain, categories,
    ) -> bytes:
        from weasyprint import HTML  # Lazy import — keeps test envs without GTK3 healthy
        template = self._env.get_template("shopping_list.html")
        html_str = template.render(
            week_start=week_start,
            week_start_long_it=week_start_long_it,
            domain=domain,
            categories=categories,
        )
        # base_url required so @font-face url(file://...) resolves; with woff2 base64 inline
        # this is a defensive setting (no external resources).
        return HTML(string=html_str, base_url=str(Path(__file__).parent / "../templates")).write_pdf()


class ReportLabExporter(PdfExporter):
    """Fallback backend (D-14). Activated only if Plan 02-01 spike fails."""

    async def render_shopping_list(
        self, *, week_start, week_start_long_it, domain, categories,
    ) -> bytes:
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=20*2.83, bottomMargin=20*2.83)
        styles = getSampleStyleSheet()
        flow: list = [
            Paragraph(f"<b>Lista spesa</b>", styles["Title"]),
            Paragraph(f"settimana del {week_start_long_it}", styles["Italic"]),
            Spacer(1, 12),
        ]
        for cat in categories:
            flow.append(Paragraph(f"<b>{cat['name']}</b>", styles["Heading2"]))
            for item in cat["items"]:
                flow.append(Paragraph(f"☐  {item['name']} — {item['quantity_it']}", styles["Normal"]))
            flow.append(Spacer(1, 12))
        doc.build(flow)
        return buf.getvalue()


def get_pdf_exporter() -> PdfExporter:
    """FastAPI Depends() factory. Returns active backend per env."""
    backend = (settings.PDF_BACKEND or "weasyprint").lower()
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    if backend == "reportlab":
        return ReportLabExporter()
    return WeasyPrintExporter(template_dir=template_dir)
```

**When to use:** SHOP-07 endpoint composes `categories` from `shopping_service.aggregate_for_week()` and calls `exporter.render_shopping_list(...)`. Endpoint signature:

```python
# backend/app/api/shopping.py
@router.post("/{week_start}/export-pdf")
async def export_pdf(
    week_start: str,
    user: User = Depends(get_current_user),
    exporter: PdfExporter = Depends(get_pdf_exporter),
    session: AsyncSession = Depends(get_session),
) -> Response:
    payload = await shopping_service.build_pdf_payload(session, user_id=user.id, week_start=week_start)
    pdf_bytes = await exporter.render_shopping_list(**payload)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="spesa-{week_start}.pdf"'},
    )
```

### Pattern 3: Italian Quantity Parser Heuristic Dictionary

**What:** Tightly-scoped regex + lookup parser tuned to Stefano+Marta MD plan corpus (and synthetic fixtures `marta_synthetic.md` / `stefano_synthetic.md`). NOT NLP. NOT fuzzy. NOT LLM.

```python
# backend/app/services/ingredient_parser.py
"""Italian recipe quantity parser (D-05).

Inputs are short ingredient strings from MD plans (e.g. `Yogurt greco 200g`,
`mela e 20g noci`, `pasta integrale 80g + pomodoro + olio EVO q.b.`).
Output is a list of `(amount: float|None, unit: str|None, name: str)` tuples.

Strategy (heuristic, deterministic, no NLP):
1. Normalize: NFC + lowercase + strip + collapse whitespace.
2. Split candidate boundaries on ` + ` or `,` (one row may carry multiple ingredients;
   the caller then explodes one row → many).
3. For each candidate: scan with a prioritized regex set (longest unit first to
   avoid `g` matching inside `gnocchi`).
4. Words remaining after amount/unit removal = ingredient name.
5. Special tokens: `q.b.`, `q.b`, `qb`, `quanto basta` → unit = `qb`, amount = None.
6. Special tokens: `un`, `una`, `uno` BEFORE a noun → amount = 1, unit inferred from noun
   (`un pizzico` → (1, 'pizzico'), `una manciata` → (1, 'manciata')).

Out of scope for Phase 2 (D-06):
- Fuzzy ingredient matching ("pomodorini" ≠ "pomodori").
- Synonym dictionary (Phase 5 AI).
- Cross-language unit conversion (g ↔ kg ↔ oz).
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

# Order matters: longest first, otherwise `g` swallows `gr` swallows `grammi`.
_UNITS_LONG_FIRST = (
    "grammi", "gr", "kg", "g",
    "ml", "cl", "litro", "litri", "l",
    "cucchiai", "cucchiaio", "cucchiaini", "cucchiaino",
    "tazza", "tazze",
    "pizzico", "pizzichi",
    "manciata", "manciate",
    "fetta", "fette",
    "spicchio", "spicchi",
    "mazzo", "mazzi",
    "confezione", "confezioni",
    "bustina", "bustine",
    "lattina", "lattine",
    "barattolo", "barattoli",
    "pezzo", "pezzi",
    "foglia", "foglie",
)

_UNIT_RE = re.compile(
    r"(?P<amount>\d+(?:[.,]\d+)?)\s*(?P<unit>" + "|".join(_UNITS_LONG_FIRST) + r")\b",
    flags=re.IGNORECASE,
)
_QB_RE = re.compile(r"\bq\.?\s?b\.?\b|\bquanto\s+basta\b", flags=re.IGNORECASE)
_UN_RE = re.compile(
    r"\b(?:un|una|uno)\s+(?P<unit>pizzico|manciata|fetta|spicchio|mazzo|cucchiaio|cucchiaino)\b",
    flags=re.IGNORECASE,
)
_NUMERIC_PREFIX_RE = re.compile(r"^\s*(?P<amount>\d+(?:[.,]\d+)?)\s+(?P<rest>.+)$")


@dataclass(frozen=True)
class ParsedIngredient:
    name: str           # canonical lowercase name, NFC normalized
    amount: float | None
    unit: str | None    # None for `qb` left as-is; "qb" for quanto basta


def normalize(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s


def parse(line: str) -> list[ParsedIngredient]:
    """Parse one ingredient line into one-or-more (amount, unit, name) tuples."""
    norm = normalize(line)

    # Split candidates on " + " or "," (handles `pasta 80g + pomodoro + olio q.b.`)
    parts = [p.strip(" -*•") for p in re.split(r"\s*\+\s*|\s*,\s*", norm) if p.strip(" -*•")]
    out: list[ParsedIngredient] = []

    for part in parts:
        out.append(_parse_single(part))
    return out


def _parse_single(part: str) -> ParsedIngredient:
    # 1. quanto basta — explicit "qb" sentinel
    if _QB_RE.search(part):
        name = _QB_RE.sub("", part).strip(" -*•")
        return ParsedIngredient(name=name, amount=None, unit="qb")

    # 2. amount + unit (e.g. "200g", "1 confezione", "2 cucchiai")
    m = _UNIT_RE.search(part)
    if m:
        amount = float(m.group("amount").replace(",", "."))
        unit = _normalize_unit(m.group("unit"))
        name = (part[: m.start()] + part[m.end() :]).strip(" -*•")
        return ParsedIngredient(name=name, amount=amount, unit=unit)

    # 3. "un pizzico", "una manciata" (no digit, "un/una/uno" + noun)
    m = _UN_RE.search(part)
    if m:
        unit = _normalize_unit(m.group("unit"))
        name = _UN_RE.sub("", part).strip(" -*•")
        return ParsedIngredient(name=name, amount=1.0, unit=unit)

    # 4. Bare numeric prefix without unit (rare but seen in plans: "2 mele")
    m = _NUMERIC_PREFIX_RE.match(part)
    if m:
        return ParsedIngredient(
            name=m.group("rest").strip(" -*•"),
            amount=float(m.group("amount").replace(",", ".")),
            unit=None,
        )

    # 5. No quantity detected — return as plain name
    return ParsedIngredient(name=part.strip(" -*•"), amount=None, unit=None)


_UNIT_CANON = {
    "grammi": "g", "gr": "g", "g": "g",
    "kg": "kg",
    "litro": "l", "litri": "l", "l": "l",
    "ml": "ml", "cl": "cl",
    "cucchiaio": "cucchiai", "cucchiai": "cucchiai",
    "cucchiaino": "cucchiaini", "cucchiaini": "cucchiaini",
    "tazza": "tazze", "tazze": "tazze",
    "pizzico": "pizzico", "pizzichi": "pizzico",
    "manciata": "manciata", "manciate": "manciata",
    "fetta": "fette", "fette": "fette",
    "spicchio": "spicchi", "spicchi": "spicchi",
    "mazzo": "mazzi", "mazzi": "mazzi",
    "confezione": "confezione", "confezioni": "confezione",
    "bustina": "bustine", "bustine": "bustine",
    "lattina": "lattine", "lattine": "lattine",
    "barattolo": "barattoli", "barattoli": "barattoli",
    "pezzo": "pezzi", "pezzi": "pezzi",
    "foglia": "foglie", "foglie": "foglie",
}


def _normalize_unit(raw: str) -> str:
    return _UNIT_CANON.get(raw.lower(), raw.lower())
```

**Evil-corpus seed (must pass — derived from Marta+Stefano synthetic plans):**

| Input line | Expected output |
|------------|-----------------|
| `Yogurt greco 200g + frutta secca 30g + miele 10g` | `[(200, g, yogurt greco), (30, g, frutta secca), (10, g, miele)]` |
| `Pasta integrale 80g + pomodoro + olio EVO` | `[(80, g, pasta integrale), (None, None, pomodoro), (None, None, olio evo)]` |
| `Avena 50g + mirtilli + 1 uovo` | `[(50, g, avena), (None, None, mirtilli), (1, None, uovo)]` |
| `Pesce bianco 150g + zucchine` | `[(150, g, pesce bianco), (None, None, zucchine)]` |
| `Mela + 20g noci` | `[(None, None, mela), (20, g, noci)]` |
| `Olio EVO q.b.` | `[(None, qb, olio evo)]` |
| `Sale q.b.` | `[(None, qb, sale)]` |
| `Un pizzico di sale` | `[(1, pizzico, di sale)]` |
| `Una manciata di basilico` | `[(1, manciata, di basilico)]` |
| `2 cucchiai di olio` | `[(2, cucchiai, di olio)]` |
| `1 confezione di pasta` | `[(1, confezione, di pasta)]` |
| `1,5 kg pomodori` | `[(1.5, kg, pomodori)]` |
| `300 ml latte` | `[(300, ml, latte)]` |
| `Vitamina D3: 1000 UI` | `[(1000, None, vitamina d3 ui)]` (UI not in unit table — falls through) |
| `Magnesio: 300mg sera` | `[(None, None, magnesio 300mg sera)]` (mg not in unit table — Phase 2 leaves as-is) |

[ASSUMED] The `UI` unit (international units) and `mg` may need future entries when Stefano's real supplement plan is uploaded — Plan 02-04 should run real plans through parser and add to `_UNITS_LONG_FIRST` if found.

### Pattern 4: WeeklyPlanVariant LWW + If-Unmodified-Since Header

**What:** Optimistic concurrency via HTTP precondition header. Server-side compare against `updated_at TIMESTAMPTZ`. Mismatch → 409 with conflict info.

```python
# backend/app/services/variant_service.py
"""WeeklyPlanVariant CRUD + LWW conflict resolution (D-17, FAM-04).

Pattern: client sends `If-Unmodified-Since: <updated_at ISO>` header derived from
the version it last fetched. Server compares to current row.updated_at:
  - match (or row not yet existing): proceed; bump version + updated_at via SQLAlchemy default.
  - mismatch: raise AppException(409, ..., code="version_conflict", conflicting_user="Marta").

The 409 response carries `conflicting_user` so the client toast can name the partner
(D-17: `copy.sync.conflictToast: "Aggiornato da {nome}. Ricarica per vedere l'ultima versione."`).
"""
from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.user import User
from app.models.variant import Visibility, WeeklyPlanVariant

_MSG_CONFLICT = "Aggiornato da {nome}. Ricarica per vedere l'ultima versione."


async def upsert_variant(
    session: AsyncSession,
    *,
    user: User,
    plan_id: UUID,
    week_start: date,
    day_of_week: int,
    meal_type: str,
    variant_key: str,
    visibility: Visibility | None = None,
    if_unmodified_since: datetime | None = None,
) -> WeeklyPlanVariant:
    """Create or update a WeeklyPlanVariant with LWW conflict detection.

    `if_unmodified_since` is parsed from `If-Unmodified-Since` header by the API layer
    (RFC 7232 HTTP-date OR Python ISO-8601 — the Phase 2 client sends ISO-8601).
    """
    row = (
        await session.scalars(
            select(WeeklyPlanVariant).where(
                WeeklyPlanVariant.user_id == user.id,
                WeeklyPlanVariant.week_start == week_start,
                WeeklyPlanVariant.day_of_week == day_of_week,
                WeeklyPlanVariant.meal_type == meal_type,
            )
        )
    ).first()

    # Conflict detection — only when row exists AND client sent a precondition.
    if row is not None and if_unmodified_since is not None:
        # Compare with second-precision tolerance: PostgreSQL TIMESTAMPTZ stores microseconds,
        # but client serialization may round. Use >= rather than > to allow exact equality.
        if row.updated_at > if_unmodified_since:
            # Look up who made the conflicting edit so the client toast can name them.
            partner = await _conflict_partner_name(session, row=row, current_user=user)
            raise AppException(
                409,
                _MSG_CONFLICT.format(nome=partner or "un familiare"),
                "version_conflict",
                extra={"conflicting_user": partner},
            )

    if row is None:
        # Default visibility per FAM-02: pranzi+cene group_shared, others private.
        if visibility is None:
            visibility = (
                Visibility.GROUP_SHARED
                if meal_type in ("lunch", "dinner")
                else Visibility.PRIVATE
            )
        row = WeeklyPlanVariant(
            user_id=user.id,
            plan_id=plan_id,
            week_start=week_start,
            day_of_week=day_of_week,
            meal_type=meal_type,
            variant_key=variant_key,
            visibility=visibility,
            version=1,
        )
        session.add(row)
    else:
        row.variant_key = variant_key
        if visibility is not None:
            row.visibility = visibility
        row.version += 1  # SQLAlchemy `onupdate` could automate, but explicit reads better

    await session.commit()
    await session.refresh(row)
    return row


async def _conflict_partner_name(
    session: AsyncSession, *, row: WeeklyPlanVariant, current_user: User
) -> str | None:
    """Return the username/full_name of the user who last edited this row, if not us."""
    if row.user_id == current_user.id:
        # Same user — they're racing themselves (e.g. two tabs). No "partner" to name.
        return None
    other = (await session.scalars(select(User).where(User.id == row.user_id))).first()
    return other.username if other else None
```

**API layer wiring:**

```python
# backend/app/api/weekly.py
from datetime import datetime
from fastapi import Header

@router.patch("/{week_start}/variant")
async def patch_variant(
    week_start: str,
    payload: PatchVariantPayload,
    if_unmodified_since: str | None = Header(default=None, alias="If-Unmodified-Since"),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> VariantResponse:
    parsed_ius = datetime.fromisoformat(if_unmodified_since) if if_unmodified_since else None
    row = await variant_service.upsert_variant(
        session, user=user, plan_id=payload.plan_id, week_start=date.fromisoformat(week_start),
        day_of_week=payload.day_of_week, meal_type=payload.meal_type,
        variant_key=payload.variant_key, visibility=payload.visibility,
        if_unmodified_since=parsed_ius,
    )
    return VariantResponse.model_validate(row)
```

**Frontend hook:**

```typescript
// frontend/src/services/weekly.ts
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

export function useSetVariant(weekStart: string, userId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: SetVariantPayload & { ifUnmodifiedSince?: string }) => {
      return apiClient.request({
        url: `/api/weekly/${weekStart}/variant`,
        method: 'PATCH',
        body: payload,
        headers: payload.ifUnmodifiedSince
          ? { 'If-Unmodified-Since': payload.ifUnmodifiedSince }
          : {},
      });
    },
    onMutate: async (payload) => {
      // Optimistic update — TanStack Query rollback on 409
      await qc.cancelQueries({ queryKey: ['weekly', userId, weekStart] });
      const prev = qc.getQueryData(['weekly', userId, weekStart]);
      qc.setQueryData(['weekly', userId, weekStart], (old: any) =>
        applyVariantOptimistic(old, payload),
      );
      return { prev };
    },
    onError: (err: any, _payload, ctx) => {
      qc.setQueryData(['weekly', userId, weekStart], ctx?.prev);
      if (err?.code === 'version_conflict') {
        toast.info(copy.sync.conflictToast.replace('{nome}', err.conflicting_user ?? 'un familiare'), {
          action: { label: 'Ricarica', onClick: () => qc.invalidateQueries({ queryKey: ['weekly', userId, weekStart] }) },
        });
      }
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['weekly', userId, weekStart] }),
  });
}
```

**[ASSUMED]** TanStack Query optimistic-update pattern works identically for offline mutations — the mutation queue replay in Plan 06 fires `useSetVariant` mutations on reconnect. Plan 02-02 should verify by toggling airplane mode mid-variant-change.

### Pattern 5: APScheduler Per-User Shopping List Reset Cron

**What:** AsyncIOScheduler installed at FastAPI lifespan startup; one `CronTrigger` per user with timezone bound to `user.timezone` IANA name.

```python
# backend/app/core/scheduler.py
"""APScheduler async scheduler factory + lifespan integration (D-09, SHOP-08).

Usage:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        scheduler = AsyncIOScheduler()
        await register_user_jobs(scheduler, session_factory=app.state.session_factory)
        scheduler.start()
        app.state.scheduler = scheduler
        yield
        scheduler.shutdown(wait=False)

DST correctness: APScheduler computes next-fire each run via `zoneinfo` (Python 3.12 native).
NEVER use additive `timedelta(weeks=1)` — DST boundaries break it (Pitfall #7 inherited).
"""
from __future__ import annotations

from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.user import User
from app.services.shopping_service import reset_shopping_list_for_user


async def register_user_jobs(
    scheduler: AsyncIOScheduler,
    *,
    session_factory: async_sessionmaker,
) -> None:
    """Register one Monday 00:00 reset job per user, in user's IANA tz."""
    async with session_factory() as session:
        users = (await session.scalars(select(User))).all()
    for user in users:
        scheduler.add_job(
            _run_user_reset,
            trigger=CronTrigger(
                day_of_week="mon",
                hour=0,
                minute=0,
                timezone=ZoneInfo(user.timezone),  # e.g. "Europe/Rome"
            ),
            args=(str(user.id),),
            id=f"shopping_reset_{user.id}",
            replace_existing=True,
        )


async def _run_user_reset(user_id: str) -> None:
    """Job body — opens its own session because APScheduler runs outside request scope."""
    from app.core.database import get_session_factory
    factory = get_session_factory()
    async with factory() as session:
        await reset_shopping_list_for_user(session, user_id=user_id)
```

**Test pattern (DST-correctness):**

```python
# backend/tests/integration/test_scheduler.py
"""Test that APScheduler computes correct next-fire across DST boundaries (Pitfall #7).

Italy DST:
- Winter → Summer (last Sunday of March): 02:00 → 03:00 jump forward
- Summer → Winter (last Sunday of October): 03:00 → 02:00 jump back
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.triggers.cron import CronTrigger


def test_dst_spring_forward_2026():
    """2026 last-Sunday-of-March = March 29 — clocks jump 02:00 → 03:00."""
    rome = ZoneInfo("Europe/Rome")
    trig = CronTrigger(day_of_week="mon", hour=0, minute=0, timezone=rome)
    # Sat 28 Mar 23:59 Rome — pre-DST
    fire = trig.get_next_fire_time(None, datetime(2026, 3, 28, 23, 59, tzinfo=rome))
    # Should fire Mon 30 Mar 00:00 Rome (post-DST), NOT Sun 29 + offset arithmetic.
    assert fire.year == 2026 and fire.month == 3 and fire.day == 30
    assert fire.hour == 0 and fire.minute == 0


def test_dst_fall_back_2026():
    """2026 last-Sunday-of-October = October 25 — clocks fall back 03:00 → 02:00."""
    rome = ZoneInfo("Europe/Rome")
    trig = CronTrigger(day_of_week="mon", hour=0, minute=0, timezone=rome)
    fire = trig.get_next_fire_time(None, datetime(2026, 10, 24, 23, 59, tzinfo=rome))
    assert fire.year == 2026 and fire.month == 10 and fire.day == 26
    assert fire.hour == 0 and fire.minute == 0
```

**[VERIFIED]** APScheduler's `CronTrigger` with `timezone=ZoneInfo(...)` is the documented DST-correct pattern. The library explicitly warns against time zones that DO observe DST only when scheduling AT 02:00-03:00 boundary (the ambiguous hour). Lunedì 00:00 is unambiguous on both spring-forward and fall-back days [CITED: apscheduler.readthedocs.io 3.11.2.post1 — User guide].

### Pattern 6: Alembic 0001_activate_groups.py Idempotent Data Migration

**What:** Per-user backfill: create one `Group(name=user.full_name + " · household")` per User and assign `user.group_id`. Idempotent — safe to re-run.

```python
# backend/alembic/versions/0001_activate_groups.py
"""Activate groups for all existing users (D-22, D-23).

Phase 1 baseline 0000_baseline.py created the `groups` table + `users.group_id` FK.
Phase 2 backfills: for each User without a group_id, create a personal household group
and link them. Idempotent — skip users that already have a group_id.

Revision ID: 0001
Revises: 0000_baseline
Create Date: 2026-05-XX
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = "0000_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Backfill personal household group for every user without one."""
    bind = op.get_bind()
    # Reflective SQL — DOES NOT import app.models so the migration stays stable
    # if the User/Group ORM shape evolves later.
    users_t = sa.table(
        "users",
        sa.column("id", sa.UUID()),
        sa.column("username", sa.String()),
        sa.column("group_id", sa.UUID()),
    )
    groups_t = sa.table(
        "groups",
        sa.column("id", sa.UUID()),
        sa.column("name", sa.String()),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )

    # Idempotency: only operate on users without a group.
    rows = bind.execute(
        sa.select(users_t.c.id, users_t.c.username).where(users_t.c.group_id.is_(None))
    ).fetchall()

    if not rows:
        return  # All users already have a group — migration is already applied.

    now = datetime.now(timezone.utc)
    for user_id, username in rows:
        new_group_id = uuid.uuid4()
        bind.execute(
            groups_t.insert().values(
                id=new_group_id,
                name=f"{username} · household",
                created_at=now,
            )
        )
        bind.execute(
            users_t.update()
            .where(users_t.c.id == user_id)
            .values(group_id=new_group_id)
        )


def downgrade() -> None:
    """Reverse: null out users.group_id, delete personal households.

    NOTE: This is destructive — only safe if no shared resources have been written
    yet (Phase 2 is the first phase that uses group_id at all).
    """
    bind = op.get_bind()
    users_t = sa.table("users", sa.column("group_id", sa.UUID()))
    groups_t = sa.table("groups", sa.column("name", sa.String()))
    # Null out user.group_id pointers
    bind.execute(users_t.update().values(group_id=None))
    # Delete only " · household" personal groups (manually-created groups untouched)
    bind.execute(groups_t.delete().where(groups_t.c.name.like("% · household")))
```

**Idempotence test:**

```python
# backend/tests/integration/test_alembic_0001.py
async def test_0001_idempotent(alembic_engine, db_session):
    """Running 0001 twice produces the same outcome as once."""
    from alembic.config import Config
    from alembic import command

    cfg = Config("alembic.ini")
    command.upgrade(cfg, "0001")
    first = (await db_session.execute(sa.text("SELECT user_id, group_id FROM users"))).all()
    command.upgrade(cfg, "0001")  # Re-run — should be no-op
    second = (await db_session.execute(sa.text("SELECT user_id, group_id FROM users"))).all()
    assert first == second  # No new groups created, no group_ids changed
```

### Pattern 7: Negative-Authz Test Matrix (FAM-08)

**What:** 8 endpoints × 5 scenarios = 40 tests in `test_family_authz_matrix.py`. Pattern extends Plan 04 `test_plans_api.py::test_activate_other_user_plan_403` and Plan 07 weight/workout cross-user 404 (V13).

**Endpoint list (8):**
1. `GET /api/today?user_id={target}`
2. `GET /api/weekly/{week_start}?user_id={target}`
3. `GET /api/weekly/{week_start}/summary?user_id={target}`
4. `PATCH /api/weekly/{week_start}/variant` (mutating other user's variant)
5. `GET /api/shopping/{week_start}?user_id={target}`
6. `PATCH /api/shopping/{week_start}/check`
7. `POST /api/shopping/{week_start}/export-pdf?user_id={target}`
8. `PATCH /api/family/share/{meal_id}` (changing visibility)

**Scenario matrix (5):**

| ID | Scenario | Expected response | Code |
|----|----------|-------------------|------|
| S1 | own data | 200 | (success) |
| S2 | shared-via-group (group_shared resource of partner in same group) | 200 | (success) |
| S3 | private-other-user (resource of partner with `visibility=private`) | 404 | `not_found` (V13 info-disclosure) |
| S4 | non-family (resource of user in different group) | 404 | `not_found` |
| S5 | ex-member (formerly in group, now removed; old JWT still valid) | 404 | `not_found` |

**Test structure:**

```python
# backend/tests/integration/test_family_authz_matrix.py
"""Negative authz matrix: 8 endpoints × 5 scenarios = 40 tests (FAM-08, D-21).

Pattern: parametrize with `(endpoint_id, scenario_id, expected_status, expected_code)`.
Fixtures provide:
- `stefano` (in group_brunelli)
- `marta` (in group_brunelli — shared)
- `outsider` (in group_other)
- `ex_member` (was in group_brunelli, now removed; JWT still valid for 15 min)
- meal/variant/shopping rows pre-seeded for each owner.

Test body invokes endpoint with current_user=stefano, target_user_id varying per scenario.
"""
import pytest

ENDPOINTS = [
    ("GET", "/api/today", "today", "GET"),
    ("GET", "/api/weekly/{week_start}", "week", "GET"),
    ("GET", "/api/weekly/{week_start}/summary", "summary", "GET"),
    ("PATCH", "/api/weekly/{week_start}/variant", "variant", "PATCH"),
    ("GET", "/api/shopping/{week_start}", "shopping", "GET"),
    ("PATCH", "/api/shopping/{week_start}/check", "check", "PATCH"),
    ("POST", "/api/shopping/{week_start}/export-pdf", "pdf", "POST"),
    ("PATCH", "/api/family/share/{meal_id}", "share", "PATCH"),
]
SCENARIOS = ["own", "shared", "private_other", "non_family", "ex_member"]
EXPECTED = {
    "own": (200, None),
    "shared": (200, None),
    "private_other": (404, "not_found"),
    "non_family": (404, "not_found"),
    "ex_member": (404, "not_found"),
}


@pytest.mark.parametrize("method,url_template,name,_", ENDPOINTS)
@pytest.mark.parametrize("scenario", SCENARIOS)
async def test_authz_matrix(
    method, url_template, name, _, scenario,
    async_client, stefano_token, marta_id, outsider_id, ex_member_id,
):
    target_user_id = {
        "own": None,  # endpoint scoped to current_user
        "shared": marta_id,
        "private_other": marta_id,  # but on a private resource
        "non_family": outsider_id,
        "ex_member": ex_member_id,
    }[scenario]

    expected_status, expected_code = EXPECTED[scenario]

    url = url_template.format(week_start="2026-05-04", meal_id="...")
    if target_user_id:
        url += f"?user_id={target_user_id}"

    r = await async_client.request(
        method, url, headers={"Authorization": f"Bearer {stefano_token}"},
        json={} if method in ("PATCH", "POST") else None,
    )
    assert r.status_code == expected_status, f"{name}/{scenario}: got {r.status_code} {r.text}"
    if expected_code:
        assert r.json()["code"] == expected_code, f"{name}/{scenario}: code"
```

**Why 404 (not 403) for cross-user reads:** V13 info-disclosure mitigation, inherited from Phase 1 (`backend/app/services/weight_service.py` L104-105 comment: *"V13 — same envelope as truly-missing; never reveal cross-user existence"*). 403 leaks the existence of the resource; 404 makes private-other-user indistinguishable from non-existent.

### Pattern 8: WeasyPrint Italian Font Embedding (woff2 base64 inline)

**What:** Embed Plus Jakarta Sans + Geist Mono + Instrument Serif as `data:font/woff2;base64,...` inside `<style>` of `shopping_list.html`. Guarantees accents render regardless of OS-installed fonts at PDF gen time.

**Why inline, not URL:**
- WeasyPrint `HTML(string=...).write_pdf()` runs at API request time. Network access from Windows Server to e.g. fonts.googleapis.com is policy-gated and adds latency.
- `base_url` for `file://` URLs requires correct path on every OS — fragile.
- Inline base64 = self-contained PDF generation, deterministic accents.

**Build-time helper:**

```python
# backend/app/templates/_build_inline_fonts.py
"""One-off helper to compute base64 strings for woff2 embedding into shopping_list.html.

Run once during Plan 02-05 setup; output goes into the template's @font-face blocks.
"""
import base64
from pathlib import Path

FONT_DIR = Path(__file__).resolve().parent.parent / "static" / "fonts"

for woff2 in FONT_DIR.glob("*.woff2"):
    encoded = base64.b64encode(woff2.read_bytes()).decode("ascii")
    print(f"--- {woff2.name} ---")
    print(f"data:font/woff2;base64,{encoded[:80]}...({len(encoded)} bytes total)")
```

**Template fragment:**

```html
<!-- backend/app/templates/shopping_list.html -->
<style>
  @font-face {
    font-family: "Plus Jakarta Sans";
    src: url(data:font/woff2;base64,d09GMgABAAAAAFXk...) format("woff2");
    font-weight: 400 800;
    font-display: block;  /* block: don't render text until font loaded — prevents accent fallback */
  }
  @font-face {
    font-family: "Geist Mono";
    src: url(data:font/woff2;base64,d09GMgABAAAAA...) format("woff2");
    font-weight: 400 600;
    font-display: block;
  }
  @font-face {
    font-family: "Instrument Serif";
    src: url(data:font/woff2;base64,d09GMgABAAAAA...) format("woff2");
    font-style: italic;
    font-weight: 400;
    font-display: block;
  }
</style>
```

**Verification (T-PDF-02):**
1. Generate PDF for shopping list containing `Pasta integrale, Olio EVO, Pomodorì, Caffè`
2. Open in iPhone Safari (`Files` app → tap PDF) — accents render
3. Open in Mail.app preview attachment — accents render
4. Open in Adobe Reader Windows — accents render
5. Open in macOS Preview — accents render

**[CITED]** WeasyPrint `@font-face` with `data:` URLs is supported and is the recommended pattern for self-contained PDFs [doc.courtbouillon.org/weasyprint/stable].

### Pattern 9: Visual Regression Baseline Regen Workflow

**What:** Plan 09 left TODO comments in `frontend/tests/visual/{light,dark}.spec.ts`. Plan 02-02 first task: regenerate baselines for `/today` (post Plan 09 Lifesum Pure theme) AND new `/week` route.

```bash
# Plan 02-02 Wave 0 — regenerate visual regression baselines
cd frontend

# 1. Build production bundle (test infra runs against `pnpm preview`, NOT `pnpm dev` — Pitfall #12 inherited)
pnpm build

# 2. Update snapshots — Playwright generates new baseline PNGs
pnpm test:visual --update-snapshots

# 3. Commit baselines under version control
git add tests/visual/__screenshots__/ -A
git commit -m "test(visual): regenerate baselines post Lifesum Pure + /week (Plan 02-02)"

# 4. Run CI to validate match
pnpm test:visual
# Should now report 0 diffs

# 5. Push — CI runs again, must pass
git push
```

**CI job pattern (`.github/workflows/visual.yml`):**
```yaml
- name: Run visual regression
  run: pnpm test:visual
  # If snapshots fail (delta >0.02), upload diff PNGs as artifacts for review.
- uses: actions/upload-artifact@v4
  if: failure()
  with:
    name: visual-diffs
    path: frontend/tests/visual/__screenshots__/**/*-diff.png
```

**Survives CI re-run:** baselines are committed binaries; CI never regenerates — only compares. Designer/dev regenerates locally when intentional UI change ships, then commits.

### Pattern 10: BroadcastChannel + Fallback for iOS Safari

**What:** Cross-tab shopping list checkbox sync. BroadcastChannel where supported, `window.focus` event listener fallback elsewhere.

```typescript
// frontend/src/lib/broadcastChannel.ts
/**
 * D-25 — multi-tab shopping list sync.
 *
 * BroadcastChannel is supported in Safari 15.4+ and all modern browsers.
 * Detection: 'BroadcastChannel' in window. iOS Safari Private mode restricts it,
 * so we always feature-detect and fall back gracefully.
 */
type Listener<T> = (msg: T) => void;

export function createSyncChannel<T>(name: string, listener: Listener<T>): () => void {
  if ('BroadcastChannel' in window) {
    const bc = new BroadcastChannel(name);
    const handler = (e: MessageEvent<T>) => listener(e.data);
    bc.addEventListener('message', handler);
    return () => {
      bc.removeEventListener('message', handler);
      bc.close();
    };
  }
  // Fallback: refetch on focus event. Coarser-grained but works on iOS Safari Private mode.
  const onFocus = () => listener({ type: 'focus_refetch' } as unknown as T);
  window.addEventListener('focus', onFocus);
  return () => window.removeEventListener('focus', onFocus);
}

export function postSyncMessage<T>(name: string, msg: T): void {
  if ('BroadcastChannel' in window) {
    const bc = new BroadcastChannel(name);
    try {
      bc.postMessage(msg);
    } finally {
      bc.close();
    }
  }
  // Fallback path: nothing to do — focus event in the OTHER tab triggers refetch.
}
```

**Usage in `frontend/src/services/shopping.ts`:**
```typescript
// On mutation success, broadcast to other tabs
postSyncMessage('wb-shopping-sync', { weekStart, type: 'check_changed' });

// In Shopping.tsx
useEffect(() => {
  const queryClient = useQueryClient();
  return createSyncChannel('wb-shopping-sync', () => {
    queryClient.invalidateQueries({ queryKey: ['shopping', userId, weekStart] });
  });
}, [userId, weekStart]);
```

**[VERIFIED]** caniuse / testmu data: BroadcastChannel supported Safari 15.4+ (Spring 2022). All Brunelli iPhones running iOS 16+ (PWA push requirement) have it. Private-mode restriction is documented but doesn't apply to installed PWAs in standalone display mode. [CITED: WebSearch — testmu.ai BroadcastChannel Safari 2026]

### Anti-Patterns to Avoid

- **`group_id` in JWT claims** — Pitfall #3 inheritance. Always re-look-up from DB per request via `get_user_with_group_access`.
- **412 Precondition Failed for variant conflicts** — D-17 locks 409 with custom code `version_conflict`. 412 has different RFC semantics (caching) and would need separate Italian copy mapping. Stick to 409.
- **Optimistic UI for SHARED state changes** — Pitfall #8 inheritance. Optimistic only for OWN selections; shared visibility toggle shows `Sincronizzazione...` until server confirms.
- **`datetime.utcnow() + timedelta(weeks=1)` for cron** — DST-broken. Use `CronTrigger(timezone=ZoneInfo(...))` and let APScheduler compute next-fire each run.
- **WeasyPrint URL-referenced fonts** — network dependency at PDF gen time. Always inline base64.
- **In-place Dexie schema migration for cache_*** — Pitfall #5 inheritance. cache_* tables DROP-and-refetch on bump; only mutation_queue (opaque HTTP requests) survives.
- **403 (not 404) for cross-user reads** — V13 info-disclosure leak. Always 404 with `not_found` code.
- **Hex literals in WeasyPrint template** — D-12 mirror contract. Use OKLCH coords matching `theme.css`. CI grep gate enforces.
- **Fuzzy ingredient matching** — D-06 explicit deferral. Stays deferred Phase 2 even if it would resolve "pomodorini ≠ pomodori" duplicate rows.
- **Modal calendar for week picker** — UI-SPEC §6.2 + CONTEXT specifics: chip-row + jump-to-date popover, NOT modal. Modal overkill at 390px.
- **`!` in error/info messages** — UI-17 inheritance. NEVER. Conflict toast included.
- **Ascii avocado/mascot Phase 2** — D-32 + Phase 3 deferral. AI widget invariato. No mascot until Phase 3 review.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTML → PDF | Custom rendering loop with PIL/cairo | WeasyPrint (primary) | CSS reuse, font handling, accent rendering, page-break logic — all built in |
| PDF fallback | Roll own template DSL | ReportLab Platypus | Battle-tested imperative API; survives WeasyPrint outage |
| Italian quantity parsing | Generic NLP / spacy / huggingface | Heuristic dict + regex (Pattern 3) | NLP overkill for ~25 unit terms; deterministic + auditable |
| Weekly date math | Custom `getMonday(date)` | `date-fns` `startOfWeek({ weekStartsOn: 1 })` | Locale + DST + ISO week awareness; already in Phase 1 deps |
| Cron scheduling | Custom `asyncio.sleep` loop | APScheduler `AsyncIOScheduler` + `CronTrigger` | DST handling, missed-fire recovery, multiple jobs |
| Optimistic concurrency | Lock tables / SELECT FOR UPDATE | `If-Unmodified-Since` + version int | HTTP-native, scales without DB locks, low p99 latency |
| Cross-tab sync | Custom localStorage polling | BroadcastChannel API + focus fallback | Browser-native, low overhead, supported by all targets |
| Font embedding for PDF | OS-installed font fallback | woff2 base64 inline `@font-face` | Self-contained, deterministic accents on every OS |
| Group authz | Mix `current_user.group_id` filters into endpoints ad-hoc | `get_user_with_group_access(target_user_id)` dependency | One audit point; matches Phase 1 dependency pattern |
| Shopping list category mapping | Hand-edit per ingredient | Keyword fallback dict in `category_mapper.py` + `**Categoria:** <name>` MD annotation | Plan author override path + sane defaults |
| TanStack Query cache invalidation | Custom event bus | `queryClient.invalidateQueries({ queryKey })` | Already wired Phase 1 |
| Toast for 409 | Custom modal | sonner `toast.info()` with action | Phase 1 sonner already standard |
| Visual regression | Pixel-by-pixel custom comparator | Playwright `toHaveScreenshot()` `maxDiffPixelRatio: 0.02` | Already in Phase 1 CI |
| Italian copy in components | Inline strings | Extend `frontend/src/i18n/copy.it.ts` (FND-09) | Single source of truth |

**Key insight:** Phase 2 has zero "build the wheel" temptations remaining — every problem has a Phase 1 primitive or a well-known external library that's already in the stack. The two genuinely novel pieces (Italian quantity parser, GTK3 install) are bounded: parser is 100 lines of regex, GTK3 install is documented MSYS2 commands.

## Runtime State Inventory

> Phase 2 is partly a feature phase, partly a refactor (Group activation backfill). Inventory required for the Group activation step.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | `users.group_id` is currently NULL for all existing users (only Plan 01-03 invite-flow created users to date). `weekly_plan_variants.visibility` enum already in baseline as `'private'` default — Phase 2 will write `'group_shared'` for cene/pranzi via `variant_service`. No legacy data to migrate. | Code edit (variant_service emits new visibility) + data migration (0001_activate_groups.py for User.group_id backfill) |
| Live service config | None — APScheduler not yet running. Plan 02-04 introduces it; jobs registered fresh at startup. NSSM service config (`AppDirectory`, `AppEnvironment`) needs PATH entry for `C:\msys64\mingw64\bin` post Plan 02-01 spike → updated in DEPLOY.md. | Runbook update (DEPLOY.md addendum after Plan 02-01) |
| OS-registered state | NSSM service `WellnessBuddyAPI` exists post Plan 01-08 but no PATH for GTK3 yet. After Plan 02-01: PATH update + service restart required. | NSSM AppEnvironmentExtra append (one-time) |
| Secrets/env vars | New env var `PDF_BACKEND` (default `weasyprint`, `reportlab` if spike fails) — added to `backend/.env` + `.env.example`. No new secret material. | `.env.example` update + DEPLOY.md secrets section addendum |
| Build artifacts / installed packages | `weasyprint`, `apscheduler`, `reportlab` added to `pyproject.toml` — `uv sync --frozen` regenerates lockfile. No stale installed packages from Phase 1 (greenfield). MSYS2 + Pango installed once on production host (one-time, persists). | `uv.lock` regen + production `uv sync --frozen` after deploy pull |

**Nothing found in category** — categories above all have findings; no "None — verified by X" entries needed.

## Common Pitfalls

> Phase 1 PITFALLS.md catalogues #1-#12. Phase 2 inherits all and adds the Phase-2-specific entries below. Pitfall #11 (PostgreSQL connection pool exhaustion) is most relevant to Phase 2's morning resume storm pattern.

### Pitfall #14 (NEW): Italian Quantity Ambiguity in Recipe Strings

**What goes wrong:** Parser merges `200g pasta` and `200g pomodoro` correctly but treats `2 mele` (no unit) and `200 g pomodoro` (with explicit unit) as different aggregation keys. Result: `200 g pomodoro` and `2 mele · pomodoro` appear as separate rows when the user expects them merged. Or `q.b. olio EVO` from 5 different recipes shows 5 times because qb has no aggregable amount.

**Why it happens:** The parser is heuristic and deterministic, not semantic. It cannot know that `gocce di limone` and `succo di limone` are functionally interchangeable. It treats `qb` as its own "unit" so `qb` rows DO merge by name (good) but never aggregate amounts (correct, but visually counts as 1 row regardless of how many recipes called for it).

**How to avoid:**
- Aggregation key: `(canonical_name, unit)` — `pomodoro` with unit `g` and `pomodoro` with unit `None` are distinct rows (UI shows both with separator: `Pomodoro — 200 g · 1 pezzo`).
- `qb` rows display as `q.b.` quantity, count = 1 regardless of recipe count (no fake aggregation).
- Manual override path: plan parser extends optional `**Categoria:** <name>` annotation; same precedent enables future `**Aggregato:** <key>` annotation if drift becomes painful.
- Document expected ambiguities in `02-04-SUMMARY.md`: "Stefano e Marta accettano duplicati legittimi (pomodorini ≠ pomodori) Phase 2; Phase 5 AI risolve."

**Warning signs:**
- Marta reports "ha generato la lista due volte per la stessa cosa" — examine the `(name, unit)` pair difference.
- Shopping list has > 50 rows for a 7-day plan (typical is 30-40) — likely fragmentation.
- `qb` rows count >5 — same item recurring; merge by name only for `qb`.

**Phase to address:** Plan 02-04 (shopping list aggregation). Test corpus must include real Stefano+Marta plans, not just synthetics.

### Pitfall #15 (NEW): BroadcastChannel Absent on iOS Safari Private Mode

**What goes wrong:** Stefano opens shopping list in two iPhone Safari tabs (one in Private mode for testing). Tab A checks an item. Tab B doesn't update until next focus. Or worse, BroadcastChannel constructor throws unhandled in Private mode.

**Why it happens:** Safari restricts BroadcastChannel in Private Browsing mode (privacy isolation). The API may fail to construct or silently no-op.

**How to avoid:**
- Feature-detect with `'BroadcastChannel' in window` (Pattern 10 above).
- Fallback to `window.addEventListener('focus', refetch)` — coarser but always works.
- For installed PWA on iPhone home screen, `display-mode: standalone` is NOT private mode — full support.
- Wrap the constructor in try/catch defensively — even if detection passes, Private mode may throw.

**Warning signs:**
- Bug reports of "ha smesso di sincronizzare tra tab" only from Safari users.
- Browser console error `SecurityError: BroadcastChannel`.
- Sentry/log capture (Phase 4) shows `'BroadcastChannel' in window` true but `new BroadcastChannel(...)` throws.

**Phase to address:** Plan 02-04 (shopping list). Detection + fallback in `lib/broadcastChannel.ts`.

### Pitfall #16 (NEW): Group Migration Race When Admin Assigns Concurrently

**What goes wrong:** Admin runs `0001_activate_groups.py` while a new user registers via `/api/auth/invite` accept. Race: migration reads users (no group_id), invite handler creates user with `group_id=None`. Migration commits group assignment for previously-existing users. New user is missed — has `group_id=None` indefinitely until next migration run.

**Why it happens:**
- Phase 1 invite handler does NOT auto-create personal group (Group activation deferred Phase 2).
- Migration is one-shot; not re-run after every new user.
- No DB-level constraint forces `group_id NOT NULL` (NULL allowed in baseline schema).

**How to avoid:**
- Plan 02-06 must update invite handler (`backend/app/services/auth_service.py`) to auto-create a personal group on user creation:

```python
# After user.id is committed, before returning:
new_group = Group(name=f"{user.username} · household")
session.add(new_group)
await session.flush()
user.group_id = new_group.id
await session.commit()
```

- Migration `0001_activate_groups.py` runs ONCE for backfill. After that, every new user gets a group on creation.
- Tests `test_alembic_0001.py::test_idempotent` AND `test_auth.py::test_register_creates_personal_group` cover both paths.
- Optional: Phase 4 adds `users.group_id NOT NULL` constraint after Phase 2 backfill confirmed clean.

**Warning signs:**
- `users.group_id IS NULL` rows in production after Phase 2 deploys.
- New users registered post-Phase-2 deploy report "non vedo i pasti condivisi di Marta".
- Audit log shows `user_register` events without paired `group_create`.

**Phase to address:** Plan 02-06 (group activation + auth handler patch).

### Pitfall #17 (NEW): APScheduler Timezone Drift on DST Boundaries

**What goes wrong:** Italy spring-forward (last Sunday of March): clocks jump 02:00 → 03:00. User's shopping list reset job scheduled for "Lunedì 00:00 Europe/Rome" — fires correctly that Sunday→Monday because 00:00 isn't ambiguous. But: APScheduler internally caches the next-fire time, and a long-running scheduler that survives multiple DST transitions WITHOUT recomputing may drift.

**Why it happens:**
- APScheduler `CronTrigger(timezone=ZoneInfo(...))` recomputes next-fire after each fire — generally DST-safe.
- BUT: a scheduler restarted at 02:30 CEST on the spring-forward day may compute next-fire incorrectly if the trigger was cached.
- Worse: if the user's `timezone` field is updated (rare but possible — they travel) but the registered job uses the OLD timezone object.

**How to avoid:**
- On every NSSM restart (which happens after deploys), `lifespan` startup re-registers all jobs from current DB state. This guarantees fresh `ZoneInfo` instances.
- Test `test_scheduler.py::test_dst_spring_forward_2026` (Pattern 5) validates next-fire across DST.
- Test `test_scheduler.py::test_dst_fall_back_2026` validates the inverse.
- Document: "Job re-registration on lifespan startup is REQUIRED. APScheduler does not auto-refresh `ZoneInfo` instances."
- Phase 3 (push notifications) inherits same pattern — same DST coverage tests.

**Warning signs:**
- User reports "la lista non si è resettata lunedì mattina" the week after DST.
- Comparing job fire-time logs against `datetime.now(rome).weekday() == 0` shows ±1 hour drift.
- Any code using `datetime.now()` without explicit timezone in scheduler internals.

**Phase to address:** Plan 02-04 (cron registration) + verification carries forward to Phase 3 push.

### Pitfall #18 (NEW): LWW Silent Loss When Both Partners Edit Within Same Second

**What goes wrong:** Stefano and Marta both tap "Opzione B" for tonight's cena within 200ms of each other. Both reads see the same `updated_at`. Both PATCHes pass `If-Unmodified-Since: <same ts>`. Server processes Stefano first → row updated. Marta's PATCH arrives, server compares `If-Unmodified-Since` to row's NEW `updated_at` (post-Stefano) → 409. Toast shows "Aggiornato da Stefano". Marta's choice is silently dropped.

**Why it happens:**
- TIMESTAMPTZ has microsecond precision but client serialization rounds to seconds in some clients.
- `If-Unmodified-Since` is a precondition — by design, the second writer must yield.
- This is the CORRECT behavior for the LWW + 409 contract — but UX matters: Marta needs to know HER choice didn't take.

**How to avoid:**
- Toast copy is explicit (FAM-05): `"Aggiornato da Stefano. Ricarica per vedere l'ultima versione."` — user knows their write was discarded.
- Action button "Ricarica" triggers `queryClient.invalidateQueries(['weekly', userId, weekStart])` so they see Stefano's choice and can re-pick if needed.
- Optimistic UI rollback (TanStack Query `onError → setQueryData(prev)`) restores the original variant in Marta's UI on 409.
- DO NOT auto-merge — silent merge is worse than visible conflict for shared meal decisions.
- Test `test_weekly_api.py::test_concurrent_variant_edit_409` validates the race + toast outcome.

**Warning signs:**
- Bug reports "ho cambiato la variante ma è tornata indietro" — match against 409 logs in same second.
- Conflict-rate metric (Phase 4 observability) trending up over time → investigate UX (maybe variant pill needs longer debounce).

**Phase to address:** Plan 02-02 (variant CRUD with LWW) + Plan 02-06 (family sync end-to-end).

### Pitfall #19 (NEW): Visual Regression Baseline Staleness Post Plan 09 Theme Swap

**What goes wrong:** Plan 09 (Lifesum Pure theme propagation) shipped with TODO comments in `frontend/tests/visual/{light,dark}.spec.ts` because regenerating baselines was deferred. Plan 02-02 starts, runs `pnpm test:visual` against the OLD baselines (from Geist Sans Sprint 1 era), every test fails with massive pixel diffs, planner concludes "everything is broken" and rolls back.

**Why it happens:**
- Theme change = systemic visual change. Baseline images encode the OLD theme.
- TODO-deferred regen leaves a landmine for whoever runs CI next.
- Playwright `toHaveScreenshot()` fails on first run if no baseline exists, OR on every run if baseline is stale.

**How to avoid:**
- D-31 lock: Plan 02-02 first task = `pnpm test:visual --update-snapshots` THEN commit baselines THEN run `pnpm test:visual` to validate match.
- Commit message MUST be explicit: `test(visual): regenerate baselines post Lifesum Pure (Plan 09 → Plan 02-02)` — future devs grep for it.
- CI publishes diff PNGs as artifacts on failure (Pattern 9) so a reviewer can SEE what changed before approving regen.
- `frontend/tests/visual/README.md` (NEW Plan 02-02 deliverable) documents the regen workflow + when it's allowed (= intentional theme/component change, NOT to mask bugs).

**Warning signs:**
- CI consistently fails on `visual-light` / `visual-dark` jobs after Plan 09 merge → not addressed promptly.
- Diff PNG artifacts show systematic shift (every page same magnitude) → theme issue, not page-specific.
- PR descriptions say "snapshots needed regen" instead of explaining intentional UI change.

**Phase to address:** Plan 02-02 first task (Wave 0 of W2). Regenerate + commit + validate before any other Plan 02-02 work.

## Code Examples

### Common Operation 1: Create variant + 409 conflict + Italian toast

```typescript
// frontend/src/services/weekly.ts — see Pattern 4 above for full source
const setVariant = useSetVariant(weekStart, userId);

setVariant.mutate({
  plan_id: planId, day_of_week: 0, meal_type: 'dinner',
  variant_key: 'B',
  ifUnmodifiedSince: variant.updated_at,  // ISO string from last fetch
});
// onError handler shows sonner toast + offers "Ricarica" action
```

### Common Operation 2: WeasyPrint export endpoint

```python
# backend/app/api/shopping.py — see Pattern 2 above
@router.post("/{week_start}/export-pdf")
async def export_pdf(...):
    payload = await shopping_service.build_pdf_payload(...)
    pdf_bytes = await exporter.render_shopping_list(**payload)
    return Response(content=pdf_bytes, media_type="application/pdf", ...)
```

### Common Operation 3: Cross-user dependency

```python
# backend/app/core/deps.py — extension point for FAM-06
async def get_user_with_group_access(
    target_user_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Authz dependency for cross-user reads on group_shared resources.

    - target_user_id == current_user.id → return current_user (own data path).
    - target_user_id in same group + resource visibility=group_shared → return target user.
    - any other case → raise 404 (V13 info-disclosure).
    """
    if target_user_id == current_user.id:
        return current_user
    target = (await session.scalars(select(User).where(User.id == target_user_id))).first()
    if not target or target.group_id is None or target.group_id != current_user.group_id:
        raise AppException(404, "Risorsa non trovata", "not_found")
    return target
```

### Common Operation 4: Italian quantity parser smoke

```python
# backend/tests/unit/test_ingredient_parser.py
from app.services.ingredient_parser import parse, ParsedIngredient

def test_yogurt_greco_line():
    out = parse("Yogurt greco 200g + frutta secca 30g + miele 10g")
    assert out == [
        ParsedIngredient(name="yogurt greco", amount=200, unit="g"),
        ParsedIngredient(name="frutta secca", amount=30, unit="g"),
        ParsedIngredient(name="miele", amount=10, unit="g"),
    ]


def test_qb_line():
    out = parse("Olio EVO q.b.")
    assert out == [ParsedIngredient(name="olio evo", amount=None, unit="qb")]


def test_un_pizzico():
    out = parse("Un pizzico di sale")
    assert out == [ParsedIngredient(name="di sale", amount=1.0, unit="pizzico")]
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| WebSocket for real-time shared state | Polling refetchOnFocus + 30s staleTime (D-16) | Phase 2 lock (2026-05-02) | Adequate for 2 users; convergence ≤5s |
| Hand-coded weekly calendar widget | shadcn Popover + react-day-picker month grid | Phase 1 deps | UI-SPEC §6.2 WeekPicker pattern |
| Server-side template engines (Jinja2 + WeasyPrint) for HTML→PDF | Same — still state of the art for branded reports | 2026 stable | Pairs with CSS reuse for drift-impossible brand |
| ETag for HTTP optimistic concurrency | `If-Unmodified-Since` (TIMESTAMPTZ-driven) | D-17 lock | Simpler than ETag for resources with version+updated_at; matches FAM-04 verbiage |
| Single-language Italian-only via constants file | Same (FND-09 lock) | Phase 1 | Refactor to react-i18next deferred v2 if non-Italian users |
| Imperative PDF (ReportLab Platypus) | HTML+CSS PDF (WeasyPrint) | STACK.md decision Phase 1 | Brand consistency + fallback retained |

**Deprecated/outdated:**
- `wkhtmltopdf` — unmaintained + security concerns; NEVER use [STACK.md L356]
- `pytz` — superseded by Python 3.9+ stdlib `zoneinfo` [PITFALLS.md #7]
- `Moment.js` — superseded by `date-fns v4` [STACK.md L344]
- ETag-based optimistic concurrency for our scale — `If-Unmodified-Since` simpler when server already tracks `updated_at`

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | TanStack Query optimistic-update onError rollback works for queued mutations on reconnect | Pattern 4 | Plan 06 mutation queue might not call `onError`; verify in Plan 02-02 with airplane-mode test |
| A2 | `UI` (international units) and `mg` (milligrams) are not in current parser unit table; Stefano supplements may need them | Pattern 3 evil-corpus | Real plan upload reveals; Plan 02-04 expands `_UNITS_LONG_FIRST` if found |
| A3 | iPhone Safari standalone display mode is NOT subject to Private Browsing BroadcastChannel restrictions | Pattern 10 + Pitfall #15 | Stefano's iPhone test (Plan 02-03) is the verification point; if fails, fallback `window.focus` listener handles it |
| A4 | APScheduler `CronTrigger` survives `lifespan` restart cleanly when re-registered each startup | Pattern 5 + Pitfall #17 | Test `test_scheduler.py` plus production observation Plan 02-04 onwards |
| A5 | WeasyPrint 62.x renders accents correctly on iPhone Safari with woff2 base64 inline | Pattern 8 + T-PDF-02 | Plan 02-05 verification with real device — fallback ReportLab if not |
| A6 | Plan 02-01 GTK3 spike 7-day window is sufficient signal for production stability decision | Pattern 1 + D-11 | If false negatives (passes spike, fails in production), mid-Phase-2 fallback to ReportLab via env-flip; ABC enables runtime swap without code change |
| A7 | shadcn `tooltip`, `alert-dialog`, `collapsible`, `toggle-group`, `popover` blocks integrate cleanly with Tailwind 4 `@theme` tokens already locked Phase 1 | UI-SPEC §14 | Plan 02-02 component dev surfaces issues immediately; shadcn 2026 has Tailwind 4 native support per STACK.md |
| A8 | The 5xx >2% threshold over 7 days is sufficient noise floor to distinguish "GTK3 instability" from "ordinary backend flakes" | D-11 | Project owner judgment call; supplement with structured logs `{exporter_backend, error_class}` for forensics |

**Status:** 8 assumed claims. The most consequential (A6, A8) belong to project-owner judgment on Plan 02-01 spike outcome — not technical research questions. A1-A5 verifiable via tests scheduled into the validation plan below.

## Open Questions

1. **APScheduler job persistence across NSSM restarts**
   - What we know: lifespan re-registers all jobs from DB on every startup (Pattern 5).
   - What's unclear: does APScheduler need a persistent JobStore (e.g., SQLAlchemy JobStore) for at-least-once semantics across crashes?
   - Recommendation: Phase 2 ships with default in-memory MemoryJobStore (jobs re-registered on startup). If a user reports "lista non resettata" because backend crashed Sun → Mon, Phase 4 adds SQLAlchemyJobStore. RESOLVED for Phase 2 = MemoryJobStore.

2. **Variant `version` increment strategy**
   - What we know: D-CD lists "auto-increment SQL trigger vs explicit service" as Claude's discretion.
   - What's unclear: which is more maintainable.
   - Recommendation: explicit service-layer increment (`row.version += 1` in `variant_service.upsert_variant`) — colocated with the LWW conflict check, no SQL trigger surface area to manage. RESOLVED.

3. **TanStack Query key shape**
   - What we know: D-CD lists `['weekly', userId, weekStart]` vs flat as Claude's discretion.
   - What's unclear: which scales better.
   - Recommendation: tuple `['weekly', userId, weekStart]` — matches Phase 1 `['today']` convention plus user/period scoping. Enables `invalidateQueries({queryKey: ['weekly', userId]})` for full-user cache nuke on logout. RESOLVED.

4. **5xx threshold for spike pass/fail**
   - What we know: D-CD lists "mid-spike trip OR end-of-spike summary" as project-owner discretion.
   - What's unclear: cadence.
   - Recommendation: end-of-spike summary (Day 7) — fewer false alarms; mid-spike daily 5xx report as informational. DEFERRED to project owner.

5. **Real Stefano+Marta plans availability**
   - What we know: STATE.md TODO backlog: "Locate Stefano + Marta MD plans, copy into `/plans/` repo path before Phase 1 `/today` testing." Plan 01 used synthetic.
   - What's unclear: whether real plans are now in `/plans/` for Phase 2 ingredient parser tuning.
   - Recommendation: Plan 02-04 (shopping aggregation) MUST validate against real plans. If still unavailable, escalate before merging Plan 02-04. DEFERRED to plan author (block until resolved).

6. **PDF page break behavior with > 50 ingredients**
   - What we know: WeasyPrint `page-break-inside: avoid` keeps small categories whole (UI-SPEC §6.4).
   - What's unclear: behavior with extremely long lists (Stefano's 4-week plan stretch).
   - Recommendation: Plan 02-05 includes a synthetic 100-row test to validate; small categories whole, large categories break naturally. RESOLVED via test.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 | Backend services | ✓ | 3.12.x | — |
| PostgreSQL | Data layer | ✓ (already running on Windows Server 2019) | unspecified — verify Plan 02-03 | — |
| MSYS2 + Pango (`mingw-w64-x86_64-pango`) | WeasyPrint | ✗ (must install Plan 02-01 spike) | install latest | ReportLab |
| GTK3 runtime DLLs in PATH | WeasyPrint | ✗ (must add `C:\msys64\mingw64\bin` to System PATH) | — | ReportLab |
| WeasyPrint Python package | PDF export | ✗ | `^62.x` to install | ReportLab |
| ReportLab | PDF fallback | ✗ | `^4.x` to install | None — Phase 2 ships at least one PDF backend |
| APScheduler | Cron jobs | ✗ | `^3.11` to install | None — required by SHOP-08 |
| MSYS2 installer | Pango install | ✗ | latest from msys2.org | None |
| iPhone (real device, iOS 16+) | Plan 02-03 deploy validation + T-PDF-02 accent verification | ✓ (Stefano + Marta personal devices) | iOS 16+ | None — pause-gate criterion |
| Mail.app (macOS or iOS) | T-PDF-02 PDF preview accent verification | ✓ (Stefano's macOS or iPhone) | latest | iOS Files preview |
| Adobe Reader (Windows) | Optional T-PDF-02 cross-check | ✓ (likely on Windows Server) | n/a | macOS Preview / iOS Safari PDF |
| `pnpm` / `pnpm dlx shadcn` | Frontend net-new shadcn blocks | ✓ | latest | None |
| `wacs.exe` (win-acme) | Plan 02-03 SSL renew | ✓ (from Phase 1 deploy artifacts) | latest | None — pause-gate |
| `nssm` | Plan 02-03 service install | ✓ | latest | None |

**Missing dependencies with no fallback:** APScheduler (required), shadcn CLI access (required).
**Missing dependencies with fallback:** WeasyPrint stack — ReportLab takes over via `PdfExporter` ABC if Plan 02-01 spike fails.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Backend framework | pytest 8 + pytest-asyncio 0.24 + httpx AsyncClient (existing Phase 1) |
| Backend config | `backend/pyproject.toml` `[tool.pytest.ini_options]` |
| Frontend framework | Vitest 2.x (unit) + Playwright 1.x (e2e + visual + a11y) |
| Frontend config | `frontend/vitest.config.ts`, `frontend/playwright.config.ts`, `frontend/lighthouserc.json` |
| Quick run command (backend) | `cd backend && uv run pytest tests/unit -x` |
| Full suite command (backend) | `cd backend && uv run pytest --cov` |
| Quick run command (frontend) | `cd frontend && pnpm test` |
| Full suite command (frontend) | `cd frontend && pnpm test:all` (test + axe + visual) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| WEEK-01 | `/week` route loads + week picker chip row + jump-to-date | e2e + unit | `pnpm test src/components/week/WeekPicker.test.tsx` | ❌ Wave 0 (Plan 02-02) |
| WEEK-02 | Day section shows 4 meal slots with macro target | unit (component) | `pnpm test src/components/week/DaySection.test.tsx` | ❌ Wave 0 |
| WEEK-03 | VariantSelector dropdown — 3 options + active dot | unit (component) + a11y | `pnpm test src/components/week/VariantSelector.test.tsx` + `pnpm test:axe` | ❌ Wave 0 |
| WEEK-04 | PATCH variant — 200 own / 409 conflict / 404 cross-user | integration | `cd backend && pytest tests/integration/test_weekly_api.py -k variant` | ❌ Wave 0 (Plan 02-02) |
| WEEK-05 | GET summary — kcal/macros aggregate | integration | `pytest tests/integration/test_weekly_api.py::test_weekly_summary` | ❌ Wave 0 |
| SHOP-01 | List auto-generates from chosen variants | integration | `pytest tests/integration/test_shopping_api.py::test_aggregate_from_variants` | ❌ Wave 0 (Plan 02-04) |
| SHOP-02 | Aggregation merges same name+unit | unit | `pytest tests/unit/test_shopping_service.py::test_aggregation` | ❌ Wave 0 |
| SHOP-03 | Checkbox state persists cross-device | integration | `pytest tests/integration/test_shopping_api.py::test_check_persists` + Playwright `e2e/shopping-cross-device.spec.ts` | ❌ Wave 0 |
| SHOP-04 | 5 categories rendered in fixed order | unit | `pytest tests/unit/test_category_mapper.py` | ❌ Wave 0 |
| SHOP-05 | View toggle Per giorno renders day-grouped rows | unit (component) | `pnpm test src/components/shopping/ShoppingViewToggle.test.tsx` | ❌ Wave 0 |
| SHOP-06 | Copia testo button copies plain text | unit (component) | `pnpm test src/components/shopping/CopyTextButton.test.tsx` | ❌ Wave 0 |
| SHOP-07 | Esporta PDF returns valid PDF stream | integration | `pytest tests/integration/test_pdf_export.py::test_export_returns_pdf` | ❌ Wave 0 (Plan 02-05) |
| SHOP-08 | Reset cron lunedì 00:00 user tz | integration | `pytest tests/integration/test_scheduler.py::test_dst_*` | ❌ Wave 0 |
| FAM-01 | Group entity backfilled per user | integration | `pytest tests/integration/test_alembic_0001.py` | ❌ Wave 0 (Plan 02-06) |
| FAM-02 | Default visibility cene/pranzi=group_shared | integration | `pytest tests/integration/test_weekly_api.py::test_default_visibility` | ❌ Wave 0 |
| FAM-03 | Condiviso badge renders for partner shared meal | unit (component) + visual | `pnpm test src/components/family/SharedBadge.test.tsx` + `pnpm test:visual` | ❌ Wave 0 |
| FAM-04 | If-Unmodified-Since 409 envelope | integration | `pytest tests/integration/test_weekly_api.py::test_concurrent_variant_409` | ❌ Wave 0 |
| FAM-05 | Sonner toast italian copy on 409 | unit (component) | `pnpm test src/components/family/ConflictToast.test.tsx` | ❌ Wave 0 |
| FAM-06 | get_user_with_group_access dependency | unit | `pytest tests/unit/test_deps.py::test_group_access` | ❌ Wave 0 |
| FAM-07 | group_id NOT in JWT — re-lookup | integration | `pytest tests/integration/test_auth.py::test_no_group_id_in_jwt` | ❌ Wave 0 |
| FAM-08 | Negative authz matrix 8×5=40 | integration | `pytest tests/integration/test_family_authz_matrix.py` | ❌ Wave 0 |
| FAM-09 | Polling refetchOnFocus + 30s staleTime convergence ≤5s | integration | `pytest tests/integration/test_family_api.py::test_polling_convergence` (uses two httpx clients with frozen time) | ❌ Wave 0 |
| DEP-06 | WeasyPrint GTK3 spike 7-day stability | manual checklist | `02-01-GTK3-SPIKE.md` (Pattern 1 §Plan 02-01 GTK3 spike checklist) | ❌ Plan 02-01 |
| UI-04 | Motion budget honored on `/week` + `/spesa` | unit | `pnpm test motion.test.ts` (extend Phase 1 list) | ⏳ extend |
| UI-05 | reduced-motion honored | e2e | `pnpm test:axe` Playwright reducedMotion: 'reduce' (extend Phase 1) | ⏳ extend |
| UI-10 | axe-core ≥4.5:1 body / ≥3:1 large icons on `/week` + `/spesa` | a11y | `pnpm test:axe` (extend Phase 1 routes) | ⏳ extend |
| UI-11 | Lighthouse a11y ≥95 on `/week` + `/spesa` | lighthouse | `pnpm test:lighthouse-pwa` (extend Phase 1) | ⏳ extend |
| UI-12 | Dark-mode visual snapshots `/week` + `/spesa` | visual | `pnpm test:visual` (extend Phase 1 list — D-31 baseline regen first) | ⏳ extend |
| Plan 02-03 (D-26..D-28) | iPhone install + offline `/today` + Lighthouse PWA ≥95 | manual checklist | `02-03-DEPLOY-CHECKLIST.md` (Stefano + Marta sign-off) | ❌ Plan 02-03 |

### Sampling Rate

- **Per task commit:** `cd backend && uv run pytest tests/unit -x` + `cd frontend && pnpm test`
- **Per wave merge:** `cd backend && uv run pytest --cov` + `cd frontend && pnpm test:all`
- **Phase gate:** Full suite green + `02-01-GTK3-SPIKE.md` PASS + `02-03-DEPLOY-CHECKLIST.md` Stefano+Marta PASS + Lighthouse PWA ≥95 + axe-core green on every Phase 2 route.

### Wave 0 Gaps

Wave 0 = "test infrastructure exists for the requirement" check. All Phase 2 tests are net-new — no existing files cover them. Specifically:

**Wave 0 deliverables (extend `tests/` and `frontend/tests/` directories):**
- [ ] `backend/tests/unit/test_ingredient_parser.py` — covers SHOP-02 (parser correctness)
- [ ] `backend/tests/unit/test_category_mapper.py` — covers SHOP-04 (mapping)
- [ ] `backend/tests/unit/test_variant_service.py` — covers WEEK-04 (LWW unit)
- [ ] `backend/tests/unit/test_shopping_service.py` — covers SHOP-01..02
- [ ] `backend/tests/integration/test_weekly_api.py` — covers WEEK-01..05 + concurrent 409
- [ ] `backend/tests/integration/test_shopping_api.py` — covers SHOP-01..08
- [ ] `backend/tests/integration/test_family_api.py` — covers FAM-03..05, FAM-09
- [ ] `backend/tests/integration/test_family_authz_matrix.py` — FAM-08 (40 tests)
- [ ] `backend/tests/integration/test_pdf_export.py` — SHOP-07
- [ ] `backend/tests/integration/test_alembic_0001.py` — FAM-01 idempotence
- [ ] `backend/tests/integration/test_scheduler.py` — SHOP-08 + DST
- [ ] `backend/tests/conftest.py` — extend with `marta`, `outsider`, `ex_member` fixtures
- [ ] `frontend/src/components/week/*.test.tsx` (8 files for the 7 components in §6.2)
- [ ] `frontend/src/components/shopping/*.test.tsx` (3 files)
- [ ] `frontend/src/components/family/*.test.tsx` (3 files)
- [ ] `frontend/src/services/__tests__/weekly.test.ts` + `shopping.test.ts` + `family.test.ts`
- [ ] `frontend/tests/visual/light.spec.ts` + `dark.spec.ts` — extend route list with `/week` + `/spesa`; **D-31 regen first**
- [ ] `frontend/tests/a11y/a11y.spec.ts` — extend route list with `/week` + `/spesa`
- [ ] `.planning/phases/02-differentiators/02-01-GTK3-SPIKE.md` — manual spike checklist (Plan 02-01)
- [ ] `.planning/phases/02-differentiators/02-03-DEPLOY-CHECKLIST.md` — manual deploy checklist (Plan 02-03)

## Security Domain

> Required when `security_enforcement` is enabled (absent = enabled). Phase 2 introduces multi-user data sharing — security is the headline.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V1 Architecture, Design, Threat Modeling | yes | Threat-modeled in CONTEXT.md decisions D-15..D-21 (visibility defaults, cross-user authz, no group_id in JWT) |
| V2 Authentication | inherited | Phase 1 JWT + refresh rotation + 10s grace (auth_service) — unchanged Phase 2 |
| V3 Session Management | inherited | Phase 1 HttpOnly+Secure+SameSite=Lax cookie + family-revocation — unchanged |
| V4 Access Control | yes | New: `get_user_with_group_access` + cross-user 404 (V13 info-disclosure) + visibility enum filtering |
| V5 Input Validation | yes | New: variant_key locked enum (`'A'`/`'B'`/`'pasta'`); meal_type locked enum; If-Unmodified-Since parsed via `datetime.fromisoformat` (rejects malformed); category in PDF template Jinja2-escaped |
| V6 Cryptography | inherited | Phase 1 bcrypt 12+ rounds; no new crypto Phase 2 |
| V7 Error Handling | yes | API envelope `{detail, code}` consistent; 409 carries `conflicting_user` (controlled disclosure — partner names within same group) |
| V8 Data Protection | yes | PDF generation server-side; no client-side template render that could leak via DOM |
| V9 Communication | inherited | HTTPS via IIS + win-acme |
| V10 Malicious Code | inherited | No new dependencies with elevated trust beyond WeasyPrint/ReportLab/APScheduler (mainstream) |
| V11 Business Logic | yes | LWW + 409 prevents lost-update; visibility default cene/pranzi group_shared; admin merge groups deferred Phase 4 |
| V12 Files and Resources | yes | PDF generation NEVER accepts user-uploaded HTML — only server-built Jinja2 template; PDF response sets `Content-Disposition: attachment` |
| V13 API and Web Service | yes | Cross-user 404 not 403 (info-disclosure mitigation, Phase 1 inheritance) |
| V14 Configuration | yes | New env var `PDF_BACKEND` (no secret); MSYS2 PATH on production host documented in DEPLOY.md |

### Known Threat Patterns for {Wellness Buddy stack}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Cross-family data leakage (Marta sees outsider's meals) | Information disclosure | `get_user_with_group_access` + 404 not 403 + 8×5 negative authz matrix in CI (FAM-08) |
| Stale group membership in JWT (ex-member retains access) | Privilege escalation | `group_id` MAI in JWT — re-look-up DB every request (FAM-07, D-20) |
| Optimistic UI desync of shared state | Tampering | Server-canonical write + optimistic only for OWN data; shared shows `Sincronizzazione...` until 200 |
| LWW silent loss between partners | Tampering / repudiation | 409 toast names conflicting partner; user can re-pick (Pitfall #18) |
| PDF template injection (HTML in user data) | Tampering / Elevation | Jinja2 autoescape + variant_key locked enum + ingredient_name NFC-normalized; `text-decoration` etc. impossible from user input |
| Server-side template injection in WeasyPrint | Tampering | Template loaded via `FileSystemLoader` from server-only dir; user data never enters template path/name |
| Prompt-injection via meal/ingredient name into AI context | Tampering / Information disclosure | AI invariato Phase 2 (D-32); Phase 5 owns this surface |
| 1GB MD upload DoS | DoS | 1MB cap inherited Phase 1 (`MAX_FILE_BYTES` in plan_service); shopping list endpoint inherits FastAPI default body limit |
| Race-condition reset cron firing twice during DST | Repudiation | APScheduler CronTrigger DST-correctness tests (Pitfall #17) |
| BroadcastChannel cross-tab message tampering | Spoofing | Same-origin only by spec; messages opaque payload; never carries auth tokens |
| Cross-user PDF export (Stefano exports Marta's list) | Information disclosure | `?user_id=` query param routed via `get_user_with_group_access`; cross-user shopping is `group_shared`-aware aggregation, only includes ingredients from cene/pranzi (default) |

## Project Constraints (from CLAUDE.md)

> Compliance checks the planner MUST verify per task / wave.

**Code conventions inherited Phase 1:**
1. Mobile-first 390px → tablet → desktop with container queries — Phase 2 `/week` + `/spesa` honor.
2. Italian-only Sprint 1 — extend `frontend/src/i18n/copy.it.ts` namespaces (D-33 `~95 strings`). Never inline.
3. JWT access in memory + refresh HttpOnly cookie + rotation — unchanged.
4. API errors `{detail: string, code: string}` — unchanged. New code: `version_conflict`, `not_found` (cross-user reuse).
5. AI layer SEMPRE astratto via `AIProvider` ABC — Phase 2 changes nothing.
6. Solo Alembic per migrazioni DB — `0001_activate_groups.py` is the only Phase 2 migration.
7. Server canonical truth, Dexie cache + outbox queue — extend cache_weekly + cache_shopping; mutation_queue invariant (opaque HTTP requests).
8. UUIDs server-generated — unchanged.
9. TIMESTAMPTZ + UTC storage + IANA tz on User — `WeeklyPlanVariant.updated_at` and `ShoppingListState.updated_at` are TIMESTAMPTZ already (verified baseline).
10. `group_id` MAI in JWT — re-look-up DB (D-20 reinforces).
11. Cross-user reads via `get_user_with_group_access(target_user_id)` — Phase 2 wires this dep into 4 endpoints.
12. MD parser tollerante in `parsers/`, validation strict Pydantic in `schemas/` — Phase 2 extends parser with optional `**Categoria:**` annotation.
13. Conflict resolution last-write-wins + 409 → toast UX — Phase 2 implements (FAM-04, FAM-05).
14. Visibility enum: `private` | `group_shared` — cene+pranzi default group_shared, weight+workout always private.

**UI/UX conventions (every PR — UI-01..UI-20):**
1. Tutti colori/font/radius/motion via Tailwind 4 `@theme` tokens — UI-SPEC §1-§5 inherited verbatim. CI hex-ban grep enforces; PDF template uses OKLCH coords mirroring `theme.css`.
2. Motion budget ≤250ms / ≤800ms / ≤2 simultaneous — UI-SPEC §5 lists the 10 Phase 2 motions.
3. `prefers-reduced-motion: reduce` honored — `--motion-scale: 0` inherited.
4. Touch microinteractions tap scale 0.97 80ms ease — VariantSelector pill, week picker chips, share toggle all comply.
5. Dark mode first-class — UI-SPEC §4 60/30/10 reuse map covers light + dark for every new surface; visual snapshots both schemes.
6. axe-core CI ≥4.5:1 body / ≥3:1 large icons — UI-SPEC §4 contrast pairs verified for new surfaces.
7. Illustrations decorative `aria-hidden`, meaningful `<title>` + `aria-labelledby` italiani — Phosphor icons in MealCard get aria-hidden when decorative; Condiviso badge uses descriptive aria-label.
8. Form errors italian copy + icon + `role="alert"` + color — ConflictToast uses sonner `info` role + leaf-500 + ArrowsClockwise icon + italian copy.
9. iOS keyboard `visualViewport` API — Phase 2 surfaces have minimal text input (only week jump-to-date popover); Plan 06 input-focus pattern reused.
10. Tone: NO `!` in errors — ConflictToast verbatim `"Aggiornato da Stefano. Ricarica per vedere l'ultima versione."` no exclamation.
11. `Intl.NumberFormat('it-IT')` — quantities `400 g`, `2 confezioni`, weekly kcal `12.320 / 15.400`. `lib/format.ts` extends with `italianTimeAgo` helper.
12. Emoji ≤1-2 per screen — Phase 2 surfaces emoji-free.
13. ≤1 celebration per session — Phase 2 has ZERO celebrations (UI-SPEC §5 explicit).
14. Mascot Sprint 3 — D-32 confirms invariato.

**Build order locks:**
- Models (Phase 1) before any feature ✓ (baseline ships variant + shopping_list_state + groups)
- Auth (Phase 1) before user-scoped endpoints ✓
- MD Parser (Phase 1) before /today ✓ — extended Phase 2 with `**Categoria:**` (backward compat)
- AI ABC (Phase 1) before AI endpoint ✓ — invariato Phase 2
- Group entity (Phase 1 schema) before family sync (Phase 2) ✓ — Plan 02-06 backfills via 0001 migration
- VAPID keys → Phase 3 (deferred)
- TIMESTAMPTZ + IANA tz (Phase 1) before notifications (Phase 3) ✓

## Sources

### Primary (HIGH confidence)
- `.planning/phases/02-differentiators/02-CONTEXT.md` — 34 locked decisions D-01..D-34
- `.planning/phases/02-differentiators/02-UI-SPEC.md` — APPROVED 6/6 design contract revision 2
- `.planning/REQUIREMENTS.md` §WEEK §SHOP §FAM §DEP-06 + UI-01..UI-20 cross-cutting
- `.planning/phases/01-foundation/01-CONTEXT.md` — 33 Phase 1 locked decisions carried forward
- `.planning/phases/01-foundation/01-RESEARCH.md` — Phase 1 patterns (auth, parser, deps, refresh rotation)
- `.planning/research/STACK.md` — WeasyPrint primary + ReportLab fallback decision context, version pins
- `.planning/research/PITFALLS.md` — #1-#12 inherited; #11 (pool exhaustion) most relevant Phase 2 morning resume storm
- `.planning/research/ARCHITECTURE.md` — 3-tier offline-first model, Group entity rationale, server canonical truth
- `CLAUDE.md` — project conventions, build-order locks, UI-01..UI-14 active rules
- `backend/app/services/weight_service.py` (L104-105 cross-user 404 V13 pattern, comment verbatim)
- `backend/app/core/deps.py` (existing `get_current_user`, `require_admin`, `get_ai_provider` patterns)
- `backend/app/models/{variant,shopping,group}.py` (baseline schema confirmation)
- `backend/alembic/versions/0000_baseline.py` (visibility enum + version int already in baseline)
- [WeasyPrint First Steps — doc.courtbouillon.org](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html) (authoritative install + verification cmd `python -m weasyprint --info`)
- [APScheduler 3.x User Guide — apscheduler.readthedocs.io](https://apscheduler.readthedocs.io/en/3.x/userguide.html) (AsyncIOScheduler + CronTrigger + tz)
- [APScheduler CronTrigger — apscheduler.readthedocs.io](https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html) (DST behavior documentation)

### Secondary (MEDIUM confidence)
- [Installing WeasyPrint on Windows — gist.github.com/doobeh](https://gist.github.com/doobeh/3188318) (community Windows install gist; verified against official docs)
- [PWA iOS Limitations and Safari Support 2026 — magicbell.com](https://www.magicbell.com/blog/pwa-ios-limitations-safari-support-complete-guide) (BroadcastChannel iOS standalone PWA support)
- [BroadcastChannel Browser Compatibility — testmu.ai](https://www.testmu.ai/web-technologies/broadcastchannel-safari/) (Safari 15.4+ confirmation)
- [HTTP 412 Precondition Failed — dev-toolbox.tech](https://www.dev-toolbox.tech/tools/http-status-codes/codes/412-precondition-failed) (semantic comparison vs 409 — locked 409)
- [FastAPI + ETags + Conditional Writes — Medium @kaushalsinh73](https://medium.com/@kaushalsinh73/fastapi-etags-conditional-writes-prevent-lost-updates-without-heavy-locking-d517c91c9850) (optimistic concurrency pattern reference)
- [Tom Schoonjans GTK3 runtime installer — github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer) (alternative Windows GTK install, named in WeasyPrint v52.5 docs)

### Tertiary (LOW confidence — flagged for plan-time validation)
- Italian quantity parser: no PyPI library targets Italian recipes; design is custom heuristic (Pattern 3). Verify against real Stefano+Marta plans Plan 02-04.
- 7-day GTK3 spike duration: no published benchmark for "WeasyPrint Windows Server stability over X days" — A6 assumption, project-owner-judgment-based.
- Phosphor `Wine` glyph reading as decanter/condiment vs literal wine bottle — UI-SPEC §6.5 + revision 2 fix flag 1 corrected this; designer call within token system.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — every dep already in Phase 1 except WeasyPrint/ReportLab/APScheduler which are tightly bounded additions with mainstream support
- Architecture: HIGH — every pattern inherits from Phase 1 or is a textbook well-known primitive (HTTP precondition, async scheduler, Alembic data migration, cross-user dependency, BroadcastChannel)
- Pitfalls: HIGH for inherited #1-#12; MEDIUM for new #14-#19 — all are reasoned from CONTEXT decisions + Phase 1 lessons, not field-tested in Phase 2 production yet

**Research date:** 2026-05-02
**Valid until:** 2026-06-01 (30 days for stable stack; refresh if WeasyPrint releases breaking change or Plan 02-01 spike outcome changes ABC choice)
