# Plan 02-03 — Production Deploy CHECKPOINT (Stefano + Marta)

**Date attempted:** ____________  
**Server:** Windows Server 2019 · `wellness-buddy.epartner.it`  
**Deploy script source:** `DEPLOY.md` (Plan 01-08 deliverable + Plan 02-01 Appendix B)

## 1. Pre-flight — DNS + firewall
- [ ] DNS A record `wellness-buddy.epartner.it` → server IP (verify via `nslookup wellness-buddy.epartner.it`)
- [ ] Firewall allows 80/443 inbound (verify via `Test-NetConnection -ComputerName wellness-buddy.epartner.it -Port 443`)
- [ ] PostgreSQL service running (`Get-Service postgresql-x64-*`)

## 2. Database
- [ ] CREATE DATABASE `wellness_buddy_prod` OWNER `wellness_buddy`
- [ ] `uv sync --frozen` in backend dir (pulls weasyprint + reportlab + apscheduler from Plan 02-01)
- [ ] `alembic upgrade head` returns no errors (`a694bcd4d792` Phase 1 baseline; Plan 02-06 ships `0001_activate_groups`)
- [ ] `\dt` in psql shows expected 12+ tables (users, groups, refresh_tokens, invite_tokens, nutrition_plans, weekly_plan_variants, weight_logs, workout_logs, shopping_list_states, ai_event_log, audit_log, alembic_version)

## 3. Secrets
- [ ] `pwsh deploy/scripts/generate-secrets.ps1` produces `.env.production`
- [ ] JWT secret rotated (≠ dev value; ≥32 random bytes)
- [ ] DATABASE_URL points to `wellness_buddy_prod`
- [ ] CORS_ORIGINS = `https://wellness-buddy.epartner.it`
- [ ] PDF_BACKEND=weasyprint (Plan 02-01 default; Stefano flips to reportlab if 7-day spike fails)

## 4. NSSM service
- [ ] `nssm install WellnessBuddyAPI` succeeded (script: `deploy/nssm/install-service.ps1`)
- [ ] Service auto-start enabled
- [ ] Service starts cleanly (`Get-Service WellnessBuddyAPI` → Running)
- [ ] Application Event Log shows uvicorn startup, no errors
- [ ] `C:\msys64\mingw64\bin` present in System PATH AND inherited by NSSM (`nssm get WellnessBuddyAPI AppEnvironmentExtra` lists it OR System PATH propagated post reboot)

## 5. IIS reverse proxy
- [ ] `web.config` deployed at IIS site root (file: `deploy/iis/web.config`)
- [ ] URL Rewrite + ARR modules confirmed installed (`Get-WindowsFeature` + IIS GUI)
- [ ] HTTPS smoke test 200 from local → reverse-proxy → backend (`Invoke-WebRequest https://wellness-buddy.epartner.it/api/health`)
- [ ] WebSocket upgrade headers preserved (`curl -i -H "Connection: Upgrade" -H "Upgrade: websocket" ...` returns 101 or 200 with no rewrite stripping)

## 6. SSL via win-acme
- [ ] `wacs.exe` interactive run completed for `wellness-buddy.epartner.it` (script: `deploy/win-acme/README.md`)
- [ ] Certificate issued + auto-renewal scheduled task created (`Get-ScheduledTask | Where-Object { $_.TaskName -match 'win-acme' }`)
- [ ] `https://wellness-buddy.epartner.it` returns 200 from EXTERNAL connection (mobile network, NOT same LAN)
- [ ] Browser shows "Connessione protetta" (no cert warnings, no mixed-content)

## 7. Smoke test
- [ ] `pwsh deploy/scripts/smoke-test.ps1` → all checks green
- [ ] `/api/health` returns `{"status": "ok"}`
- [ ] `/api/version` returns expected git sha (matches `git rev-parse HEAD` on deploy host)
- [ ] First user login succeeds end-to-end (Stefano account)
- [ ] /api/weekly/{week_start} returns 200 for Stefano's seeded plan (Plan 02-02 endpoint live)

## 8. iPhone install (Stefano)
- [ ] Open Safari → `https://wellness-buddy.epartner.it`
- [ ] Tap Share → "Aggiungi a Home" visible in share menu
- [ ] Add to home screen — custom icon visible (NOT generic web clip; FND-05 + UI-09 manifest icons 192/512 + theme color)
- [ ] Tap home-screen icon → app opens in standalone mode (no Safari chrome, no URL bar)
- [ ] /today renders with Lifesum Pure theme (warm cream bg, MacroRing centered, Plus Jakarta font, leaf-sage primary CTA, Geist Mono numerics, Instrument Serif greeting)
- [ ] /settimana/{thisWeek} renders (Plan 02-02 ship validation) — week picker + variant pills visible
- [ ] Toggle airplane mode ON → reload /today → cached page renders + sync pip shows "Offline"
- [ ] Toggle airplane mode OFF → sync pip flips to "Sincronizzato" within 5s (TanStack Query refetchOnReconnect)
- [ ] Kill app via swipe-up → reopen → still logged in (no logout storm — refresh token rotation working, AUTH-08 grace window)

## 9. iPhone install (Marta)
- [ ] Same 9 steps as §8, with Marta's account on Marta's iPhone
- [ ] Verify Marta sees ONLY her plan / weight / workout (NOT Stefano's data)
- [ ] (FAM-* not yet shipped — Plan 02-06 will validate cross-user) — for Plan 02-03 only verify Marta's data isolation

## 10. Lighthouse audit (Stefano, Chrome desktop pointing at production URL `https://wellness-buddy.epartner.it/today`)
- [ ] Lighthouse PWA score: ____ / 100 (target ≥95 per D-28 — record actual; lock 100/100 if achievable)
- [ ] Lighthouse Accessibility score: ____ / 100 (target ≥95 per D-28)
- [ ] Lighthouse Performance score: ____ / 100 (informational — Phase 4 hardens)
- [ ] Lighthouse Best Practices score: ____ / 100 (informational)

## 11. Tone calibration sign-off (Stefano + Marta — IN PERSON, both iPhones present)
- [ ] Both users open /today on their respective iPhones (production install from §8 / §9)
- [ ] Confirm Lifesum Pure variant A rendering matches `mockups/tone-calibration-v2/A-lifesum-pure.html` expectation
- [ ] Confirm fonts (Plus Jakarta + Geist Mono + Instrument Serif greeting) load correctly
- [ ] Confirm dark mode toggle works (Settings → Tema → Scuro)
- [ ] No "office app" tone drift observed
- [ ] No infantile mascots or `!` in error copy spotted (UI-17 inheritance)
- [ ] Variante A · Lifesum Pure: LOCKED (cross-reference `01-08-tone-calibration-checklist.md` final sign-off)

## 12. Sign-off

| Reviewer | Initial | Date (YYYY-MM-DD) | Time (HH:MM) | Verdict (PASS/CONCERNS/BLOCK) | Notes |
|----------|---------|-------------------|--------------|-------------------------------|-------|
| Stefano  |         |                   |              |                               |       |
| Marta    |         |                   |              |                               |       |

**Closure rule (D-26):** Any `BLOCK` verdict from either reviewer keeps this checkpoint non-merged → blocks Phase 2 progression to Plan 02-04. `CONCERNS` notes must be triaged into Plan 02-07 closure tasks. Both reviewers must mark `PASS` for the checkpoint to clear.
