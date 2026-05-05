# Wellness Buddy v0.2.0 — Update Deploy Step-by-Step

**Tipo:** re-deploy incrementale (NON fresh install)
**Da:** v0.1.x (Phase 1, primo deploy 2026-05-04)
**A:** v0.2.0 (Phase 2 closure — Plans 02-01..02-07)
**Pacchetto:** `wellness-buddy-6e90d36-20260505-1547.zip` (2.44 MB)
**SHA256:** `566243165992a22960727dc246b4af94081126a824d89620e0d76bd94533442c`
**Build hash:** `6e90d36`

> **Prerequisito:** primo deploy v0.1.x già installato in `E:\www\wellnessBuddy\` su Windows Server 2019. NSSM service `WellnessBuddyAPI` attivo su port 8000. IIS site `wellness-buddy.epartner.it` con cert wildcard. PostgreSQL su LAN `192.168.3.243`.
>
> Se NON hai un deploy precedente: usa la checklist completa `02-03-DEPLOY-CHECKLIST.md` (fresh install §0 → §13).

---

## Cosa cambia in v0.2.0

| Area | Change |
|------|--------|
| Backend code | Plans 02-04 (parser grid), 02-05 (shopping + APScheduler), 02-06 (PDF export), 02-07 (family sync) |
| DB schema | 2 nuove migrazioni Alembic: `0001_weekly_variant_per_day`, `0002_activate_groups` |
| Backend deps | `apscheduler`, `weasyprint`, `pypdf` (test-only), `radix-ui` adjustments — già nel `pyproject.toml` |
| Frontend code | /settimana per-day variant + /spesa lista spesa + carousel snack + family sync UI |
| Frontend assets | Bundle ricompilato con build_hash 6e90d36, PWA SW aggiornato (Workbox), 43 precache entries |
| .env | Nuova var `PDF_BACKEND=weasyprint` (default prod, fallback `reportlab` se GTK3 fail) |
| Routes nuove | `/api/family/share/{variant_id}`, `/api/shopping/{w}/export-pdf`, `/api/shopping/{w}/check`, `/api/shopping/{w}/reset` |

**Downtime atteso:** ~2-3 minuti (stop service → migrate → start service).

---

## §1. Pre-flight (sul tuo PC dev — già fatto, da verificare)

- [x] Pacchetto buildato: `dist-package\wellness-buddy-6e90d36-20260505-1547.zip` (2.44 MB)
- [x] SHA256: `566243165992a22960727dc246b4af94081126a824d89620e0d76bd94533442c`

Trasferisci il `.zip` + `.zip.sha256` sul Windows Server 2019 via:
- RDP copy/paste
- SCP / WinSCP
- Network share (`\\server\share`)
- OneDrive / Dropbox / chiavetta USB

Path destinazione consigliato: `C:\Deploys\v0.2.0\`

---

## §2. Verifica integrità pacchetto (sul Windows Server)

PowerShell come Administrator sul server:

```powershell
cd C:\Deploys\v0.2.0
$expected = '566243165992a22960727dc246b4af94081126a824d89620e0d76bd94533442c'
$actual = (Get-FileHash wellness-buddy-6e90d36-20260505-1547.zip -Algorithm SHA256).Hash.ToLower()
if ($actual -eq $expected) { Write-Host 'SHA256 OK' -ForegroundColor Green } else { Write-Host "SHA256 MISMATCH: $actual" -ForegroundColor Red; exit 1 }
```

Se mismatch: trasferisci di nuovo. Non procedere.

---

## §3. Backup (mandatorio prima di ogni update)

PowerShell admin sul server. Ferma niente ancora — stai facendo solo backup logico.

```powershell
$backupRoot = 'E:\Backups\WellnessBuddy'
$ts = Get-Date -Format 'yyyyMMdd-HHmm'
$backupDir = Join-Path $backupRoot "v0.1-pre-v0.2-$ts"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# 3.1 Backup codice corrente (frontend dist + backend app + .env)
Compress-Archive -Path 'E:\www\wellnessBuddy\frontend\dist\*' -DestinationPath (Join-Path $backupDir 'frontend-dist.zip') -Force
Compress-Archive -Path 'E:\www\wellnessBuddy\backend\app\*' -DestinationPath (Join-Path $backupDir 'backend-app.zip') -Force
Copy-Item 'E:\www\wellnessBuddy\backend\.env' (Join-Path $backupDir '.env.backup')
Copy-Item 'E:\www\wellnessBuddy\backend\alembic\versions\*' (Join-Path $backupDir 'alembic-versions') -Recurse

# 3.2 Backup DB (su LAN 192.168.3.243)
$dbHost = '192.168.3.243'
$dbName = 'WellnessBuddy'
$dumpFile = Join-Path $backupDir 'wellnessbuddy-db.dump'
& pg_dump.exe -h $dbHost -U postgres -d $dbName -Fc -f $dumpFile
if ($LASTEXITCODE -eq 0) { Write-Host "DB dump OK: $dumpFile" -ForegroundColor Green } else { Write-Host 'DB dump FAILED — stop and fix' -ForegroundColor Red; exit 1 }

Write-Host "Backup completo: $backupDir" -ForegroundColor Green
```

**Verifica:** `Get-ChildItem $backupDir` deve mostrare 4 file/dir (frontend-dist.zip, backend-app.zip, .env.backup, alembic-versions/, wellnessbuddy-db.dump).

---

## §4. Stop services

```powershell
# 4.1 Stop NSSM service (backend uvicorn)
Stop-Service WellnessBuddyAPI -Force
Get-Service WellnessBuddyAPI  # deve mostrare Status: Stopped

# 4.2 Stop IIS site + app pool (frontend)
Import-Module WebAdministration
Stop-Website -Name 'wellness-buddy.epartner.it'
Stop-WebAppPool -Name 'wellness-buddy-pool'  # nome esatto se diverso, controlla con Get-WebAppPool
```

Verifica:
- `Get-Service WellnessBuddyAPI` → Stopped
- `(Get-Website 'wellness-buddy.epartner.it').State` → Stopped

---

## §5. Estrai nuovo pacchetto (overlay sopra installazione esistente)

**ATTENZIONE:** non sovrascrivere `.env` esistente — contiene SECRET_KEY + DATABASE_URL produzione. Estrazione esclude `.env`.

```powershell
$source = 'C:\Deploys\v0.2.0\wellness-buddy-6e90d36-20260505-1547.zip'
$target = 'E:\www\wellnessBuddy'

# 5.1 Estrai in temp dir, poi merge selettivo
$tempExtract = "C:\Deploys\v0.2.0\extracted-$ts"
Expand-Archive -Path $source -DestinationPath $tempExtract -Force

# 5.2 Sostituisci backend/app (preserva .env, .venv, alembic.ini se modificati)
robocopy "$tempExtract\backend\app" "$target\backend\app" /MIR /XF '*.pyc' /NJH /NJS /NFL /NDL /NP

# 5.3 Sostituisci frontend/dist (asset hashati, safe overwrite totale)
robocopy "$tempExtract\frontend\dist" "$target\frontend\dist" /MIR /NJH /NJS /NFL /NDL /NP

# 5.4 Aggiorna deploy/ scripts (NON web.config se modificato manualmente — verifica)
robocopy "$tempExtract\deploy" "$target\deploy" /E /XO /NJH /NJS /NFL /NDL /NP

# 5.5 Aggiorna alembic versions (CRITICO — porta le 2 nuove migrations)
robocopy "$tempExtract\backend\alembic\versions" "$target\backend\alembic\versions" /E /XF '*.pyc' /NJH /NJS /NFL /NDL /NP

# 5.6 Verifica file presenti
Test-Path "$target\backend\alembic\versions\0001_weekly_variant_per_day.py"  # → True
Test-Path "$target\backend\alembic\versions\0002_activate_groups.py"          # → True
Test-Path "$target\backend\app\templates\shopping_list.html"                  # → True (Plan 02-06)
Test-Path "$target\backend\app\templates\fonts"                               # → True (woff2)
```

Se qualcuno False → estrazione incompleta, ripeti.

---

## §6. Aggiorna .env (aggiungi PDF_BACKEND)

```powershell
$envFile = 'E:\www\wellnessBuddy\backend\.env'
$content = Get-Content $envFile -Raw

# 6.1 Verifica se PDF_BACKEND già presente
if ($content -notmatch 'PDF_BACKEND=') {
    Add-Content $envFile "`nPDF_BACKEND=weasyprint`n"
    Write-Host 'PDF_BACKEND=weasyprint aggiunto a .env' -ForegroundColor Green
} else {
    Write-Host 'PDF_BACKEND già presente, controlla manualmente' -ForegroundColor Yellow
    Get-Content $envFile | Select-String 'PDF_BACKEND'
}
```

**Atteso `.env` finale contiene almeno:**
- `DATABASE_URL=postgresql+asyncpg://...@192.168.3.243:5432/WellnessBuddy`
- `SECRET_KEY=...` (64+ char hex)
- `CORS_ORIGINS=https://wellness-buddy.epartner.it`
- `ADMIN_EMAIL=s.brunelli@epartner.it`
- `PDF_BACKEND=weasyprint`
- `MAX_USERS=100`
- `JWT_ACCESS_MIN=15`
- `JWT_REFRESH_DAYS=7`

Se mancante qualcosa → recupera da backup `$backupDir\.env.backup`.

---

## §7. Apply DB migrations (CRITICAL — 2 nuove)

PowerShell admin in `E:\www\wellnessBuddy\backend\`:

```powershell
cd E:\www\wellnessBuddy\backend
.venv\Scripts\python.exe -m alembic current
# Output atteso: 8137b2e24001 (head) o simile — la revisione del primo deploy

.venv\Scripts\python.exe -m alembic upgrade head
# Output atteso (in ordine):
#   INFO Running upgrade ... -> 0001, weekly_variant_per_day
#   INFO Running upgrade 0001 -> 0002, activate_groups

.venv\Scripts\python.exe -m alembic current
# Output atteso: 0002 (head)
```

**Verifiche post-migration:**

```powershell
# 7.1 Schema check — colonna day_of_week presente
$sql = "SELECT column_name FROM information_schema.columns WHERE table_name='weekly_plan_variants' AND column_name='day_of_week';"
& psql.exe -h 192.168.3.243 -U postgres -d WellnessBuddy -c $sql
# Output atteso: 1 row (day_of_week)

# 7.2 Schema check — group_id su users + groups table popolata
$sql = "SELECT count(*) FROM groups; SELECT count(*) FROM users WHERE group_id IS NULL;"
& psql.exe -h 192.168.3.243 -U postgres -d WellnessBuddy -c $sql
# Output atteso: groups=N (>=1 per ogni user esistente), users con group_id NULL = 0
```

Se `users con group_id NULL > 0` → migration backfill incompleta. Re-run:
```powershell
.venv\Scripts\python.exe -m alembic downgrade -1
.venv\Scripts\python.exe -m alembic upgrade head
```

---

## §8. Restart services

```powershell
# 8.1 Start NSSM service
Start-Service WellnessBuddyAPI
Start-Sleep -Seconds 5
Get-Service WellnessBuddyAPI  # → Running

# 8.2 Verifica logs uvicorn (NSSM stderr)
Get-Content 'E:\www\wellnessBuddy\stderr.log' -Tail 20
# Cerca: "Application startup complete" + "Scheduler started"
# Errori comuni:
#   - ModuleNotFoundError → re-run: .venv\Scripts\python.exe -m uv sync
#   - validation_error su settings → .env mancante o malformato
#   - DB connection refused → verifica 192.168.3.243:5432 raggiungibile

# 8.3 Smoke check API
$health = Invoke-RestMethod http://127.0.0.1:8000/api/health
$health  # → @{status='ok'; version='0.2.0'; build_hash='6e90d36'}

# 8.4 Verifica nuove route Plan 02-04 + 02-05 + 02-07 esposte
$openapi = Invoke-RestMethod http://127.0.0.1:8000/openapi.json
$openapi.paths.PSObject.Properties.Name | Where-Object { $_ -match 'shopping|family|weekly' } | Sort-Object
# Atteso (10 route minimo):
#   /api/family/share/{variant_id}
#   /api/shopping/{week_start}
#   /api/shopping/{week_start}/check
#   /api/shopping/{week_start}/export-pdf
#   /api/shopping/{week_start}/reset
#   /api/weekly/{week_start}
#   /api/weekly/{week_start}/summary
#   /api/weekly/{week_start}/variant
```

```powershell
# 8.5 Start IIS site + app pool
Start-WebAppPool -Name 'wellness-buddy-pool'
Start-Website -Name 'wellness-buddy.epartner.it'
(Get-Website 'wellness-buddy.epartner.it').State  # → Started
```

---

## §9. Smoke test E2E (browser PC + iPhone)

### 9.1 Da PC desktop

Apri `https://wellness-buddy.epartner.it` in browser:

- [ ] Pagina carica senza errore
- [ ] Login con account Stefano funziona
- [ ] /today mostra: Greeting + MacroRing leggibile + 5 pasti (colazione, pranzo, 4 spuntini pomeriggio, cena, 3 spuntini serale)
- [ ] /settimana mostra 7 giorni × 5 slot per giorno con date picker italiano
- [ ] /spesa mostra 5 categorie con items aggregati Stefano
- [ ] Esporta PDF: download `Lista-spesa-{w}.pdf` + toast "PDF pronto."
- [ ] /piano upload `PIANO_NUTRIZIONALE_STEFANO.md` → NO toast "Sezioni non riconosciute"

### 9.2 Da iPhone (Stefano + Marta)

- [ ] Apri Safari su iPhone → `https://wellness-buddy.epartner.it`
- [ ] Login Stefano funziona
- [ ] Tap "Condividi" → "Aggiungi a schermata Home" (PWA install)
- [ ] Aprire app dalla home — tab bar bottom, icone Phosphor visibili
- [ ] Carousel spuntini: swipe sx/dx tra 4 alternative pomeriggio
- [ ] Esporta PDF da /spesa: si apre in Safari, accenti Italian leggibili (à è ì ò ù)
- [ ] Condividi PDF via Mail.app: anteprima rendering accenti corretto
- [ ] Login Marta su altro iPhone → vede pranzi/cene Stefano con badge "Condiviso con Stefano"

---

## §10. Run human-verify checklist (post-deploy obbligatorio)

Phase 2 closure CHECKPOINT richiede 4 firme. Prendi 30-45 minuti:

1. **Tone review (Stefano + Marta, ~15min):** apri `.planning/phases/02-differentiators/02-08-TONE-REVIEW-CHECKLIST.md`. Vai su 7 surface della PWA installata, segui matrice Lifesum Pure variant A, firma + data + verdetto.

2. **iPhone PDF accent verify (Stefano, ~10min):** apri `.planning/phases/02-differentiators/02-06-IPHONE-PDF-VERIFY.md`. Genera PDF su prod, testa 7-string corpus (Pomodorì, Caffè, Olio d'oliva, Yogurt grèco, piada, puttanèsca, Tiramisù) su 4 surface (Safari, Mail.app, Files, Adobe Reader/Preview). Se FAIL: flip `PDF_BACKEND=reportlab` in `.env` + restart service.

3. **GTK3 Day 7 stability (Stefano, ~5min ora + 7 giorni monitoring):** apri `.planning/phases/02-differentiators/02-01-GTK3-SPIKE.md`. Compila Day 0 (oggi), poi Day 1/3/4/7. 5xx-rate <2% PASS, ≥2% flip backend.

4. **Production Lighthouse (Stefano, ~5min):** apri Chrome DevTools su `https://wellness-buddy.epartner.it/today` (e /settimana, /spesa). F12 → Lighthouse tab → Generate report (mobile + Performance + PWA + Accessibility). Target: PWA ≥95 + a11y ≥95. Registra 6 score in `.planning/phases/02-differentiators/VERIFICATION.md` §1.

---

## §11. Rollback plan (se qualcosa va storto)

Trigger rollback se:
- §8.3 health check fallisce
- §8.4 route mancanti
- §9 errori browser persistenti
- §7 migration error che corrompe DB

```powershell
# 11.1 Stop services
Stop-Service WellnessBuddyAPI -Force
Stop-Website -Name 'wellness-buddy.epartner.it'

# 11.2 Restore code da backup
$backupDir = 'E:\Backups\WellnessBuddy\v0.1-pre-v0.2-{ts}'  # path corretto
Expand-Archive -Path "$backupDir\backend-app.zip" -DestinationPath 'E:\www\wellnessBuddy\backend\app' -Force
Expand-Archive -Path "$backupDir\frontend-dist.zip" -DestinationPath 'E:\www\wellnessBuddy\frontend\dist' -Force
Copy-Item "$backupDir\.env.backup" 'E:\www\wellnessBuddy\backend\.env' -Force

# 11.3 Rollback migrations
cd E:\www\wellnessBuddy\backend
.venv\Scripts\python.exe -m alembic downgrade -2  # da 0002 → 0000

# 11.4 Restore DB se schema corrotto (last resort)
& pg_restore.exe -h 192.168.3.243 -U postgres -d WellnessBuddy -c "$backupDir\wellnessbuddy-db.dump"

# 11.5 Restart services
Start-Service WellnessBuddyAPI
Start-Website -Name 'wellness-buddy.epartner.it'
```

---

## §12. Post-deploy cleanup

Una volta verificato tutto OK:

```powershell
# 12.1 Rimuovi diagnostic endpoint (opzionale)
# /api/_debug/parser-introspect è in app/api/health.py — lascialo, è harmless

# 12.2 Cancella zip pacchetto (riapri-da-zero in caso serva)
# Tieni 1-2 backup recenti, cancella i più vecchi
Get-ChildItem E:\Backups\WellnessBuddy\v0.1-pre-v0.2-* | Sort-Object CreationTime -Descending | Select-Object -Skip 2 | Remove-Item -Recurse -Force

# 12.3 Aggiorna .planning/STATE.md (sul tuo PC dev) → phase_2_status: completed
# (Verrà fatto da /gsd:execute-phase 02-differentiators dopo le 4 firme)
```

---

## Riassunto comandi essenziali (cheat-sheet)

```powershell
# Pre-deploy
Get-FileHash wellness-buddy-6e90d36-20260505-1547.zip -Algorithm SHA256

# Stop tutto
Stop-Service WellnessBuddyAPI -Force
Stop-Website -Name 'wellness-buddy.epartner.it'

# Backup minimal
Compress-Archive 'E:\www\wellnessBuddy\backend\app\*' -DestinationPath 'C:\backup-app-pre-update.zip'
pg_dump -h 192.168.3.243 -U postgres -d WellnessBuddy -Fc -f C:\db-backup.dump

# Deploy
Expand-Archive wellness-buddy-6e90d36-20260505-1547.zip -DestinationPath C:\extract -Force
robocopy C:\extract\backend\app E:\www\wellnessBuddy\backend\app /MIR /XF *.pyc
robocopy C:\extract\frontend\dist E:\www\wellnessBuddy\frontend\dist /MIR
robocopy C:\extract\backend\alembic\versions E:\www\wellnessBuddy\backend\alembic\versions /E

# Migrate
cd E:\www\wellnessBuddy\backend
.venv\Scripts\python.exe -m alembic upgrade head

# Start tutto
Start-Service WellnessBuddyAPI
Start-Website -Name 'wellness-buddy.epartner.it'

# Smoke
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

---

**Tempo stimato totale:** 30-40 minuti (deploy ~10min + smoke test ~10min + 4 human-verify ~30min).

**Done = Phase 2 chiusa.** Run `/gsd:execute-phase 02-differentiators` su PC dev dopo firme per flippare STATE.md a `completed`.
