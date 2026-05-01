# win-acme — Let's Encrypt cert for `wellness-buddy.epartner.it`

> **Status:** Production setup (DEP-04). Stefano è familiare con win-acme da altri sottodomini epartner.it (CONTEXT.md "Integration Points") — questo documento è un riferimento rapido, non un tutorial.

---

## Quick start (interactive `wacs.exe`)

```powershell
cd C:\Tools\win-acme
.\wacs.exe
```

Interactive flow on Windows Server:

| Step | Choice | Notes |
|------|--------|-------|
| 1 | `M` — Create renewal with advanced options | Skip the simple flow so we can pick rsa key + IIS auto-binding |
| 2 | `1` — Read bindings from IIS | Picks up sites already configured |
| 3 | Select site `wellness-buddy` | The site created in DEPLOY.md §8 |
| 4 | `5` — SAN certificate including `wellness-buddy.epartner.it` | One host per cert is enough Phase 1 |
| 5 | `1` — HTTP-01 ACME validation via IIS file | Default; works because IIS site already serves on port 80 |
| 6 | `2` — RSA key | Stable, broad client compat |
| 7 | `3` — PFX archive in IIS Cert Store | Bound automatically to the site's HTTPS binding |
| 8 | `1` — IIS Web (auto-binding) | Adds the 443 binding + cert to IIS |
| 9 | Email: `<admin email>` | For renewal notifications + Let's Encrypt account |
| 10 | Accept TOS | Required by ACME |

---

## One-shot non-interactive (CI / scripted)

```powershell
.\wacs.exe `
  --target iis `
  --siteid <site-id> `
  --installation iis `
  --emailaddress admin@your-domain.it `
  --accepttos
```

`<site-id>` is the IIS site numeric ID — find it via `Get-Website wellness-buddy | Select-Object Id`.

---

## Auto-renewal

win-acme installs a Windows Scheduled Task at first run:

- **Task name:** `win-acme renew (acme-v02.api.letsencrypt.org)`
- **Trigger:** daily, 09:00 (default)
- **Action:** `wacs.exe --renew --baseuri "https://acme-v02.api.letsencrypt.org/"`

Verify it exists:

```powershell
Get-ScheduledTask -TaskName 'win-acme*'
```

The task renews any cert with ≤30 days left automatically. No further action needed.

---

## Smoke test after install

```powershell
pwsh ../scripts/smoke-test.ps1 https://wellness-buddy.epartner.it
```

The smoke test checks `/api/health`, `/version.json`, root HTML, and **HTTPS cert expiry days remaining**. A warning is printed if cert expires within 14 days (auto-renewal should prevent this — investigate the scheduled task if it fires).

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| HTTP-01 challenge fails | IIS site not reachable on port 80 from internet | Verify firewall + DNS A record `wellness-buddy.epartner.it` → server IP |
| Renewal task missing | win-acme not run interactively yet | Run `.\wacs.exe` once interactively to create the task |
| Cert binds but browser shows untrusted | Intermediate chain missing | Re-run `wacs.exe --target` with `--installation iis` to refresh chain |

---

*Last updated: Phase 1 close (Plan 08).*
