# Phase 2: Differentiators - Context

**Gathered:** 2026-05-02 (auto mode)
**Status:** Ready for UI design + planning

<domain>
## Phase Boundary

Wellness Buddy diventa strumento settimanale reale per la famiglia Brunelli: vista settimanale + variant selector A/B/Pasta speciale, lista spesa auto-aggregata con esportazione PDF brand-consistent, multi-user family sync con badge "condiviso" e gestione grazia dei conflitti di edit concorrenti. Questa fase esprime i differenziatori competitivi vs Eat This Much / Plan to Eat / Prospre. Phase 1 production deploy + iPhone install + Lighthouse PWA validation **assorbiti in Phase 2** (deferred T3 dal pause gate Phase 1).

**In scope:**
- WEEK-01..05: vista settimanale + variant selector + summary endpoint
- SHOP-01..08: lista spesa aggregata + categorie + checkbox + reset settimanale + PDF
- FAM-01..09: Group entity attivata + visibility enum + badge condiviso + LWW + 409 toast + authz matrix
- DEP-06: WeasyPrint GTK3 spike Windows Server (validate prima di lockare)
- Plan 08 T3 deferred items: deploy DEPLOY.md walkthrough + win-acme + iPhone install + Lighthouse PWA 100/100 + Stefano+Marta tone sign-off (mid-phase, vedi D-26)

**Out of scope (vedi Deferred Ideas):**
- Fuzzy ingredient matching ("pomodorini" ≠ "pomodori" rimangono separati Phase 2)
- WebSocket/SSE real-time (polling 30s lockato per FAM-09)
- Mascot custom + Lottie celebrations (Phase 3)
- Push notifications lunedì pesata (Phase 3)
- Dashboard KPI (Phase 3)
- Admin panel (Phase 4)
- AI features (Phase 5 — widget Phase 2 resta locked placeholder per D-26 Phase 1)

</domain>

<decisions>
## Implementation Decisions

### Variant model
- **D-01:** Variant naming locked verbatim REQ WEEK-03: "Opzione A" / "Opzione B" / "Pasta speciale". No free-text varianti Phase 2.
- **D-02:** Variant override granularity = **per-meal-day** (ogni `(week_start, day, meal_slot)` ha la propria scelta). Default = "Opzione A".
- **D-03:** Default variant inheritance: nuova settimana mai visitata → tutti i pasti default "Opzione A". Persistenza server-side keyed by `(user_id, week_start, day, meal_slot)` su tabella `WeeklyPlanVariant` (già in schema Plan 02).
- **D-04:** Endpoint summary ritorna macro aggregati settimana basati su varianti scelte: `{kcal_total, protein_g, carbs_g, fat_g, days: [...]}` (WEEK-05).

### Shopping list aggregation
- **D-05:** Ingredient unit normalization: parse stringhe quantità italiane in `(amount, unit)` strutturato (`200g` → `(200, 'g')`, `1 confezione` → `(1, 'confezione')`, `2 cucchiai` → `(2, 'cucchiai')`, `1 pizzico` → `(1, 'pizzico')`). Merge same-name+same-unit; lista separata quando units divergono (es. "Pasta — 400 g · 2 confezioni"). Phase 2 ships heuristic dictionary in `backend/app/services/ingredient_parser.py`, NOT full NLP.
- **D-06:** Fuzzy name matching: **NO Phase 2**. Exact match dopo lowercase + NFC + trim. "pomodorini" e "pomodori" restano separati. Synonym dictionary deferred Phase 5 AI.
- **D-07:** Categorization SHOP-04 lista fissa locked: Frigo & Freschi / Frutta & Verdura / Dispensa / Condimenti / Integratori. Plan parser estende grammar opzionale `**Categoria:** <nome>` per ogni ingredient block (default "Dispensa" se assente). Mapping tabellare keyword italiana in `backend/app/services/category_mapper.py` come fallback (es. "yogurt"→Frigo, "pomodoro"→Frutta&Verdura).
- **D-08:** Week start = **lunedì** (convenzione italiana, REQ SHOP-08). UI week picker date-fns `startOfWeek({ weekStartsOn: 1 })`.
- **D-09:** Reset settimanale automatico lunedì 00:00 IANA tz user (SHOP-08). Server cron via APScheduler già installato (Phase 1) → job `reset_shopping_lists_at_user_midnight`. Checkbox state cleared, item list re-aggregates da current week varianti.
- **D-10:** Checkbox persistence cross-device server-canonical: `ShoppingListState` table (già in schema Plan 02) keyed `(group_id, week_start, ingredient_canonical_name, ingredient_unit)`. Client = Dexie cache + mutation queue (pattern Plan 06 esistente).

### PDF export (WeasyPrint)
- **D-11:** Plan 02-01 = **GTK3 spike** PRIMA di scrivere shopping list code che dipende da PDF. 7-day stability run su Windows Server staging. Soglia fallback: 5xx >2% in 7d → attiva ReportLab branch (`backend/app/services/pdf_export.py` con strategy interface). Spike report committato in `.planning/phases/02-differentiators/02-01-GTK3-SPIKE.md`.
- **D-12:** PDF brand: HTML+CSS template `backend/app/templates/shopping_list.html` consuma stessa palette `@theme` Lifesum Pure (`frontend/src/styles/theme.css` mirror). Drift impossibile via shared OKLCH coords token.
- **D-13:** Italian accents: WeasyPrint native font support (Plus Jakarta Sans woff2 embedded in HTML), verifica iPhone Safari + Mail.app a fine Phase 2 prima del pause gate.
- **D-14:** ReportLab fallback wiring: scaffolded (interface + null impl) Plan 02-01 spike, attivato SOLO se spike fallisce. Branching nascosto dietro service `PdfExporter` ABC.

### Family sync (Group entity activation)
- **D-15:** Visibility defaults verbatim REQ FAM-02: cene + pranzi `group_shared`, colazione + spuntini `private`. User override per-meal toggle in MealCard `⋯` menu (Phosphor `DotsThreeOutline` icon → dropdown con switch "Condividi con la famiglia").
- **D-16:** Real-time strategy verbatim REQ FAM-09: TanStack Query `refetchOnFocus: true` + `staleTime: 30_000`. NO WebSocket. NO Server-Sent Events Phase 2. Convergence ≤5s validata in test concorrente.
- **D-17:** Conflict UX: PATCH endpoint accetta `If-Unmodified-Since` header derivato da `WeeklyPlanVariant.updated_at` (FAM-04). Mismatch → 409 con body `{detail, code: "version_conflict", conflicting_user: "Marta"}`. Frontend mostra toast italiano da nuova chiave `copy.sync.conflictToast: "Aggiornato da {nome}. Ricarica per vedere l'ultima versione."` (FAM-05).
- **D-18:** "Condiviso" badge UI: piccolo Phosphor `UsersThree` icon + caption nome partner inline accanto al meal title. Mai blocca layout, tap → tooltip Radix con timestamp ultima edit ("aggiornato 2 min fa"). Il badge appare solo per pasti `visibility=group_shared` di altri utenti dello stesso gruppo.

### Authz extension
- **D-19:** Cross-user reads SEMPRE via `get_user_with_group_access(target_user_id)` dependency (FAM-06). Endpoint matrix che richiedono extension: `GET /api/today?user_id=...`, `GET /api/weekly/{week_start}?user_id=...`, `GET /api/shopping/{week_start}?user_id=...`.
- **D-20:** `group_id` MAI in JWT (FAM-07). Re-look-up da DB ogni request via `get_user_with_group_access`.
- **D-21:** Negative-authz test matrix CI (FAM-08): 8 endpoints × 5 scenari (own / shared-via-group / private-other-user / non-family / ex-member dopo group change) = 40 test minimum. File `backend/tests/integration/test_family_authz_matrix.py`. Cross-user reads non autorizzati ritornano 404 (info-disclosure mitigation, pattern Phase 1 ereditato).

### Migration strategy (Group activation)
- **D-22:** Alembic migration data-only `0001_activate_groups.py`: per ogni User esistente crea `Group(name=user.full_name + " · household", created_at=now())` + `user.group_id = group.id`. Idempotente (skip se già assegnato).
- **D-23:** No schema changes — Group + visibility enum + WeeklyPlanVariant.version già nel baseline Plan 02. Migration solo data backfill.
- **D-24:** Admin merge gruppi → deferred Phase 4 admin panel.

### iOS Safari quirks
- **D-25:** Multi-tab sync shopping list checkbox via BroadcastChannel API. Se Safari iOS 15.x non supporta → fallback `window.addEventListener('focus', refetch)`. Detection runtime `'BroadcastChannel' in window`.

### Plan 08 T3 deferred — production deploy mid-phase
- **D-26:** **Plan 02-03 = production deploy CHECKPOINT** posizionato a metà Phase 2 (DOPO `/week` + variant selector ship in Plan 02-02; PRIMA di Plan 02-04 shopping list). Stefano esegue DEPLOY.md su Windows Server 2019: PostgreSQL CREATE DATABASE → `uv sync --frozen` → Alembic upgrade → `pwsh deploy/scripts/generate-secrets.ps1` → NSSM install → IIS reverse proxy → win-acme cert per `wellness-buddy.epartner.it` → smoke test 200.
- **D-27:** Stefano + Marta validation: iPhone Safari install via Share menu → verifica offline `/today` (post Plan 09 Lifesum Pure rendering) + variant selector → kill app → reopen → no logout storm. Sign-off in `.planning/phases/02-differentiators/02-03-DEPLOY-CHECKLIST.md` con ✓ per ogni criterio Phase 1 pause gate originale.
- **D-28:** Lighthouse PWA score ≥95 + accessibility ≥95 misurato sulla URL HTTPS produzione (`https://wellness-buddy.epartner.it/today`). Risultati committati nel checklist.

### Performance
- **D-29:** Shopping list con ~336 righe: NO virtualization Phase 2. Flat scroll list. Threshold per introdurre virtualization: >500 righe (sposta a Phase 4 hardening se cresce).
- **D-30:** Weekly view pre-fetch ±1 week con `useWeeklyQuery({ week_start })` per swipe navigation smoothness.

### Visual regression baselines
- **D-31:** Plan 09 left TODO comments in `frontend/tests/visual/{light,dark}.spec.ts`. Rigeneration step incluso in Plan 02-02 (`/week` view) come prima azione: `pnpm test:visual --update-snapshots` → commit baselines → run CI per validare match.

### AI widget
- **D-32:** AI widget Phase 2 = locked placeholder invariato (D-26 Phase 1 carried forward). NO surface change. Sprint 5 owns activation.

### Italian copy expansion
- **D-33:** ~30 new strings in `frontend/src/i18n/copy.it.ts` sotto namespaces nuovi:
  - `week.*` (heading, dayLabels Lun-Dom, variantA/B/Special, summarySection)
  - `shopping.*` (heading, categoryFridge/Veggie/Pantry/Condiments/Supplements, exportTxt/PDF, resetToast, dayView)
  - `family.*` (sharedBadge, lastEditAgo, sharePerMealToggle)
  - `sync.conflictToast` (toast 409 di FAM-05)
  - `pwa.installFollowUp` (post-deploy iPhone install help)
  - Pattern FND-09 source-of-truth invariato.

### Wave structure (suggested — planner-flexible)
- **D-34:** Wave shape raccomandato:
  - **W1**: Plan 02-01 — GTK3 WeasyPrint spike Windows Server (gating subsequent PDF work)
  - **W2**: Plan 02-02 — `/week` vista + variant selector backend+frontend (REQ WEEK-01..05) + visual baseline regen
  - **W3**: Plan 02-03 — Production deploy CHECKPOINT human-verify (Stefano DEPLOY.md walkthrough + iPhone install + Lighthouse) ← Plan 08 T3 deferred dissolved here
  - **W4**: Plan 02-04 — Shopping list aggregation + categorie + checkbox + Dexie persistence + reset cron (REQ SHOP-01..06, SHOP-08)
  - **W5**: Plan 02-05 — PDF export WeasyPrint + brand template + iPhone Safari/Mail accent verification (REQ SHOP-07)
  - **W6**: Plan 02-06 — Family sync activation: Group migration + visibility enum + condiviso badge + 409 conflict UX + authz matrix tests (REQ FAM-01..09, DEP backfill)
  - **W7**: Plan 02-07 — Phase 2 closure: integration tests cross-feature + axe-core run + tone review Stefano+Marta confirms Phase 2 surfaces match Lifesum Pure quality + Phase 2 verifier goal-backward

### Claude's Discretion
- Exact `WeeklyPlanVariant.version` increment strategy (auto-increment SQL trigger vs explicit service)
- TanStack Query key shape (`['weekly', userId, weekStart]` vs flat)
- Phosphor icon choice per shopping category (Snowflake/Carrot/Package/Wine/Pill OR similar — designer call within token system)
- Exact 5xx threshold timing in 7-day spike (project owner decides if mid-spike trip OR end-of-spike summary)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope + requirements
- `.planning/PROJECT.md` — vision, WIN REQUISITE UI/UX, Brunelli use case
- `.planning/REQUIREMENTS.md` §WEEK §SHOP §FAM §DEP-06 — locked acceptance criteria
- `.planning/ROADMAP.md` §"Phase 2: Differentiators" lines 82-114 — goal, success criteria, pause gate

### Phase 1 carry-forward
- `.planning/phases/01-foundation/01-CONTEXT.md` — 33 locked decisions D-01..D-33 (palette, fonts, auth, AI, group entity in schema, etc.) all carry forward
- `.planning/phases/01-foundation/01-UI-SPEC.md` — design contract Lifesum Pure approved 6/6
- `.planning/phases/01-foundation/01-08-tone-calibration-checklist.md` — variant A locked + Plan 08 T3 deferral note (absorbed into D-26..D-28 here)
- `.planning/phases/01-foundation/VERIFICATION.md` — Phase 1 14/15 PASS verdict + remaining human-verifiable items

### Architecture + research
- `.planning/research/ARCHITECTURE.md` — 3-tier offline-first, server canonical truth, Dexie cache+outbox patterns
- `.planning/research/STACK.md` — WeasyPrint primary + ReportLab fallback decision context
- `.planning/research/PITFALLS.md` — #5 BOM normalization, #7 dark mode pitfalls, GTK3 Windows fragility (DEP-06)

### Visual ground truth
- `mockups/tone-calibration-v2/A-lifesum-pure.html` — locked design contract (Lifesum Pure variant A); Phase 2 components must converge on this rendering
- `frontend/src/styles/theme.css` — production OKLCH tokens (post Plan 09); shopping list PDF template MUST mirror these
- `frontend/src/i18n/copy.it.ts` — Italian copy single-source pattern (FND-09)

### Code patterns (Phase 1 deliverables)
- `backend/app/services/{plan_service,today_service,weight_service,workout_service}.py` — service layer pattern Phase 2 extends
- `backend/app/api/{plans,today,weight,workout}.py` — FastAPI endpoint pattern + envelope `{detail, code}`
- `backend/app/services/auth_service.py` — refresh rotation + 10s grace
- `backend/app/parsers/{normalizer,plan_parser,plan_sections}.py` — tolerant parser pattern (extend per `**Categoria:**` annotation)
- `frontend/src/components/today/MacroRing.tsx` — signature SVG hero pattern (replicable for week view summary)
- `frontend/src/services/today.ts` — TanStack Query mutation + optimistic update + Dexie cache pattern
- `frontend/src/components/icons/index.ts` — Phosphor facade (Phase 2 adds Users/UsersThree, Snowflake, Carrot, Package, Wine, Pill, DotsThreeOutline)
- `frontend/src/lib/{mutationQueue,refreshTokenAtomic,format}.ts` — offline-first plumbing
- `frontend/src/db/dexie.ts` — schema v1 cache_* tables (Phase 2 extends with `cache_weekly`, `cache_shopping`)

### Deploy
- `DEPLOY.md` — Windows Server 2019 walkthrough (16 sezioni, Plan 08 deliverable)
- `deploy/nssm/install-service.ps1` + `deploy/iis/web.config` + `deploy/scripts/{generate-secrets,smoke-test}.ps1` — pronti
- `deploy/win-acme/README.md` — Let's Encrypt cert per `wellness-buddy.epartner.it`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets (from Phase 1)
- **Service layer pattern**: `plan_service`, `today_service`, `weight_service`, `workout_service` show the established async SQLAlchemy + Pydantic v2 + audit log shape. Phase 2 services (`weekly_service`, `variant_service`, `shopping_service`, `pdf_export`, `ingredient_parser`, `category_mapper`) follow same template.
- **Phosphor icon facade**: `frontend/src/components/icons/index.ts` — Phase 2 adds Users/UsersThree, Snowflake, Carrot, Package, Wine, Pill, DotsThreeOutline. Single import surface.
- **MacroRing component**: replicable for `/week` summary (weekly macro aggregation as multi-arc ring).
- **MealCard layout**: Phase 2 extends with "Condiviso con {nome}" badge slot + variant chooser dropdown.
- **TanStack Query persister**: cache_* + mutation_queue Dexie pattern from Plan 06 → extend with `cache_weekly`, `cache_shopping`.
- **APScheduler**: backend already includes (Phase 3 push) — Phase 2 reuses for shopping list reset cron lunedì 00:00 user tz.
- **Cross-user dependency stub**: `backend/app/core/deps.py::get_user_with_group_access` defined (FAM-06 plumbing) — Phase 2 wires real lookup.

### Established Patterns
- **API error envelope** `{detail: italian, code: snake_case}` consistent across Phase 1 endpoints. Phase 2 inherits.
- **Italian copy single source** `frontend/src/i18n/copy.it.ts` — Phase 2 extends namespaces, NEVER inline strings.
- **Offline-first**: server canonical truth, Dexie cache + mutation_queue. Phase 2 cache_weekly/cache_shopping follow DROP-and-refetch contract.
- **Authz negative tests** pattern from Plan 04 `test_plans_api.py::test_activate_other_user_plan_403` — extend for FAM-08 matrix.
- **Visual regression** Playwright `toHaveScreenshot()` `maxDiffPixelRatio=0.02` — baselines need regen first (D-31).
- **Hex-ban ESLint rule**: zero hex literals in `frontend/src/`. Phase 2 inherits.
- **Phosphor facade rule**: zero direct `@phosphor-icons/react` imports outside `components/icons/index.ts`. Phase 2 inherits.

### Integration Points
- **`/today` page**: gains "Condiviso con {nome}" badge slot on MealCard (FAM-03). Existing aggregator extends to include partner's shared meals.
- **`/storico` page**: unchanged Phase 2 (Phase 3 owns dashboard expansion).
- **Plan parser**: extends optional `**Categoria:**` line per ingredient block. Backward compat — fixtures Plan 04 senza category restano green (default "Dispensa").
- **`AppShell`**: bottom tab bar gets `/spesa` icon (Phosphor `ShoppingCart`) and `/settimana` icon (Phosphor `CalendarBlank`).
- **Backend routers**: new `app/api/{weekly,shopping,family}.py` + extend `app/api/today.py` for cross-user reads.
- **Dexie schema bump**: v1 → v2 con cache_weekly + cache_shopping. Plan 06 mutation_queue rimane opaque-HTTP-requests (PITFALLS #5).

</code_context>

<specifics>
## Specific Ideas

- Vista settimanale stile Lifesum "weekly overview" ma con Italian editorial twist locked Phase 1 (Lifesum Pure variant A è il design language)
- Shopping list category icons devono sembrare "kitchen objects", non "office tags" (Phosphor: Snowflake/Carrot/Package/Wine/Pill, NOT generic shapes)
- PDF shopping list deve sentirsi come "lista che Marta scriverebbe a mano e plastificherebbe per il frigo", non "office report" — typography Plus Jakarta + Fraunces accent OK, MAI Helvetica/Times
- Badge "condiviso" deve essere semantico ma non rumoroso — piccolo Phosphor UsersThree + nome, non bordo colorato vistoso
- Conflict toast tone: spiega chi ha modificato, suggerisce ricarica, mai panic/error tone (no `!`)
- Variant selector: dropdown stile Lifesum, NON tabs orizzontali (mantiene tap targets ≥44px su mobile)
- Week picker: stile chip-row settimane recenti + jump-to-date (NON full calendar modal — overkill su iPhone 390px)

</specifics>

<deferred>
## Deferred Ideas

### To Phase 3 (Engagement)
- Mascot custom (water-droplet o scale-spirit, NON avocado) — review tone con Stefano+Marta dopo Phase 2 ship
- Lottie celebrations per first weekly streak completed
- Dashboard KPI con adherence ring (Phase 3 calcola da Phase 2 variant data)
- Push notification lunedì pesata + DST handling

### To Phase 4 (Admin & Hardening)
- Admin panel per merge gruppi famiglia
- Row-Level Security PostgreSQL defense-in-depth oltre logica applicativa
- Stress test mattina lunedì simultaneo
- Shopping list virtualization se cresce >500 righe

### To Phase 5 (AI)
- Fuzzy ingredient matching synonym dictionary ("pomodorini" ≈ "pomodori")
- AI shopping suggestions ("hai mancato basilico per la ricetta del pranzo")
- Plan editor con AI-assisted variant generation
- Streaming chat AI widget activation

### Out of scope (mai)
- Mobile native iOS/Android app
- Wearable integration Garmin/Apple Watch
- Barcode scanner alimenti
- USDA food database
- Sistema billing/subscription

### Reviewed Todos (not folded)
None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-differentiators*
*Context gathered: 2026-05-02 (auto mode — recommended defaults selected for all 12 gray areas; user can revise via direct CONTEXT.md edit before plan-phase)*
