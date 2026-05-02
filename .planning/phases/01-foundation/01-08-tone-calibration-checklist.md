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

## DECISION (User Sign-Off)

**Date:** 2026-05-02
**Decided by:** Stefano Brunelli (project owner)
**Locked variant:** **A · Lifesum Pure** (`mockups/tone-calibration-v2/A-lifesum-pure.html`)
**Rationale:**

- Lifesum is the established visual reference; users (Stefano + Marta) already understand the language
- Macro ring as hero element validated as core focal point (kcal + 4-arc P/C/F/kcal in one glance)
- Sage + cream + coral palette: warm-clinical, premium without being aggressive
- Plus Jakarta Sans + Phosphor Icons set the friendly-rounded foundation across the app
- New blueberry-purple (protein) + amber (fat) macro families give clear color-coding without infantile overload

### Tasks deferred to Phase 2 pause gate

Production-bound verifications (Plan 08 Task 3 sub-items) are explicitly **DEFERRED** to the Phase 2 pause gate per project owner decision (2026-05-02):

- Real iPhone install + offline /today verification
- Lighthouse PWA 100/100 score
- DEPLOY.md walk-through on Windows Server 2019
- win-acme cert for `wellness-buddy.epartner.it`
- Stefano + Marta in-person sign-off ritual

**Reasoning:** Variant A is now locked in code via Plan 01-09 propagation, so Phase 2 (variants + shopping list + family sync) ships on the right design foundation. Production deploy + iPhone install + Lighthouse run combine more naturally with Phase 2 deliverables at the next pause gate; verifying those production criteria today would only re-verify them after the Phase 2 surface area lands.

Plan 01-09 fulfills the **code-side** half of the Phase 1 pause gate ("tone calibration locked" → variant A propagated to source). Plan 08 Task 3 production-side criteria are reclassified as **Phase 2 pause gate prerequisites**.

### What Plan 01-09 actually shipped

Code-side propagation (commits on `plan-01-09-lifesum-pure` branch, merged via Wave 7 reconciliation):

- `frontend/src/styles/theme.css` — full OKLCH palette migration (warm-cream bg, sage-leaf 150-hue, refined coral 30-hue, NEW blueberry 280, NEW amber 75, `--color-carb-soft` for macro ring tracks). Light + dark variants for every token.
- `frontend/src/components/today/MacroRing.tsx` — Lifesum-signature 4-arc SVG ring (kcal outer + P/C/F inner) consuming token colors only. Plus Jakarta 800 kcal value (NOT Instrument Serif — escape hatch reserved for /today greeting). Italian `aria-label` "{consumed} di {target} kcal oggi".
- `frontend/src/components/today/MacroDisplay.tsx` — restyled 3-up macro pills (blueberry/leaf-deep/amber).
- `frontend/src/components/today/MealCard.tsx` — Lifesum Pure layout: 80×80 photo (or gradient placeholder + Phosphor slot icon) + info column + 44×44 Phosphor check button. Photo `<img>` uses `loading="lazy"` + explicit dimensions (DoS mitigation).
- `frontend/src/components/icons/index.ts` — Phosphor facade enforced via grep gate (CI / `pnpm lint`).
- `frontend/src/pages/Today.tsx` — restructured to mockup A populated layout (greeting + score pill, hero ring card, "I tuoi pasti" section, meal list, weight+workout, AI placeholder).
- `frontend/src/pages/{History,Settings}.tsx` + layout (`AppBar`, `BottomTabBar`, `NavigationRail`) — Phosphor + leaf-700 active state.
- `frontend/src/i18n/copy.it.ts` — italian copy keys added for the macro ring and section headers (FND-09 source-of-truth preserved; no inline italian in components).
- Backend: `MealOption.photo_url: str | None (max 500)` + parser opt-into `**Foto:** <url>` line + today_service passes through. Existing 134 backend tests stay green; 6 evil-corpus parser fixtures unchanged.

**Verification snapshot (worktree before merge):**

- Backend: 134/134 pass
- Frontend unit: 62/62 pass (was 48 — +7 MacroRing + +7 MealCard)
- `pnpm typecheck` / `pnpm lint` / `pnpm build` all green
- Hex grep on `frontend/src` clean (zero hits)
- Phosphor facade grep clean (no direct `@phosphor-icons/react` imports outside the facade)

Visual regression Playwright baselines need a one-time refresh post-merge (TODO in `frontend/tests/visual/{light,dark}.spec.ts`).

---

*Generated: Phase 1 Plan 08 Task 1 (Wave 6). Locked: Plan 01-09 (Wave 7) — variant A · Lifesum Pure. Filed for archival in `.planning/phases/01-foundation/`.*
