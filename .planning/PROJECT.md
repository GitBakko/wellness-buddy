# Wellness Buddy

## What This Is

Wellness Buddy è una **Progressive Web App (PWA) self-hosted** per tracking nutrizionale e wellness, progettata per famiglie/coppie con piani nutrizionali distinti ma pasti condivisi. Affianca un piano alimentare in formato Markdown consentendo tracking di pasti, allenamento e peso corporeo, con generazione automatica della lista della spesa e architettura AI pluggabile (Ollama on-premise + cloud API). Caso d'uso primario: Stefano e Marta Brunelli — due profili separati con piani distinti e cene/pranzi condivisi.

## Core Value

**L'utente segue il piano nutrizionale in modo aderente e visibile**: ogni pasto è chiaro, la spesa è generata automaticamente, peso e allenamento sono tracciati senza attrito. Se tutto il resto fallisce, il valore minimo è "vedo cosa devo mangiare oggi e segno il peso".

## Win Requisite — UI/UX Elite (CRITICAL)

L'app **deve avere aspetto a metà tra eleganza/minimal e giocoso/friendly**. Senza questo, il progetto è considerato fallito. Approccio:

- Tipografia raffinata + spaziatura ariosa (eleganza/minimal)
- Microinterazioni gioiose, illustrazioni custom, palette calda/vivace ma controllata (giocoso/friendly)
- Skill grafiche da impiegare attivamente in tutte le fasi UI: `impeccable:frontend-design`, `impeccable:polish`, `impeccable:delight`, `impeccable:colorize`, `impeccable:animate`, `impeccable:harden`, `impeccable:adapt`, `impeccable:critique`
- Mobile-first 390px, breakpoint tablet/desktop
- PWA installabile, sensazione "native-quality" su iPhone

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] PWA installabile iOS/Android con offline support tramite Service Worker + IndexedDB (Dexie.js)
- [ ] Auth JWT con registrazione su invito (no signup pubblico), ruoli admin/user, max 100 utenti
- [ ] Upload e parsing piano nutrizionale Markdown (sezioni: dati personali, macro target, struttura giornaliera, colazione, pranzi, cene, spuntini, supplementazione, proiezione peso, regole)
- [ ] Diff view tra piani prima di applicare nuovo upload, archivio storico
- [ ] Vista "Oggi" come landing: pasti del giorno, varianti selezionate, workout, peso
- [ ] Vista settimanale con week picker e variant selector per ogni pasto (Opzione A / B / Pasta speciale)
- [ ] Lista spesa auto-generata da varianti selezionate, aggregazione ingredienti, checkbox persistenti, divisione per categoria
- [ ] Lista spesa: vista per giorno + esportazione testo/PDF + reset settimanale automatico
- [ ] Tracking allenamento giornaliero (allenato bool, durata, calorie, tipo, note) + storico calendar mensile
- [ ] Tracking peso corporeo con grafico linea + curva proiezione teorica + banda tolleranza ±0,5 kg/sett
- [ ] Dashboard KPI: peso/delta/kg persi/streak allenamento/aderenza piano + grafici progressi
- [ ] Multi-user family sync: pasti condivisi (cene/pranzi) visibili tra utenti stesso gruppo con badge "condiviso"
- [ ] Notifiche PWA push: promemoria pesata lunedì mattina (opt-in)
- [ ] Admin panel: gestione utenti, generazione token invito, assegnazione/upload piani
- [ ] AI layer architetturato come provider pattern astratto (`AIProvider` ABC) con `NullProvider` attivo Sprint 1
- [ ] AI providers Sprint 5: Ollama (on-premise GX10 ARM64 + gemma3:27b), OpenAI, Anthropic
- [ ] AI features Sprint 5: meal suggestion, week analysis, shopping tips, chat conversazionale
- [ ] Frontend AI chat widget locked Sprint 1 con placeholder "coming soon", architettura WebSocket predisposta
- [ ] Deploy Windows Server 2019: Uvicorn via NSSM service + IIS/Nginx reverse proxy
- [ ] SSL Let's Encrypt via win-acme su dominio configurabile (default `wellness-buddy.epartner.it`)
- [ ] UI/UX di livello ELITE — eleganza minimal + tocco giocoso/friendly (WIN REQUISITE)

### Out of Scope

- App mobile nativa iOS/Android — PWA è sufficiente, riduce manutenzione
- Integrazione wearable (Garmin/Apple Watch) — valutabile post-v1, calorie input manuale
- Calcolo automatico calorie bruciate — input manuale dall'utente
- Barcode scanner alimenti — fuori scope per dimensione utenza (max 100)
- Database alimenti USDA/INRAN — i piani MD sono fonte di verità
- Sistema billing/subscription — self-hosted gratuito per famiglia
- Registrazione pubblica — solo su invito per controllo utenza
- Scaling oltre 100 utenti — nessuna ottimizzazione orizzontale prevista

## Context

**Tecnico:**
- PostgreSQL già installato in produzione su Windows Server 2019 — nessuna migrazione necessaria
- Ecosistema NXTLink esistente: Notiq (React/Zustand), MANTIS/ePartner (FastAPI) — pattern noti riusati
- GX10 ARM64 disponibile per Ollama on-premise quando AI Sprint 5 attivo
- Stefano Brunelli: dev senior con esperienza Go/React/FastAPI; familiare con win-acme, NSSM, IIS

**Prior work:**
- Prompt contract dettagliato (`docs/PROMPT_CONTRACT_WELLNESS_BUDDY.md` v1.0 del 27/04/2026) — fonte di verità requisiti
- Piani nutrizionali Stefano + Marta in formato MD già esistenti, da posizionare in `/plans/`

**User research:**
- 2 utenti reali (Stefano + Marta), pasti serali condivisi → multi-user sync è must-have non vanity
- Lunedì = giorno pesata + reset settimana → ritmo settimanale forte

## Constraints

- **Stack frontend**: React 19 + Vite 7 + **TailwindCSS 4** (deviazione da contract v3 — vedi Key Decision) + Zustand + TanStack Query v5 + Dexie.js + shadcn/ui + Motion v12 + Geist Sans/Mono + lucide-react + sonner — coerenza ecosistema NXTLink
- **Stack backend**: FastAPI Python 3.12 + SQLAlchemy 2 + PostgreSQL + Alembic + JWT/bcrypt — coerenza MANTIS/ePartner
- **Deployment**: Windows Server 2019 (Uvicorn + NSSM + IIS reverse proxy) — ambiente target produzione
- **Database**: PostgreSQL già installato; database `WellnessBuddy` creato manualmente prima primo avvio (`CREATE DATABASE WellnessBuddy;`)
- **Mobile-first**: ogni componente progettato per 390px prima — caso d'uso primario è iPhone PWA
- **AI astratto**: nessuna chiamata diretta Ollama/OpenAI nel codice business — sempre via `AIProvider` ABC
- **Migrazioni**: solo Alembic — mai modificare schema direttamente
- **JWT**: access token 15 min, refresh token 7 giorni
- **API errors**: sempre JSON `{detail: string, code: string}`
- **Max utenti**: 100 (controllo manuale, no enforcement automatico)
- **AI non-blocking**: app deve funzionare al 100% senza AI attiva (default Sprint 1)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| PWA invece di app nativa | Riduce manutenzione, installabile iOS/Android, offline via SW+IndexedDB | — Pending |
| AIProvider abstract pattern fin da Sprint 1 | Evita lock-in, permette swap Ollama→OpenAI→Anthropic senza refactor | — Pending |
| Markdown come formato piano nutrizionale | Editabile a mano, versionabile, source of truth chiara | — Pending |
| Variant selector pasti A/B/Pasta | Aderenza reale > rigidità — utente sceglie giornalmente | — Pending |
| Multi-user "famiglia" via Group entity | Stefano+Marta caso primario; estendibile altri nuclei | — Pending |
| Self-hosted on Windows Server 2019 | Stack esistente, no costi cloud ricorrenti, dati privati | — Pending |
| Registrazione su invito | Max 100 utenti, controllo qualità community | — Pending |
| Dexie.js per offline state | IndexedDB wrapper maturo, supporta sync ottimistica | — Pending |
| TanStack Query v5 + Zustand | Coerenza Notiq, separazione server/client state | — Pending |
| **TailwindCSS 4** (deviazione da contract v3) | Oxide engine 2-5x faster, container queries, CSS-first `@theme` tokens, shadcn/ui v4 native — fondazione WIN REQUISITE UI/UX | — Pending |
| **WeasyPrint** primary + ReportLab fallback | Shopping list data-driven HTML+CSS→PDF, riusa Tailwind tokens per brand consistency, Italian accents nativi. Sprint 2 spike valida GTK3 su Windows Server | — Pending |
| Auth: access in-memory + refresh HttpOnly cookie + rotation + 10s grace | Previene logout storm su iPhone resume-from-background, mitiga JWT refresh race | — Pending |
| Server canonical truth, Dexie cache + outbox | Risolve iOS storage eviction, schema migration, conflict in un solo principio | — Pending |
| Group entity in schema Sprint 1 | Evita migrazione FK costosa quando family sync arriva Sprint 2 | — Pending |
| TIMESTAMPTZ + IANA tz su User da Sprint 1 | DST correctness per push lunedì mattina dipende da disciplina schema giorno uno | — Pending |
| Italian-only Sprint 1, no react-i18next | Overhead non giustificato per 100 utenti famiglia; refactor a i18n se non-italiani emergono | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-01 after initialization*
