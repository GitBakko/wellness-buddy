# Plan 02-06 — iPhone Safari + Mail.app PDF Accent Verification (T-PDF-02)

> **Status (Plan 02-08 closure, 2026-05-05):** PENDING — awaiting iPhone test on real device.
>
> Plan 02-08 closure has prepared this artifact for sign-off. The 4 surfaces × 7 accent strings cannot be verified autonomously — they require a physical iPhone with the installed PWA against the production deploy. Stefano signs each row of the matrix below after running the steps. Phase 2 pause-gate cannot close until at least Surfaces 1, 2, 3 sign PASS (Surface 4 desktop is a complement, not a blocker).

**Verification opened:** _________________ (Stefano fills date)
**Production URL:** `https://wellness-buddy.epartner.it/spesa/{currentWeek}`
**PDF endpoint:** `POST /api/shopping/{week_start}/export-pdf`
**Default backend:** `PDF_BACKEND=weasyprint` (production); local dev uses `reportlab` because the dev box lacks GTK3/Pango.

---

## Why this checklist exists

Plan 02-06 ships the PDF brand template (`backend/app/templates/shopping_list.html`) with woff2 fonts embedded as base64 data URLs (D-13 Italian-accent guarantee). The font data travels inline so the PDF renders the same on any device, but **iPhone Safari and Mail.app preview surfaces** are notorious for falling back to system Helvetica when @font-face directives are not honored exactly. T-PDF-02 (UI-RESEARCH §8) requires manual verification on the real iPhone Stefano + Marta will use day-to-day.

This artifact is filled out by Stefano AFTER the production deploy is live (Plan 02-03 already shipped Plan 02-03 prod environment). Plan 02-08 closure consumes this sign-off.

---

## Test corpus — Italian accents that MUST render correctly

The 7-string accent corpus exercises the full Italian Latin Extended A glyph range plus apostrophe punctuation that often breaks in early-1990s PDF readers:

1. **Pomodorì** (final ì)
2. **Caffè** (final è)
3. **Olio d'oliva extravergine** (apostrophe + d')
4. **Yogurt grèco** (è inside word)
5. **Una piada** (a inside, plus apostrophe-form fallback test)
6. **Spaghetti alla puttanèsca** (è inside word, double s)
7. **Tiramisù** (final ù)

**Acceptance:** every string must render without `?` placeholders, square `□` boxes, or visible Helvetica fallback (Plus Jakarta Sans 700 must render the body — verify the title chrome reads with Plus Jakarta's distinct lowercase `g` two-storey form, not Helvetica's single-storey).

To inject the corpus into a real PDF for testing: ensure Stefano's active plan parsed_json has a meal containing all 7 strings as ingredient names. Easiest path: edit a `_test_accents.md` plan and upload via `/piano`, set as active, then export.

---

## Surfaces

### Surface 1 — iPhone Safari direct download

Steps Stefano runs on his iPhone:

1. [ ] Open `https://wellness-buddy.epartner.it/spesa/{thisWeek}` on the **installed PWA** (NOT browser tab).
2. [ ] Tap **"Esporta PDF"** button in the sticky bottom bar.
3. [ ] Button enters loading state — `CircleNotch` spinner replaces `FilePdf` icon, label "Esporta PDF" stays width-stable.
4. [ ] Sonner toast `"PDF pronto."` appears (4s auto-dismiss).
5. [ ] PDF downloads. Safari opens the inline preview.
6. [ ] All 7 accent test strings render correctly (no `?`, no `□`, no font fallback to system Helvetica).
7. [ ] Page header `Lista spesa` renders Plus Jakarta 700 28pt slate-ink.
8. [ ] Subtitle `settimana del {long it date}` renders Instrument Serif italic 14pt color leaf-700.
9. [ ] Category headings (Frigo & Freschi, Frutta & Verdura, Dispensa, Condimenti, Integratori) render Plus Jakarta 600 14pt with leaf-700 underline 2pt.
10. [ ] Quantity column renders Geist Mono right-aligned tabular-nums.
11. [ ] Footer reads `Wellness Buddy · wellness-buddy.epartner.it` + page counter `1/N` Geist Mono.

### Surface 2 — iPhone Mail.app preview

1. [ ] From Safari preview tap **Share → Mail**.
2. [ ] Compose email with PDF attachment to self.
3. [ ] Tap PDF attachment in compose view → Mail.app preview opens.
4. [ ] All 7 accent strings render correctly.
5. [ ] No layout shift or font fallback observed (the title still reads Plus Jakarta two-storey g).
6. [ ] Wordmark `Wellness Buddy` (top-right) renders with letter-spacing 0.04em.

### Surface 3 — iPhone Files app preview

1. [ ] From Safari preview tap **Share → Save to Files**.
2. [ ] Open Files app → On My iPhone / iCloud Drive → wherever saved.
3. [ ] Tap the PDF → Files preview opens.
4. [ ] All 7 accent strings render correctly.
5. [ ] No glyph regressions vs Surface 1.

### Surface 4 — Desktop reader (macOS Preview OR Adobe Reader Windows)

1. [ ] Transfer PDF to laptop (AirDrop or shared file).
2. [ ] Open in macOS Preview (Stefano laptop) OR Adobe Reader DC (Windows).
3. [ ] All 7 accent strings render correctly.
4. [ ] @page footer renders `Wellness Buddy · wellness-buddy.epartner.it` + page counter `1/N`.
5. [ ] Print Preview uses A4 portrait, 20mm margins; no truncation.

---

## Sign-off matrix

| Surface | Stefano initial | Date | Verdict | Notes |
|---|---|---|---|---|
| 1 — iPhone Safari direct | | | PASS / FAIL | |
| 2 — iPhone Mail.app preview | | | PASS / FAIL | |
| 3 — iPhone Files preview | | | PASS / FAIL | |
| 4 — macOS Preview / Adobe Reader | | | PASS / FAIL | |

---

## Closure rule

- **All 4 surfaces PASS** → SHOP-07 verified end-to-end. WeasyPrint primary backend confirmed working on production (D-13 honored). Plan 02-08 closure documents the WeasyPrint-on-Windows-Server-2019 outcome for future reference.
- **Any FAIL on Surface 1/2/3** → Pitfall: woff2 font missing glyphs OR @font-face directive lost in WeasyPrint render OR iPhone Safari ignored data URL. **Mitigation:** flip `PDF_BACKEND=reportlab` in `.env.production`, restart NSSM service, re-test. ReportLab uses Latin-1 base fonts which render Italian accents natively at the cost of a less-branded layout (no Plus Jakarta + Instrument Serif). Plan 02-08 captures the fix work.
- **FAIL on Surface 4 only** → woff2 base64 issue affects all renderers. Same flip as above.

---

## Notes on local dev validation (already executed)

The dev box (`d:/Develop/AI/WellnessBuddy`) lacks GTK3/Pango libraries; WeasyPrint cannot `dlopen libgobject-2.0-0`. Plan 02-06 therefore validated end-to-end via the **ReportLab fallback** path on dev:

- `backend/.env` has `PDF_BACKEND=reportlab` for local development.
- `backend/.env.production` (Plan 02-03) keeps `PDF_BACKEND=weasyprint` for the Windows Server 2019 deployment which has GTK3 installed (Plan 02-01 spike Day 1 verdict).
- ASGI smoke-test against the running app:
  - **Status:** 200 OK
  - **Content-Type:** `application/pdf`
  - **Content-Length:** ~3.5 KB (3-row real plan)
  - **Magic bytes:** `25 50 44 46 2d 31 2e 34` = `%PDF-1.4`
  - **Content-Disposition:** `attachment; filename="Lista-spesa-2026-05-04.pdf"`
  - **Cache-Control:** `private, no-store`

ReportLab fallback emits Italian accents correctly because it uses Latin-1 base fonts; **the visual brand contract** (Plus Jakarta + Instrument Serif + leaf-700 underlines) is verified ONLY when WeasyPrint runs in production. That is the gate this checklist enforces.
