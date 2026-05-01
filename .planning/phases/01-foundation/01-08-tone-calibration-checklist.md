# Phase 1 — Tone Calibration Sign-Off Checklist

> **Status:** Awaiting Stefano + Marta sign-off (Phase 1 exit gate, UI-20)
> **Source:** `.planning/phases/01-foundation/01-08-PLAN.md` Task 3 — `checkpoint:human-verify gate=blocking`
> **Mockups:** `mockups/tone-calibration/index.html`
> **UI-SPEC reference:** §8.3 (scene-ratio table, focal points locked)

---

## Reviewers

| Role | Name | Date | Signature / initials |
|------|------|------|----------------------|
| **Stefano (admin)** | _______________ | ____ / ____ / ______ | _______ |
| **Marta** | _______________ | ____ / ____ / ______ | _______ |

**Date opened:** ____ / ____ / ______
**Date closed:** ____ / ____ / ______

---

## Open command per device

| Device | Command | Notes |
|--------|---------|-------|
| iPhone Safari | Open `file:///<repo>/mockups/tone-calibration/index.html` directly, OR over LAN via `python -m http.server 8888` from `mockups/tone-calibration/` | Verify 390×844 layout reads naturally without zoom |
| Desktop Chrome | Open `file://` or LAN URL | Use DevTools device toolbar at 390×844 to confirm focal points carry to mobile |
| Desktop second screen | Side-by-side A/B and B/C comparison | Helpful for converging on a final ratio per scene |

---

## Per-surface ratio table (UI-SPEC §8.3 — fill the "Confirmed" column)

For each surface, both reviewers independently pick A / B / C, then converge.
**Focal Point column is LOCKED** — feedback there requires a UI-SPEC revision bump, not a silent change.

| # | Scene | Default ratio | Focal Point (locked) | Stefano | Marta | Final | Confirmed | Notes |
|---|-------|---------------|----------------------|---------|-------|-------|-----------|-------|
| 1 | `/today` populated | 65/35 elegant | Greeting (display-serif) + first incomplete MealCard | ____ | ____ | ____ | [ ] | |
| 2 | `/today` empty (no plan) | 50/50 | Centered hero illustration + `Carica piano` CTA | ____ | ____ | ____ | [ ] | |
| 3 | `/today` empty (day blank) | 60/40 | Date subline + body copy (no illustration, no CTA — passive) | ____ | ____ | ____ | [ ] | |
| 4 | Login | 70/30 elegant | Centered card with form, no hero illustration | ____ | ____ | ____ | [ ] | |
| 5 | Invite signup | 55/45 | Centered card, token field emphasized, small Open Doodles accent | ____ | ____ | ____ | [ ] | |
| 6 | Plan upload | 70/30 | Full-width raised dropzone with dashed border + upload-cloud icon | ____ | ____ | ____ | [ ] | |
| 7 | Plan diff preview | 70/30 | Mobile: stacked diff list. Desktop: side-by-side. | ____ | ____ | ____ | [ ] | |
| 8 | Settings | 75/25 elegant | Top-aligned grouped toggles + theme picker, no hero | ____ | ____ | ____ | [ ] | |
| 9 | Update toast | 80/20 elegant | Mobile: bottom sheet. Desktop: top-right toast. | ____ | ____ | ____ | [ ] | |
| 10 | iOS install banner | 50/50 | Bottom sheet with Storyset illustration of share menu highlighted | ____ | ____ | ____ | [ ] | |
| 11 | Error states | 65/35 | Storyset illustration + IT heading + body + retry CTA | ____ | ____ | ____ | [ ] | |
| 12 | Empty state generic | 50/50 | Minimal Storyset illustration + 1-line copy + 1 primary CTA | ____ | ____ | ____ | [ ] | |

**Encoding helper for orchestrator resume signal:**
> "approved + ratios A,B,B,C,B,B,A,A,B,A,B,B" (12 letters = scenes 1-12 in this order).

---

## Per-variant feedback

### Variante A — 75% elegant / 25% playful

- **Stefano:** _________________________________________________________________
- **Marta:** ___________________________________________________________________
- **Convergenza:** ___________________________________________________________

### Variante B — 50/50 (raccomandata)

- **Stefano:** _________________________________________________________________
- **Marta:** ___________________________________________________________________
- **Convergenza:** ___________________________________________________________

### Variante C — 25% elegant / 75% playful

- **Stefano:** _________________________________________________________________
- **Marta:** ___________________________________________________________________
- **Convergenza:** ___________________________________________________________

---

## Final decision

**Locked variant for production /today:**

- [ ] **A** — 75/25 elegant
- [ ] **B** — 50/50 balanced
- [ ] **C** — 25/75 playful
- [ ] **Hybrid** (specify per surface in the table above)

**Rationale (one paragraph, written by Stefano):**

> _________________________________________________________________________________
> _________________________________________________________________________________
> _________________________________________________________________________________

---

## Mascot decision (Phase 3 — defer-or-decide)

Phase 1 documents both candidates only. Final decision lands at Phase 3 mockup review (STATE.md open Q6).

- [ ] **Goccio** (water-droplet) — universally readable, ties to hydration habit
- [ ] **Bilancina** (scale-spirit) — direct tie to lunedì pesata ritual
- [ ] **Defer to Phase 3 mockup review** (recommended unless strong preference now)

Notes: _____________________________________________________________________________

---

## Sign-off conditions met (UI-20, ENG-06, ROADMAP Phase 1 pause gate)

- [ ] Tutti gli scene confermati nella tabella sopra
- [ ] Nessuna deriva infantile rilevata in alcuna variante
- [ ] Nessun `!` in errori, nessuna emoji in chrome
- [ ] Dark mode parità verificata (ogni variante ha lo scenario dark)
- [ ] Mockups aperti su iPhone reale (Safari) e su desktop
- [ ] Italian copy verbatim rispetto a UI-SPEC §7.2 confermata in tutte le varianti
- [ ] Focal points immutati rispetto a UI-SPEC §8.3 confermati in tutte le varianti

---

## Approval

| | Stefano | Marta |
|--|---------|-------|
| Final variant | ____ | ____ |
| Date | ____ / ____ / ______ | ____ / ____ / ______ |
| Signature | ___________________ | ___________________ |

---

*Generated: Phase 1 Plan 08 Task 1 (Wave 6). Filed for archival in `.planning/phases/01-foundation/`.*
