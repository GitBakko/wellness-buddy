# Plan 02-01 — WeasyPrint GTK3 7-Day Stability Spike

**Spike opened:** ____________ (Stefano fills Day 0 — date the install ran on Windows Server 2019 staging host)
**Spike closes:** Day 7 (Stefano fills final verdict)
**Server:** Windows Server 2019 · staging host · `wellness-buddy.epartner.it`
**Threshold (D-11):** 5xx rate <2% over 7-day window → PASS · ≥2% → activate ReportLab fallback via `PDF_BACKEND=reportlab`
**Scope of this artifact:** opens during Plan 02-01 (this commit). Day 0 install + 7-day continuous logging happen during Plan 02-03 deploy walkthrough on the production-bound box. Verdict reviewed by Plan 02-07 closure before Phase 2 pause gate.

---

## GTK3 WeasyPrint 7-Day Stability Spike

This is the spike checklist that locks D-11 (PDF backend choice). All commands run on Windows Server 2019, **NOT** developer dev box. See `DEPLOY.md` Appendix B for verbatim install commands; this artifact records the verdict.

> **[HUMAN: Stefano runs Section "Day 0 install verification" during Plan 02-03 deploy walkthrough on Windows Server 2019. Then logs Day 1/3/4/7 cadence checks over the following week. Plan 02-07 reviews the filled-in matrix before the Phase 2 pause gate. The Day 0 row cannot be filled by Claude — it requires touching the production-bound NSSM service.]**

---

## Day 0 install verification

| Check | Expected | Result | Date |
|-------|----------|--------|------|
| MSYS2 installer ran | `C:\msys64` exists | | |
| `pacman -Q mingw-w64-x86_64-pango` | Version recorded (e.g. `1.51.0-1`) | | |
| `C:\msys64\mingw64\bin` in System PATH | `$env:Path -split ';' \| Where-Object { $_ -match 'mingw64' }` returns the path | | |
| NSSM service restarted with new PATH | `Get-Service WellnessBuddyAPI` Status=Running | | |
| `python -m weasyprint --info` | Returns version + Pango + Cairo lines (≥3 lines) | | |
| Smoke `HTML(string='<h1>à è ì ò ù</h1>').write_pdf(...)` | Non-zero PDF, accents render in Adobe Reader | | |
| Endpoint `POST /api/shopping/{week}/export-pdf` | Returns 200 + valid PDF byte stream (Plan 02-05 deliverable) | | |
| iPhone Safari opens PDF | Renders, accents intact | | |
| Mail.app preview | Renders, accents intact | | |

---

## 7-day stability checklist (continuous logging)

| Check | Pass criterion | Cadence | Day 1 | Day 3 | Day 7 |
|-------|----------------|---------|-------|-------|-------|
| `python -m weasyprint --info` | Returns version info post-reboot | Day 1, Day 4 | | | |
| 50 sample PDFs generated | All open in Adobe Reader, accents correct | Day 0 | | | |
| NSSM service PATH stable through reboot | `--info` survives `Restart-Computer` | Day 1, Day 4 | | | |
| Memory leak check | RSS stable over 100 PDFs (no monotonic growth — record start/end MB) | Day 3 | | | |
| Cold-start time post-reboot | First PDF generated <10s | Day 1 | | | |
| Pango pinned (no auto-update breakage) | `pacman -Q mingw-w64-x86_64-pango` matches Day 0 | Day 7 | | | |
| 5xx rate during 7-day window | <2% (D-11 threshold — count `500/502/503/504` from `/api/shopping/*/export-pdf` divided by total PDF requests in backend logs) | Continuous | | | |

---

## Verdict (filled by Stefano on Day 7)

| Outcome | Action |
|---------|--------|
| ✅ PASS — 5xx <2% AND all checks green | Lock `PDF_BACKEND=weasyprint` in `.env.production`. Plan 02-05 ships WeasyPrint primary. Document install in DEPLOY.md Appendix B as canonical. |
| ❌ FAIL — any check red OR 5xx ≥2% | Flip `PDF_BACKEND=reportlab` in `.env.production` and `Restart-Service WellnessBuddyAPI`. Plan 02-05 ships ReportLab as active backend. Update Phase 2 STATE.md decisions log with reason + date. Open follow-up issue to revisit Phase 4 hardening. |

---

## Sign-off

| Reviewer | Initial | Date (YYYY-MM-DD) | Verdict (PASS/FAIL) | Notes |
|----------|---------|-------------------|---------------------|-------|
| Stefano  |         |                   |                     |       |

---

## Operator notes (collected during the 7-day window)

> Free-form log. Stefano captures any GTK3-related observation here:
> - Did Pango auto-update? When?
> - Any antivirus quarantine event on `weasyprint.exe`?
> - PDF generation latency drift (Day 0 vs Day 7)?
> - Memory consumption envelope of NSSM service over the week?

```
Day 0 (____________):

Day 1:

Day 3:

Day 4:

Day 7 (verdict):
```

---

*Plan 02-01 ships the spike scaffold (this file + PdfExporter ABC + ReportLab fallback). The 7-day run is owned by Stefano on the Windows Server 2019 production-bound host during/after Plan 02-03 deploy walkthrough. Phase 2 pause gate (Plan 02-07) cannot close until this artifact is signed-off.*
