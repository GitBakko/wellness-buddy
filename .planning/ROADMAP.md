# Roadmap: Wellness Buddy

**Created:** 2026-05-01
**Granularity:** standard
**Mode:** yolo
**Total v1 requirements:** ~145
**Coverage:** 100% (every v1 REQ-ID mapped to exactly one phase)
**Phases:** 5
**Cross-cutting:** UI-01 â€” UI-20 (WIN REQUISITE UI/UX) apply to **every** phase

## Core Value Anchor

> L'utente segue il piano nutrizionale in modo aderente e visibile â€” ogni pasto chiaro, spesa generata, peso e allenamento tracciati senza attrito. Se tutto il resto fallisce: "vedo cosa devo mangiare oggi e segno il peso".

> **WIN REQUISITE (non-negotiable):** UI/UX a metÃ  tra eleganza/minimal e giocoso/friendly. Senza questo il progetto Ã¨ fallito.

## Phases

- [ ] **Phase 1: Foundation** â€” Stack scaffolding + auth + models + tolerant MD parser + PWA shell + `/today` + weight/workout log + AI ABC stub + Windows Server deploy + WIN REQUISITE UI/UX foundations
- [ ] **Phase 2: Differentiators** â€” Weekly view + variant selector A/B/Pasta + auto shopping list + WeasyPrint PDF (GTK3 spike) + multi-user family sync via Group/visibility + LWW conflict UX
- [ ] **Phase 3: Engagement & Polish** â€” Weight projection band + KPI dashboard + adherence ring + lunedÃ¬ check-in + push notifications (VAPID + DST-aware APScheduler) + plan diff polish + custom mascot + Lottie + Rive
- [ ] **Phase 4: Admin & Hardening** â€” Admin panel CRUD + invite tokens + plan assignment + audit log + PostgreSQL Row-Level Security + k6 load test + Vite 7â†’8 re-evaluation
- [ ] **Phase 5: AI Activation** â€” Ollama (GX10 ARM64 gemma3:27b) + OpenAI + Anthropic providers + meal/week/shopping AI features + chat widget unlocked with SSE streaming + prompt-injection defenses + cost caps + family isolation

## Phase Details

### Phase 1: Foundation

**Goal**: Un singolo utente puÃ² installare la PWA, fare login, caricare il piano MD e vedere `/today` con i pasti del giorno + registrare peso e allenamento â€” il valore minimo dichiarato in PROJECT.md ("vedo cosa devo mangiare oggi e segno il peso") Ã¨ raggiunto e deployato in produzione su Windows Server 2019, con WIN REQUISITE UI/UX foundations giÃ  in piedi (design tokens, dark mode, axe-core CI gate, motion budget).

**Depends on**: Nothing (first phase)

**Requirements**:
FND-01, FND-02, FND-03, FND-04, FND-05, FND-06, FND-07, FND-08, FND-09,
AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05, AUTH-06, AUTH-07, AUTH-08, AUTH-09, AUTH-10, AUTH-11, AUTH-12,
MOD-01, MOD-02, MOD-03, MOD-04, MOD-05, MOD-06, MOD-07, MOD-08, MOD-09, MOD-10,
PLAN-01, PLAN-02, PLAN-03, PLAN-04, PLAN-05, PLAN-06, PLAN-07, PLAN-08, PLAN-09, PLAN-10,
TODAY-01, TODAY-02, TODAY-03, TODAY-04, TODAY-05, TODAY-06, TODAY-07, TODAY-08,
WEIGHT-01, WEIGHT-02,
WORK-01, WORK-02,
AI-01, AI-02, AI-03, AI-04, AI-05, AI-06, AI-07,
DEP-01, DEP-02, DEP-03, DEP-04, DEP-05, DEP-08, DEP-09,
UI-01 â€” UI-20 (cross-cutting â€” foundations land here)

**Hard dependency locks honored**:
- `Group` entity in schema (MOD-02) â€” Sprint 1 even though family sync is Sprint 2 (avoid late FK migration churn)
- `TIMESTAMPTZ + IANA tz` on User (MOD-01, MOD-09) â€” DST correctness for Phase 3 push depends on it
- AI ABC + NullProvider (AI-01 â€” AI-07) â€” endpoints return 501 but type is locked
- Tolerant MD parser â†’ strict Pydantic split (PLAN-02 â€” PLAN-06) â€” must precede `/today`
- Refresh token rotation + family-revocation + 10s idempotent grace window (AUTH-06, AUTH-08) â€” prevents iPhone resume logout storm
- `navigator.storage.persist()` + Dexie-empty-but-JWT-valid resync (FND-07, FND-08) â€” iOS storage eviction defense
- NetworkFirst for `index.html` + version.json polling + skipWaiting toast (FND-05, FND-06) â€” SW staleness defense
- WIN REQUISITE foundations: Tailwind 4 `@theme` tokens, Geist Sans/Mono, lucide-react, Motion v12, sonner, axe-core CI â‰¥95, dark mode CI screenshot tests, `prefers-reduced-motion` honored, tone calibration mockups locked + reviewed by Stefano+Marta (UI-01 â€” UI-20)

**Success Criteria** (what must be TRUE):
1. **Solo install + login funziona end-to-end**: utente installa PWA su iPhone reale, riceve token invito, registra account, fa login, refresh browser e sessione persiste 7 giorni; logout revoca refresh token; resume da background dopo >15 min non causa logout storm
2. **Plan MD upload + parse + display**: admin carica piano MD reale Stefano (con BOM/CRLF/NBSP/smart quotes/emoji prefix), parser estrae tutte le sezioni canoniche tollerando input "evil-corpus", attiva il piano e `/today` mostra i pasti del giorno corrente con macro target
3. **Tracking minimo senza attrito**: utente registra peso (con grafico linea base, no proiezione ancora), marca pasto come completato, registra allenamento (trained sÃ¬/no + durata + note); tutti gli stati persistono offline via Dexie e sync al ritorno online via mutation queue
4. **Deploy produzione Windows Server 2019**: app live su `https://wellness-buddy.epartner.it` (o dominio configurato) servita da IIS/Nginx reverse proxy con SSL Let's Encrypt, backend Uvicorn-via-NSSM stabile, AI endpoint `/api/ai/*` ritorna 501 con NullProvider, frontend AIWidget mostra placeholder "AI non disponibile â€” coming soon"
5. **WIN REQUISITE foundations in piedi**: design tokens Tailwind 4 `@theme` consumati ovunque (zero hex hardcoded), dark mode parity verificata da CI screenshot test su ogni route esistente, axe-core CI gate verde su ogni PR (â‰¥4.5:1 body / â‰¥3:1 large), Lighthouse PWA 100/100 + a11y â‰¥95, motion budget rispettato (â‰¤250ms micro), `prefers-reduced-motion: reduce` disabilita animazioni via `--motion-scale: 0`, tone calibration mockups firmati da Stefano+Marta

**Pause Gate (exit criteria)**: Real iPhone install riuscita; offline `/today` testato; upgrade path da vecchia versione funziona (toast â†’ skipWaiting â†’ reload); resync dopo manual Dexie wipe ricostruisce la cache; axe-core verde; Lighthouse PWA 100/100; tone calibration approvata da entrambi gli utenti reali.

**Plans:** 10 plans

Plans:
- [x] 01-01-PLAN.md — Monorepo + tooling + Docker Compose dev postgres + GitHub Actions CI workflows (completed 2026-05-01, commits e9756c6, 2a9fb2e, 739de1d)
- [x] 01-02a-PLAN.md — Backend core: FastAPI + SQLAlchemy 2 async + 10 models + Alembic baseline + audit_service + Pydantic v2 base schemas + /api/health + /version.json (completed 2026-05-01, commits b4bf521, 011352b)
- [ ] 01-02b-PLAN.md — Backend AI layer: AIProvider ABC + NullProvider + factory + DI lifespan + stub routers (auth/plans/today/weekly/workout/weight/shopping/admin) + AI endpoints
- [x] 01-05a-PLAN.md — Frontend build: Vite + React 19 + Tailwind 4 @theme tokens + shadcn/ui 17 customized primitives + dark mode + ESLint hex ban + 4 PWA icons (completed 2026-05-01, commits fcd0795, e7bf9a5)
- [ ] 01-05b-PLAN.md — Frontend behavior: Italian copy.it.ts + format.ts + hooks (useReducedMotion/useOnline/useTheme) + Zustand stores + Vitest + Playwright + axe + visual diff + Lighthouse CI
- [ ] 01-03-PLAN.md — Auth: JWT 15min + refresh 7d rotation + 10s grace + family revocation + invite-only signup + frontend Zustand + singleton refresh promise + Login/Register pages + PersistStorageWelcome
- [ ] 01-06-PLAN.md — PWA shell: vite-plugin-pwa Workbox (NetworkFirst index, CacheFirst hashed, NetworkOnly auth+writes) + Dexie v1 schema + mutation_queue + persist() + update toast + AppShell layout + locked AIWidget
- [ ] 01-04-PLAN.md — MD parser tolerant pipeline + strict Pydantic v2 schema + evil-corpus fixtures (BOM/CRLF/NFD/emoji/Obsidian/NBSP) + /api/plans/* + admin assign-plan + frontend Plans page (dropzone + diff view)
- [ ] 01-07-PLAN.md — /today landing (Italian greeting Instrument Serif escape hatch + MealCard + MacroDisplay + WeightQuickLog + WorkoutForm + AIWidget) + /api/today + /api/weight + /api/workout CRUD + WeightChart (UI-08 CSS variable colors) + History + Settings
- [ ] 01-08-PLAN.md — Tone calibration mockups (3 variants A/B/C — Stefano+Marta sign-off blocking checkpoint) + complete DEPLOY.md (Windows Server 2019 + NSSM + IIS + win-acme) + smoke test script

**UI hint**: yes

---

### Phase 2: Differentiators

**Goal**: La famiglia Brunelli usa effettivamente l'app come strumento settimanale: scelgono varianti pasti A/B/Pasta speciale, ricevono lista spesa auto-aggregata stampabile in PDF brand-consistent, vedono i pasti condivisi del partner con badge "condiviso" e gestiscono in modo grazioso i conflitti di edit concorrenti. Questa fase esprime i veri differenziatori competitivi del prodotto rispetto a Eat This Much / Plan to Eat / Prospre.

**Depends on**: Phase 1 (Group entity in schema, auth, plan parser, models, design tokens)

**Requirements**:
WEEK-01, WEEK-02, WEEK-03, WEEK-04, WEEK-05,
SHOP-01, SHOP-02, SHOP-03, SHOP-04, SHOP-05, SHOP-06, SHOP-07, SHOP-08,
FAM-01, FAM-02, FAM-03, FAM-04, FAM-05, FAM-06, FAM-07, FAM-08, FAM-09,
DEP-06,
UI-01 â€” UI-20 (cross-cutting â€” every new component inherits tokens; PDF inherits brand via shared CSS variables)

**Hard dependency locks honored**:
- WEEK-* must precede SHOP-* (lista aggrega da varianti selezionate â€” locked in research)
- `get_user_with_group_access` dependency separato da `get_current_user` per cross-user reads (FAM-06)
- `group_id` MAI in JWT â€” sempre re-look-up da DB (FAM-07)
- Negative-authz test matrix in CI: own/shared/private/non-family/ex-member access patterns (FAM-08)
- WeasyPrint Sprint 2 spike valida GTK3 stability su Windows Server prima di lockare (DEP-06, SHOP-07) â€” fallback ReportLab documentato se 5xx >2% in 7 giorni
- LWW + `If-Unmodified-Since` style version + 409 â†’ toast UX (FAM-04, FAM-05, MOD-04 `version` int)

**Success Criteria** (what must be TRUE):
1. **Vista settimanale + variant selector funzionano**: utente naviga settimane via week picker, per ogni pasto sceglie Opzione A / Opzione B / Pasta speciale, le selezioni persistono server-side e il summary endpoint ritorna macro aggregati settimana
2. **Lista spesa auto-generata + esportabile**: dalla settimana di varianti scelte, lista spesa aggregata (ingredienti uguali sommati) con divisione per categoria italiana (Frigo & Freschi / Frutta & Verdura / Dispensa / Condimenti / Integratori), checkbox persistenti via Dexie+sync, vista alternativa "per giorno", esportazione testo (copia/condividi) e PDF via WeasyPrint con accenti italiani nativi e brand Tailwind tokens; reset settimanale automatico lunedÃ¬ 00:00 user timezone
3. **Multi-user family sync visibile**: Marta vede cene/pranzi di Stefano (e viceversa) marcati con badge "condiviso con [nome]"; colazione + spuntini restano private per default; admin assegna group_id; TanStack Query refetch on focus + 30s staleTime mantiene il badge convergente entro 5s
4. **Conflict UX grazioso**: due utenti che modificano lo stesso pasto condiviso ricevono 409 sul secondo PATCH e vedono toast "Aggiornato da [nome] â€” ricarica per vedere ultima versione"; nessun dato perso lato server (LWW determinato esplicitamente)
5. **WIN REQUISITE su nuovo terreno**: shopping-list PDF Ã¨ "loving home brand" non "office print" (review Stefano+Marta firmata), variant selector usa motion budget rispettato (â‰¤250ms transition), badge "condiviso" Ã¨ semantico ma non rumoroso, tutta UI Phase 2 mantiene contrasto WCAG AA in dark mode con CI screenshot tests

**Pause Gate (exit criteria)**: Family-sync authz tests verdi (matrix completa own/shared/private/non-family/ex-member); PDF shopping list rende correttamente accenti italiani su iPhone Safari + Mail.app; badge "condiviso" converge entro 5s in test concorrente; WeasyPrint GTK3 stabile in produzione (5xx <2% in spike di 7 giorni) â€” altrimenti decisione esplicita fallback ReportLab.

**Plans**: TBD

**UI hint**: yes

---

### Phase 3: Engagement & Polish

**Goal**: L'app diventa "delightful" â€” non solo funzionale ma quotidianamente coinvolgente: il dashboard KPI dÃ  feedback motivazionale calibrato, il rituale lunedÃ¬ pesata viene celebrato senza essere infantile, le notifiche push (DST-aware) ricordano la pesata, le animazioni Lottie celebrano milestones reali, il mascot custom appare solo nei momenti giusti, e Rive nel `/progress` hero rende il progresso visivo memorabile. Questa Ã¨ la fase dove WIN REQUISITE UI/UX entra nel suo punto piÃ¹ alto.

**Depends on**: Phase 1 (auth, weight log, workout log, design tokens, IANA tz on User), Phase 2 (weekly variants for adherence calculation)

**Requirements**:
WEIGHT-03, WEIGHT-04, WEIGHT-05,
WORK-03, WORK-04,
DASH-01, DASH-02, DASH-03, DASH-04, DASH-05, DASH-06, DASH-07, DASH-08,
PUSH-01, PUSH-02, PUSH-03, PUSH-04, PUSH-05, PUSH-06, PUSH-07,
ENG-01, ENG-02, ENG-03, ENG-04, ENG-05, ENG-06,
DEP-07,
UI-01 â€” UI-20 (cross-cutting â€” picco WIN REQUISITE: mascot + Lottie + Rive + lunedÃ¬ copy + dark mode parity)

**Hard dependency locks honored**:
- VAPID keys generated + persisted (DEP-07, PUSH-01) before push reminders (PUSH-04, PUSH-05)
- TIMESTAMPTZ + IANA tz on User (already locked Phase 1) â†’ DST-correct lunedÃ¬ 07:00 reminder (PUSH-04, PUSH-06)
- DST boundary tests in CI: last Sunday October + last Sunday March (PUSH-06)
- Push solo su PWA installata iOS 16.4+ â€” UI Settings opt-in mai auto-prompt (PUSH-02, PUSH-07)
- ENG-06 (tone calibration mockups review) propagato da Phase 1 â€” lock confermato qui prima di introdurre mascot
- Lottie â‰¤1 per session, â‰¤800ms, never blocks input (ENG-03, UI-04)
- Mascot **mai** in chrome routine â€” solo milestones + empty states (ENG-02)

**Success Criteria** (what must be TRUE):
1. **Weight tracking completo**: grafico peso con punti reali + curva proiezione teorica dal piano + banda tolleranza Â±0,5 kg/sett (Recharts ReferenceArea); indicatore delta vs target ("In linea / +X kg sopra / -X kg sotto") chiaro a colpo d'occhio in light/dark mode
2. **Dashboard KPI rituale**: utente apre `/dashboard` e vede in <2s peso attuale + delta vs target + kg persi + streak allenamento + adherence ring (single elegant ring, no badge/XP/leaderboard) + countdown prossima pesata; lunedÃ¬ mattina la stessa vista mostra special copy "Ãˆ lunedÃ¬, tempo della pesata" + UI state distinta
3. **Push notification lunedÃ¬ 07:00 funziona DST-aware**: utente opt-in da Settings (mai auto-prompt), riceve push reminder lunedÃ¬ 07:00 ora locale Italia, test DST boundary (ultima domenica Ottobre + ultima domenica Marzo) verde; push funziona solo su PWA installata
4. **Engagement layer rispetta il brief**: mascot custom (water-droplet o scale-spirit, **non** avocado) appare con 3 espressioni solo a milestones + empty states, mai in chrome routine; Lottie celebrations su prima pesata + 7-day streak + weight goal hit (â‰¤1 per session, â‰¤800ms, never blocks input); Rive in `/progress` hero rende progress dinamico; plan diff view polish con semantic diff ("Pranzo LunedÃ¬: Pasta integrale â†’ Riso basmati")
5. **WIN REQUISITE picco**: VoiceOver smoke test verde su ogni screen Phase 3 su iPhone reale; contrast audit dark mode verde (axe-core); tone review Stefano+Marta conferma "elegante con tocco giocoso, mai infantile" (no `!` in errori, no emoji in chrome, mascot non trope, copy "warm slightly playful but never silly"); workout calendar mensile + grafico settimanale rispettano motion budget

**Pause Gate (exit criteria)**: DST notification test verde; mobile VoiceOver pass su ogni screen; contrast audit verde in dark mode; tone review con Stefano+Marta conferma il bilanciamento elegante/giocoso; `impeccable:critique` + `impeccable:harden` run dopo sprint close.

**Plans**: TBD

**UI hint**: yes

---

### Phase 4: Admin & Hardening

**Goal**: L'admin (Stefano) gestisce utenti, inviti, piani e assegnazioni con un'interfaccia decente (no "office app" drift), il sistema regge la mattina di lunedÃ¬ quando tutta la famiglia apre l'app simultaneamente (stress test reale), e il database ha defense-in-depth via Row-Level Security oltre alla logica applicativa. Tutto pronto per Phase 5 (AI activation) senza debt strutturale.

**Depends on**: Phase 1 (auth, models, group entity, deploy), Phase 2 (group_id assignment per family sync â€” admin lo gestisce qui), Phase 3 (audit log pattern emerges from push history)

**Requirements**:
ADM-01, ADM-02, ADM-03, ADM-04, ADM-05, ADM-06, ADM-07,
UI-01 â€” UI-20 (cross-cutting â€” admin panel rispetta gli stessi tokens, no drift verso "office app")

**Hard dependency locks honored**:
- Invite token (24h expiry, single-use, revocable) â€” pattern definito Phase 1 (AUTH-10), UI completa qui (ADM-03)
- PostgreSQL RLS come **defense-in-depth**, non sostituisce authorization applicativa (ADM-07) â€” i policy match `get_user_with_group_access` definito Phase 2 (FAM-06)
- Audit log scrive ogni azione admin (ADM-06) â€” strutturato JSONB
- k6 load test simulando "morning resume storm" lunedÃ¬ 07:05 (mass push wake) â€” gate prima di Phase 5
- Vite 7 â†’ 8 re-evaluation (research deferred decision) â€” decidere upgrade o hold

**Success Criteria** (what must be TRUE):
1. **Admin gestisce utenti end-to-end**: admin entra in `/admin` (solo role=admin), vede lista utenti con stato (attivo, gruppo, piano attivo), genera token invito (24h single-use revocable), revoca token, assegna piano a un utente, assegna group_id, vede storico piani per utente
2. **Audit log osservabile**: ogni azione admin (invite generate, plan assign, user role change, etc.) viene scritta in audit log con `who/what/when`; admin puÃ² visualizzare log filtrabile per utente target / azione / data range
3. **Database defense-in-depth attivo**: PostgreSQL RLS policies attive sulle tabelle group-scoped (`weekly_plan_variant`, `nutrition_plan` quando shared); test di sicurezza confermano che anche con un bug applicativo, il DB rifiuta cross-group reads
4. **Sistema regge il carico realistico**: k6 ramp test simulando lunedÃ¬ 07:05 (50+ utenti che aprono l'app dopo push reminder) verde â€” pool 15/10 sufficiente, p95 latency `/today` <500ms, nessun deadlock; decisione esplicita Vite 7 â†’ 8 documentata
5. **WIN REQUISITE non degrada**: admin panel rispetta tokens Tailwind 4 (no `border: 1px solid #ddd` hardcoded), Lighthouse a11y â‰¥95 anche su `/admin`, tabelle dati con `Intl.NumberFormat('it-IT')` + `Intl.Collator('it')` sorting + 24h time, dark mode parity

**Pause Gate (exit criteria)**: RLS tests passano (anche con app-layer auth disabilitato in test, DB blocca cross-group); k6 ramp test verde p95 `/today` <500ms; admin panel a11y pass; Vite upgrade decision presa esplicitamente.

**Plans**: TBD

**UI hint**: yes

---

### Phase 5: AI Activation

**Goal**: La AI passa da NullProvider stub a effettivamente attiva â€” Ollama on-premise (GX10 ARM64 con gemma3:27b) come default privacy-first, con OpenAI/Anthropic come fallback opzionali; chat widget `/ai` sblocca con SSE streaming, gli utenti ricevono meal suggestion / week analysis / shopping tips; la sicurezza Ã¨ gerarchica (prompt-injection defense, output validation, cost caps, family isolation), e l'intero AI layer puÃ² essere spento via `AI_PROVIDER=null` env senza redeploy.

**Depends on**: Phase 1 (AI ABC + NullProvider already wired), Phase 2 (variants for meal context), Phase 3 (week analysis needs adherence data), Phase 4 (admin can toggle AI provider per env, audit log captures AI changes)

**Requirements**:
AI-08, AI-09, AI-10, AI-11, AI-12, AI-13, AI-14, AI-15, AI-16,
UI-01 â€” UI-20 (cross-cutting â€” chat widget streaming UX rispetta motion budget, skeleton placeholders, "Sto pensando..." dots)

**Hard dependency locks honored**:
- AI ABC + NullProvider exists since Phase 1 (AI-01 â€” AI-07) â€” qui swap a provider concreti senza refactor
- Capabilities endpoint + frontend feature detection â€” **no Liskov-violating `isinstance`** (AI-14)
- Kill-switch `AI_PROVIDER=null` env disabilita tutto senza redeploy (AI-15)
- Family isolation: AI context user-scoped, mai cross-user data nei prompts (AI-16)
- Prompt injection defense: `<user_note>...</user_note>` delimited prompts, output validation rifiuta email/JWT-looking strings (AI-13)
- Cost caps: max_tokens=500 hard cap, per-user daily quota, rate limit (AI-09, AI-10)
- Ollama: GX10 ARM64 + gemma3:27b, 60s first-request timeout (warmup), httpx.AsyncClient reuse (AI-08)
- SSE streaming + skeleton + "Sto pensando..." dots (AI-12, UI-04)

**Success Criteria** (what must be TRUE):
1. **Provider swap funziona end-to-end**: cambio `AI_PROVIDER=null|ollama|openai|anthropic` in `.env` + restart NSSM service â‡’ stesso codice, AI features attivano/disattivano; Ollama warmup primo request entro 60s, request successive normale; OpenAI/Anthropic con max_tokens=500 + rate limit + per-user daily quota
2. **AI features in produzione**: utente apre `/ai` chat widget (sbloccato da locked-placeholder Phase 1), riceve risposta in streaming SSE con skeleton + "Sto pensando..." dots; meal suggestion offre opzione coerente con piano + macro target; week analysis riassume aderenza/peso/workout settimana; shopping tips contestualizzano lista
3. **Sicurezza adversarial-tested**: corpus prompt-injection (incluso "ignora istruzioni precedenti", embedded JWT-looking strings, email exfiltration) testato in CI â€” output validation rifiuta pattern sospetti; family isolation verificata (Marta non puÃ² vedere context Stefano via AI prompts)
4. **Cost & kill-switch funzionano**: simulazione 100+ richieste/utente in poche ore innesca rate limit grazioso (toast "Hai raggiunto il limite giornaliero AI"); `AI_PROVIDER=null` env disabilita tutto e restituisce 501 senza redeploy; capabilities endpoint riflette stato corrente, frontend feature detection non rompe se AI off
5. **WIN REQUISITE su streaming UX**: skeleton placeholder appare in <100ms, "Sto pensando..." dots rispettano motion budget (`prefers-reduced-motion` honored), token streaming non causa layout shift, errori AI hanno copy italiano sobrio (no `!`, no infantile), chat widget integrato col design system Tailwind 4 tokens senza drift

**Pause Gate (exit criteria)**: Prompt-injection adversarial corpus tests verdi; cost-cap simulation cleanly rate-limited (utente vede toast italiano sobrio, sistema non degrada); family isolation test verde (cross-user prompt leakage = 0); kill-switch `AI_PROVIDER=null` testato senza redeploy.

**Plans**: TBD

**UI hint**: yes

---

## Coverage Validation

Every v1 REQ-ID is mapped to **exactly one** phase. Cross-cutting UI-01 â€” UI-20 apply to every phase as quality gates (verified at each phase pause gate).

| Requirement Range | Phase | Notes |
|-------------------|-------|-------|
| FND-01 â€” FND-09 | Phase 1 | Foundation tooling, PWA shell, Dexie schema, copy file |
| AUTH-01 â€” AUTH-12 | Phase 1 | Full auth incl. invite tokens (admin UI for invite gen lands Phase 4) |
| MOD-01 â€” MOD-10 | Phase 1 | All models incl. Group entity (used Phase 2) and InviteToken (admin UI Phase 4) |
| PLAN-01 â€” PLAN-10 | Phase 1 | Tolerant parser + strict schema + activate + diff base (polish Phase 3) |
| TODAY-01 â€” TODAY-08 | Phase 1 | /today landing + meal completion + offline support |
| WEIGHT-01, WEIGHT-02 | Phase 1 | Base chart + history table |
| WEIGHT-03, WEIGHT-04, WEIGHT-05 | Phase 3 | Projection curve + tolerance band + delta indicator |
| WORK-01, WORK-02 | Phase 1 | Form + filter history |
| WORK-03, WORK-04 | Phase 3 | Calendar mensile + weekly chart |
| WEEK-01 â€” WEEK-05 | Phase 2 | Weekly view + variant selector |
| SHOP-01 â€” SHOP-08 | Phase 2 | Auto-aggregation + categorization + PDF + reset |
| FAM-01 â€” FAM-09 | Phase 2 | Multi-user sync + visibility + LWW + 409 UX + authz tests |
| DASH-01 â€” DASH-08 | Phase 3 | KPI cards + streak + adherence ring + lunedÃ¬ copy |
| PUSH-01 â€” PUSH-07 | Phase 3 | VAPID + opt-in + APScheduler + DST-aware reminders |
| ENG-01 â€” ENG-06 | Phase 3 | Mascot + Lottie + Rive + plan diff polish + tone calibration |
| ADM-01 â€” ADM-07 | Phase 4 | Admin panel + audit log + RLS |
| AI-01 â€” AI-07 | Phase 1 | ABC + NullProvider + DI + endpoints stub + locked widget |
| AI-08 â€” AI-16 | Phase 5 | Concrete providers + features + chat unlock + injection defense + isolation |
| DEP-01 â€” DEP-05, DEP-08, DEP-09 | Phase 1 | Windows Server deploy + IIS + win-acme + .env + DEPLOY.md |
| DEP-06 | Phase 2 | WeasyPrint GTK3 spike & validation |
| DEP-07 | Phase 3 | VAPID keys generation/persistence |
| UI-01 â€” UI-20 | All Phases | Cross-cutting WIN REQUISITE â€” verified at every pause gate |

**Coverage:** ~145/~145 v1 requirements mapped. **Orphans:** 0. **Duplicates:** 0.

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 2/10 | In progress | â€” |
| 2. Differentiators | 0/0 | Not started | â€” |
| 3. Engagement & Polish | 0/0 | Not started | â€” |
| 4. Admin & Hardening | 0/0 | Not started | â€” |
| 5. AI Activation | 0/0 | Not started | â€” |

(Plan counts populate after `/gsd:plan-phase {N}` runs.)

## Cross-Cutting WIN REQUISITE UI/UX (every phase)

UI-01 â€” UI-20 are **not** in any single phase. They are quality gates verified at every pause gate:

- **Design tokens** (UI-01, UI-07): Tailwind 4 `@theme` consumed everywhere, OKLCH/HSL with explicit dark variants
- **Mobile-first** (UI-02): 390px â†’ tablet â†’ desktop, container queries
- **Components** (UI-03): shadcn/ui + Radix customizzati, no vanilla shadcn
- **Motion budget** (UI-04, UI-05, UI-06): â‰¤250ms micro / â‰¤800ms celebration / â‰¤2 simultaneous moving / `prefers-reduced-motion` via `--motion-scale: 0` / tap scale 0.97 80ms
- **Charts** (UI-08): Recharts colors via CSS variables only
- **PWA chrome** (UI-09): manifest theme color media queries dark/light
- **A11y CI gates** (UI-10, UI-11, UI-12, UI-13): axe-core in Playwright (â‰¥4.5:1 body, â‰¥3:1 large) / Lighthouse a11y â‰¥95 / dark-mode CI screenshot tests / VoiceOver smoke every sprint
- **Illustrations & forms** (UI-14, UI-15): decorative `aria-hidden`, meaningful `<title>`+`aria-labelledby` Italian; form errors Italian + icon + `role="alert"` + color
- **iOS keyboard** (UI-16): `visualViewport` API + scroll into view
- **Tone guardrails** (UI-17, UI-19): no `!` in errors, no infantile mascots, empty states minimalist Italian, emoji â‰¤1-2 per screen in copy only never in chrome
- **Italian formatting** (UI-18): `Intl.NumberFormat('it-IT')` / 24h / NFC normalize / `Intl.Collator('it')` sorting
- **Skill discipline** (UI-20): `impeccable:critique` + `impeccable:harden` run after each sprint close; `impeccable:frontend-design` / `polish` / `delight` / `colorize` / `animate` / `adapt` invoked actively across UI sprints

Foundations (tokens, axe-core CI, dark-mode screenshots, motion budget, tone calibration mockups) **land in Phase 1** so subsequent phases inherit, not retrofit.

---
*Roadmap created: 2026-05-01*
*Last updated: 2026-05-01 — Plan 01-05a (frontend skeleton + WIN REQUISITE token foundation) complete*
