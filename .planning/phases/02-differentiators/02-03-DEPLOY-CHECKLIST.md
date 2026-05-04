# Plan 02-03 — Production Deploy CHECKPOINT (Stefano + Marta)

**Date attempted:** ____________
**App server:** Windows Server 2019 · `wellness-buddy.epartner.it`
**DB server (LAN):** `192.168.3.243` · PostgreSQL 14+ (esistente, gestito separatamente)
**Deploy script source:** `DEPLOY.md` (Plan 01-08 deliverable + Plan 02-01 Appendix B GTK3)

> **Convenzioni:**
> - Comandi PowerShell 7 (`pwsh`) come Administrator se non diverso indicato
> - `E:\www\wellnessBuddy` = path codice su app server (es. `C:\Apps\WellnessBuddy`)
> - `postgres` = utente PostgreSQL con CREATEDB+CREATEROLE su 192.168.3.243 (di solito `postgres`)
> - `NuovaPasswordRobusta2026!` = password admin DB (chiedere a chi gestisce 192.168.3.243)
> - Spunta `[X]` solo dopo verifica reale, non in anticipo

---

## 0. Build & install pacchetto deploy

> **Razionale:** codice NON ancora su Windows Server. Build pacchetto su workstation dev (questa macchina), transfer zip su server, estrazione in `E:\www\wellnessBuddy`, poi prosegui con §1.

### 0.1 Build pacchetto su workstation dev

Esegui dalla **root del repo** sulla tua macchina Windows dev (`d:\Develop\AI\WellnessBuddy`):

```powershell
cd d:\Develop\AI\WellnessBuddy
pwsh deploy\scripts\package-release.ps1
```

Lo script:

1. Verifica tool richiesti (`git`, `pnpm`, `node 22+`)
2. Esegue `pnpm install --frozen-lockfile` (se mancano `node_modules`)
3. Esegue `pnpm --filter frontend build` con `VITE_BUILD_HASH=<git-sha>`
4. Stage in temp:
   - `backend/` (esclude `.venv`, `__pycache__`, `tests`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`)
   - `frontend/dist/` (PWA pre-built)
   - `deploy/` (NSSM + IIS + win-acme + scripts + `.env.production.example`)
   - `DEPLOY.md` + `README.md` + `DEPLOY-CHECKLIST.md`
   - `VERSION.txt` (git sha + branch + build date + APP_VERSION)
5. Comprime in `dist-package\wellness-buddy-<sha>-<yyyyMMdd-HHmm>.zip`
6. Genera SHA256 affianco (`<zip>.sha256`)

Verifiche:

- [X] Output finale stampa percorso zip + dimensione (~10-30 MB tipico)
- [X] File esiste: `dist-package\wellness-buddy-<sha>-<timestamp>.zip`
- [X] File checksum esiste: `dist-package\wellness-buddy-<sha>-<timestamp>.zip.sha256`
- [X] Working tree NON dirty (se warning "uncommitted changes" → committa o stash prima di rebuild per coerenza sha)

**Opzioni:**

```powershell
# Skip frontend rebuild se dist già aggiornato
pwsh deploy\scripts\package-release.ps1 -SkipFrontendBuild

# Override APP_VERSION (default 0.2.0)
pwsh deploy\scripts\package-release.ps1 -AppVersion 0.2.1

# Output dir custom
pwsh deploy\scripts\package-release.ps1 -OutputDir D:\releases
```

### 0.2 Transfer zip al Windows Server 2019

Scegli UNA modalità:

**A) RDP copy-paste (più semplice per 1 file):**

- [X] Apri Remote Desktop verso server
- [ ] Drag-and-drop `wellness-buddy-<sha>-<timestamp>.zip` + `.sha256` da locale a server desktop
- [ ] Sposta su server: `Move-Item C:\Users\<you>\Desktop\wellness-buddy-*.zip* C:\Temp\`

**B) Network share (se share esiste):**

```powershell
Copy-Item dist-package\wellness-buddy-*.zip \\<SERVER>\<share>\
Copy-Item dist-package\wellness-buddy-*.zip.sha256 \\<SERVER>\<share>\
```

**C) SCP via OpenSSH (se SSH abilitato su server):**

```powershell
scp dist-package\wellness-buddy-*.zip <user>@<SERVER>:C:/Temp/
scp dist-package\wellness-buddy-*.zip.sha256 <user>@<SERVER>:C:/Temp/
```

Verifiche:

- [ ] Zip presente su server (es. `C:\Temp\wellness-buddy-<sha>-<timestamp>.zip`)
- [ ] File `.sha256` presente affianco

### 0.3 Verifica integrità su server

Da PowerShell **sul Windows Server 2019**:

```powershell
cd C:\Temp
$zip = Get-ChildItem wellness-buddy-*.zip | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$expected = (Get-Content "$($zip.Name).sha256").Split(' ')[0].ToLower()
$actual = (Get-FileHash $zip.Name -Algorithm SHA256).Hash.ToLower()
Write-Host "Expected: $expected"
Write-Host "Actual:   $actual"
if ($expected -eq $actual) { Write-Host 'OK' -ForegroundColor Green } else { Write-Host 'CORRUPT' -ForegroundColor Red }
```

- [X] Output finale `OK` (hash match)
- [ ] Se `CORRUPT` → ri-trasferisci, NON estrarre

### 0.4 Estrazione su server

Path target: `E:\www\wellnessBuddy` (NON `C:\Program Files\...` — evita UAC writelock).

```powershell
# Crea cartella target se non esiste
if (-not (Test-Path E:\www)) { New-Item -ItemType Directory -Path E:\www -Force | Out-Null }

# Backup install precedente se esiste (idempotente)
if (Test-Path E:\www\wellnessBuddy) {
    $backup = "E:\www\wellnessBuddy.bak.$(Get-Date -Format yyyyMMdd-HHmm)"
    Move-Item E:\www\wellnessBuddy $backup
    Write-Host "Backup precedente salvato in: $backup"
}

# Estrai zip
Expand-Archive -Path C:\Temp\wellness-buddy-*.zip -DestinationPath E:\www\ -Force

# Lo zip estrae in subfolder con nome pacchetto — rinomina in 'wellnessBuddy'
$extracted = Get-ChildItem E:\www -Directory | ? Name -like 'wellness-buddy-*' | Select-Object -First 1
Rename-Item $extracted.FullName E:\www\wellnessBuddy
```

Verifiche struttura:

```powershell
cd E:\www\wellnessBuddy
Get-ChildItem | Select-Object Name
Get-Content VERSION.txt
```

- [X] Cartelle presenti: `backend\`, `frontend\dist\`, `deploy\`
- [X] File presenti: `DEPLOY.md`, `DEPLOY-CHECKLIST.md`, `VERSION.txt`
- [X] `VERSION.txt` mostra GIT_SHA + BUILD_DATE + APP_VERSION corretti
- [X] `backend\app\main.py` esiste
- [X] `frontend\dist\index.html` esiste
- [X] `deploy\nssm\install-service.ps1` esiste
- [X] `deploy\iis\web.config` esiste
- [X] `deploy\.env.production.example` esiste

### 0.5 Permessi cartella

Service NSSM girerà come `LocalService` (default install-service.ps1) → grant read sulla root, write solo su `logs/`:

```powershell
# Crea logs dir
New-Item -ItemType Directory -Path E:\www\wellnessBuddy\logs -Force | Out-Null

# ACL: Administrators full, LocalService read
icacls E:\www\wellnessBuddy /inheritance:d /grant:r 'Administrators:(OI)(CI)F' 'NT AUTHORITY\LocalService:(OI)(CI)R' /T
icacls E:\www\wellnessBuddy\logs /grant:r 'NT AUTHORITY\LocalService:(OI)(CI)M'
```

- [X] `icacls E:\www\wellnessBuddy` mostra Administrators full + LocalService Read
- [X] `icacls E:\www\wellnessBuddy\logs` mostra LocalService Modify (write per log files)

### 0.6 Cleanup zip su server (opzionale)

```powershell
Remove-Item C:\Temp\wellness-buddy-*.zip
Remove-Item C:\Temp\wellness-buddy-*.zip.sha256
```

- [X] File zip rimossi (mantieni solo `dist-package\` su workstation dev come archivio)

---

## 1. Pre-flight — DNS, firewall, connettività DB

### 1.1 DNS pubblico

- [X] `nslookup wellness-buddy.epartner.it` ritorna IP del server pubblico (NON `192.168.x`)

- [X] Da rete esterna (4G mobile): `Test-NetConnection -ComputerName wellness-buddy.epartner.it -Port 443` → `TcpTestSucceeded: True`

### 1.2 Firewall app server (porte pubbliche)

- [X] `Get-NetFirewallRule -DisplayName "*HTTP*" | ? Enabled` mostra regole 80/443 inbound abilitate

- [X] Da rete esterna: porta 80 raggiungibile (per challenge HTTP-01 win-acme)

### 1.3 Connettività app server → DB server (CRITICO — DB su LAN)

- [X] App server raggiunge DB: `Test-NetConnection -ComputerName 192.168.3.243 -Port 5432` → `TcpTestSucceeded: True`

- [X] Se `False`: verificare firewall su 192.168.3.243 (porta 5432 inbound) e ruta LAN
- [X] `pg_hba.conf` su 192.168.3.243 contiene riga `host wellness_buddy_prod wnbd <APP_SERVER_IP>/32 scram-sha-256` (oppure subnet `192.168.3.0/24`)
- [X] Service `postgresql-x64-*` su 192.168.3.243 in stato Running (verifica via RDP o monitoring esistente)
- [X] `postgresql.conf` su 192.168.3.243 ha `listen_addresses = '*'` (o include LAN IP) — NON solo `localhost`

### 1.4 Tool installati su app server (verifica veloce)

> **Server-side runtime tools only.** Frontend già pre-built in pacchetto (§0.1) → NO `node`/`pnpm`/`git` sul server.

```powershell
psql --version              # client, >= 14 — per gestione DB remoto da app server
nssm --version              # >= 2.24 — wrapper service uvicorn
uv --version                # ultima — Python deps + venv runner
python --version            # 3.12.x — base interpreter (uv usa questo)
```

- [X] `psql` ritorna versione (client locale per query remote DB)
- [X] `nssm` ritorna versione
- [X] `uv` ritorna versione (vedi §1.4 install instructions in conversazione)
- [X] `python` 3.12.x

> **NON necessari sul server:** `git`, `node`, `pnpm` — restano sulla workstation dev solo.
> **Necessari più tardi (Plan 02-05 PDF):** GTK3 Runtime via MSYS2 (vedi `DEPLOY.md` Appendix B).

---

## 2. Database setup (remoto su 192.168.3.243)

### 2.1 Test login admin remoto
```powershell
$env:PGPASSWORD = 'NuovaPasswordRobusta2026!'
.\psql.exe -h 192.168.3.243 -U postgres -d postgres -c "SELECT version();"
```
- [X] Comando ritorna versione PostgreSQL (es. `PostgreSQL 14.x ...`)
- [ ] Se errore `password authentication failed`: chiedi credenziali corrette al manager 192.168.3.243
- [ ] Se errore `no pg_hba.conf entry`: vedi §1.3 ultimo bullet

### 2.2 CREATE DATABASE + USER
```powershell
# Generare DB_PASSWORD prima (vedi §3.1) — NON usare placeholder qui
$env:PGPASSWORD = 'NuovaPasswordRobusta2026!'
.\psql.exe -h 192.168.3.243 -U postgres -d postgres -c "CREATE DATABASE wellness_buddy_prod;"
.\psql.exe -h 192.168.3.243 -U postgres -d postgres -c "CREATE USER wnbd WITH PASSWORD 'Wb4321@';"
.\psql.exe -h 192.168.3.243 -U postgres -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE wellness_buddy_prod TO wnbd;"
.\psql.exe -h 192.168.3.243 -U postgres -d wellness_buddy_prod -c "GRANT ALL ON SCHEMA public TO wnbd;"
```
- [X] CREATE DATABASE OK (oppure `database already exists` accettabile se ri-deploy)
- [X] CREATE USER OK (oppure `role already exists` → eseguire invece `ALTER USER wnbd WITH PASSWORD '<NEW>';`)
- [X] Entrambi i GRANT OK

### 2.3 Verifica login `wnbd` da app server
```powershell
$env:PGPASSWORD = 'Wb4321@'
.\psql.exe -h 192.168.3.243 -U wnbd -d wellness_buddy_prod -c "SELECT current_user, current_database();"
```
- [X] Output mostra `current_user=wnbd` + `current_database=wellness_buddy_prod`
- [X] Pulisci variabile: `Remove-Item Env:PGPASSWORD`

### 2.4 Backup pre-migration (precauzione)

- [X] DB nuovo → skip backup (nessun dato)

- [ ] DB esistente con dati → `pg_dump -h 192.168.3.243 -U postgres wellness_buddy_prod > backup-pre-deploy-$(Get-Date -Format yyyyMMdd-HHmm).sql` salvato in folder sicura

### 2.5 Backend dependencies + migrations

> ⚠️ **PREREQUISITI OBBLIGATORI prima di alembic:**
>
> 1. §0 completato — codice estratto in `E:\www\wellnessBuddy` (con `pyproject.toml` + `uv.lock` + `alembic.ini` + `alembic/`)
> 2. `uv` installato Machine-wide (verificato §1.4)
> 3. **`backend/.env` ESISTE** con almeno `DATABASE_URL`, `SECRET_KEY`, `ADMIN_EMAIL` valorizzati — **esegui §3.1 + §3.2 PRIMA di proseguire qui**
>
> `alembic env.py` importa `app.core.config.settings` che usa `pydantic-settings` con `env_file=".env"` — fail-fast su var mancanti.
>
> **Password con char speciali in `DATABASE_URL`:** URL-encode `@` come `%40`, `#` come `%23`, `/` come `%2F`. Esempio: password `Wb4321@` → `postgresql+asyncpg://wnbd:Wb4321%40@192.168.3.243:5432/...`

```powershell
cd E:\www\wellnessBuddy\backend
uv sync --frozen
# Crea .venv fresh + installa weasyprint==62.3, reportlab==4.5.0, jinja2==3.1.6, apscheduler==3.11.2
# (.venv NON è nel pacchetto — viene creata qui dal lock file)
uv run alembic current
# Output: stato attuale (vuoto o head precedente)
uv run alembic upgrade head
# Output: ogni migration → "Running upgrade ... -> ..., done"
```

- [X] `.venv\` creata in `E:\www\wellnessBuddy\backend\.venv\`
- [X] `uv sync --frozen` zero errori
- [X] `alembic upgrade head` termina con `a694bcd4d792` (Phase 1 baseline) o successivo se Plan 02-06 già migrato (`0001_activate_groups`)
- [X] Ri-esecuzione `alembic current` mostra ultima revision

### 2.6 Verifica schema
```powershell
$env:PGPASSWORD = 'Wb4321@'
.\psql.exe -h 192.168.3.243 -U wnbd -d wellness_buddy_prod -c "\dt"
Remove-Item Env:PGPASSWORD
```

Tabelle attese da `0000_baseline` (Phase 1) + `alembic_version`:

- [X] `users` (auth + profilo)
- [X] `groups` (multi-user families — schema present, sync logic in Plan 02-06)
- [X] `refresh_tokens` (JWT refresh rotation)
- [X] `invite_tokens` (invite-only signup)
- [X] `nutrition_plans` (parsed MD plans)
- [X] `weekly_plan_variants` (Plan 02-02 — variant A/B/Speciale per meal-day)
- [X] `weight_log` (singolare — tracking peso)
- [X] `workout_log` (singolare — tracking allenamento)
- [X] `shopping_list_state` (singolare — checkbox state shopping list)
- [X] `audit_log` (security events)
- [X] `alembic_version` (auto-managed da alembic)
- [X] **Totale: 11 tabelle** (Phase 1 baseline)
- [X] Plan 02-06 aggiungerà tabelle group-sync (12+ dopo Wave 6)

> **NOTA:** `ai_event_log` **NON esiste in Phase 2** — è Sprint 5 (AI integration). Checklist precedente la elencava per errore.

---

## 3. Secrets

### 3.1 Generazione
```powershell
cd E:\www\wellnessBuddy
pwsh deploy\scripts\generate-secrets.ps1
```
- [X] Output stampa `SECRET_KEY` (64 hex chars) + `DB_PASSWORD` (~32 chars) + comandi pronti
- [X] Copia ENTRAMBI i valori in un blocco note temporaneo (NON salvare su disco condiviso)

### 3.2 Creazione `backend/.env`
```powershell
cd E:\www\wellnessBuddy
Copy-Item deploy\.env.production.example backend\.env
notepad backend\.env
```
Modifiche obbligatorie:
- [X] `DATABASE_URL=postgresql+asyncpg://wnbd:<DB_PASSWORD>@192.168.3.243:5432/wellness_buddy_prod` — **HOST = 192.168.3.243, NON localhost** (script genera `localhost` di default — sostituire manualmente)
- [X] `SECRET_KEY=<64 hex from §3.1>`
- [X] `CORS_ORIGINS=https://wellness-buddy.epartner.it` (NESSUN wildcard, validato a boot)
- [X] `ADMIN_EMAIL=s.brunelli@epartner.it`
- [X] `BUILD_HASH=<git rev-parse --short HEAD>`
- [X] `APP_VERSION=0.2.0` (Phase 2 bump)
- [X] `TZ=Europe/Rome`
- [X] `AI_PROVIDER=null` (Sprint 5 attiverà)
- [X] **Aggiungi:** `PDF_BACKEND=weasyprint` (Plan 02-01 default; flippa a `reportlab` solo se spike GTK3 fallisce)

### 3.3 ACL lockdown (dopo modifica)
```powershell
icacls "E:\www\wellnessBuddy\backend\.env" /inheritance:r /grant:r "NT AUTHORITY\LocalService:R" "Administrators:F"
icacls "E:\www\wellnessBuddy\backend\.env"
```
- [X] Output mostra solo `Administrators` + `LocalService` (NESSUN `Users` / `Authenticated Users`)

### 3.4 DPAPI encryption (opzionale, raccomandato — D-25)
```powershell
$bytes = [System.IO.File]::ReadAllBytes("E:\www\wellnessBuddy\backend\.env")
$protected = [System.Security.Cryptography.ProtectedData]::Protect($bytes, $null, "LocalMachine")
[System.IO.File]::WriteAllBytes("E:\www\wellnessBuddy\backend\.env.dpapi", $protected)
```
- [X] File `.env.dpapi` creato (NON sostituisce `.env` per ora — copia di sicurezza)

### 3.5 Verifica boot config
```powershell
cd E:\www\wellnessBuddy\backend
uv run python -c "from app.core.config import settings; print('DB host:', settings.DATABASE_URL.split('@')[1].split('/')[0]); print('CORS:', settings.CORS_ORIGINS)"
```
- [X] Output mostra `DB host: 192.168.3.243:5432` (NON `localhost`)
- [X] Output mostra `CORS: https://wellness-buddy.epartner.it`

### 3.6 Smoke test connessione DB da app
```powershell
cd E:\www\wellnessBuddy\backend
uv run python -c "import asyncio; from app.core.db import async_session_factory; from sqlalchemy import text; asyncio.run((lambda: async_session_factory().__aenter__().__await__())()) if False else None"
# Più semplice: avvia uvicorn manualmente 5s, controlla log connessione
uv run uvicorn app.main:app --host 127.0.0.1 --port 8001 &
Start-Sleep 3
Invoke-WebRequest http://127.0.0.1:8001/api/health
```
- [X] Risposta HTTP 200 con `{"status":"ok","version":"...","build_hash":"..."}` (DB connection verificata implicitamente da `alembic upgrade head` + uvicorn lifespan)
- [ ] Termina processo uvicorn manuale: `Get-Process python | Stop-Process -Force` (solo se nessun altro python in esecuzione)

---

## 4. Frontend — verifica dist pre-built

> **Razionale:** frontend è già compilato dentro il pacchetto (§0.1 step 3 esegue `pnpm --filter frontend build` su workstation dev). Il server **NON** ricostruisce — non servono `pnpm`, `node`, `git` sul Windows Server. Solo verifica che `frontend\dist\` sia presente e completo.

### 4.1 Verifica struttura dist

```powershell
cd E:\www\wellnessBuddy\frontend\dist
Get-ChildItem | Select-Object Name
```

- [X] `index.html` presente
- [X] `sw.js` presente (Workbox service worker)
- [X] `manifest.webmanifest` presente
- [X] Cartella `assets\` presente (JS+CSS hashati)
- [X] Almeno 1 icona PNG (`icon-192.png` o simile)

### 4.2 Verifica BUILD_HASH coerente con package

```powershell
Get-Content E:\www\wellnessBuddy\VERSION.txt
Get-Content E:\www\wellnessBuddy\frontend\dist\index.html | Select-String 'data-build-hash|VITE_BUILD_HASH' | Select-Object -First 3
```

- [X] `VERSION.txt` GIT_SHA matcha quello stampato dal server `/api/version` dopo §5 (es. `7bca119`)

### 4.3 Verifica manifest PWA

```powershell
Get-Content E:\www\wellnessBuddy\frontend\dist\manifest.webmanifest | ConvertFrom-Json |
    Select-Object name, short_name, theme_color, background_color, display, start_url, icons
```

- [X] `name` = `Wellness Buddy` (o equivalente)
- [X] `theme_color` valorizzato (NON vuoto)
- [X] `display` = `standalone`
- [X] `icons` array contiene almeno una entry con `sizes: "192x192"` e una con `sizes: "512x512"`

### 4.4 (Opzionale) Re-build sul server

Solo se serve correggere qualcosa al volo SENZA tornare in dev. Richiede installazione manuale di Node 22+, pnpm, git, poi `git clone` del repo. **Non raccomandato** — ricostruisci su dev, ri-pacchettizza, ri-deploya con §0.

- [X] Skip — frontend pre-built nel pacchetto è source-of-truth

---

## 5. NSSM service install

### 5.1 Installazione

> **DB remoto su 192.168.3.243** → script omette `DependOnService` (nessun PG locale). Per DB locale (raro), passa `-PostgresService postgresql-x64-16`.

```powershell
cd E:\www\wellnessBuddy
pwsh deploy\nssm\install-service.ps1
```

Output atteso:

```text
=== Wellness Buddy — NSSM service installer ===
App root: E:\www\wellnessBuddy
Backend:  E:\www\wellnessBuddy\backend
Logs:     E:\www\wellnessBuddy\logs
nssm:     ...
uv:       ...
Installing service 'WellnessBuddyAPI'...
Remote DB scenario — no local PG service dependency.
Starting service...
Name        : WellnessBuddyAPI
Status      : Running
StartType   : Automatic
DisplayName : Wellness Buddy API
```

- [X] Script ritorna senza errori
- [X] `Get-Service WellnessBuddyAPI` → status `Running`

**Se hai già un service rotto da run precedente (errore `postgresql-x64-16`):**

```powershell
# Rimuovi service corrotto
nssm remove WellnessBuddyAPI confirm

# Verifica rimosso
Get-Service WellnessBuddyAPI -ErrorAction SilentlyContinue   # null = OK

# Re-run installer (con script aggiornato)
pwsh deploy\nssm\install-service.ps1
```

- [ ] Service rimosso pulitamente prima di reinstall
- [ ] Reinstall completata senza warning `postgresql-x64-*`

### 5.2 Auto-start + recovery
```powershell
Set-Service WellnessBuddyAPI -StartupType Automatic
nssm set WellnessBuddyAPI AppExit Default Restart
nssm set WellnessBuddyAPI AppRestartDelay 5000
```
- [X] StartupType = Automatic
- [X] Restart on exit configurato

### 5.3 Verifica avvio + log

> **Nota:** NSSM non scrive di default in Application Event Log (sorgente `WellnessBuddyAPI` non registrata — è atteso). `stdout.log` può essere vuoto perché uvicorn gira con `--no-access-log` (configurato in install-service.ps1). Check primario è `Get-Service` + health endpoint.

```powershell
# Service status (check primario)
Get-Service WellnessBuddyAPI

# Stderr.log = source-of-truth per crash (uvicorn lifespan errors, traceback)
Get-Content E:\www\wellnessBuddy\logs\stderr.log -Tail 50

# Stdout.log spesso vuoto (--no-access-log) — non bloccante
Get-Content E:\www\wellnessBuddy\logs\stdout.log -Tail 30 -ErrorAction SilentlyContinue

# NSSM event log (Windows-specific, non standard Application source)
Get-WinEvent -LogName 'Application' -MaxEvents 20 -ErrorAction SilentlyContinue |
    Where-Object { $_.ProviderName -like '*nssm*' -or $_.Message -like '*WellnessBuddyAPI*' } |
    Select-Object TimeCreated, LevelDisplayName, Message | Format-List
```

- [ ] `Get-Service WellnessBuddyAPI` → Status `Running` (NON `Stopped`/`Paused`)
- [ ] `stderr.log` ZERO traceback Python (vuoto OK — significa nessun crash)
- [ ] Se `stderr.log` mostra traceback → vedi Appendice A troubleshooting
- [ ] (Opzionale) `stdout.log` mostra eventuali log INFO dell'app — vuoto è normale

> **Check definitivo:** §5.4 health endpoint. Se 200 OK → service realmente funzionante. Se Status=Running ma health timeout → uvicorn appeso (rare).

### 5.4 Health diretto (senza IIS)
```powershell
Invoke-WebRequest http://127.0.0.1:8000/api/health | Select-Object -ExpandProperty Content
```
- [ ] Risposta `{"status":"ok","version":"...","build_hash":"..."}`

### 5.5 PATH GTK3 propagato (per Phase 2 PDF — DEP-06)
```powershell
nssm get WellnessBuddyAPI AppEnvironmentExtra
```
- [ ] Output contiene `PATH=C:\msys64\mingw64\bin;...` OPPURE PATH di sistema include `C:\msys64\mingw64\bin` (verificato dopo reboot)
- [ ] **Solo se Plan 02-01 GTK3 spike completato** — altrimenti skip e marcare TODO Plan 02-05

---

## 6. IIS reverse proxy

### 6.1 Modulo IIS prerequisiti
```powershell
Get-WindowsFeature Web-Server, Web-Http-Redirect, Web-Static-Content, Web-Default-Doc | ? InstallState -eq Installed
Get-IISAppPool   # verifica IIS attivo
```
- [X] IIS installato + URL Rewrite + ARR (vedi DEPLOY.md §1)

### 6.2 Crea sito

- [X] IIS Manager → Add Website
  - Site name: `wellness-buddy`
  - Physical path: `E:\www\wellnessBuddy\frontend\dist`
  - Binding: `http`, port `80`, host header `wellness-buddy.epartner.it`
- [X] Sito appare in IIS Manager → Sites

### 6.3 Deploy web.config
```powershell
Copy-Item E:\www\wellnessBuddy\deploy\iis\web.config E:\www\wellnessBuddy\frontend\dist\web.config -Force
```
- [X] File presente in `dist\web.config`

### 6.4 ARR proxy abilitato (server-level, una volta sola)

- [X] IIS Manager → server node → "Application Request Routing Cache" → "Server Proxy Settings" → tick `Enable proxy` → Apply

### 6.5 Restart + smoke

> **NON usare `iisreset`** — impatta tutti gli altri siti `epartner.it` sullo stesso IIS. Riavvia solo il sito + app pool `wellness-buddy`.

```powershell
Import-Module WebAdministration

# Identifica app pool del sito (di solito stesso nome del sito)
$site = Get-Website -Name 'wellness-buddy'
$poolName = $site.applicationPool
Write-Host "Site: $($site.Name) | App Pool: $poolName"

# Recycle app pool (necessario dopo modifiche web.config)
Restart-WebAppPool -Name $poolName

# Restart sito (assicura ri-lettura bindings + web.config)
Stop-Website -Name 'wellness-buddy' -ErrorAction SilentlyContinue
Start-Website -Name 'wellness-buddy'

Start-Sleep 3

# Smoke test
Invoke-WebRequest http://wellness-buddy.epartner.it/api/health
Invoke-WebRequest http://wellness-buddy.epartner.it/
```

- [X] App pool name identificato correttamente
- [X] `Restart-WebAppPool` zero errori
- [X] `Stop-Website` + `Start-Website` zero errori
- [X] Risposta 200 su `/api/health` con `status=ok` (proxy IIS → uvicorn end-to-end)
- [X] Risposta 200 su `/` con HTML `index.html` (frontend dist served)
- [X] Altri siti `epartner.it` rimasti UP durante restart (verifica visitando uno: `Invoke-WebRequest https://<altro-sito>.epartner.it`)

---

## 7. SSL — wildcard cert già applicato

> **Scenario:** wildcard cert `*.epartner.it` già installato su IIS e legato al binding HTTPS del sito `wellness-buddy`. Skip flow win-acme interattivo. Verifica solo che cert funzioni + redirect HTTP→HTTPS attivo.

### 7.1 Verifica binding HTTPS sul sito

```powershell
Import-Module WebAdministration
Get-WebBinding -Name 'wellness-buddy' | Select-Object protocol, bindingInformation, sslFlags
```

- [ ] Output include riga `protocol: https`, `bindingInformation: *:443:wellness-buddy.epartner.it`
- [ ] Se manca binding HTTPS → IIS Manager → site bindings → Add → https + cert wildcard + host header `wellness-buddy.epartner.it` + tick "Require Server Name Indication"

### 7.2 Verifica certificato bound

```powershell
$binding = Get-WebBinding -Name 'wellness-buddy' -Protocol https
$cert = Get-ChildItem Cert:\LocalMachine\My | Where-Object { $_.Thumbprint -eq $binding.certificateHash }
$cert | Select-Object Subject, Issuer, NotAfter, Thumbprint | Format-List
```

- [ ] `Subject` contiene `*.epartner.it` (wildcard)
- [ ] `NotAfter` data scadenza futura (verifica che ci siano almeno 30 giorni)
- [ ] `Issuer` riconosciuto (Let's Encrypt / Sectigo / DigiCert / etc.)

### 7.3 Verifica HTTPS pubblico (da rete ESTERNA — 4G mobile NON LAN)

- [ ] Browser su iPhone (4G ON, wifi OFF): `https://wellness-buddy.epartner.it` → carica
- [ ] Lucchetto verde, "Connessione protetta"
- [ ] Cert details mostra issuer wildcard + dominio `*.epartner.it`
- [ ] Nessun warning "certificate not trusted" / "name mismatch"

### 7.4 Forza HTTPS redirect

```powershell
# Test redirect HTTP → HTTPS (web.config rule)
$resp = Invoke-WebRequest http://wellness-buddy.epartner.it -MaximumRedirection 0 -ErrorAction SilentlyContinue
Write-Host "Status: $($resp.StatusCode) | Location: $($resp.Headers.Location)"
```

- [ ] Status `301` o `302` con Location header verso `https://wellness-buddy.epartner.it`
- [ ] Se status 200 → redirect mancante in web.config (verifica `<rule name="Redirect to HTTPS">` presente)

### 7.5 Smoke HTTPS dal server

```powershell
Invoke-WebRequest https://wellness-buddy.epartner.it/api/health
```

- [ ] Status 200 + JSON `{"status":"ok",...}`

---

## 8. Smoke test end-to-end

### 8.1 Script automatico
```powershell
cd E:\www\wellnessBuddy
pwsh deploy\scripts\smoke-test.ps1 https://wellness-buddy.epartner.it
```
- [ ] `/api/health` → 200, `status=ok`, `version`, `build_hash` presenti
- [ ] `/api/version` o `/version.json` → ritorna `version` + `build_hash` (match `git rev-parse --short HEAD`)
- [ ] `/` → serve `index.html` (contiene "Wellness Buddy")
- [ ] HTTPS cert valido + non scaduto

### 8.2 Crea primo invite admin (Stefano)
```powershell
cd E:\www\wellnessBuddy\backend
uv run python -c "
import asyncio
from app.services.auth_service import create_invite
from app.core.db import async_session_factory

async def main():
    async with async_session_factory() as s:
        token = await create_invite(s, email='s.brunelli@epartner.it', role='admin')
        print(f'Invite link: https://wellness-buddy.epartner.it/register?token={token}')

asyncio.run(main())
"
```
- [ ] Comando stampa link invite — copialo

### 8.3 Login Stefano

- [ ] Apri link invite su browser → form pre-filled → completa registrazione → auto-login

- [ ] Reindirizzato a `/today`

### 8.4 Endpoint Plan 02-02 live (settimana)

- [ ] Da `/today` naviga a `/settimana/<thisWeek>` → carica

- [ ] DevTools Network: `GET /api/weekly/<week_start>` → 200
- [ ] Variant pills (Opzione A / Opzione B / Speciale) visibili
- [ ] Macro ring settimanale renderizza

### 8.5 Crea invite Marta
```powershell
cd E:\www\wellnessBuddy\backend
uv run python -c "
import asyncio
from app.services.auth_service import create_invite
from app.core.db import async_session_factory

async def main():
    async with async_session_factory() as s:
        token = await create_invite(s, email='m.capotosti@epartner.it', role='user')
        print(f'Invite link Marta: https://wellness-buddy.epartner.it/register?token={token}')

asyncio.run(main())
"
```
- [ ] Link generato, condividi con Marta via canale sicuro

---

## 9. iPhone install Stefano

### 9.1 Installazione PWA

- [ ] Safari su iPhone Stefano → `https://wellness-buddy.epartner.it`

- [ ] Login Stefano OK
- [ ] Tap Share → "Aggiungi a Home" visibile
- [ ] Conferma → icona custom su home screen (NON generic web clip; verifica icona = 192/512 da manifest)
- [ ] Tap icona home → app apre in standalone (NESSUNA Safari chrome, NESSUN URL bar)

### 9.2 Tema Lifesum Pure

- [ ] `/today` renderizza con: warm cream bg, MacroRing centrato, font Plus Jakarta, CTA primaria leaf-sage, numerici Geist Mono, greeting Instrument Serif italic

- [ ] Settings → Tema → Scuro → applica dark mode senza flash
- [ ] Toggle Sistema → segue iPhone setting

### 9.3 Plan 02-02 ship validation

- [ ] `/settimana/<thisWeek>` carica

- [ ] Week picker chip-row settimane recenti
- [ ] Variant selector dropdown apre, 3 opzioni mostrate
- [ ] Tap variant → optimistic update <100ms
- [ ] Background refetch riconferma scelta

### 9.4 Offline-first

- [ ] Airplane mode ON → reload `/today` → cached page renderizza + pip "Offline"

- [ ] Airplane mode OFF → entro 5s pip flippa a "Sincronizzato"

### 9.5 Auth resilience

- [ ] Swipe-up kill app → riapri → ancora loggato (refresh token rotation OK, no logout storm)

- [ ] Background 30 min → riapri → access token refreshato silently (DevTools → Network non mostra `/login`)

---

## 10. iPhone install Marta

### 10.1 Setup base

- [ ] Marta clicca link invite (§8.5) → registra → login

- [ ] Stessi step §9.1 → §9.5 ripetuti su iPhone Marta

### 10.2 Isolamento dati

- [ ] Marta vede SOLO suoi dati (piano nutrizionale Marta, weight Marta, workout Marta)

- [ ] NESSUN dato Stefano visibile
- [ ] **Family sync NON ancora attivo** (Plan 02-06 attiverà) → per ora ogni utente isolato

---

## 11. Lighthouse audit (Stefano, Chrome desktop)

### 11.1 Esecuzione

- [ ] Chrome desktop (Win/Mac) → `https://wellness-buddy.epartner.it/today`

- [ ] Login Stefano via desktop
- [ ] DevTools (F12) → Lighthouse tab
- [ ] Configura: device `Mobile`, categories `Performance, Accessibility, Best Practices, PWA`
- [ ] Run audit (può richiedere 30-60s)

### 11.2 Score (target D-28)

- [ ] PWA: ____ / 100 (target ≥95 — record actual; lock 100/100 se raggiunto)

- [ ] Accessibility: ____ / 100 (target ≥95)
- [ ] Performance: ____ / 100 (informational — Phase 4 hardens)
- [ ] Best Practices: ____ / 100 (informational)

### 11.3 Issue critici

- [ ] PWA installable → green check

- [ ] Service worker registered → green
- [ ] Manifest valid + icons 192/512 → green
- [ ] HTTPS → green
- [ ] Color contrast (axe-core CI già verifica) → 0 violazioni serie

### 11.4 Salva report

- [ ] Lighthouse → Export → JSON → salva in `E:\www\wellnessBuddy\.planning\phases\02-differentiators\lighthouse-prod-deploy.json`

- [ ] Allegare path al sign-off §13

---

## 12. Tone calibration sign-off (Stefano + Marta — IN PERSONA)

> **Ritual:** Stefano + Marta seduti insieme, entrambi iPhone in mano, mockup di riferimento aperto su laptop.

### 12.1 Setup

- [ ] Mockup riferimento aperto: `mockups/tone-calibration-v2/A-lifesum-pure.html` su desktop

- [ ] Entrambi iPhone su `https://wellness-buddy.epartner.it/today` (installato §9 + §10)

### 12.2 Confronto visivo

- [ ] Match palette: bg cream, MacroRing leaf+coral+blueberry+amber arcs

- [ ] Match tipografia: Plus Jakarta Sans body, Geist Mono numerici, Instrument Serif greeting
- [ ] Match densità: padding/margins coerenti con mockup (NON denso "office", NON sparse "spa")
- [ ] Match microinteractions: tap-scale 0.97 / 80ms su CTA primaria
- [ ] Dark mode: stesso check su `/today` con Tema Scuro attivo

### 12.3 Tone audit (UI-17 inheritance)

- [ ] Zero `!` in error copy

- [ ] Zero mascot infantili
- [ ] Empty states italiani minimalisti (es. "Nessun piano per oggi" NON "Ops! Niente da vedere qui!")
- [ ] Copy italiano coerente con `frontend/src/i18n/copy.it.ts` (FND-09)

### 12.4 Verdict

- [ ] Variante A · Lifesum Pure: **LOCKED in production** ✓

- [ ] Cross-reference closure: `01-08-tone-calibration-checklist.md` final sign-off marcato CLOSED

---

## 13. Sign-off

| Reviewer | Initial | Date (YYYY-MM-DD) | Time (HH:MM) | Verdict (PASS / CONCERNS / BLOCK) | Notes |
|----------|---------|-------------------|--------------|-----------------------------------|-------|
| Stefano  |         |                   |              |                                   |       |
| Marta    |         |                   |              |                                   |       |

**Lighthouse JSON allegato:** `lighthouse-prod-deploy.json` ✅ / ❌

**Closure rule (D-26):**
- `BLOCK` da uno solo dei due → checkpoint NON merged → Phase 2 Wave 4+ bloccata
- `CONCERNS` da uno solo → triagiare in Plan 02-07 closure tasks
- `PASS` da entrambi → checkpoint cleared, sblocca `/gsd:execute-phase 2 --wave 4`

---

## Appendice A — Troubleshooting comune

### "Connection refused" su 192.168.3.243:5432
1. Verifica service PostgreSQL su 192.168.3.243 (RDP o monitoring)
2. Verifica `Test-NetConnection 192.168.3.243 -Port 5432` da app server
3. Verifica `pg_hba.conf` riga per IP app server
4. Verifica `postgresql.conf` `listen_addresses = '*'`
5. Riavvia service PostgreSQL su 192.168.3.243 dopo modifiche conf

### "password authentication failed for user wnbd"
1. Riapplica password: `.\psql.exe -h 192.168.3.243 -U postgres -d postgres -c "ALTER USER wnbd WITH PASSWORD '<NEW>';"`
2. Aggiorna `DATABASE_URL` in `backend/.env` con nuova password
3. `Restart-Service WellnessBuddyAPI`

### Service NSSM non parte
1. `Get-EventLog -LogName Application -Source WellnessBuddyAPI -Newest 20` → cerca traceback
2. Verifica `E:\www\wellnessBuddy\logs\stderr.log` ultime 50 righe
3. Run uvicorn manuale per riprodurre: `cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000`

### IIS proxy 502
1. Service WellnessBuddyAPI Running? `Get-Service WellnessBuddyAPI`
2. Backend risponde diretto? `Invoke-WebRequest http://127.0.0.1:8000/api/health`
3. ARR proxy abilitato? IIS Manager → server → ARR Cache → tick "Enable proxy"
4. `Restart-WebAppPool -Name <pool>` + `Stop-Website` + `Start-Website` (NON `iisreset` — impatta altri siti epartner.it)

### Lighthouse PWA score <95
1. Service worker registrato? Chrome DevTools → Application → Service Workers
2. Manifest valido? Chrome DevTools → Application → Manifest
3. Icone 192+512 servite con corretto MIME type? Network tab
4. HTTPS senza mixed content? Console tab

### iPhone PWA non installabile
1. HTTPS ufficiale (NON self-signed)? Lucchetto verde Safari?
2. Manifest theme_color presente?
3. Icone 192/512 raggiungibili? `curl https://wellness-buddy.epartner.it/icon-192.png`
4. Visit page ≥1 volta + ≥30s prima share → Apple richiede "engagement"

---

*Last updated: Plan 02-03 (Phase 2 — production deploy CHECKPOINT, DB remoto LAN 192.168.3.243).*
