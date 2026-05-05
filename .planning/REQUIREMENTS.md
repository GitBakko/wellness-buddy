# Requirements: Wellness Buddy

**Defined:** 2026-05-01
**Core Value:** L'utente segue il piano nutrizionale in modo aderente e visibile — ogni pasto chiaro, spesa generata, peso e allenamento tracciati senza attrito

## v1 Requirements

Requirements per release v1 (Sprint 1-5). Ogni requisito mappa a una fase roadmap.

### Foundation (Sprint 1)

- [ ] **FND-01**: Monorepo pnpm workspaces con `frontend/` (React 19 + Vite 7 + TailwindCSS 4) e `backend/` (FastAPI Python 3.12) configurato con linter (ESLint 9 flat, Prettier, ruff, mypy)
- [ ] **FND-02**: Database PostgreSQL `WellnessBuddy` creato + Alembic init con migration baseline
- [ ] **FND-03**: Backend FastAPI skeleton con SQLAlchemy 2 async + asyncpg pool 15/10 + lifespan startup
- [ ] **FND-04**: Frontend Vite skeleton con React 19 + TailwindCSS 4 `@theme` tokens + shadcn/ui CLI inizializzato + Geist Sans/Mono + lucide-react + sonner + Motion v12
- [ ] **FND-05**: PWA shell con vite-plugin-pwa, manifest (icons 192/512, theme color, display standalone), Service Worker con strategia NetworkFirst per `index.html` + CacheFirst hashed assets
- [ ] **FND-06**: Update flow PWA con `/version.json` polling + toast "Nuova versione disponibile" + `skipWaiting` + postMessage
- [ ] **FND-07**: Dexie schema con `cache_*` tables + `mutation_queue` + `drafts` (UUIDs server-generated), upgrade hooks documentate
- [x] **FND-08**: `navigator.storage.persist()` request flow dopo first login + rilevamento Dexie-empty-but-JWT-valid → full-resync da server (Plan 01-03 ships PersistStorageWelcome + lib/persistStorage; Plan 01-06 ships useDexieResync hook)
- [x] **FND-09**: Italian-only constant file (`copy.it.ts`) con tutti label/messaggi/errori UI (Plan 01-05b — 114 strings, 13 namespaces, UI-SPEC §7.2 verbatim)

### Authentication (Sprint 1)

- [x] **AUTH-01**: User può effettuare login con email + password (Plan 01-03)
- [x] **AUTH-02**: User può effettuare logout da qualunque pagina (revoca refresh token) (Plan 01-03)
- [x] **AUTH-03**: Sessione utente persiste tra refresh browser (refresh token rotation) (Plan 01-03)
- [x] **AUTH-04**: Access token JWT in memory (Zustand) con scadenza 15 minuti (Plan 01-03)
- [x] **AUTH-05**: Refresh token in HttpOnly+Secure+SameSite=Lax cookie scoped `/api/auth` con scadenza 7 giorni (Plan 01-03)
- [x] **AUTH-06**: Refresh token rotation con family-revocation su reuse detection (Plan 01-03)
- [x] **AUTH-07**: Singleton refresh promise client-side (tutti 401 await in-flight refresh) (Plan 01-03)
- [x] **AUTH-08**: Server-side 10s idempotent grace window per evitare logout storm iPhone resume (Plan 01-03)
- [x] **AUTH-09**: User può registrarsi solo con token invito valido (no signup pubblico) (Plan 01-03)
- [x] **AUTH-10**: Admin può generare token invito (24h expiry, single-use, revocable) (Plan 01-03)
- [x] **AUTH-11**: Endpoint `GET /api/auth/me` ritorna profilo user corrente (Plan 01-03)
- [x] **AUTH-12**: API errors sempre JSON `{detail: string, code: string}` (Plan 01-03)

### Data Models (Sprint 1)

- [ ] **MOD-01**: Modello `User` (id, email, username, hashed_password, role admin|user, group_id FK, timezone IANA default `Europe/Rome`, created_at TIMESTAMPTZ)
- [ ] **MOD-02**: Modello `Group` (id, name) — esiste in schema Sprint 1 anche se family sync arriva Sprint 2
- [ ] **MOD-03**: Modello `NutritionPlan` (id, user_id, name, raw_md, parsed_json JSONB, uploaded_at, is_active)
- [ ] **MOD-04**: Modello `WeeklyPlanVariant` (id, user_id, plan_id, week_start, day_of_week, meal_type, variant_key, visibility enum private|group_shared, version int per LWW)
- [ ] **MOD-05**: Modello `WorkoutLog` (id, user_id, date, trained bool, duration_min, calories_burned, workout_type, notes) — visibility sempre private
- [ ] **MOD-06**: Modello `WeightLog` (id, user_id, date, weight_kg) — visibility sempre private
- [ ] **MOD-07**: Modello `ShoppingListState` (id, user_id, week_start, items_json checklist serializzata, version int)
- [ ] **MOD-08**: Modello `InviteToken` (id, token, created_by, used_by nullable, expires_at, revoked bool)
- [ ] **MOD-09**: Tutte timestamp colonne sono TIMESTAMPTZ + UTC storage + IANA tz su User
- [ ] **MOD-10**: Indici time-series su `workout_log(user_id, date)`, `weight_log(user_id, date)`, `weekly_plan_variant(user_id, week_start)`

### Markdown Plan Parsing (Sprint 1)

- [ ] **PLAN-01**: User (admin) può caricare file `.md` piano nutrizionale via multipart/form-data
- [ ] **PLAN-02**: Parser estrae sezioni (case-insensitive heading match by stem, prefissi emoji tollerati): DATI PERSONALI, CALCOLO CALORICO E MACRO TARGET, STRUTTURA GIORNALIERA, COLAZIONE, PRANZI, CENE, SPUNTINO POMERIGGIO, SUPPLEMENTAZIONE, PROIEZIONE PESO, REGOLE FONDAMENTALI
- [ ] **PLAN-03**: Parser normalizza input: `utf-8-sig` BOM strip → `\r\n→\n` → NFC unicode → NBSP→space → smart-punct→ASCII
- [ ] **PLAN-04**: Parser robusto su corpus evil-input (Word/Notes.app/Notion/Obsidian/Notepad) — testato in CI
- [ ] **PLAN-05**: Sezioni non riconosciute loggate ma non bloccano parsing
- [ ] **PLAN-06**: Validazione strict via Pydantic v2 schema (`PlanParsedSchema`) downstream del parser tollerante
- [ ] **PLAN-07**: Piano caricato archiviato con timestamp, vecchi piani non eliminati
- [ ] **PLAN-08**: User può attivare un piano (POST `/api/plans/{id}/activate`) — disattiva precedenti
- [ ] **PLAN-09**: Diff view base tra piano nuovo e piano attivo prima di applicare (lista sezioni cambiate)
- [ ] **PLAN-10**: Un piano può essere assegnato a uno o più utenti (admin via `POST /api/admin/users/{id}/assign-plan`)

### Today View & Daily Tracking (Sprint 1)

- [x] **TODAY-01**: Vista `/today` come landing page mostra pasti del giorno con varianti default selezionate (Plan 01-07)
- [x] **TODAY-02**: User può marcare pasto come completato (checkbox) — stato persistente (Plan 01-07)
- [x] **TODAY-03**: User può registrare allenamento giornaliero: trained sì/no, durata minuti, calorie (opzionale), tipo (testo libero), note (testo libero) (Plan 01-07)
- [x] **TODAY-04**: User può modificare/cancellare entry workout (Plan 01-07)
- [x] **TODAY-05**: User può registrare peso corporeo con data (default oggi) (Plan 01-07)
- [x] **TODAY-06**: User può modificare/cancellare entry peso (Plan 01-07)
- [x] **TODAY-07**: Indicatore visivo stato giorno: completato / parziale / pianificato (Plan 01-07 — DayStatusIndicator with leaf-green/neutral-half/neutral-outline tokens)
- [x] **TODAY-08**: Vista `/today` accessibile offline da Dexie cache + mutation queue per write (Plan 01-07 — useToday mirrors to cache_today, useLogWeight/useLogWorkout enqueue when navigator.onLine=false)

### Weight Tracking (Sprint 1, projection band Sprint 3)

- [x] **WEIGHT-01**: Grafico linea peso nel tempo (Recharts) con punti reali rilevati (Plan 01-07 — WeightChart with var(--color-neutral-700) stroke per UI-08 + PITFALLS#8)
- [x] **WEIGHT-02**: Storico tabellare peso completo (Plan 01-07 — WeightHistoryTable with edit-in-place + delete confirm; italianDateLong for row dates)
- [ ] **WEIGHT-03**: Curva proiezione teorica dal piano nutrizionale visualizzata sul grafico
- [ ] **WEIGHT-04**: Banda tolleranza ±0,5 kg/settimana (Recharts ReferenceArea)
- [ ] **WEIGHT-05**: Indicatore delta vs proiezione: "In linea / +X kg sopra target / -X kg sotto target"

### Workout Tracking (Sprint 1, calendar view Sprint 3)

- [x] **WORK-01**: Form giornaliero workout con toggle allenato/non allenato (Plan 01-07 — WorkoutForm with Switch toggle + conditional duration/type/calories/notes; trained=false alone is a valid minimal payload)
- [x] **WORK-02**: Storico workout filtrabile per range date (Plan 01-07 — GET /api/workout?start=&end= + WorkoutHistoryTable month-grouped Italian view)
- [ ] **WORK-03**: Calendario mensile con indicatori workout per giorno
- [ ] **WORK-04**: Grafico settimanale minuti/calorie allenamento

### Weekly Plan & Variants (Sprint 2)

- [ ] **WEEK-01**: Vista settimanale `/week` navigabile con week picker
- [ ] **WEEK-02**: Per ogni giorno: colazione, pranzo, cena, spuntini con macro target visualizzati
- [ ] **WEEK-03**: Variant selector per ogni pasto: Opzione A / Opzione B / Pasta speciale
- [ ] **WEEK-04**: Selezioni varianti settimanali persistenti (POST `/api/weekly/{week_start}/variant`)
- [ ] **WEEK-05**: Endpoint `GET /api/weekly/{week_start}/summary` ritorna riepilogo macro settimana

### Shopping List (Sprint 2)

- [ ] **SHOP-01**: Lista spesa auto-generata da varianti selezionate per settimana
- [ ] **SHOP-02**: Aggregazione intelligente: ingredienti uguali sommati tra colazione/pranzo/cena
- [ ] **SHOP-03**: Checkbox interattivi con stato persistente (Dexie + sync server)
- [ ] **SHOP-04**: Divisione per categoria italiana: Frigo & Freschi / Frutta & Verdura / Dispensa / Condimenti / Integratori
- [ ] **SHOP-05**: Vista alternativa "lista per giorno" (cosa serve lunedì, martedì, ecc.)
- [ ] **SHOP-06**: Esportazione lista come testo semplice (copia/condividi)
- [x] **SHOP-07**: Esportazione lista come PDF via WeasyPrint con brand Tailwind tokens (Italian accents nativi) (Plan 02-06 — shopping_list.html Jinja2 template + woff2 base64 inline + Esporta PDF blob download; Stefano iPhone Safari + Mail.app verification pending production deploy via 02-06-IPHONE-PDF-VERIFY.md)
- [ ] **SHOP-08**: Reset settimanale automatico ogni lunedì 00:00 (user timezone) con possibilità rollover

### Multi-User Family Sync (Sprint 2)

- [ ] **FAM-01**: User può appartenere a un gruppo (`Group`) — admin assegna group_id
- [ ] **FAM-02**: Cene e pranzi default `visibility=group_shared`; colazione e spuntini default `private`
- [ ] **FAM-03**: User può vedere pasti `group_shared` di altri membri stesso gruppo con badge "condiviso con [nome]"
- [ ] **FAM-04**: Conflict resolution last-write-wins con `If-Unmodified-Since` style version su PATCH
- [ ] **FAM-05**: Conflitto 409 → toast UX "Aggiornato da [nome] — ricarica per vedere ultima versione"
- [ ] **FAM-06**: Endpoint `get_user_with_group_access(target_user_id)` dependency per cross-user reads (mai riusare `get_current_user` per shared paths)
- [ ] **FAM-07**: `group_id` MAI in JWT — sempre re-look-up da DB
- [ ] **FAM-08**: Test matrix negative-authz in CI: own/shared/private/non-family/ex-member access patterns
- [ ] **FAM-09**: Polling TanStack Query (refetch on focus + 30s `staleTime`) per badge `condiviso` real-time (WebSocket deferred)

### Dashboard & KPI (Sprint 3)

- [ ] **DASH-01**: Card KPI: peso attuale, delta vs target, kg persi, settimane al target
- [ ] **DASH-02**: Streak allenamento: giorni consecutivi con workout registrato
- [ ] **DASH-03**: Aderenza piano: % giorni con pasti registrati settimana corrente
- [ ] **DASH-04**: Adherence ring (single elegant ring, no badges/XP/leaderboards)
- [ ] **DASH-05**: Prossima rilevazione peso: data lunedì successivo con countdown
- [ ] **DASH-06**: Notifica motivazionale (statica Sprint 3, AI-generated Sprint 5 se attiva)
- [ ] **DASH-07**: Grafici aggregati: peso nel tempo, minuti allenamento settimanali, calorie bruciate settimanali
- [ ] **DASH-08**: Lunedì check-in special copy + UI state ("È lunedì! Tempo della pesata")

### Push Notifications (Sprint 3)

- [ ] **PUSH-01**: VAPID keypair generato e persistito su server
- [ ] **PUSH-02**: User può opt-in a notifiche push da Settings (mai auto-prompt)
- [ ] **PUSH-03**: User subscription persistita server-side associata a user_id
- [ ] **PUSH-04**: Reminder pesata lunedì 07:00 in user IANA timezone (DST-aware)
- [ ] **PUSH-05**: APScheduler job settimanale che dispatcha push reminders
- [ ] **PUSH-06**: Test crossing DST boundary (last Sunday October + last Sunday March) green
- [ ] **PUSH-07**: Push notifications funzionano solo su PWA installata (iOS 16.4+ requirement)

### Engagement & Polish UI/UX (Sprint 3)

- [ ] **ENG-01**: Mascot character custom (water-droplet o scale-spirit, **non** trope avocado) con 3 espressioni
- [ ] **ENG-02**: Mascot appare solo a milestones + empty states, mai in chrome routine
- [ ] **ENG-03**: Lottie celebrations per: prima pesata, 7-day streak, weight goal hit (≤1 per session, ≤800ms)
- [ ] **ENG-04**: Rive in `/progress` hero per visualizzazione progress dinamica
- [ ] **ENG-05**: Plan diff view polish con semantic diff ("Pranzo Lunedì: Pasta integrale → Riso basmati")
- [ ] **ENG-06**: Tone calibration mockups Sprint 1 reviewed Stefano+Marta — locked design system

### Admin Panel (Sprint 4)

- [ ] **ADM-01**: Admin panel `/admin` (solo role=admin) con gestione utenti
- [ ] **ADM-02**: Admin può visualizzare lista utenti con stato (attivo, gruppo, piano attivo)
- [ ] **ADM-03**: Admin può generare/revocare token invito
- [ ] **ADM-04**: Admin può assegnare/aggiornare piano nutrizionale qualsiasi utente
- [ ] **ADM-05**: Admin può vedere storico piani per utente
- [ ] **ADM-06**: Audit log per azioni admin (chi ha fatto cosa quando)
- [ ] **ADM-07**: PostgreSQL Row-Level Security come defense-in-depth su tabelle group-scoped

### AI Layer Architecture (Sprint 1 stub, Sprint 5 active)

- [ ] **AI-01**: `AIProvider` abstract base class definita Sprint 1 con metodi `generate_meal_suggestion`, `analyze_week_progress`, `generate_shopping_tips`, `chat`
- [ ] **AI-02**: `NullProvider` implementato Sprint 1 — risponde "AI non disponibile" — default
- [ ] **AI-03**: AI provider DI singleton via `Depends(get_ai_provider)` da `app.state` lifespan startup
- [ ] **AI-04**: Endpoint `/api/ai/*` esistono Sprint 1 e ritornano 501 con NullProvider
- [ ] **AI-05**: Frontend AIWidget locked Sprint 1 con placeholder "AI non disponibile — coming soon"
- [ ] **AI-06**: Architettura WebSocket/SSE predisposta Sprint 1 per chat streaming Sprint 5
- [ ] **AI-07**: Configurazione via `.env`: `AI_PROVIDER=null|ollama|openai|anthropic`
- [ ] **AI-08**: `OllamaProvider` implementato Sprint 5 (GX10 ARM64, gemma3:27b, 60s first-request timeout, httpx.AsyncClient reuse)
- [ ] **AI-09**: `OpenAIProvider` implementato Sprint 5 con rate limit + max_tokens=500 + per-user daily quota
- [ ] **AI-10**: `AnthropicProvider` implementato Sprint 5 con stesso pattern
- [ ] **AI-11**: AI features Sprint 5: meal suggestion, week analysis, shopping tips, chat conversazionale
- [ ] **AI-12**: Frontend AI chat widget unlocked Sprint 5 con streaming SSE + skeleton placeholder + "Sto pensando..." dots
- [ ] **AI-13**: Prompt injection defense Sprint 5: `<user_note>...</user_note>` delimited prompts, output validation rifiuta email/JWT-looking strings
- [ ] **AI-14**: AI capabilities endpoint Sprint 5 + frontend feature detection (no Liskov-violating isinstance)
- [ ] **AI-15**: Kill-switch `AI_PROVIDER=null` env disabilita AI senza redeploy
- [ ] **AI-16**: Family isolation: AI context user-scoped, mai cross-user data in prompts

### Deployment (Sprint 1 + Sprint 5 hardening)

- [ ] **DEP-01**: Backend deploy come Windows Service via NSSM (Uvicorn 1 worker, port 8000)
- [ ] **DEP-02**: Frontend build statica servita da IIS o Nginx for Windows
- [ ] **DEP-03**: IIS/Nginx reverse proxy: `/api/*` → localhost:8000, `/*` → dist/
- [ ] **DEP-04**: SSL Let's Encrypt via win-acme su dominio configurabile
- [ ] **DEP-05**: File `.env` produzione con SECRET_KEY, DATABASE_URL, CORS_ORIGINS, AI_*, MAX_USERS=100, ADMIN_EMAIL
- [x] **DEP-06**: WeasyPrint GTK3 Runtime MSI installato + spike validation Sprint 2 (Plan 02-01 spike + Plan 02-06 endpoint live; Plan 02-08 production observability + Stefano iPhone sign-off)
- [ ] **DEP-07**: VAPID keys generated e persistite (Sprint 3)
- [ ] **DEP-08**: Docker Compose opzionale per dev/staging
- [ ] **DEP-09**: Documentazione DEPLOY.md con setup step-by-step Windows Server 2019

### WIN REQUISITE UI/UX (cross-cutting, ogni sprint)

- [ ] **UI-01**: TailwindCSS 4 `@theme` design tokens — colors OKLCH/HSL con dark variants, typography Geist, radius, motion
- [ ] **UI-02**: Mobile-first 390px → tablet → desktop con container queries
- [ ] **UI-03**: shadcn/ui + Radix primitives customizzati (no vanilla shadcn)
- [~] **UI-04**: Motion v12 per ogni state transition con motion budget enforced (≤250ms micro, ≤800ms celebration, ≤2 simultaneous moving elements) (Plan 01-05b — motion test infra + tokens; full enforcement at component level Plans 03/04/07)
- [x] **UI-05**: `prefers-reduced-motion: reduce` honored via `--motion-scale: 0` (full disable) (Plan 01-05b — useReducedMotion hook + motion.test.ts 4/4 + Playwright reducedMotion: 'reduce' global)
- [ ] **UI-06**: Touch microinteractions: every tap scales 0.97 con 80ms ease
- [ ] **UI-07**: Dark mode first-class — palette OKLCH con dark variants da day one
- [ ] **UI-08**: Recharts colors via CSS variables (mai hardcoded hex)
- [ ] **UI-09**: PWA manifest theme color con `media` queries dark/light
- [~] **UI-10**: axe-core in Playwright CI su ogni PR — fail at <4.5:1 body, <3:1 large/icons (Plan 01-05b — a11y.spec.ts wcag2aa scaffold; baseline pending Plans 03/04/07 page UI)
- [~] **UI-11**: Lighthouse a11y ≥95 su ogni route UI (Plan 01-05b — lighthouserc.json thresholds locked; baseline pending Plan 05a + page UI)
- [~] **UI-12**: Dark mode screenshot tests CI per ogni pagina (Plan 01-05b — visual/{light,dark}.spec.ts scaffold for 4 routes × 2 schemes; baselines pending real UI)
- [ ] **UI-13**: VoiceOver smoke test ogni sprint su real iOS device
- [ ] **UI-14**: Illustrations: decorative `aria-hidden="true"`, meaningful `<title>` + `aria-labelledby` Italian copy
- [ ] **UI-15**: Form errors: Italian copy + icon + `role="alert"` + color (mai color alone)
- [ ] **UI-16**: iOS keyboard: `visualViewport` API + scroll input into view
- [~] **UI-17**: Tone guardrails: no `!` in error messages, no infantile mascots, empty states minimalist Italian (Plan 01-05b — copy.it.ts compliance verified, no `!` in errors namespace)
- [x] **UI-18**: Italian formatting: `Intl.NumberFormat('it-IT')`, 24h time, NFC normalize, `Intl.Collator('it')` sorting (Plan 01-05b — lib/format.ts ships all four)
- [ ] **UI-19**: Emoji budget ≤1-2 per screen in copy only, mai in chrome
- [ ] **UI-20**: `impeccable:critique` + `impeccable:harden` run dopo ogni sprint close

## v2 Requirements (deferred, post-Sprint 5)

### Notifiche extra

- **NOTF-V2-01**: Notifica weekly summary domenica sera (opt-in)
- **NOTF-V2-02**: Notifica plan-updated-by-admin event

### Real-time

- **RT-V2-01**: WebSocket/SSE per badge `condiviso` real-time se polling 30s insufficiente
- **RT-V2-02**: Notifica push quando partner aggiorna pasto condiviso

### i18n

- **I18N-V2-01**: Refactor a `react-i18next` se utenti non-italiani emergono
- **I18N-V2-02**: Locale en-US/de-DE/fr-FR

## Out of Scope

| Feature | Reason |
|---------|--------|
| App mobile nativa iOS/Android | PWA sufficiente, riduce manutenzione |
| Wearable sync (Garmin/Apple Watch) | Calorie input manuale per v1, scope creep |
| Calcolo automatico calorie bruciate | Input manuale dall'utente |
| Barcode scanner alimenti | Anti-feature plan-driven, fuori dominio |
| Database alimenti USDA/INRAN | I piani MD sono fonte di verità |
| Sistema billing/subscription | Self-hosted gratuito famiglia |
| Registrazione pubblica | Solo invito per controllo utenza max 100 |
| Scaling oltre 100 utenti | Single-worker async sufficiente |
| Recipe library con foto | Anti-feature plan-driven |
| Calorie burn auto-calc | Input manuale |
| Social/feed/like features | Anti-feature, distrugge focus plan-driven |
| Badges/XP/levels/trophies/leaderboards | Engagement clichés, contraria a UI/UX elegant |
| Daily nag notifications | Notification budget 3 max/settimana |
| AI photo recognition pasti | Anti-feature, scope creep |
| In-app purchases | Self-hosted free |
| Public meal/plan sharing community | Anti-feature, distrugge privacy |
| Automatic workout detection | Input manuale |
| Micronutrient tracking | Macro sufficienti per piani Stefano/Marta |
| Meal photo journal | Anti-feature visuale |
| Recipe scaling | Out of scope, MD è fonte verità |
| WebSocket per shared meals real-time | v2 se polling 30s insufficiente |

## Traceability

**LOCKED 2026-05-01 during roadmap creation.** Ogni requisito v1 mappato a esattamente una fase. Cross-cutting UI-01 — UI-20 applicano a tutte le fasi come quality gate al pause gate di ogni fase.

| Requirement | Phase | Phase Name | Status |
|-------------|-------|------------|--------|
| FND-01 — FND-09 | Phase 1 | Foundation | Pending |
| AUTH-01 — AUTH-12 | Phase 1 | Foundation | Complete (Plan 01-03) |
| MOD-01 — MOD-10 | Phase 1 | Foundation | Pending |
| PLAN-01 — PLAN-10 | Phase 1 | Foundation | Pending |
| TODAY-01 — TODAY-08 | Phase 1 | Foundation | Complete (Plan 01-07) |
| WEIGHT-01, WEIGHT-02 | Phase 1 | Foundation | Complete (Plan 01-07) |
| WEIGHT-03, WEIGHT-04, WEIGHT-05 | Phase 3 | Engagement & Polish | Pending |
| WORK-01, WORK-02 | Phase 1 | Foundation | Complete (Plan 01-07) |
| WORK-03, WORK-04 | Phase 3 | Engagement & Polish | Pending |
| WEEK-01 — WEEK-05 | Phase 2 | Differentiators | Pending |
| SHOP-01 — SHOP-08 | Phase 2 | Differentiators | Pending |
| FAM-01 — FAM-09 | Phase 2 | Differentiators | Pending |
| DASH-01 — DASH-08 | Phase 3 | Engagement & Polish | Pending |
| PUSH-01 — PUSH-07 | Phase 3 | Engagement & Polish | Pending |
| ENG-01 — ENG-06 | Phase 3 | Engagement & Polish | Pending |
| ADM-01 — ADM-07 | Phase 4 | Admin & Hardening | Pending |
| AI-01 — AI-07 | Phase 1 | Foundation (ABC + NullProvider stub) | Pending |
| AI-08 — AI-16 | Phase 5 | AI Activation | Pending |
| DEP-01 — DEP-05, DEP-08, DEP-09 | Phase 1 | Foundation | Pending |
| DEP-06 | Phase 2 | Differentiators (WeasyPrint GTK3 spike + PDF endpoint) | Plan 02-01 + 02-06 done; production iPhone sign-off pending |
| DEP-07 | Phase 3 | Engagement & Polish (VAPID keys) | Pending |
| UI-01 — UI-20 | All Phases | Cross-cutting WIN REQUISITE | Pending |

**Coverage:**

- v1 requirements: ~145 totali
- Mapped to phases: 100%
- Unmapped: 0
- Duplicates: 0
- Locked: 2026-05-01

---
*Requirements defined: 2026-05-01*
*Traceability locked: 2026-05-01 during roadmap creation*
*Last updated: 2026-05-01 — traceability table verified and locked against ROADMAP.md*
