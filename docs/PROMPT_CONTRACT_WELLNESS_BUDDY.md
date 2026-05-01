# PROMPT CONTRACT — Wellness Buddy PWA
**Versione:** 1.0  
**Data:** 27 aprile 2026  
**Autore:** Stefano Brunelli  
**AI implementatore:** Claude Opus 4  
**Repository target:** `D:\Develop\Wellness Buddy\`

---

## 0. CONTESTO E OBIETTIVO

Wellness Buddy è una **Progressive Web App (PWA)** self-hosted su Windows Server 2019, progettata per supportare fino a **100 utenti** nel primo anno. L'app affianca un piano nutrizionale personalizzato in formato Markdown, consentendo il tracking dei pasti, dell'allenamento e del peso corporeo, con generazione automatica della lista della spesa e un sistema AI pluggabile (on-premise via Ollama + cloud API come fallback, non implementato nello Sprint 1 ma architetturato fin dalle fondamenta).

**Caso d'uso primario:** Stefano Brunelli e Marta Brunelli — due profili con piani nutrizionali distinti ma pasti serali/pranzi condivisi.

---

## 1. STACK TECNOLOGICO

### Scelta motivata da Opus

| Layer | Tecnologia | Motivazione |
|---|---|---|
| **Frontend** | React 19 + Vite 7 + TailwindCSS 3 | PWA-native, familiare a Stefano, ecosistema maturo |
| **PWA** | Vite PWA Plugin + Workbox | Service Worker, offline support, installabile su iOS/Android |
| **State management** | Zustand + TanStack Query v5 | Coerente con Notiq, leggero per 100 utenti |
| **Local storage offline** | Dexie.js v4 | IndexedDB wrapper, sync ottimistica |
| **Backend** | FastAPI (Python 3.12) | Coerente con MANTIS/ePartner, async nativo |
| **ORM / DB** | SQLAlchemy 2 + PostgreSQL | già installato in produzione, nessuna migrazione necessaria |
| **Auth** | JWT + bcrypt, sessioni stateless | Semplice, no dipendenze esterne |
| **Markdown parsing** | Python-Markdown + regex custom | Parsing dei piani nutrizionali in MD |
| **AI layer** | AIProvider abstract class | Ollama (on-premise) + OpenAI/Anthropic (cloud, stub) |
| **Deployment** | Uvicorn + Nginx for Windows (IIS reverse proxy) | Windows Server 2019 compatibile |
| **Containerizzazione** | Docker Desktop for Windows (opzionale) | Semplifica il deploy futuro |

### Struttura monorepo

```
wellness-buddy/
├── frontend/               # React PWA
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── stores/         # Zustand
│   │   ├── hooks/
│   │   ├── services/       # API client
│   │   └── ai/             # AI client stub
│   ├── public/
│   ├── vite.config.ts
│   └── package.json
├── backend/                # FastAPI
│   ├── app/
│   │   ├── api/            # Routes
│   │   ├── core/           # Config, auth, dependencies
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── parsers/        # MD plan parser
│   │   └── ai/             # AI provider abstraction
│   ├── alembic/            # Migrations
│   ├── requirements.txt
│   └── main.py
├── plans/                  # Piani nutrizionali MD (Stefano, Marta)
├── CLAUDE.md               # Questo file
└── docker-compose.yml
```

---

## 2. FUNZIONALITÀ — SPECIFICHE DETTAGLIATE

### 2.1 Upload e parsing del piano nutrizionale

- L'utente carica un file `.md` formattato secondo lo standard generato dalla sessione Claude (vedere sezione 8 — Formato MD atteso)
- Il parser estrae automaticamente:
  - Dati anagrafici (nome, età, peso attuale, obiettivo)
  - Struttura giornaliera (orari, kcal, proteine per pasto)
  - Colazione: ingredienti con quantità e macro
  - Pranzi: rotazione settimanale con opzione A e opzione B per ogni giorno
  - Cene: rotazione settimanale con piatto principale, note, porzione alternativa
  - Spuntini: lista opzioni con macro
  - Supplementazione: lista supplementi con dosi e timing
  - Proiezione peso: tabella data/peso atteso
  - Regole fondamentali: lista testuale
- Alla ricezione di un nuovo MD, l'app propone un **riepilogo delle differenze** rispetto al piano precedente prima di applicarlo (diff view semplice)
- Il vecchio piano viene archiviato con timestamp, non eliminato
- Un piano può essere **assegnato a uno o più utenti** (es. piano Stefano → user Stefano)

### 2.2 Piano settimanale

- Vista settimanale navigabile (week picker)
- Per ogni giorno: colazione, pranzo, cena, spuntini con i macro target
- **Selector di variante** per ogni pasto: l'utente sceglie tra Opzione A / Opzione B / Pasta (opzione speciale intercambiabile)
- Le selezioni delle varianti per la settimana corrente vengono salvate
- Indicatore visivo dello stato del giorno: ✅ completato / 🔄 parziale / ⏳ pianificato
- Vista **"Oggi"** come landing page: mostra i pasti del giorno con relative varianti selezionate

### 2.3 Lista della spesa

- Generata automaticamente partendo dalle **varianti selezionate** per la settimana
- Aggregazione intelligente: ingredienti uguali sommati tra pranzo/cena/colazione
- Checkbox interattivi con stato persistente (spuntare = acquistato)
- Divisione per categoria: Frigo & Freschi / Frutta & Verdura / Dispensa / Condimenti / Integratori
- Vista aggiuntiva: **lista per giorno** (cosa serve lunedì, cosa martedì, ecc.)
- Esportazione come testo semplice (copia/condividi) e come PDF (via API backend)
- Reset settimanale automatico ogni lunedì con possibilità di rollover

### 2.4 Tracking allenamento

Per ogni giorno l'utente può registrare:
- **Allenato:** sì / no
- **Durata:** minuti (input numerico)
- **Calorie bruciate:** opzionale (se disponibili dall'app/orologio)
- **Tipo di workout:** campo testo libero (es. "misto 30 min", "yoga", "corsa")
- **Note libere**

Vista storica: calendario mensile con indicatori allenamento, grafico settimanale minuti/calorie.

### 2.5 Tracking peso

- Input peso corporeo con data (default: oggi)
- Frequenza consigliata: lunedì mattina (promemoria opzionale via notifica PWA)
- Grafico a linea con:
  - Peso rilevato (punti reali)
  - Curva proiezione teorica (dal piano nutrizionale)
  - Banda di tolleranza ±0,5 kg/settimana
- Indicatore delta rispetto alla proiezione: "In linea / +X kg sopra target / -X kg sotto target"
- Storico tabellare completo

### 2.6 Dashboard personale

- **Card KPI:** peso attuale / delta vs target / kg persi / settimane al target
- **Streak allenamento:** giorni consecutivi con workout registrato
- **Aderenza piano:** % giorni con pasti registrati nella settimana corrente
- **Prossima rilevazione peso:** data lunedì successivo con countdown
- **Notifica motivazionale:** messaggio semplice (statico o AI-generato se AI attiva)
- Grafici: peso nel tempo, minuti allenamento settimanali, calorie bruciate settimanali

### 2.7 Gestione utenti

- **Registrazione su invito** (no registrazione pubblica): l'admin genera un token invito
- Profili separati: ogni utente ha il proprio piano, i propri dati di tracking
- **Multi-user meal sync:** utenti nella stessa "famiglia" (gruppo) possono vedere i pasti condivisi (cene/pranzi) dell'altro con badge "condiviso con [nome]"
- Ruoli: `admin` / `user`
- L'admin può caricare/aggiornare i piani nutrizionali di qualsiasi utente
- Max 100 utenti: nessun sistema di billing o limitazione automatica, controllo manuale

### 2.8 Sistema AI — Architettura (stub Sprint 1, implementazione futura)

#### Principio di design

Il sistema AI è progettato come **provider pattern astratto** fin dallo Sprint 1. Nessuna logica AI viene hardcoded. Tutto passa per `AIProvider` abstract class.

#### AIProvider interface (backend Python)

```python
from abc import ABC, abstractmethod
from typing import Optional

class AIProvider(ABC):
    
    @abstractmethod
    async def generate_meal_suggestion(
        self,
        user_profile: dict,
        available_ingredients: list[str],
        meal_type: str,          # "breakfast" | "lunch" | "dinner" | "snack"
        macro_target: dict,      # {"protein": 40, "carbs": 50, "fat": 15, "kcal": 480}
        preferences: dict
    ) -> str: ...

    @abstractmethod
    async def analyze_week_progress(
        self,
        weight_log: list[dict],
        workout_log: list[dict],
        plan_target: dict
    ) -> str: ...

    @abstractmethod
    async def generate_shopping_tips(
        self,
        shopping_list: list[dict]
    ) -> str: ...

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        system_prompt: str,
        user_profile: dict
    ) -> str: ...
```

#### Implementazioni previste

| Provider | Status Sprint 1 | Note |
|---|---|---|
| `OllamaProvider` | **Stub** (classe vuota, returns placeholder) | GX10 ARM64, modello configurabile via env |
| `OpenAIProvider` | **Stub** | API key via env |
| `AnthropicProvider` | **Stub** | API key via env |
| `NullProvider` | **Implementato** | Risponde "AI non disponibile" — default Sprint 1 |

#### Configurazione AI (`.env`)

```env
AI_PROVIDER=null            # null | ollama | openai | anthropic
OLLAMA_BASE_URL=http://192.168.3.191:11434
OLLAMA_MODEL=gemma3:27b
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

#### Endpoint AI già presenti dallo Sprint 1 (tutti restituiscono 501 con NullProvider)

- `POST /api/ai/meal-suggestion`
- `POST /api/ai/week-analysis`
- `POST /api/ai/shopping-tips`
- `POST /api/ai/chat`

#### Frontend AI chat widget

Presente come componente disabilitato/locked nello Sprint 1, con placeholder UI "AI non disponibile — coming soon". Architettura WebSocket già predisposta.

---

## 3. MODELLO DATI (SQLAlchemy)

```python
# Entità principali

User               # id, email, username, hashed_password, role, group_id, created_at
Group              # id, name (es. "Famiglia Brunelli")
NutritionPlan      # id, user_id, name, raw_md, parsed_json, uploaded_at, is_active
WeeklyPlanVariant  # id, user_id, plan_id, week_start, day_of_week, meal_type, variant_key
WorkoutLog         # id, user_id, date, trained (bool), duration_min, calories_burned, workout_type, notes
WeightLog          # id, user_id, date, weight_kg
ShoppingListState  # id, user_id, week_start, items_json (checklist serializzata)
InviteToken        # id, token, created_by, used_by, expires_at
```

---

## 4. API ENDPOINTS

### Auth
```
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/me
POST   /api/auth/invite          (admin only)
POST   /api/auth/register        (richiede token invito)
```

### Piani nutrizionali
```
POST   /api/plans/upload         (multipart/form-data, .md file)
GET    /api/plans/               (lista piani utente)
GET    /api/plans/{id}           
GET    /api/plans/{id}/diff/{old_id}   (diff tra due piani)
POST   /api/plans/{id}/activate  
```

### Piano settimanale & varianti
```
GET    /api/weekly/{week_start}         (YYYY-MM-DD del lunedì)
POST   /api/weekly/{week_start}/variant (salva variante selezionata per giorno/pasto)
GET    /api/weekly/{week_start}/summary (riepilogo macro settimana)
```

### Lista della spesa
```
GET    /api/shopping/{week_start}       (genera da varianti selezionate)
PATCH  /api/shopping/{week_start}/item  (spunta/inspunta item)
GET    /api/shopping/{week_start}/pdf   (esporta PDF)
POST   /api/shopping/{week_start}/reset 
```

### Tracking
```
POST   /api/workout/log
GET    /api/workout/log?from=&to=
PATCH  /api/workout/log/{id}
DELETE /api/workout/log/{id}

POST   /api/weight/log
GET    /api/weight/log?from=&to=
DELETE /api/weight/log/{id}
```

### Dashboard
```
GET    /api/dashboard/kpi
GET    /api/dashboard/progress
```

### AI (stub)
```
POST   /api/ai/meal-suggestion
POST   /api/ai/week-analysis
POST   /api/ai/shopping-tips
POST   /api/ai/chat
```

### Admin
```
GET    /api/admin/users
POST   /api/admin/users/{id}/assign-plan
GET    /api/admin/users/{id}/plans
```

---

## 5. FRONTEND — PAGINE E NAVIGAZIONE

```
/                   → redirect a /today
/today              → Vista "Oggi": pasti del giorno, varianti, workout, peso
/week               → Vista settimanale con selector varianti
/shopping           → Lista della spesa con checklist
/progress           → Grafici peso + allenamento + aderenza
/plans              → Gestione piani nutrizionali (upload, storico, diff)
/settings           → Profilo utente, notifiche, preferenze
/admin              → (solo admin) Gestione utenti, inviti, piani
/ai                 → (locked Sprint 1) Chat AI placeholder
```

### Componenti chiave

| Componente | Descrizione |
|---|---|
| `MealCard` | Card pasto con variante selector, macro, stato completato |
| `WeekCalendar` | Vista 7 giorni con status indicator per ogni giorno |
| `ShoppingList` | Lista con checkbox, filtri categoria, esportazione |
| `WeightChart` | Recharts LineChart con proiezione e tolleranza |
| `WorkoutTracker` | Form giornaliero con toggle allenato/non allenato |
| `PlanUploader` | Drag & drop MD upload con preview diff |
| `KPICards` | Dashboard KPI grid |
| `AIWidget` | Placeholder locked con UI "coming soon" |

---

## 6. PWA — REQUISITI

- **Manifest:** nome "Wellness Buddy", icone 192x192 e 512x512, theme color verde
- **Service Worker:** cache-first per assets statici, network-first per API
- **Offline mode:** visualizzazione piani e dati cached, tracking locale con sync al ripristino connessione (via Dexie.js)
- **Notifiche push:** promemoria pesata lunedì mattina (opt-in), opzionalmente promemoria pasto
- **Installabile:** su iOS Safari ("Aggiungi a schermata Home") e Android Chrome
- **Responsive:** mobile-first, breakpoint tablet e desktop

---

## 7. DEPLOYMENT — WINDOWS SERVER 2019

### Setup

```
backend/  → Uvicorn su porta 8000 (come Windows Service via NSSM)
frontend/ → Build statica servita da IIS o Nginx for Windows
IIS/Nginx → Reverse proxy: /api/* → localhost:8000, /* → dist/
```

### File `.env` richiesti

```env
# Backend
SECRET_KEY=<random 32 bytes hex>
DATABASE_URL=postgresql://wnbd:WnBd4321@@localhost:5432/WellnessBuddy
# NOTA: il database "WellnessBuddy" NON esiste ancora e va creato manualmente prima del primo avvio.
# PostgreSQL e gia installato in produzione. Eseguire una volta sola:
#   psql -U postgres -c "CREATE DATABASE WellnessBuddy;"
# Le tabelle vengono create automaticamente da Alembic:
#   alembic upgrade head
CORS_ORIGINS=https://wellness-buddy.epartner.it

# AI (Sprint 1: tutto null/vuoto)
AI_PROVIDER=null
OLLAMA_BASE_URL=http://192.168.3.191:11434
OLLAMA_MODEL=gemma3:27b
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# App
MAX_USERS=100
ADMIN_EMAIL=stefano@nxtlink.it
```

### SSL

Certificato Let's Encrypt via win-acme (già familiare a Stefano). Il dominio target è a scelta (es. `wellness-buddy.epartner.it`).

---

## 8. FORMATO MD ATTESO DAL PARSER

Il parser è progettato per riconoscere la struttura dei piani generati nella sessione Claude. Sezioni riconosciute tramite heading H2:

```markdown
## DATI PERSONALI
## CALCOLO CALORICO E MACRO TARGET  
## STRUTTURA GIORNALIERA
## COLAZIONE
## PRANZI — Piano Settimanale
## CENE — Piano Settimanale
## SPUNTINO POMERIGGIO
## SUPPLEMENTAZIONE
## PROIEZIONE PESO
## REGOLE FONDAMENTALI
```

Il parser deve essere **tollerante** a variazioni minori nel testo dei heading (case insensitive, prefissi emoji, trattini extra). Le tabelle Markdown vengono parsate riga per riga. In caso di sezione non riconosciuta, viene loggata ma non blocca il parsing.

---

## 9. SPRINT PLAN

### Sprint 1 — Foundation (priorità massima)
**Goal:** app funzionante con upload piano, vista oggi, tracking peso e workout

- [ ] Setup monorepo, tooling, vite config PWA
- [ ] Backend FastAPI: struttura, auth JWT, modelli SQLAlchemy, Alembic
- [ ] MD Parser: parsing completo piani Stefano e Marta
- [ ] API: auth, plans upload/activate, workout log, weight log
- [ ] Frontend: layout shell, navigazione, pagina `/today`, `WorkoutTracker`, `WeightChart` base
- [ ] Deploy su Windows Server 2019 (IIS reverse proxy + Uvicorn NSSM service)
- [ ] AIProvider abstract class + NullProvider + stub endpoints

**Acceptance criteria Sprint 1:**
- Upload MD di Stefano e Marta → parsing corretto senza errori
- Registrazione peso con data → visibile in grafico
- Log allenamento → salvato e visibile in `/today`
- App installabile come PWA su iPhone
- Deploy funzionante su Windows Server

---

### Sprint 2 — Piano settimanale & Lista spesa
**Goal:** gestione varianti pasti e lista della spesa interattiva

- [ ] API: weekly plan, variant selection, shopping list generation
- [ ] Frontend: `WeekCalendar`, `MealCard` con variant selector
- [ ] Frontend: `ShoppingList` con checkbox, filtri, persistenza
- [ ] Esportazione lista spesa (testo + PDF)
- [ ] Multi-user family sync (pasti condivisi)

**Acceptance criteria Sprint 2:**
- Selezione variante pranzo lunedì → lista spesa aggiornata automaticamente
- Checklist spesa persistente tra sessioni
- Badge "condiviso" visibile su pasti cena condivisi Stefano/Marta

---

### Sprint 3 — Dashboard & Progress
**Goal:** dashboard KPI completa e grafici avanzati

- [ ] API: dashboard KPI, progress aggregati
- [ ] Frontend: `KPICards`, grafici aderenza e workout
- [ ] Peso: curva proiezione con banda tolleranza
- [ ] Streak allenamento
- [ ] Notifiche PWA: promemoria pesata lunedì

**Acceptance criteria Sprint 3:**
- Dashboard mostra peso attuale, delta, settimane al target
- Grafico peso con proiezione teorica visibile
- Notifica push lunedì mattina (se opt-in)

---

### Sprint 4 — Plan diff & Admin
**Goal:** gestione aggiornamenti piano e admin panel

- [ ] Diff view tra piano vecchio e nuovo prima di applicare
- [ ] Storico piani con timeline
- [ ] Admin panel: gestione utenti, inviti, assegnazione piani
- [ ] Archivio piani per utente

---

### Sprint 5 — AI Integration (quando pronto)
**Goal:** attivazione OllamaProvider e chat

- [ ] Implementare `OllamaProvider` (connessione GX10 → Ollama → modello configurabile)
- [ ] Implementare `AnthropicProvider` / `OpenAIProvider` come fallback
- [ ] Attivare endpoint `/api/ai/*`
- [ ] Frontend: sbloccare `AIWidget`, implementare chat UI
- [ ] Suggerimenti pasto basati su ingredienti disponibili
- [ ] Analisi settimanale progressi AI-generated

---

## 10. VINCOLI E NON-OBIETTIVI

### Vincoli
- Windows Server 2019 come piattaforma primaria
- Max 100 utenti: nessuna ottimizzazione per scala
- PostgreSQL — già disponibile in produzione
- Nessuna dipendenza da servizi cloud a pagamento per il funzionamento base
- L'AI non deve essere necessaria per il funzionamento dell'app

### Non-obiettivi (fuori scope)
- App mobile nativa (iOS/Android)
- Integrazione con wearable (Garmin, Apple Watch) — valutabile Sprint 6+
- Calcolo automatico calorie bruciate (input manuale)
- Barcode scanner per alimenti
- Database alimenti (USDA/INRAN) — i piani MD sono la fonte di verità
- Sistema di pagamento / subscription

---

## 11. CLAUDE.md — ISTRUZIONI PER OPUS

```markdown
# WELLNESS BUDDY — CLAUDE.md

## Progetto
PWA nutrizionale self-hosted. React 19 + FastAPI + PostgreSQL. Windows Server 2019.

## Regole implementazione
1. Seguire rigorosamente lo Sprint Plan della sezione 9. Non anticipare sprint successivi.
2. Ogni sprint termina con una PAUSE GATE: presentare riepilogo e attendere "procedi".
3. Il MD parser deve essere testato su entrambi i piani reali (Stefano e Marta).
4. L'AI layer è SEMPRE astratto: nessuna chiamata diretta a Ollama/OpenAI nel codice business.
5. Mobile-first: ogni componente frontend viene progettato prima per 390px.
6. Non usare librerie non elencate nello stack senza approvazione esplicita.
7. Alembic per tutte le migrazioni DB — mai modificare lo schema direttamente.
8. JWT access token: 15 min. Refresh token: 7 giorni.
9. Errori API: sempre JSON con struttura {detail: string, code: string}.
10. I piani MD di Stefano e Marta si trovano in /plans/. Usarli per test di parsing.

## Path progetto
D:\Develop\Wellness Buddy\

## Pause gates
- Fine Sprint 1: conferma deploy su Windows Server
- Fine Sprint 2: conferma lista spesa con PDF export
- Fine Sprint 3: conferma notifiche PWA su iPhone
- Fine Sprint 4: conferma diff view piani
- Fine Sprint 5: conferma connessione Ollama GX10
```

---

## 12. DOMANDE APERTE (da risolvere prima di Sprint 2)

1. **Dominio:** `wellness-buddy.epartner.it` o altro? Impatta CORS e certificato SSL.
2. **Famiglia/gruppo:** Stefano e Marta devono poter vedere i pasti condivisi dell'altro in tempo reale (WebSocket) o è sufficiente un refresh manuale?
3. **Notifiche push:** serve un server push (es. Web Push con VAPID keys) — confermato che è accettabile gestirlo self-hosted?
4. **PDF export lista spesa:** usare ReportLab (già familiare) o WeasyPrint?


---

*Documento generato il 27 aprile 2026 — sessione di pianificazione con Claude Sonnet 4.6*  
*Implementazione: Claude Opus 4 + Stefano Brunelli*
