# Wellness Buddy — Deploy Guide (Windows Server 2019)

> **Status:** Production-ready (Phase 1 close, Plan 08).
> **Domain:** `wellness-buddy.epartner.it` (D-05 — sottodominio epartner.it esistente, win-acme flow noto)
> **Strategy:** D-06 — first deploy deferred to end of Phase 1, full app structured + verified locally before going live.

---

## 1. Prerequisites

| Tool | Version | Status on Windows Server | Install if missing |
|------|---------|--------------------------|---------------------|
| PostgreSQL | 14 or higher | Already installed (existing infra) | n/a |
| IIS | 10 | Already configured for other epartner.it sites | Server Manager → Add Roles → Web Server (IIS) |
| URL Rewrite module (IIS) | 2.x | Likely present, verify in IIS Manager | <https://www.iis.net/downloads/microsoft/url-rewrite> |
| Application Request Routing (ARR) | 3.x | Likely present, verify "Application Request Routing Cache" appears at server level in IIS Manager | <https://www.iis.net/downloads/microsoft/application-request-routing> |
| NSSM | 2.24+ | Install | <https://nssm.cc/download> — extract to `C:\Tools\nssm` and add to PATH |
| win-acme | latest | Already used for other epartner.it subdomains | <https://www.win-acme.com/> — extract to `C:\Tools\win-acme` |
| Python | 3.12.x | Install | <https://www.python.org/downloads/> — tick "Add to PATH" during install |
| uv (Astral) | latest | Install via PowerShell (Administrator) | `iwr -useb https://astral.sh/uv/install.ps1 \| iex` |
| Git | latest | Likely present | <https://git-scm.com/> |
| Node.js LTS | 22.x | Install for build only | <https://nodejs.org/> |
| pnpm | 9+ | Install | `iwr https://get.pnpm.io/install.ps1 -useb \| iex` |

**Phase 2 prerequisites (NOT NEEDED for Phase 1 deploy):**

| Tool | Phase | Notes |
|------|-------|-------|
| GTK3 Runtime (WeasyPrint dependency) | Phase 2 | URL must be re-verified before Phase 2 spike (per STATE.md TODO Backlog). Tentative source: <https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer> |

---

## 2. Database setup (D-28)

```powershell
psql -U postgres -h localhost -c "CREATE DATABASE \"WellnessBuddy\";"
psql -U postgres -h localhost -c "CREATE USER wnbd WITH PASSWORD '<DB_PASSWORD_FROM_GENERATE_SECRETS>';"
psql -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE \"WellnessBuddy\" TO wnbd;"
psql -U postgres -h localhost -d WellnessBuddy -c "GRANT ALL ON SCHEMA public TO wnbd;"
```

If the database already exists, the first command errors harmlessly.

---

## 3. Generate secrets (D-24, D-25)

```powershell
pwsh deploy/scripts/generate-secrets.ps1
```

The script outputs to stdout only (never to disk):

- `SECRET_KEY` — 32-byte hex (64 chars) for JWT signing
- `DB_PASSWORD` — URL-safe random 24+ chars for `wnbd` PostgreSQL user
- A ready-to-paste `DATABASE_URL` line and an `ALTER USER wnbd WITH PASSWORD '...'` SQL line

Copy the values straight into `backend/.env` (next step). They will not be shown again.

**Encrypt `backend/.env` at rest using DPAPI** (manual procedure, per CONTEXT D-25):

```powershell
$bytes = [System.IO.File]::ReadAllBytes("backend\.env")
$protected = [System.Security.Cryptography.ProtectedData]::Protect($bytes, $null, "LocalMachine")
[System.IO.File]::WriteAllBytes("backend\.env.dpapi", $protected)
```

Lock down ACL so only the service account + Administrators can read:

```powershell
icacls "backend\.env" /inheritance:r /grant:r "NT AUTHORITY\LocalService:R" "Administrators:F"
```

---

## 4. Configure `backend/.env`

Copy `deploy/.env.production.example` to `backend/.env` and fill values:

```bash
DATABASE_URL=postgresql+asyncpg://wnbd:<DB_PASSWORD>@localhost:5432/WellnessBuddy
SECRET_KEY=<32-byte hex from generate-secrets.ps1>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CRITICAL: never wildcard in prod (Settings rejects it at boot)
CORS_ORIGINS=https://wellness-buddy.epartner.it

AI_PROVIDER=null

MAX_USERS=100
ADMIN_EMAIL=stefano@<your-domain>

LOG_LEVEL=INFO
SQL_ECHO=false
APP_VERSION=0.1.0
BUILD_HASH=<git rev-parse --short HEAD>
TZ=Europe/Rome
```

**Never commit `backend/.env`.** It is in `.gitignore` already.

---

## 5. Backend install + migrations

```powershell
cd C:\path\to\WellnessBuddy\backend
uv sync --frozen
uv run alembic upgrade head
# Verify schema:
psql -U postgres -d WellnessBuddy -c "\dt"
# Expected: ~10 tables (users, groups, nutrition_plans, weekly_plan_variants,
# workout_logs, weight_logs, shopping_list_states, invite_tokens, audit_log,
# alembic_version)
```

Smoke the import path:

```powershell
uv run python -c "from app.main import app; print(app.title)"
# Expected: Wellness Buddy
```

---

## 6. Frontend build

```powershell
cd C:\path\to\WellnessBuddy
pnpm install --frozen-lockfile
$env:VITE_BUILD_HASH = (git rev-parse --short HEAD)
pnpm --filter frontend build
# Output: frontend/dist/  (index.html + hashed assets + manifest + sw.js)
```

---

## 7. Install NSSM Windows service for backend (DEP-01)

```powershell
pwsh deploy/nssm/install-service.ps1
# Wraps Uvicorn with `nssm install WellnessBuddyAPI <uv.exe>` + AppParameters.
# Service name: WellnessBuddyAPI
# Verify: Get-Service WellnessBuddyAPI -> Status: Running
# Verify: Invoke-WebRequest http://127.0.0.1:8000/api/health -> 200
```

The script is idempotent — running it again will stop, remove, and re-install cleanly.
Logs land in `C:\path\to\WellnessBuddy\logs\stdout.log` and `stderr.log`, rotated at 10 MB.

---

## 8. Configure IIS reverse proxy (DEP-02, DEP-03)

1. Open IIS Manager.
2. Create new site:
   - Site name: `wellness-buddy`
   - Physical path: `C:\path\to\WellnessBuddy\frontend\dist`
   - Binding: HTTP, port 80, host header `wellness-buddy.epartner.it`
3. Copy `deploy/iis/web.config` into the site root (overrides any existing).
4. Verify ARR proxy is enabled at the **server level**: IIS Manager → server node → Application Request Routing Cache → Server Proxy Settings → tick **Enable proxy**.
5. Restart IIS:

   ```powershell
   iisreset
   ```

6. Verify proxy:

   ```powershell
   Invoke-RestMethod http://wellness-buddy.epartner.it/api/health
   ```

---

## 9. HTTPS via win-acme (DEP-04)

```powershell
cd C:\Tools\win-acme
.\wacs.exe
# Interactive flow:
#  1. M  -> Create renewal with advanced options
#  2. 1  -> Read bindings from IIS
#  3. Select site "wellness-buddy"
#  4. 5  -> SAN certificate including wellness-buddy.epartner.it
#  5. 1  -> HTTP-01 ACME validation via IIS file
#  6. 2  -> RSA key
#  7. 3  -> PFX archive in IIS Cert Store
#  8. 1  -> IIS Web (auto-binding)
#  9. Email: <admin email>
# 10. Accept TOS
```

Auto-renewal scheduled task is created automatically by win-acme; verify with:

```powershell
Get-ScheduledTask -TaskName "win-acme*"
```

See `deploy/win-acme/README.md` for the full step-by-step.

---

## 10. First admin user

Wellness Buddy uses invite-only signup (D-17). To onboard Stefano as the first admin:

```powershell
cd C:\path\to\WellnessBuddy\backend
uv run python -c "
import asyncio
from app.services.auth_service import create_invite
from app.core.db import async_session_factory

async def main():
    async with async_session_factory() as s:
        token = await create_invite(s, email='stefano@<your-domain>', role='admin')
        print(f'Invite link: https://wellness-buddy.epartner.it/register?token={token}')

asyncio.run(main())
"
```

Stefano clicks the link → form pre-filled with token → creates account → automatic login.

---

## 11. Smoke test (DEP-09)

```powershell
pwsh deploy/scripts/smoke-test.ps1 https://wellness-buddy.epartner.it
```

Expected output:

- `/api/health` returns 200 with `status=ok`, `version=...`, `build_hash=...`, `db_ok=true`
- `/version.json` returns 200 with `version` and `build_hash`
- `/` serves `frontend/dist/index.html` (matches "Wellness Buddy")
- HTTPS cert valid + not expired

Real-iPhone Safari smoke test (manual, Phase 1 pause gate):

1. Visit `https://wellness-buddy.epartner.it` on iPhone Safari.
2. Tap Share → "Aggiungi a Home" → confirm "Aggiungi".
3. Open from Home (standalone mode, no Safari chrome).
4. Login → /welcome → tap "Abilita storage offline".
5. Land on /today → see meals.
6. Toggle airplane mode ON → reload → /today still renders from cache.
7. Log a workout → see "Modalità offline" toast.
8. Toggle airplane mode OFF → mutation queue flushes → toast `Sincronizzato`.

---

## 12. GTK3 note for Phase 2 (deferred)

WeasyPrint (Phase 2 PDF shopping list) requires GTK3 Runtime on Windows. **Do not install in Phase 1** — defer until Phase 2 spike validates Windows Server 2019 stability.

When ready in Phase 2:

1. Re-verify the GTK3 Runtime MSI URL (the maintained fork has changed hosts in the past — STATE.md TODO Backlog tracks this).
2. Tentative source: <https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer>
3. Run WeasyPrint spike per Phase 2 plan before going live.

---

## 13. Rollback procedure

If smoke fails or production issue surfaces:

```powershell
# Stop service
Stop-Service WellnessBuddyAPI

# Restore previous frontend dist (assumed taken pre-deploy as backup)
Copy-Item -Recurse C:\path\to\backups\frontend-dist-<previous>\* C:\path\to\WellnessBuddy\frontend\dist\

# Restore previous python venv via uv from previous lockfile
cd backend
git checkout <previous-tag> -- uv.lock
uv sync --frozen

# Roll back DB migration if a new one was applied
uv run alembic downgrade -1

# Restart
Start-Service WellnessBuddyAPI
iisreset

# Verify
pwsh deploy/scripts/smoke-test.ps1 https://wellness-buddy.epartner.it
```

---

## 14. Operational notes

### Logs

NSSM stdout / stderr → `C:\path\to\WellnessBuddy\logs\stdout.log` (rotated at 10 MB).

Tail live:

```powershell
Get-Content C:\path\to\WellnessBuddy\logs\stdout.log -Wait -Tail 50
```

### Bumping `APP_VERSION`

Edit `backend/.env` `APP_VERSION=` and `BUILD_HASH=` (use `git rev-parse --short HEAD`), then:

```powershell
Restart-Service WellnessBuddyAPI
```

The frontend reads `/version.json` every 5 minutes when tab is visible — a version mismatch triggers the `Nuova versione disponibile` toast.

### Database backup

Hand-off to Stefano's existing PostgreSQL backup tooling (NXTLink) — see CONTEXT.md "TODO Backlog #4". Daily `pg_dump WellnessBuddy` recommended.

### Health monitoring

Existing NXTLink monitoring polls `/api/health` every 5 min. Alert thresholds inherited.

---

## 15. Future deploys (incremental)

After the first cutover, day-to-day deploys are:

1. `git pull` on server
2. `cd backend && uv sync --frozen && uv run alembic upgrade head`
3. `pnpm install --frozen-lockfile && pnpm --filter frontend build`
4. `Restart-Service WellnessBuddyAPI`
5. `iisreset` (only if `web.config` changed)
6. `pwsh deploy/scripts/smoke-test.ps1 https://wellness-buddy.epartner.it`

---

## 16. Secret rotation (D-27 — manual procedure)

Wellness Buddy has no automated rotation Sprint 1. Rotate manually during low-traffic windows:

### `SECRET_KEY` rotation

1. Generate new value: `python -c "import secrets; print(secrets.token_hex(32))"`
2. Edit `backend/.env`
3. `Restart-Service WellnessBuddyAPI`
4. All issued JWTs become invalid → all users logged out (acceptable for the 2-user famiglia scope; users see `Sessione scaduta` toast and re-login).
5. Refresh tokens in the DB remain rows but their signature won't match — next refresh attempt redirects to `/login`.

### Database password rotation

1. Generate new value via `deploy/scripts/generate-secrets.ps1`.
2. Update PostgreSQL: `psql -U postgres -c "ALTER USER wnbd WITH PASSWORD '<new>';"`
3. Edit `backend/.env` `DATABASE_URL=...` to use the new password.
4. `Restart-Service WellnessBuddyAPI`.

---

## Appendix B: GTK3/Pango runtime for WeasyPrint (Phase 2, DEP-06)

WeasyPrint requires Pango/Cairo/GLib/GObject DLLs from MSYS2's mingw64 distribution.
Install once on Windows Server 2019 production host **before Plan 02-05 ships the PDF endpoint**.
This appendix supersedes Section 12 (the Phase 1 deferral note).

Prerequisite: deploy/baseline already done per Sections 1-15. Run as Administrator.

### B.1 — Install MSYS2

1. Download MSYS2 installer from <https://www.msys2.org/> (~150 MB, one-time).
2. Run installer with default options. Installs to `C:\msys64`.
3. From Start menu open **MSYS2 MINGW64** shell (NOT MSYS2 MSYS — must be the mingw64 variant).

### B.2 — Install Pango (pulls Cairo + GLib + GObject + GDK-PixBuf)

Inside MSYS2 MINGW64 shell:

```bash
pacman -Syu                                  # Update package DB; close shell when prompted, reopen
pacman -S mingw-w64-x86_64-pango             # ~120 MB; pulls dependencies
pacman -Q mingw-w64-x86_64-pango             # Record version for spike Day 7 check
exit
```

### B.3 — Add `C:\msys64\mingw64\bin` to System PATH (Machine scope, NOT User)

PowerShell as Administrator:

```powershell
[Environment]::SetEnvironmentVariable(
  "Path",
  $env:Path + ";C:\msys64\mingw64\bin",
  [EnvironmentVariableTarget]::Machine
)
# Reboot OR restart NSSM service so it inherits new PATH:
nssm restart WellnessBuddyAPI
```

### B.4 — Verify in NSSM service context

```powershell
cd D:\Develop\AI\WellnessBuddy\backend
.\.venv\Scripts\Activate.ps1
uv sync --frozen
python -m weasyprint --info
```

Expected output (≥3 lines):

```text
WeasyPrint version: 62.x.x
Python: 3.12.x
Pango: 1.x.x
Cairo: 1.x.x
```

**If you see `OSError: cannot load library 'gobject-2.0-0'`** → PATH not propagated to NSSM service. Either reboot OR run `nssm set WellnessBuddyAPI AppEnvironmentExtra "PATH=C:\msys64\mingw64\bin;%PATH%"` then `nssm restart WellnessBuddyAPI`.

### B.5 — Smoke test PDF generation with Italian accents

```powershell
python -c "from weasyprint import HTML; HTML(string='<h1>à è ì ò ù — Pasta integrale</h1>').write_pdf('test-accents.pdf')"
start test-accents.pdf
# Adobe Reader opens. Accents must render. If they show as ?/boxes,
# font fallback failed — Plan 02-05 ships base64 woff2 fonts inline (D-13).
```

### B.6 — Open the 7-day stability spike

After B.5 succeeds, fill the Day 0 row of `.planning/phases/02-differentiators/02-01-GTK3-SPIKE.md` and start the continuous logging window. Plan 02-07 reviews verdict before Phase 2 pause gate. If 5xx ≥2% over 7 days, flip `PDF_BACKEND=reportlab` in `.env` and `Restart-Service WellnessBuddyAPI` — the ReportLab fallback (scaffolded in Plan 02-01) takes over without code change.

---

*Last updated: Plan 02-01 (Phase 2 — GTK3 spike + PdfExporter ABC scaffold).*
