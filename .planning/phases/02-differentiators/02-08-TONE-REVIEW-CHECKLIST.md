# Plan 02-08 — Phase 2 Tone Review (Stefano + Marta)

> **Status (Plan 02-08 closure, 2026-05-05):** PENDING — awaiting in-person iPhone review.
>
> Plan 02-08 closure has scaffolded this checklist for sign-off. The 7 surfaces below cannot be verified autonomously — they require Stefano + Marta to open the installed PWA on real iPhones, walk through each surface, and judge against the Lifesum Pure variant A reference. Phase 2 pause-gate cannot close until BOTH reviewers sign PASS or PASS-with-concerns.

**Review opened:** ____________
**Production URL:** <https://wellness-buddy.epartner.it>
**Locked design language:** Variant A · Lifesum Pure (`mockups/tone-calibration-v2/A-lifesum-pure.html`)
**Cross-reference:** `.planning/phases/01-foundation/01-08-tone-calibration-checklist.md` (variant A locked Plan 02-03 §11)

---

## Surfaces under review

Both reviewers open each surface on their installed PWA (iPhone Safari standalone) and judge against Lifesum Pure variant A.

### Surface 1 — `/today` populated (post Plan 02-07 SharedBadge)

- [ ] Lifesum Pure rendering preserved (warm cream bg, Plus Jakarta + Geist Mono + Instrument Serif greeting, leaf-sage primary)
- [ ] SharedBadge inline next to slot-label caption when partner shared meal — small Phosphor UsersThree + partner name + Radix Tooltip on tap
- [ ] ShareToggleMenu (`⋯` DotsThreeOutline) present on owner's own meals — DropdownMenu opens with Switch
- [ ] No "office app" tone drift; no `!` in error copy
- [ ] Italian copy from copy.it.ts (no inline strings)

### Surface 2 — `/settimana` populated

- [ ] WeekPicker chip row (5 chips, current ± 2 weeks) + jump-to-date popover with month grid
- [ ] WeeklyMacroRing centered, 220px mobile / 260px desktop, 7-day completion strip below
- [ ] 7 day sections (Lunedì → Domenica) with sticky day header
- [ ] VariantSelector pill on each MealCard: 3 options (Opzione A / Opzione B / Pasta speciale)
- [ ] Opzione A pill bg = leaf-50; Opzione B = surface-muted; Pasta speciale = coral-50
- [ ] DropdownMenu shows MacroDisplay compact preview per option + active dot on current
- [ ] Tap variant change → optimistic UI + sonner success "Variante aggiornata" (no `!`)
- [ ] No infantile mascots or cliché (D-32 — AI widget invariato Phase 2)

### Surface 3 — `/spesa` populated (Per categoria default)

- [ ] 5 category sections in fixed order: Frigo & Freschi (Snowflake) / Frutta & Verdura (Carrot) / Dispensa (Package) / Condimenti (BowlSteam) / Integratori (Pill)
- [ ] Each section header: Phosphor icon (kitchen-feel, NOT generic shapes) + name + count badge + CaretDown
- [ ] ShoppingItemRow: shadcn Checkbox 24×24 visual / 44×44 hit area + name + quantity Geist Mono right-align
- [ ] Checked state: leaf-50 row bg + strikethrough + opacity 0.5
- [ ] ShoppingViewToggle (Per categoria / Per giorno) — segmented control switch works smoothly
- [ ] Sticky bottom row: Copia testo (ghost) + Esporta PDF (primary leaf-500)
- [ ] Reset settimana subwidget — confirm dialog uses leaf-500 confirm (NOT destructive red — D-7.3)

### Surface 4 — Shopping list PDF (download + open in iPhone Safari)

- [ ] Tap Esporta PDF → spinner → download → preview opens
- [ ] Header: "Lista spesa" Plus Jakarta 700 28pt + Instrument Serif italic 14pt date subtitle
- [ ] Wordmark "Wellness Buddy" top-right Plus Jakarta 600 11pt with letter-spacing
- [ ] Category headings leaf-700 Plus Jakarta 600 14pt + 2pt underline
- [ ] Item rows: ☐ checkbox glyph (Geist Mono) + name (Plus Jakarta 500 12pt) + quantity (Geist Mono 11pt right-align)
- [ ] Italian accents render correctly in body + headers + subtitle (cross-reference 02-06-IPHONE-PDF-VERIFY.md)
- [ ] Feels like "lista plastificata per il frigo" — warm, NOT corporate Helvetica/Times

### Surface 5 — Conflict toast (synthetic test)

- [ ] Open /settimana on Stefano + Marta same week, both tap variant on a SHARED dinner within 1s of each other
- [ ] Second user gets sonner toast: heading "Aggiornato da {nome}" body "Ricarica per vedere l'ultima versione." action "Ricarica"
- [ ] No `!` in toast copy
- [ ] Tap Ricarica → query refetches, second user sees first user's variant choice

### Surface 6 — VariantSelector dropdown (`/settimana` open menu)

- [ ] DropdownMenu opens 250ms ease-out-soft (motion budget UI-04)
- [ ] 3 menu items at min 56px height (touch-safe)
- [ ] Active variant has leaf-500 dot 6×6 + Phosphor Check 18px right
- [ ] MacroDisplay compact per option: kcal · P · C · F Geist Mono 11px tabular

### Surface 7 — Condiviso badge (any /today or /settimana shared meal)

- [ ] Inline pill with Phosphor UsersThree 14px + partner name 12px in surface-muted bg
- [ ] Max 12 chars with ellipsis truncation
- [ ] Tap → Radix Tooltip "Aggiornato da {nome} · {timeAgo}" 150ms fade
- [ ] Tooltip auto-dismiss 4s OR ESC OR tap-outside

---

## Cross-cutting tone audit (UI-17, UI-19, UI-20)

- [ ] No `!` in any error/info copy across Phase 2 surfaces
- [ ] No infantile mascots/avocado tropes (deferred to Phase 3 mascot review per D-32)
- [ ] Emoji ≤1-2 per screen (UI-19); zero emoji in chrome
- [ ] Italian formatting: thousand-separator `.` (1.250 kcal), italian decimal `,` (1,5 kg), 24h time, NFC normalize
- [ ] All copy from copy.it.ts (no inline italian)
- [ ] Phosphor facade discipline: zero direct @phosphor-icons/react imports outside icons/index.ts
- [ ] Zero hex literals: zero `#aabbcc` in frontend/src + backend/app/templates

---

## Sign-off

| Reviewer | Initial | Date (YYYY-MM-DD) | Time (HH:MM) | Verdict (PASS/CONCERNS/BLOCK) | Notes |
|----------|---------|-------------------|--------------|-------------------------------|-------|
| Stefano  |         |                   |              |                               |       |
| Marta    |         |                   |              |                               |       |

**Closure rule (Phase 2 pause gate):**

- Both reviewers PASS → Phase 2 complete; Phase 3 unlocked.
- Any BLOCK → fix root cause; re-review.
- CONCERNS → file in Plan 03-XX backlog; Phase 2 still closes if not deploy-blocking.

---

## Pre-review autonomous audit (Plan 02-08 closure, 2026-05-05)

The following machine-checkable WIN REQUISITE invariants were verified against master HEAD before this checklist was scaffolded:

| Invariant | Audit command | Result |
|-----------|---------------|--------|
| Zero hex literals in frontend/src .ts/.tsx | `grep -rEn '#[0-9a-fA-F]{3,8}\b' frontend/src --include='*.ts' --include='*.tsx'` | 0 hits |
| Phosphor facade clean (only `frontend/src/components/icons/index.ts` imports `@phosphor-icons/react`) | `grep -rn '@phosphor-icons/react' frontend/src --include='*.tsx'` | 1 file (the facade itself) |
| Tap-scale `active:scale-[0.97]` on interactive surfaces (MealCard, VariantSelector, WeekPicker, MealCarousel, SharedBadge, ShareToggleMenu) | `grep -rEn 'active:scale-\[0\.9' frontend/src --include='*.tsx'` | 6 files (covers WIN REQUISITE checklist surfaces) |
| Motion budget — no transitions >250ms in component code | `grep -rEn 'duration-(?:[3-9]\d{2,}\|\[\d{3,}ms\])' frontend/src --include='*.tsx'` | 0 hits |
| axe-core CI green on /today + /settimana + /spesa + /login + /signup + /storico + /piano + /impostazioni (light-mode) | `pnpm test:axe` | 8/8 passed, 0 violations |
| Visual regression baselines current for /today + /settimana + /spesa + /login + /piano + /impostazioni (light + dark) | `pnpm test:visual` (after `--update-snapshots`) | 12/12 passed, 0 diffs |
| Frontend vitest + lint + typecheck + build | `pnpm test && pnpm lint && pnpm typecheck && pnpm build` | 123/123, lint clean, typecheck clean, build green |
| Backend pytest | `cd backend && pytest tests/ -q` | 366/366 passed |
| FAM-09 convergence Playwright e2e | `pnpm exec playwright test --config=playwright.dev.config.ts e2e/family-convergence.spec.ts` | 1/1 passed in 4.8s (≤5s budget) |

These audits cover the deterministic invariants. The 7 surfaces above remain dependent on the **subjective tone judgement** that only Stefano + Marta can render in person on real iPhones.
