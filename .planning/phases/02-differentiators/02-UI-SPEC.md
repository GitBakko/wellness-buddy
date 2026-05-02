---
phase: 2
slug: differentiators
status: draft
shadcn_initialized: yes
preset: custom (Tailwind 4 @theme + shadcn/ui CLI — Phase 1 lock carries forward)
inherits_from: .planning/phases/01-foundation/01-UI-SPEC.md
visual_ground_truth: mockups/tone-calibration-v2/A-lifesum-pure.html
created: 2026-05-02
revised: 2026-05-02
revision: 2
---

# Phase 2 — UI Design Contract (Differentiators)

> **Inheritance contract.** Phase 2 inherits Phase 1 §1-§5 (Design System, Spacing, Type, Color, Motion) **verbatim** and adds only the surfaces, components, copy, and icons required by REQ WEEK-* / SHOP-* / FAM-* / DEP-06. Anywhere this document says "(inherited from Phase 1 §X)" it means **read Phase 1 §X — no overrides, no additions**. Drift is forbidden; if a Phase 2 surface needs a token Phase 1 didn't lock, this document amends Phase 1 §12 explicitly under §12.NEW below.

> **Revision 2 (2026-05-02 — checker fixes):** (a) BLOCKER fix — removed Fraunces silently introduced in §6.4 PDF template; date subtitle now uses Instrument Serif italic (Phase 1 escape-hatch font reused in PDF context per §3 amendment), so `theme.css` remains untouched and §12.NEW "no new fonts" claim holds. (b) FLAG 1 fix — Condimenti category icon corrected `BowlSteam` → `Wine` (BowlSteam reads as soup; Wine reads as decanter/bottle, semantically aligned with oils/vinegars/dressings). (c) FLAG 2 fix — removed `SwitchHorizontal` dead-code reservation from facade additions (ToggleGroup primitive labels are self-explanatory; if a future plan needs the icon, add then). (d) FLAG 3 fix — copy-key count corrected from "~75" to precise leaf count **95** across namespaces. (e) FLAG 4 fix — §14 reworded to distinguish Phase 1 already-added blocks (`dropdown-menu`, `dialog`, `sheet`, `tabs`) from Phase 2 net-new blocks (`popover`, `tooltip`, `alert-dialog`, `collapsible`, `toggle-group` — 5 net new). (f) FLAG 5 fix — §7.3 adds dual-framing note clarifying swipe-reveal red (gesture-intent signal) vs AlertDialog leaf-500 confirm (action recoverable). No decisions in §1-§5 changed; no new components added; italian copy semantically unchanged.

> **Locked design language:** Variant A · Lifesum Pure (`mockups/tone-calibration-v2/A-lifesum-pure.html`). Every Phase 2 surface — `/week`, `/spesa`, shopping-list PDF, condiviso badge, variant selector, conflict toast — must converge on this DNA. No new tone exploration in Phase 2.

> **Win Requisite anchor (PROJECT.md verbatim, carried forward):** *"L'app deve avere aspetto a metà tra eleganza/minimal e giocoso/friendly. Senza questo il progetto è fallito. UI/UX di livello ELITE."*

---

## 0. Source-of-Truth Map (Phase 2 deltas only)

| Section | Pre-locked by | This document's job |
|---------|---------------|---------------------|
| Stack picks (frontend + backend) | RESEARCH/STACK.md + Phase 1 UI-SPEC §1 | Cite, don't re-decide |
| Design tokens (spacing, type, color, motion, radius, elevation) | Phase 1 UI-SPEC §2-§5 + §12 | Inherit verbatim, declare ZERO new tokens unless §12.NEW amendment is explicit |
| Italian copy single-source | FND-09, Phase 1 UI-SPEC §7 | Extend `copy.it.ts` with `week.*` / `shopping.*` / `family.*` / `sync.conflictToast` namespaces |
| Phosphor facade | Phase 1 `frontend/src/components/icons/index.ts` | Extend with the 15 new icons listed in §6.5 |
| WeasyPrint primary + ReportLab fallback | RESEARCH/STACK.md + DEP-06 + 02-CONTEXT.md D-11..D-14 | PDF template anatomy + brand contract + GTK3 spike gate |
| Variant naming verbatim | REQ WEEK-03 + 02-CONTEXT.md D-01 | "Opzione A" / "Opzione B" / "Pasta speciale" — no free text |
| Visibility defaults | REQ FAM-02 + 02-CONTEXT.md D-15 | Cene+pranzi `group_shared`, colazione+spuntini `private` |
| Conflict 409 tone | REQ FAM-05 + 02-CONTEXT.md D-17 | Italian copy `sync.conflictToast` — no `!`, no panic |
| Tone calibration scene-ratio table | Phase 1 UI-SPEC §8.3 (Lifesum Pure variant A locked) | Extend table with new Phase 2 surfaces — same focal-point discipline |
| Tone-of-voice rules | Phase 1 UI-SPEC §7.1 | Inherit verbatim — Phase 2 copy MUST audit against the same 9 rules |

If a decision conflicts with Phase 1 UI-SPEC, **Phase 1 wins** and this doc is wrong — file a fix.

---

## 1. Design System

**(inherited from Phase 1 UI-SPEC §1 verbatim)**

Phase 2 reuses the entire Phase 1 design system without modification:
- shadcn/ui CLI v4 + custom Tailwind 4 `@theme` layer
- shadcn/ui primitives over Radix UI
- **Plus Jakarta Sans** primary `--font-sans` (post Plan 09 — NOT Geist Sans, which Phase 1 §1 references in the original draft; the propagated Lifesum Pure theme in `theme.css` lines 59-61 is canonical)
- **Geist Mono** for tabular numerics
- **Instrument Serif** display escape hatch — `/today` greeting AND PDF date subtitle (§6.4 — 1 occurrence per page); FORBIDDEN on `/week`, `/spesa`, modals (see §3 amendment for the second permitted context)
- **Phosphor Icons** via `@/components/icons/index.ts` facade (NEVER direct `@phosphor-icons/react` imports — CI grep gate inherited)
- Motion v12 (`motion/react`) + tailwindcss-animate
- sonner for toasts

**No new third-party libraries Phase 2.** The WeasyPrint PDF pipeline is backend-only and consumes the same OKLCH coords as the frontend (D-12 mirror contract).

---

## 2. Spacing Scale

**(inherited from Phase 1 UI-SPEC §2 verbatim — see `frontend/src/styles/theme.css` lines 28-41)**

Phase 2 introduces ZERO new spacing tokens. The 13-step scale (`--spacing-0` → `--spacing-20`) plus `--spacing-px` covers every Phase 2 surface:
- Week picker chips: `--spacing-2` between chips, `--spacing-3` chip internal padding
- Shopping list rows: `--spacing-3` row padding, `--spacing-4` section gap
- VariantSelector dropdown: `--spacing-3` menu-item padding, `--spacing-2` between option chips
- Condiviso badge: `--spacing-1` icon↔text gap, inline within MealCard caption
- PDF margins: 20mm physical (WeasyPrint print context — outside CSS pixel scale, see §6.4)

**Touch-target exception (UI-06) inherited:** every interactive element ≥44×44 px hit area. VariantSelector trigger pill, shopping-list checkbox, share toggle, conflict toast action button — all wrap any visual smaller than 44px in an invisible 44×44 hit area.

**Safe-area exceptions inherited:** `/spesa` sticky bottom export-button row uses `padding-bottom: max(var(--spacing-4), env(safe-area-inset-bottom))`.

**Container queries inherited:** `/week` switches from vertical day stack (mobile <768px) to horizontal day-tab strip (≥768px) via `@container` not `@media` to nest cleanly inside `NavigationShell`.

---

## 3. Typography

**(inherited from Phase 1 UI-SPEC §3 verbatim — see `frontend/src/styles/theme.css` lines 64-76)**

Phase 2 introduces ZERO new typography tokens.

**Fonts:**
- `--font-sans`: Plus Jakarta Sans (primary)
- `--font-mono`: Geist Mono (tabular numerics — macro chips, quantities, dates)
- `--font-display`: Instrument Serif (escape hatch — `/today` greeting AND shopping list PDF date subtitle, see §6.4)

**Base scale (4 sizes — Dimension 4 cap holds):**
- `--text-caption` 12px — day-name caption, category count badges, share-badge name, PDF item rows
- `--text-base` 16px — meal title, ingredient name, primary CTA labels, body copy
- `--text-heading` 22px — `/week` page title, `/spesa` page title, category section heading, modal titles
- `--text-display` 28px — WeeklyMacroRing center kcal value (rendered with Geist Mono tabular-nums — same size step, font-family swap, NOT a new token)

**Escape hatch (`--text-display-serif` 36px) — Instrument Serif:**
- ❌ FORBIDDEN on `/week`, `/spesa`, variant selector, condiviso badge, conflict toast, deploy checklist
- ✅ ALLOWED on `/today` greeting (already in production via `pages/Today.tsx` per Plan 07/09)
- ✅ ALLOWED in the shopping list PDF date subtitle (1 occurrence per page, 14pt italic — see §6.4) as a permitted second escape-hatch context. This is the only PDF context where Instrument Serif may be used; all other PDF surfaces (titles, body, captions, category headings, page chrome) MUST use Plus Jakarta or Geist Mono per §6.4. No new font family is introduced — `--font-display` is reused in print.

**Italian numeric formatting (UI-18) inherited:**
- Quantities: `400 g`, `2 confezioni`, `1 pizzico` — `Intl.NumberFormat('it-IT')` (italianNumberInt for ints, italianNumberDecimal for decimals)
- Weekly kcal totals: `12.320 / 15.400 kcal` — thousand separator `.`
- Dates: `lun 5 mag` (short) / `lunedì 5 maggio 2026` (long, PDF header) / `5 mag` (week picker chip)
- Time-ago: `2 minuti fa` / `1 ora fa` / `ieri` / `2 giorni fa` (custom helper `italianTimeAgo` in `frontend/src/lib/format.ts` — see §7 copy contract)
- Sorting: `Intl.Collator('it')` for ingredient names so "À" sorts after "A"
- NFC normalize on save (every ingredient string entering DB, mutation queue, Dexie cache)

**Anti-patterns inherited:** zero hardcoded font-sizes, zero hardcoded weights, zero ALL CAPS except slot-label captions in MealCard (already established).

---

## 4. Color (OKLCH, dark-mode first-class)

**(inherited from Phase 1 UI-SPEC §4 verbatim — see `frontend/src/styles/theme.css` lines 78-196 for production tokens, with manual dark-mode mirror at lines 264-316)**

Phase 2 introduces ZERO new color tokens.

**60/30/10 reuse map for new surfaces:**

| Surface | Dominant 60% | Secondary 30% | Accent 10% |
|---------|--------------|---------------|------------|
| `/week` | `--color-bg` warm cream (page) | `--color-surface` (day section cards) + `--color-neutral-200` (dividers) | `--color-leaf-500` (active variant indicator dot, weekly summary CTA) — `--color-coral-500` reserved for Phase 1 weight CTA only, NOT used on `/week` |
| `/spesa` | `--color-bg` warm cream (page) | `--color-surface` (category section cards) + `--color-surface-muted` (collapsed section header) | `--color-leaf-500` (export PDF primary, checkbox checked fill) |
| VariantSelector | `--color-leaf-50` ("Opzione A" pill bg — default), `--color-surface-muted` ("Opzione B" pill bg), `--color-coral-50` ("Pasta speciale" pill bg — accent only because the variant is semantically the "special/treat" choice, fits coral's warmth) | `--color-border` (pill hairline) | `--color-leaf-500` (active dot in dropdown menu item) |
| Condiviso badge | `--color-surface-muted` (badge pill bg) | `--color-text-muted` (badge name color), `--color-text` (icon stroke) | none — badge is intentionally non-rumoroso (D-18) |
| Conflict toast (sonner `info` variant) | `--color-bg-elev` (toast surface) | `--color-border` left border, `--color-text` body, `--color-text-muted` time | `--color-leaf-500` left accent stripe (info, NOT destructive — "Aggiornato da" is informational, not error) |
| Shopping list PDF (print) | white (paper) | `--color-neutral-700` (ink) for body + `--color-neutral-200` for hairlines | `--color-leaf-700` for category heading underline + small accent dots (≤3% of page area; print-toner-friendly per D-12 spec) |

**Color reservation contract (10% accent) — Phase 2 specifics:**

The **leaf-sage** primary brand color (`--color-leaf-500`) is the dominant accent across new Phase 2 surfaces, consistent with Lifesum Pure variant A locked in Phase 1. It is reserved for:
- Primary CTAs on `/week` and `/spesa` (Carica piano, Reset settimana confirm, Esporta PDF)
- Active variant indicator dot in VariantSelector dropdown menu item
- Checkbox checked fill on shopping-list rows
- Active day in horizontal day-tab strip (tablet+)
- WeeklyMacroRing kcal arc (inherits MacroRing convention)
- PDF category heading underline (`--color-leaf-700` darker variant for print contrast)

**Forbidden in Phase 2:**
- `--color-coral-500` on any non-weight-CTA surface (Phase 1 lock §4 — coral reserved for primary CTA + active tab + Phase 3 streak — `/spesa` reset confirm uses coral as destructive intent: see §10.3)
- Any new color outside `theme.css` palette (ESLint hex-ban inherited)
- Color-only semantic signals — the conflict toast pairs leaf-500 stripe with Phosphor `ArrowsClockwise` icon AND italian copy AND `role="status"` (UI-15)

**Contrast (axe-core gate inherited):**

Every new Phase 2 surface validated against Phase 1 §4.2 thresholds (≥4.5:1 body / ≥3:1 large icons). Specific Phase 2 pairs to verify in CI:
- Condiviso badge name (`--color-text-muted` on `--color-surface-muted` light + dark) — must hit ≥4.5:1
- VariantSelector "Opzione A" pill text (`--color-text` on `--color-leaf-50`) — must hit ≥4.5:1
- VariantSelector "Pasta speciale" pill text (`--color-text` on `--color-coral-50`) — must hit ≥4.5:1
- Shopping-list category heading on collapsed section header (`--color-text` on `--color-surface-muted`) — must hit ≥4.5:1
- Day-tab active indicator (`--color-leaf-500` underline 2px) — must hit ≥3:1 against page bg

---

## 5. Motion budget

**(inherited from Phase 1 UI-SPEC §5 verbatim — see `frontend/src/styles/theme.css` lines 165-171)**

Phase 2 introduces ZERO new motion tokens.

**Phase 2 specific motion list (the only animations allowed in this phase):**
- **VariantSelector dropdown open/close:** 250ms `ease-out-soft` opacity + translateY(-4px → 0) — Radix DropdownMenu default fade respected (UI-04)
- **Variant pill tap:** 80ms scale 0.97 (`--duration-instant`) on press, 150ms return — inherited from `Button` component
- **Shopping-list checkbox tick:** SVG path stroke-dasharray draw 200ms (Phase 1 pattern)
- **Shopping-list row checked transition:** 250ms opacity 1 → 0.5 + strikethrough fade — single transform + opacity, no layout shift
- **Shopping-list swipe-left to delete:** 250ms transform translateX (max 80px) + reveal delete button — pointer-events handled by `<motion.div>` with `dragX` constrained to negative axis only; `prefers-reduced-motion` short-circuits to instant button-tap fallback
- **Day-tab active indicator slide:** 250ms underline `left`+`width` transition (desktop horizontal day-tab only); mobile vertical stack has no slide
- **Week picker chip tap:** 80ms scale 0.97 (inherited)
- **Per-meal share toggle (Switch):** 250ms iOS-style switch motion (inherited from Phase 1 `Toggle`)
- **Sonner conflict toast:** 250ms slide-up + fade (sonner default, inherited)
- **`/week` route transition:** 250ms opacity-only crossfade (inherited)
- **`/spesa` route transition:** 250ms opacity-only crossfade (inherited)

**`prefers-reduced-motion` honored:** `--motion-scale: 0` (inherited from `theme.css` lines 322-330) — every transform-based animation reads `useReducedMotion()` and returns no-op variants. CI Playwright test extends Phase 1 list with `/week` + `/spesa` routes.

**Forbidden Phase 2:**
- Lottie / Rive / confetti (Phase 3 only)
- Layout animations on shopping list rows (no `<motion.div layout>` — would lag at 336+ rows)
- Auto-playing celebration when variant changes (would be noise; user just chose a different variant, not a milestone)

---

## 6. Component Anatomy (Phase 2 NEW components only)

Phase 2 NEW components below. **Phase 1 primitives, composites, and app-shell components are reused unchanged** (see Phase 1 UI-SPEC §6.1-§6.3).

### 6.1 Domain components — extensions of Phase 1

| Component | Variants added | States added | Notes |
|-----------|----------------|--------------|-------|
| `MealCard` | `+ shared` (Phase 2 unlocks) — receives `meal.visibility = 'group_shared'` AND `meal.owner_user_id !== current_user_id` | `+ has-share-toggle-menu` (the `⋯` menu with share switch, owner-only) | Adds: (a) Condiviso badge slot inline next to slot-label caption (rendered ONLY when shared and current_user is NOT owner), (b) `⋯` icon button (Phosphor `DotsThreeOutline`, 24px, hit area 44×44) right of meal title — opens DropdownMenu with "Condividi con la famiglia" Switch (D-15) — rendered ONLY when current_user IS owner. Layout flow: `[80px photo][info column flex-1: caption + Condiviso badge inline | title | ⋯ owner-only | macro chips][44px check button]`. Width must remain 390px-safe — Condiviso badge name truncates with ellipsis at >12 chars. |
| `MacroDisplay` | unchanged | unchanged | Reused as-is in MealCard, VariantSelector dropdown menu items, WeeklyMacroRing breakdown |

### 6.2 Domain components — NEW Phase 2

| Component | Variants | Description |
|-----------|----------|-------------|
| `WeeklyMacroRing` | `default` (mobile 220px) / `desktop` (260px) | Same SVG anatomy as `MacroRing` (4 concentric rings, leaf-500 outer kcal / blueberry-500 protein / leaf-700 carbs / amber-500 fat). Aggregates 7-day totals from chosen variants. Center text: weekly kcal Plus Jakarta 800 + subtitle `"su {target}"` (target × 7) Plus Jakarta 500 13px + caption `"kcal · settimana"` Plus Jakarta 600 11px uppercase. Below ring: 7-day completion strip — 7 horizontal pills (8px tall, 8px gap), each pill rendered as: `--color-leaf-500` (all 4 meals completed), `--color-leaf-200` (1-3 meals), `--color-neutral-100` (planned, 0 completed), `--color-neutral-200` outline (no plan that day). Day-name caption Lun-Dom Plus Jakarta 600 11px above each pill. ARIA: `role="img"` + `aria-label="{consumed} di {target} kcal questa settimana, {n} pasti su {total} completati"`. |
| `VariantSelector` | `optionA` (default) / `optionB` / `pastaSpeciale` | **Trigger pill** (44×44 min hit area): rounded `--radius-pill`, `--spacing-2` vertical / `--spacing-3` horizontal padding, `--text-base` semibold variant name + Phosphor `CaretDown` 16px (regular weight). Background per variant (light mode): `--color-leaf-50` (A), `--color-surface-muted` (B), `--color-coral-50` (Pasta speciale). Border: `1px solid --color-border`. Tap: 80ms scale 0.97. **DropdownMenu** (Radix): width 260px, opens 250ms `ease-out-soft`. 3 menu items, each row: `[active dot if selected: 6×6 leaf-500 circle][--spacing-3 gap][variant name Plus Jakarta 600 16px][--spacing-3 gap][MacroDisplay compact: kcal·P·C·F Geist Mono 11px tabular]`. Selected variant ALSO has Phosphor `Check` 18px right-aligned. Min item height 56px (44 + padding) — touch-target safe. Optimistic update on tap → mutation queue + sonner success toast `"Variante aggiornata"` (no `!`); on 409 → conflict toast (D-17). |
| `WeekPicker` | `default` (mobile chip-row) / `desktop` (chip-row + adjacent jump-to-date popover) | **Chip row** of 5 settimane (current week ± 2): horizontal scroll-snap on mobile, no wrap. Each chip: 44px min height, `--radius-pill`, `--spacing-2 --spacing-4` padding. Active chip: `--color-leaf-100` bg + `--color-text` text (Plus Jakarta 600). Inactive: `--color-surface-muted` bg + `--color-text-muted`. Chip label: `"5 mag"` (start-of-week date short IT). **"Vai al…" trigger** (right of chip row): 44×44 IconButton ghost + Phosphor `CalendarBlank` 22px → opens Radix Popover with vertically scrolling month-grid date picker (NOT modal — anchored to icon). Popover max-width 320px, `--shadow-2`, picker uses `date-fns` `startOfWeek({ weekStartsOn: 1 })` (D-08). Date select → close popover, navigate `/week/{week_start}`. ESC closes, focus returns to trigger. |
| `SharedBadge` | `default` (Phase 2 only — the only variant) | Inline pill rendered in `MealCard` slot-label caption row. Anatomy: `[Phosphor UsersThree 14px regular weight, --color-text-muted][--spacing-1 gap][partner name Plus Jakarta 500 12px --color-text-muted, max-width clamps to 12 chars + ellipsis]`. Background `--color-surface-muted`, border-radius `--radius-pill`, `--spacing-1 --spacing-2` padding. **Tap → Radix Tooltip** opens 150ms fade with copy `"Aggiornato da {nome} · {timeAgo}"` (`italianTimeAgo` helper). Tooltip dismisses on tap-outside / ESC / 4s auto-dismiss. NEVER blocks layout — if name + slot-label combined exceed available width at 390px, the badge ellipsis truncates partner name BEFORE slot-label truncates (slot-label is the higher-priority anchor). |
| `ShareToggleMenu` | `default` | The `⋯` DropdownMenu inside `MealCard` (owner-only). Trigger: Phosphor `DotsThreeOutline` 24px in a 44×44 IconButton ghost. DropdownMenu single item: `[Phosphor UsersThree 18px][--spacing-3 gap][label "Condividi con la famiglia" Plus Jakarta 500 16px][--spacing-3 gap][shadcn Switch component, current state]`. Tap Switch → optimistic update meal.visibility (`'private'` ↔ `'group_shared'`) + mutation queue + sonner success toast `"Condivisione aggiornata"`. On 409 → conflict toast. Item min height 56px touch-safe. Menu closes on selection (Radix default). |
| `ShoppingCategorySection` | `expanded` (default) / `collapsed` | Collapsible section. **Header** (44px tall, full-width tap area): `[--spacing-3 left padding][category Phosphor icon 22px regular weight, color per category][--spacing-3 gap][category name Plus Jakarta 600 16px --color-text][flex-1 spacer][count badge Geist Mono 12px in --color-surface-muted pill --spacing-1 --spacing-2 padding, e.g. "12"][--spacing-2 gap][Phosphor CaretDown 16px, rotates 180deg when expanded, 250ms transform]`. Collapsed header bg `--color-surface-muted`, expanded header bg `--color-surface` with `--spacing-px` bottom border `--color-border`. **Body**: vertical stack of `ShoppingItemRow` components, no internal divider (rows handle their own bottom hairline). |
| `ShoppingItemRow` | `unchecked` (default) / `checked` / `swiping` (transient, during swipe gesture) | Anatomy: `[--spacing-3 left padding][shadcn Checkbox 24×24 visual, 44×44 hit area, leaf-500 fill when checked][--spacing-3 gap][info column flex-1: name Plus Jakarta 500 16px line-clamp-2 + meal-context caption "PRANZO · giovedì" Plus Jakarta 600 uppercase 11px tracking-wide --color-text-muted (per-day view ONLY; per-categoria view omits this caption)][--spacing-3 gap][quantity Geist Mono 14px tabular-nums --color-text e.g. "400 g · 2 confezioni"][--spacing-3 right padding]`. Min height 56px. Bottom hairline 1px `--color-border`. **Checked state:** name strikethrough + opacity 0.5 + row bg `--color-leaf-50` 250ms ease-out-soft. **Swipe-left:** transform translateX max -80px reveals delete button 80×full-row, bg `--color-destructive`, content `[Phosphor X 22px white]`. Tap delete → Radix AlertDialog confirmation `"Rimuovere {nome ingrediente} dalla lista?"` (NOT typo: `Rimuovere` — softer than `Eliminare`, avoids destructive panic for a list item user can re-add by re-aggregating). |
| `ShoppingViewToggle` | `perCategoria` (default) / `perGiorno` | Radix ToggleGroup (segmented control): 2 buttons inline, container `--color-surface-muted` bg, `--radius-pill`, `--spacing-1` internal padding. Active button: `--color-bg` bg + `--color-text` text + `--shadow-1`. Inactive: transparent + `--color-text-muted`. Each button 44px min height, `--spacing-2 --spacing-4` padding, label Plus Jakarta 600 14px. Tap: 80ms scale 0.97 + 250ms active-pill `left`+`width` transition. ARIA: `role="radiogroup"` (Radix default), `aria-label="Vista lista spesa"`. |
| `ConflictToast` | `default` | Sonner `info` variant (NOT `destructive` — D-17). Anatomy: `[--spacing-3 left padding + 4px leaf-500 left stripe][Phosphor ArrowsClockwise 18px regular, --color-text][--spacing-3 gap][copy column: heading "Aggiornato da {nome}" Plus Jakarta 600 14px --color-text + body "Ricarica per vedere l'ultima versione." Plus Jakarta 400 13px --color-text-muted][--spacing-3 gap][action Button ghost variant "Ricarica" 14px --color-leaf-700]`. Auto-dismiss 6s (matches Phase 1 error toast — gives user time to read AND tap action). Closing dismisses; tapping "Ricarica" calls `queryClient.invalidateQueries(['weekly', userId, weekStart])` then dismisses. NO `!` in heading (UI-17). |
| `EmptyStateWeek` | `default` | EmptyState composite reuse (Phase 1 §6.2). Phosphor `CalendarBlank` 240×240 mobile / 280×280 desktop (`weight="regular"`, color `--color-leaf-200` light / `--color-leaf-700` dark) + heading "Nessuna settimana pianificata" + body "Carica un piano per vedere i pasti della settimana." + primary Button leaf-500 "Carica piano" → routes `/piano`. NO storyset illustration here — Phosphor icon at 240px renders as the focal point; aligns with Lifesum Pure minimal restraint (variant A). |
| `EmptyStateShopping` | `default` | EmptyState composite reuse. Phosphor `ShoppingCart` 200×200 mobile / 240×240 desktop (regular weight, `--color-leaf-200` light / `--color-leaf-700` dark) + heading "Nessuna spesa pianificata" + body "Scegli le varianti settimanali per generare la lista." + secondary link Button (ghost variant) "Vai alla settimana →" (Phosphor `CaretRight` 16px) → routes `/week`. |
| `DeployChecklistItem` | `pending` / `done` | (For Plan 02-03 deploy checklist artifact only — see §6.6.) Markdown checkbox row. Not a React component — these render as static markdown in `02-03-DEPLOY-CHECKLIST.md`. Inclusion here documents the visual contract for the artifact: `[ ] Step description` becomes `[x] Step description ✓ {YYYY-MM-DD HH:MM} {initial}` after sign-off. |

### 6.3 Layout patterns

**`/week` (mobile 390px):**
```
[AppBar: "La settimana" + back-to-/today caret + SyncStatusPip right]
[--spacing-4 vertical pad]
[WeekPicker chip row + jump-to-date popover trigger right]
[--spacing-6 vertical pad]
[WeeklyMacroRing centered, 220px]
[--spacing-3 vertical pad]
[7-day completion strip below ring]
[--spacing-6 vertical pad]
[Day section: sticky day header "Lunedì 5 mag" Plus Jakarta 700 22px + small meta caption (e.g. "4 pasti · 1.860 kcal previsti") + 4 MealCards stacked, each with VariantSelector pill]
[--spacing-6 between days]
[... × 7 days ...]
[--spacing-12 bottom safe-area]
[BottomTabBar — /settimana tab active]
```

**`/week` (tablet+ ≥768px):**
```
[AppBar]
[WeekPicker chip row + jump-to-date]
[Two-column: left = WeeklyMacroRing 260px + 7-day strip + summary chips | right = horizontal day-tab strip + selected day meals stacked]
[Active day-tab underline 2px --color-leaf-500, slides 250ms]
```

**`/spesa` (mobile 390px):**
```
[AppBar: "La spesa" + back-to-/today + SyncStatusPip]
[--spacing-4 vertical pad]
[Page subhead: "settimana del 5 maggio 2026" Plus Jakarta 500 14px --color-text-muted (Geist Mono on date numerics: "5", "2026")]
[--spacing-4 vertical pad]
[ShoppingViewToggle: Per categoria | Per giorno]
[--spacing-6 vertical pad]
[ShoppingCategorySection × 5, fixed order: Frigo & Freschi → Frutta & Verdura → Dispensa → Condimenti → Integratori]
   each section expanded by default
   each ShoppingItemRow with checkbox + name + quantity
[--spacing-12 vertical pad]
[Subwidget: outlined Button "Reset settimana" + Phosphor ArrowCounterClockwise 18px — full-width on mobile]
[--spacing-4 vertical pad]
[Sticky bottom action row (above BottomTabBar): two buttons --spacing-2 gap, full-width split: [ghost "Copia testo" + ClipboardText 18px] [primary leaf-500 "Esporta PDF" + FilePdf 18px]]
[BottomTabBar — /spesa tab active]
```

**`/spesa` per-giorno view:** same shell, but ShoppingCategorySection replaced by 7 day sections (`Lunedì` → `Domenica`). Each item row gains the `meal-context caption` ("PRANZO · giovedì" — slot label + day in compact form for cross-day items appearing in multiple meals).

### 6.4 Shopping list PDF template (`backend/app/templates/shopping_list.html`)

**Brand contract (D-12 — drift-impossible via shared OKLCH coords):**

```html
<!-- Embedded at top of HTML; Jinja2 renders this verbatim before WeasyPrint pipeline -->
<style>
  @page {
    size: A4 portrait;
    margin: 20mm;
    @bottom-center {
      content: "Wellness Buddy · {{ domain }}";
      font-family: "Plus Jakarta Sans", sans-serif;
      font-size: 9pt;
      color: oklch(38% 0.015 240); /* --color-neutral-700 */
    }
    @bottom-right {
      content: counter(page) "/" counter(pages);
      font-family: "Geist Mono", monospace;
      font-size: 9pt;
      color: oklch(50% 0.015 240); /* --color-neutral-600 */
    }
  }
  /* Embed fonts as woff2 base64 inline so Italian accents render natively (D-13) */
  @font-face {
    font-family: "Plus Jakarta Sans";
    src: url(data:font/woff2;base64,...) format("woff2");
    font-weight: 400 800;
    font-display: block;
  }
  @font-face {
    font-family: "Geist Mono";
    src: url(data:font/woff2;base64,...) format("woff2");
    font-weight: 400 600;
    font-display: block;
  }
  @font-face {
    font-family: "Instrument Serif";
    src: url(data:font/woff2;base64,...) format("woff2");
    font-style: italic;
    font-weight: 400;
    font-display: block;
  }
  body {
    font-family: "Plus Jakarta Sans", sans-serif;
    color: oklch(28% 0.015 240); /* --color-neutral-800 — body ink */
    line-height: 1.4;
  }
  h1.title {
    font-family: "Plus Jakarta Sans", sans-serif;
    font-weight: 700;
    font-size: 28pt;
    margin: 0 0 4pt 0;
    color: oklch(22% 0.015 240); /* --color-text */
  }
  .subtitle {
    font-family: "Instrument Serif", serif;
    font-style: italic;
    font-weight: 400;
    font-size: 14pt;
    color: oklch(48% 0.13 150); /* --color-leaf-700 — warm accent for date */
    margin: 0 0 16pt 0;
  }
  .wordmark {
    position: absolute;
    top: 20mm;
    right: 20mm;
    font-family: "Plus Jakarta Sans", sans-serif;
    font-weight: 600;
    font-size: 11pt;
    color: oklch(38% 0.015 240); /* --color-neutral-700 */
    letter-spacing: 0.04em;
  }
  section.category {
    page-break-inside: avoid; /* keep small categories whole */
    margin: 0 0 14pt 0;
  }
  section.category h2 {
    font-family: "Plus Jakarta Sans", sans-serif;
    font-weight: 600;
    font-size: 14pt;
    color: oklch(48% 0.13 150); /* --color-leaf-700 — print-friendly leaf */
    border-bottom: 2pt solid oklch(48% 0.13 150);
    padding-bottom: 3pt;
    margin: 0 0 6pt 0;
  }
  ul.items {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  ul.items li {
    display: flex;
    align-items: baseline;
    padding: 3pt 0;
    border-bottom: 1pt solid oklch(89% 0.012 85); /* --color-border */
    font-size: 12pt;
  }
  ul.items li .checkbox {
    font-family: "Geist Mono", monospace;
    font-size: 12pt;
    margin-right: 8pt;
    color: oklch(38% 0.015 240);
  }
  ul.items li .name {
    flex: 1;
    font-weight: 500;
  }
  ul.items li .qty {
    font-family: "Geist Mono", monospace;
    font-weight: 400;
    font-size: 11pt;
    color: oklch(38% 0.015 240);
    text-align: right;
    white-space: nowrap;
  }
</style>
```

**Body anatomy:**
```html
<header>
  <h1 class="title">Lista spesa</h1>
  <p class="subtitle">settimana del {{ week_start_long_it }}</p>
  <div class="wordmark">Wellness Buddy</div>
</header>

<main>
  {% for category in categories %}
  <section class="category">
    <h2>{{ category.name }}</h2>
    <ul class="items">
      {% for item in category.items %}
      <li>
        <span class="checkbox">☐</span>
        <span class="name">{{ item.name }}</span>
        <span class="qty">{{ item.quantity_it }}</span>
      </li>
      {% endfor %}
    </ul>
  </section>
  {% endfor %}
</main>
```

**Tone target (D-11 / D-12 spec):**
- Feels like a *lista plastificata per il frigo* — warm, hand-set via Instrument Serif italic on the date (Phase 1 escape-hatch font reused in PDF context per §3 amendment), NOT corporate Helvetica/Times.
- Print-friendly: ≤3% accent surface area (only category underlines + subtitle); no large coral/leaf backgrounds.
- Italian accents native: woff2 fonts embedded base64 inline → WeasyPrint always renders à è ì ò ù correctly without OS font fallback.
- Same OKLCH coords as `frontend/src/styles/theme.css` (drift-detection: CI grep enforces that any color literal in `shopping_list.html` matches a known token in theme.css; mismatch fails build).

### 6.5 Phosphor icon facade — Phase 2 additions

Add to `frontend/src/components/icons/index.ts` (NEVER direct `@phosphor-icons/react` imports outside this file — CI grep gate inherited from Phase 1):

| Icon | Used for |
|------|----------|
| `UsersThree` | Condiviso badge + ShareToggleMenu menu-item icon |
| `Snowflake` | Shopping category "Frigo & Freschi" |
| `Carrot` | Shopping category "Frutta & Verdura" |
| `Package` | Shopping category "Dispensa" |
| `Wine` | Shopping category "Condimenti" (oils, vinegars, dressings — Wine glyph reads as decanter/bottle, semantically aligned with liquid condiments per CONTEXT D-12) |
| `Pill` | Shopping category "Integratori" |
| `DotsThreeOutline` | MealCard `⋯` share-toggle menu trigger (owner-only) |
| `ArrowCounterClockwise` | "/spesa" Reset settimana button |
| `ClipboardText` | "/spesa" Copia testo export button |
| `FilePdf` | "/spesa" Esporta PDF export button |
| `ArrowsClockwise` | ConflictToast info icon (FAM-05 — paired with leaf-500 stripe + italian copy) |
| `Check` | Already exported Phase 1 — reused in VariantSelector active item indicator |
| `CaretDown` | Already exported Phase 1 — reused in VariantSelector pill + ShoppingCategorySection collapse caret |
| `X` | Already exported Phase 1 — reused in ShoppingItemRow swipe-delete button |

**Net new exports added to `index.ts`:** 11 (UsersThree, Snowflake, Carrot, Package, Wine, Pill, DotsThreeOutline, ArrowCounterClockwise, ClipboardText, FilePdf, ArrowsClockwise). Three (Check, CaretDown, X) are already in Phase 1's export.

### 6.6 Plan 02-03 deploy checklist artifact

**File:** `.planning/phases/02-differentiators/02-03-DEPLOY-CHECKLIST.md`

This is a markdown sign-off artifact (not a React component). Visual contract:

**Anatomy (12 sections):**

```markdown
# Plan 02-03 — Production Deploy CHECKPOINT (Stefano + Marta)

**Date attempted:** ____________  
**Server:** Windows Server 2019 · `wellness-buddy.epartner.it`  
**Deploy script source:** `DEPLOY.md` (Plan 01-08 deliverable)

## 1. Pre-flight — DNS + firewall
- [ ] DNS A record `wellness-buddy.epartner.it` → server IP (verify via `nslookup`)
- [ ] Firewall allows 80/443 inbound (verify via `Test-NetConnection -ComputerName ... -Port 443`)
- [ ] PostgreSQL service running (`Get-Service postgresql-x64-*`)

## 2. Database
- [ ] CREATE DATABASE `wellness_buddy_prod` OWNER `wellness_buddy`
- [ ] `uv sync --frozen` in backend dir
- [ ] `alembic upgrade head` returns no errors
- [ ] `\dt` in psql shows expected 12+ tables

## 3. Secrets
- [ ] `pwsh deploy/scripts/generate-secrets.ps1` produces `.env.production`
- [ ] JWT secret rotated (≠ dev value)
- [ ] DATABASE_URL points to `wellness_buddy_prod`
- [ ] CORS_ORIGINS = `https://wellness-buddy.epartner.it`

## 4. NSSM service
- [ ] `nssm install WellnessBuddyAPI` succeeded
- [ ] Service auto-start enabled
- [ ] Service starts cleanly (`Get-Service WellnessBuddyAPI` → Running)
- [ ] Application Event Log shows uvicorn startup, no errors

## 5. IIS reverse proxy
- [ ] `web.config` deployed at IIS site root
- [ ] URL Rewrite + ARR modules confirmed installed
- [ ] HTTPS smoke test 200 from local → reverse-proxy → backend
- [ ] WebSocket upgrade headers preserved (curl -i `Connection: Upgrade`)

## 6. SSL via win-acme
- [ ] `wacs.exe` interactive run completed for `wellness-buddy.epartner.it`
- [ ] Certificate issued + auto-renewal task scheduled
- [ ] `https://wellness-buddy.epartner.it` returns 200 from external (mobile network, NOT same LAN)
- [ ] Browser shows "Connessione protetta" (no cert warnings)

## 7. Smoke test
- [ ] `pwsh deploy/scripts/smoke-test.ps1` → all checks green
- [ ] `/api/health` returns `{"status": "ok"}`
- [ ] `/api/version` returns expected git sha
- [ ] First user login succeeds end-to-end (Stefano account)

## 8. iPhone install (Stefano)
- [ ] Open Safari → `https://wellness-buddy.epartner.it`
- [ ] Tap Share → "Aggiungi a Home" visible in menu
- [ ] Add to home screen, custom icon visible (NOT generic web clip)
- [ ] Tap home-screen icon → app opens in standalone mode (no Safari chrome)
- [ ] `/today` renders with Lifesum Pure theme (warm cream bg, MacroRing, Plus Jakarta font)
- [ ] Toggle airplane mode ON → reload `/today` → cached page renders + sync pip shows "Offline"
- [ ] Toggle airplane mode OFF → sync pip flips to "Sincronizzato" within 5s
- [ ] Kill app via swipe-up → reopen → still logged in (no logout storm — refresh token rotation working)

## 9. iPhone install (Marta)
- [ ] Same 8 steps as §8, with Marta's account on Marta's iPhone
- [ ] Verify Marta sees only HER plan / weight / workout (NOT Stefano's data)
- [ ] (FAM-* not yet shipped — Plan 02-06 will validate cross-user) — for Plan 02-03 only verify Marta's data isolation

## 10. Lighthouse audit (Stefano, Chrome desktop pointing at production URL)
- [ ] Lighthouse PWA score: ____ / 100 (target ≥95, lock 100/100 if achievable)
- [ ] Lighthouse Accessibility score: ____ / 100 (target ≥95)
- [ ] Lighthouse Performance score: ____ / 100 (informational — Phase 4 hardens)
- [ ] Lighthouse Best Practices score: ____ / 100 (informational)

## 11. Tone calibration sign-off (Stefano + Marta — in person)
- [ ] Both users open `/today` on their respective iPhones
- [ ] Confirm Lifesum Pure variant A rendering matches `mockups/tone-calibration-v2/A-lifesum-pure.html` expectation
- [ ] Confirm fonts (Plus Jakarta + Geist Mono + Instrument Serif greeting) load correctly
- [ ] Confirm dark mode toggle works (Settings → Tema → Scuro)
- [ ] No "office app" tone drift observed
- [ ] No infantile mascots or `!` in error copy spotted

## 12. Sign-off

| Reviewer | Initial | Date (YYYY-MM-DD) | Time (HH:MM) | Verdict (PASS/CONCERNS/BLOCK) | Notes |
|----------|---------|-------------------|--------------|-------------------------------|-------|
| Stefano  |         |                   |              |                               |       |
| Marta    |         |                   |              |                               |       |
```

**Visual contract:**
- Plain markdown, GitHub-style checkboxes (`- [ ]` / `- [x]`)
- Section headings `## N. Title` Plus Jakarta 600 (rendered by GitHub markdown renderer)
- Sign-off table at end — 2 reviewer rows minimum (Stefano + Marta), both required
- Verdict column locked enum: `PASS` / `CONCERNS` / `BLOCK` (any `BLOCK` from either reviewer keeps this checklist non-merged → blocks Phase 2 progression to Plan 02-04 per D-26)

---

## 7. Italian Copywriting Contract — Phase 2 extensions

**(Tone-of-voice rules inherited verbatim from Phase 1 UI-SPEC §7.1 — all 9 rules apply to every new string below. No `!` in errors. No infantile copy. Verb-first CTAs. Italian conventions.)**

All new strings live in `frontend/src/i18n/copy.it.ts` under namespaces `week.*`, `shopping.*`, `family.*`, `sync.conflictToast`, `pwa.installFollowUp` (FND-09 inherited).

### 7.1 New copy keys (verbatim — must ship as-is)

```typescript
// Append to frontend/src/i18n/copy.it.ts

  // ───── /week (Phase 2 — vista settimanale + variant selector) ─────
  week: {
    heading: 'La settimana',
    weekPickerJumpAria: 'Scegli un\'altra settimana',
    weekPickerCurrentLabel: 'Settimana corrente',
    weekPickerChipFormat: '{startDate}', // e.g. "5 mag" — italianDateShort start-of-week
    dayLabels: {
      mon: 'Lunedì',
      tue: 'Martedì',
      wed: 'Mercoledì',
      thu: 'Giovedì',
      fri: 'Venerdì',
      sat: 'Sabato',
      sun: 'Domenica',
    } as Record<string, string>,
    daySummaryFormat: '{count} pasti · {kcal} kcal previsti',
    weeklyTotalLabel: 'Settimana',
    weeklyTotalSubtitle: 'su {target}', // e.g. "su 15.400" (target × 7)
    weeklyKcalSuffix: 'kcal · settimana',
    weeklyMacroRingAria: '{consumed} di {target} kcal questa settimana, {done} pasti su {total} completati',
    completionStripDayDone: 'Tutti i pasti completati',
    completionStripDayPartial: '{done} di {total} pasti completati',
    completionStripDayPlanned: 'Pianificato',
    completionStripDayBlank: 'Nessun piano',
    variantOptionA: 'Opzione A',
    variantOptionB: 'Opzione B',
    variantSpecial: 'Pasta speciale',
    variantSelectorAria: 'Cambia variante per {meal}',
    variantSelectorActive: 'attiva',
    variantSelectorMacroFormat: '{kcal} kcal · P {protein} · C {carbs} · F {fat}',
    variantUpdateSuccess: 'Variante aggiornata',
    variantUpdateError: 'Aggiornamento variante non riuscito. Riprova.',
    emptyHeading: 'Nessuna settimana pianificata',
    emptyBody: 'Carica un piano per vedere i pasti della settimana.',
    emptyCta: 'Carica piano',
  },

  // ───── /spesa (Phase 2 — lista spesa aggregata + categorie) ─────
  shopping: {
    heading: 'La spesa',
    subtitleFormat: 'settimana del {weekStartLong}', // e.g. "settimana del 5 maggio 2026"
    viewToggleAriaLabel: 'Vista lista spesa',
    viewByCategory: 'Per categoria',
    viewByDay: 'Per giorno',
    categoryFridge: 'Frigo & Freschi',
    categoryVeggie: 'Frutta & Verdura',
    categoryPantry: 'Dispensa',
    categoryCondiments: 'Condimenti',
    categorySupplements: 'Integratori',
    categoryCountFormat: '{count}', // shown in pill — Geist Mono
    categoryToggleAria: '{action} {category}', // {action} ∈ {Mostra, Nascondi}
    categoryActionShow: 'Mostra',
    categoryActionHide: 'Nascondi',
    itemMealContextFormat: '{mealSlot} · {dayLong}', // per-day view caption — e.g. "PRANZO · giovedì"
    itemMealSlotBreakfast: 'COLAZIONE',
    itemMealSlotLunch: 'PRANZO',
    itemMealSlotDinner: 'CENA',
    itemMealSlotSnack: 'SPUNTINO',
    itemCheckedAria: 'preso',
    itemUncheckedAria: 'da prendere',
    itemDeleteAria: 'Rimuovi {name}',
    itemDeleteConfirm: 'Rimuovere {name} dalla lista?',
    itemDeleteCta: 'Rimuovi',
    itemDeleteCancel: 'Annulla',
    itemDeleteSuccess: 'Voce rimossa.',
    resetCta: 'Reset settimana',
    resetConfirmHeading: 'Resettare la lista?',
    resetConfirmBody: 'Tutte le voci verranno scollegate e la lista verrà rigenerata dalle varianti scelte.',
    resetConfirmCta: 'Resetta',
    resetConfirmCancel: 'Annulla',
    resetSuccess: 'Lista resettata.',
    autoResetMonday: 'Lista resettata per la nuova settimana.', // toast on Monday 00:00 user tz auto-trigger (D-09)
    exportCopyCta: 'Copia testo',
    exportCopySuccess: 'Lista copiata negli appunti.',
    exportPdfCta: 'Esporta PDF',
    exportPdfPreparing: 'Sto preparando il PDF...',
    exportPdfReady: 'PDF pronto.',
    exportPdfError: 'Esportazione non riuscita. Riprova tra poco.',
    emptyHeading: 'Nessuna spesa pianificata',
    emptyBody: 'Scegli le varianti settimanali per generare la lista.',
    emptyCta: 'Vai alla settimana',
  },

  // ───── Family sync (Phase 2 — badge condiviso + share toggle) ─────
  family: {
    sharedBadgeLabel: '{partnerName}', // shown next to UsersThree icon
    sharedBadgeAria: 'Condiviso con {partnerName}',
    sharedBadgeTooltipFormat: 'Aggiornato da {partnerName} · {timeAgo}', // e.g. "Aggiornato da Marta · 2 minuti fa"
    sharePerMealMenuAria: 'Opzioni pasto',
    sharePerMealToggleLabel: 'Condividi con la famiglia',
    sharePerMealOnSuccess: 'Condivisione attivata.',
    sharePerMealOffSuccess: 'Condivisione disattivata.',
    sharePerMealError: 'Aggiornamento non riuscito. Riprova.',
    timeAgoJustNow: 'adesso',
    timeAgoMinutes: '{minutes} minuti fa', // 1 → "1 minuto fa" via plural helper
    timeAgoMinutesSingular: '1 minuto fa',
    timeAgoHours: '{hours} ore fa',
    timeAgoHoursSingular: '1 ora fa',
    timeAgoYesterday: 'ieri',
    timeAgoDays: '{days} giorni fa',
  },

  // ───── Conflict 409 toast (FAM-05 — extends sync namespace) ─────
  // Note: extends existing `sync.*` namespace from Phase 1 — DO NOT create new top-level namespace.
  sync: {
    // ... Phase 1 keys preserved ...
    conflictToastHeading: 'Aggiornato da {partnerName}',
    conflictToastBody: 'Ricarica per vedere l\'ultima versione.',
    conflictToastAction: 'Ricarica',
    conflictToastAria: 'Conflitto di sincronizzazione: {partnerName} ha modificato questo elemento',
  },

  // ───── PWA install follow-up (D-26 — post-deploy iPhone install help) ─────
  // Extends Phase 1 `pwa.*` namespace.
  pwa: {
    // ... Phase 1 keys preserved ...
    installFollowUpHeading: 'Installazione completata',
    installFollowUpBody: 'Ora puoi aprire Wellness Buddy dalla schermata Home come app.',
    installFollowUpDismiss: 'Ho capito',
  },
```

### 7.2 Plural helper contract

`frontend/src/lib/format.ts` extends with:

```typescript
export function italianTimeAgo(date: Date | string, now: Date = new Date()): string {
  const diffMs = now.getTime() - new Date(date).getTime();
  const diffMin = Math.floor(diffMs / 60_000);
  const diffHr = Math.floor(diffMs / 3_600_000);
  const diffDay = Math.floor(diffMs / 86_400_000);

  if (diffMin < 1) return copy.family.timeAgoJustNow;
  if (diffMin < 60) {
    return diffMin === 1
      ? copy.family.timeAgoMinutesSingular
      : copy.family.timeAgoMinutes.replace('{minutes}', String(diffMin));
  }
  if (diffHr < 24) {
    return diffHr === 1
      ? copy.family.timeAgoHoursSingular
      : copy.family.timeAgoHours.replace('{hours}', String(diffHr));
  }
  if (diffDay === 1) return copy.family.timeAgoYesterday;
  return copy.family.timeAgoDays.replace('{days}', String(diffDay));
}
```

Plurals must be enforced at every `{count}` template (UI-SPEC §7.1 rule 8 inherited): `1 pasto` / `2 pasti`, `1 minuto` / `2 minuti`, `1 ora` / `2 ore`, `1 giorno` / `2 giorni`. Helper `italianPlural(count, singular, plural)` already exists per Plan 07 — reuse.

### 7.3 Destructive action contract — Phase 2 additions

| Action | Confirmation copy | Confirmation CTA | Cancel CTA |
|--------|------------------|------------------|------------|
| Reset shopping list | `Resettare la lista? Tutte le voci verranno scollegate e la lista verrà rigenerata dalle varianti scelte.` | `Resetta` | `Annulla` |
| Remove shopping item | `Rimuovere {nome} dalla lista?` | `Rimuovi` | `Annulla` |

Both use `Dialog` (Radix AlertDialog modal), never inline. **Reset settimana** uses primary `--color-leaf-500` confirm button (NOT `--color-destructive` — the action is recoverable; user can re-aggregate from variants without data loss). **Remove item** ALSO uses `--color-leaf-500` confirm (same reasoning — list item is rebuildable from plan + variants). Phase 2 introduces NO truly destructive actions on user data — Phase 4 admin will own the first true `--color-destructive` action (revoke invite).

**ShoppingItemRow swipe-reveal vs AlertDialog confirm — intentional dual-framing:** the swipe-reveal delete button uses `--color-destructive` red as a **gesture-intent signal** (mid-gesture — the red warns about the consequence of release); the subsequent AlertDialog confirmation uses `--color-leaf-500` because the action is **recoverable** (server is canonical, the row can be re-aggregated from variant choices). The mid-gesture warns; the confirmation softens once the user has paused to read. This is intentional, not inconsistent — color signals the *certainty* of the moment, not the destructiveness of the action.

### 7.4 Tone audit gates (must pass before merge — extends Phase 1 §7.1)

For every new Phase 2 string above:
- [ ] Zero `!` characters in any error/status copy (greppable)
- [ ] Zero ALL CAPS except meal-slot context captions in shopping list (which match Phase 1 MealCard slot-label pattern — `COLAZIONE`, `PRANZO`, `CENA`, `SPUNTINO`)
- [ ] All CTAs verb-first: `Carica`, `Esporta`, `Resetta`, `Rimuovi`, `Ricarica`, `Mostra`, `Nascondi`
- [ ] No infantile tropes (no "Ops!", "Yay!", "WOW", "Bravo!")
- [ ] All time references use 24h format if shown (`19:30` not `7:30 PM`)
- [ ] All quantities pass `Intl.NumberFormat('it-IT')` (`400 g`, `2 confezioni`, `1.250 kcal`)
- [ ] Address user by partner name when shown ("Aggiornato da Marta" not "Aggiornato da un altro utente")
- [ ] Plurals correct via `italianPlural` helper (1 minuto / 2 minuti)

---

## 8. Tone Calibration — Phase 2 scene-ratio extensions

**Lifesum Pure variant A is locked Phase 1.** Phase 2 surfaces extend the §8.3 scene-ratio table with the same focal-point discipline — no re-litigation of the elegant↔playful axis.

### 8.1 Phase 2 scene additions

| Scene | Default ratio | Focal Point (primary visual anchor) | Rationale | Confirmed by review? |
|-------|---------------|--------------------------------------|-----------|----------------------|
| `/week` populated | 70% elegant / 30% playful | WeeklyMacroRing centered at top of viewport — the eye lands on aggregate kcal then drops to first day's MealCards underneath | Functional planning surface — restraint dominates; ring carries the warmth signal; same DNA as `/today` MacroRing | pending — Stefano+Marta sign off Plan 02-07 |
| `/week` empty (no plan) | 60/40 | Phosphor `CalendarBlank` 240×240 leaf-200 fill centered + heading + body + "Carica piano" CTA | Onboarding moment — Phosphor icon at scale acts as restrained illustration (Lifesum Pure variant A precedent over Storyset) | pending |
| `/spesa` populated (per categoria) | 70/30 | First category section header "Frigo & Freschi" with Phosphor `Snowflake` 22px + count badge — list-of-lists composition reads from top-down, no hero | Routine grocery surface — list IS the surface; no hero competes with the rows | pending |
| `/spesa` populated (per giorno) | 70/30 | First day section header "Lunedì" + first item row — same list-of-lists composition rotated by day axis | Same rationale | pending |
| `/spesa` empty | 60/40 | Phosphor `ShoppingCart` 200×200 leaf-200 fill + heading + body + "Vai alla settimana →" secondary link | Onboarding before week filled | pending |
| Shopping list PDF | 75% elegant / 25% playful | Page header: "Lista spesa" 28pt Plus Jakarta 700 + Instrument Serif italic 14pt date subtitle + leaf-700 underline on category headings — typography IS the entire warmth signal in print | Print medium — Instrument Serif italic 14pt date subtitle is the singular hand-set touch (reuses Phase 1 escape-hatch font in PDF context per §3 amendment); everything else is restrained editorial | pending — Stefano+Marta in-person sign off Plan 02-05 |
| VariantSelector dropdown open | 65/35 | Active variant indicator dot leaf-500 6×6 + variant name Plus Jakarta 600 + macro chip preview row — quick decision moment, decision support data ON-SCREEN | Decision-making surface — must show macro tradeoff before commit; dot + chip preview together carry the "smart but warm" tone | pending |
| Condiviso badge inline | 80% elegant / 20% playful | Phosphor `UsersThree` 14px + partner name 12px in surface-muted pill — small, semantic, never noisy (D-18) | Background context, not foreground — restraint is the win | pending |
| ShareToggleMenu open (`⋯` dropdown) | 70/30 | Single menu item: `UsersThree` icon + "Condividi con la famiglia" label + Switch component current state — minimal decision surface | Single-action menu, not exploratory — restraint reflects functional intent | pending |
| Conflict toast (sync.conflictToast) | 75/25 | Phosphor `ArrowsClockwise` 18px + heading "Aggiornato da Marta" + body + "Ricarica" ghost action — info tone NOT panic tone (D-17, no `!`) | Sync information moment — calm, factual, actionable; leaf-500 left stripe (NOT destructive red) carries the brand convergence | pending |
| Plan 02-03 deploy checklist (artifact, not screen) | n/a | n/a — markdown artifact, no UI focal-point | Sign-off doc, not a rendered surface | n/a |

**Update for Phase 1 §8.3 row "Phase 3 milestone celebrations 30/70" — UNCHANGED.** Phase 2 introduces NO new playful-side moments; the "tilt toward 70 playful" still happens for the first time only in Phase 3 mascot/Lottie.

### 8.2 Anti-drift gate — Phase 2 surfaces converge on Lifesum Pure

For every Phase 2 surface above:
- [ ] Plus Jakarta + Geist Mono fonts (NEVER Inter, Helvetica, Times)
- [ ] Phosphor icons via facade (NEVER lucide direct on Phase 2 surfaces — even though Phase 1 UI-SPEC §1 originally mentions lucide, Plan 09 propagated Phosphor as canonical; Phase 2 honors the propagated decision)
- [ ] Leaf-sage primary accent (NOT coral) on `/week` and `/spesa` primary CTAs — coral remains Phase 1 weight-CTA-only
- [ ] Warm cream background `--color-bg` (NOT pure white) on every populated surface
- [ ] Card radius `--radius-card` 20px (NOT 16px — Plan 09 propagated 20px)
- [ ] `--shadow-1` for cards (NEVER `--shadow-3` on routine surfaces — only used for popovers/sheets per Phase 1 §6)

---

## 9. Layout patterns

**(Mobile-first 390px → tablet 768px → desktop 1280px container queries inherited from Phase 1 UI-SPEC §2.)**

### 9.1 `/week` route

- **Mobile 390px:** Single-column vertical stack. Day-name navigation = vertical stack of 7 day sections (more usable than horizontal tabs at 390px per `<phase_2_surfaces>` decision). Sticky day header per section (`position: sticky; top: 56px;` to clear AppBar).
- **Tablet 768px+:** Two-column. Left = WeeklyMacroRing 260px + 7-day completion strip + summary. Right = horizontal day-tab strip (Lun-Dom) + selected-day MealCards. Day-tab uses Radix Tabs.
- **Desktop 1280px+:** Same as tablet but max-width 1024px container, ample side margins (`--spacing-16`).
- **Pre-fetch ±1 week** for swipe smoothness (D-30) — TanStack Query `prefetchQuery` on WeekPicker chip hover/focus.

### 9.2 `/spesa` route

- **Mobile 390px:** Single-column flat scroll. ShoppingCategorySection per categoria (or ShoppingDaySection per giorno). NO virtualization Phase 2 (D-29 — flat scroll up to 500 rows; threshold for Phase 4 retrofit).
- **Sticky bottom export-row:** `position: sticky; bottom: 56px;` (clears BottomTabBar) — two-button row, full-width split.
- **Tablet 768px+:** Two-column option deferred Phase 2 — single-column on all viewports keeps focus on the list. Reset settimana subwidget aligns to right column on desktop ≥1024px.

### 9.3 Multi-tab sync (BroadcastChannel — D-25)

When a shopping-list checkbox is toggled in tab A, tab B's `/spesa` reflects the change within 1s via BroadcastChannel:
- Detection: `'BroadcastChannel' in window` runtime check
- Channel name: `wb-shopping-sync` (one channel per app, message `{type: 'shopping_item_toggled', itemKey, checked, weekStart}`)
- Fallback for Safari iOS 15.x without BroadcastChannel: `window.addEventListener('focus', () => queryClient.invalidateQueries(['shopping', weekStart]))` — refetch on tab focus

Rendered behavior: no visible UI change beyond the natural item-row checked transition (250ms strikethrough fade). No toast on cross-tab sync (would be noise).

### 9.4 Real-time strategy (D-16 — polling, NOT WebSocket Phase 2)

`/week` and `/today` shared-meal updates from partner converge ≤5s via TanStack Query:
- `staleTime: 30_000` (30s)
- `refetchOnWindowFocus: true`
- `refetchOnReconnect: true`
- No polling interval — focus-based + 30s stale window suffices per FAM-09 acceptance criteria

Convergence test (Plan 02-07 verification): two browser tabs, one user each, edit shared meal in tab A → tab B reflects within 30s on next focus event OR explicit refresh. No WebSocket / SSE Phase 2.

---

## 10. Status indicators

**(inherited from Phase 1 UI-SPEC §10.5 — SyncStatusPip persistent in AppBar)**

Phase 2 reuses SyncStatusPip without modification:
- `/week` shows pip top-right of AppBar (sync state of weekly variants + shopping aggregations)
- `/spesa` shows pip top-right of AppBar (sync state of checkbox state mutations)
- Cross-user sync (FAM-*) appears as additional `pending N` count when partner edits arrive within stale window

### 10.1 Variant change feedback (NEW — Phase 2)

After tap on VariantSelector menu item:
1. Optimistic update Dexie cache_weekly + UI re-render new variant pill
2. Mutation queue PATCH `/api/weekly/{week_start}/variant` with `If-Unmodified-Since` header (D-17)
3. Sonner success toast `"Variante aggiornata"` after 2xx response (250ms slide-up + fade, auto-dismiss 4s)
4. On 409 → ConflictToast (auto-dismiss 6s) — do NOT roll back optimistic UI; user must tap "Ricarica" to refetch authoritative state (matches Phase 1 conflict UX precedent)
5. On 5xx / network error → sonner error variant `"Aggiornamento variante non riuscito. Riprova."` + roll back optimistic UI

### 10.2 Shopping checkbox feedback (NEW — Phase 2)

After tap:
1. Optimistic update — checkbox visual + row strikethrough 250ms ease-out-soft
2. Mutation queue POST/DELETE `/api/shopping/{week_start}/items/{ingredient_canonical}/checked`
3. NO toast on success (would be noise on routine grocery checkboxing — already noisy at 336 rows)
4. On 5xx / network error → silent rollback + sonner error toast `"Sincronizzazione non riuscita. Riprova più tardi."` (existing Phase 1 key `errors.syncFailed` reused)

### 10.3 Reset settimana feedback (NEW — Phase 2)

1. Tap "Reset settimana" → Radix AlertDialog with copy `shopping.resetConfirmHeading` + body
2. Confirm → POST `/api/shopping/{week_start}/reset`
3. On 2xx → sonner success toast `"Lista resettata."` + UI refetches and re-aggregates
4. On 5xx → sonner error toast `errors.syncFailed`

### 10.4 PDF export feedback (NEW — Phase 2)

1. Tap "Esporta PDF" → button enters loading state with inline spinner replacing label (Phase 1 §11.1 pattern), button stays width-stable
2. POST `/api/shopping/{week_start}/export.pdf` (returns `application/pdf` blob)
3. On 2xx → trigger browser download `Lista-spesa-{week_start}.pdf` + sonner success toast `"PDF pronto."` (auto-dismiss 4s) + button returns to default state
4. On 5xx → sonner error toast `"Esportazione non riuscita. Riprova tra poco."` + button returns to default state. If WeasyPrint flagged unstable per D-11 spike, backend automatically routes to ReportLab fallback — frontend sees identical 2xx response with same blob shape; no UX difference visible.

---

## 11. Accessibility — Phase 2 specifics

**(Gates inherited from Phase 1 UI-SPEC §9 verbatim — axe-core ≥4.5 / 3.0, Lighthouse a11y ≥95, dark-mode CI screenshots, prefers-reduced-motion, VoiceOver smoke, 44×44 touch targets, focus rings.)**

### 11.1 Phase 2 surface a11y test list (extends Phase 1 §9)

Every route below must pass on light + dark + small viewport (390px) + standard viewport (1280px):
- `/week` populated (3 days planned) + empty (no plan) + offline
- `/spesa` per-categoria populated + per-giorno populated + empty + offline
- VariantSelector open dropdown state (each of 3 menu items focused)
- ShareToggleMenu open dropdown state
- Conflict toast visible state
- Reset settimana confirmation dialog
- Remove shopping item confirmation dialog

### 11.2 Phase 2 ARIA contract

| Element | Required ARIA |
|---------|---------------|
| `WeeklyMacroRing` | `role="img"` + `aria-label` per `week.weeklyMacroRingAria` template |
| `VariantSelector` trigger pill | `aria-haspopup="menu"` + `aria-expanded` (Radix DropdownMenu default) + `aria-label` per `week.variantSelectorAria` template |
| `VariantSelector` menu items | `role="menuitem"` (Radix default) + `aria-current="true"` on active variant |
| `WeekPicker` chip | `aria-pressed={isActive}` (toggle button semantic) |
| `WeekPicker` jump-to-date trigger | `aria-haspopup="dialog"` (Radix Popover default) + `aria-label="Scegli un'altra settimana"` |
| `SharedBadge` | `aria-label` per `family.sharedBadgeAria` template |
| `ShareToggleMenu` trigger | `aria-haspopup="menu"` + `aria-label="Opzioni pasto"` |
| `ShareToggleMenu` Switch | `role="switch"` (Radix default) + `aria-checked` + label association via `for=` |
| `ShoppingCategorySection` header | `aria-expanded` + `aria-controls={bodyId}` (Radix Collapsible default) |
| `ShoppingItemRow` checkbox | Native `<input type="checkbox">` via shadcn — `aria-label` per `shopping.itemCheckedAria` / `itemUncheckedAria` |
| `ShoppingItemRow` swipe-delete button | `aria-label` per `shopping.itemDeleteAria` template (revealed when swiped — kept in DOM with `aria-hidden` toggled by swipe state for screen-reader visibility) |
| `ShoppingViewToggle` | `role="radiogroup"` (Radix ToggleGroup default) + `aria-label="Vista lista spesa"` |
| `ConflictToast` | sonner `role="status"` (info, NOT `alert` — non-urgent) + `aria-label` per `sync.conflictToastAria` template |
| Reset confirmation Dialog | Radix AlertDialog default — `role="alertdialog"` + `aria-labelledby` + `aria-describedby` |

### 11.3 Color-blind safety (UI-15 inherited)

- Conflict toast: leaf-500 stripe + Phosphor `ArrowsClockwise` icon + italian copy (3 channels — never color alone)
- VariantSelector active state: leaf-500 dot + Phosphor `Check` icon + variant name visual distinction (3 channels)
- Shopping checkbox checked: leaf-500 fill + checkmark glyph + strikethrough text (3 channels)
- Shared badge: Phosphor `UsersThree` icon + partner name text + (no color signal — intentional restraint, badge is informational)

### 11.4 iOS keyboard & gesture (UI-16 inherited)

- VariantSelector dropdown: when triggered from middle of `/week` scroll, dropdown anchors to trigger via Radix `side="bottom"`, `align="start"`, `sideOffset={4}` — NEVER pushes content under iOS keyboard (no input field within)
- Shopping list swipe-left to delete: gesture conflicts with iOS Safari swipe-back navigation. Mitigation: swipe must START on item-row body (>20px from left edge) AND exceed 60px horizontal AND velocity threshold; otherwise treated as scroll. Implementation: `motion/react` `dragX` with constraint zones.
- Reset settimana confirmation Dialog: focus-trap, ESC closes, scrim tap closes (Radix AlertDialog defaults inherited)

### 11.5 Touch target audit (Phase 2 surfaces)

Playwright `getBoundingClientRect` test extends Phase 1 list:
- VariantSelector pill ≥44×44
- VariantSelector menu items ≥56 height
- WeekPicker chip ≥44×44
- WeekPicker jump-to-date trigger 44×44
- SharedBadge tap area ≥44×44 (tooltip trigger — wrapper invisible hit-area)
- MealCard `⋯` ShareToggleMenu trigger 44×44
- ShoppingCategorySection header tap area = full row width × ≥44 height
- ShoppingItemRow checkbox visual 24×24 inside 44×44 hit-area
- ShoppingItemRow row tap area (for screen readers — currently no full-row tap, only checkbox; documented intent: keep checkbox-only to avoid accidental check on swipe)
- Reset settimana button ≥44 height, ≥120 width
- Export buttons (Copia testo / Esporta PDF) ≥44 height

---

## 12. Final Lock List — Phase 2 deltas only

**(Phase 1 §12 lock list inherited verbatim. No new tokens introduced. The only additions are 12 Phosphor icon names appended to `frontend/src/components/icons/index.ts` and ~30 Italian copy keys appended to `frontend/src/i18n/copy.it.ts`.)**

### 12.NEW Phase 2 amendments to Phase 1 §12

**No new design tokens** — `theme.css` is unchanged by Phase 2.

**Icons added to facade (11 net new exports):**

```typescript
// frontend/src/components/icons/index.ts
export {
  // ... Phase 1 exports preserved (Leaf, BowlFood, Fish, Cookie, OrangeSlice,
  //     PersonSimpleRun, Scales, House, CalendarBlank, ShoppingCart,
  //     ClockCounterClockwise, UserIcon, CheckCircle, Check, Circle, Sparkle,
  //     ArrowDown, ArrowUp, UploadSimple, Plus, Sun, Moon, X, PencilSimple,
  //     Trash, CaretDown, CaretUp, CaretLeft, CaretRight) ...

  // Phase 2 additions:
  UsersThree,
  Snowflake,
  Carrot,
  Package,
  Wine,
  Pill,
  DotsThreeOutline,
  ArrowCounterClockwise,
  ClipboardText,
  FilePdf,
  ArrowsClockwise,
} from '@phosphor-icons/react';
```

**Copy keys added to `copy.it.ts` (count: 95 new leaves total across namespaces — counted excluding wrapper objects like `dayLabels`; CONTEXT D-33 estimate of ~30 was conservative — actual count is the table below):**

| Namespace | Keys count | Listed in §7.1 |
|-----------|-----------|----------------|
| `week.*` | 31 (incl. 7 `dayLabels` leaves: mon-sun) | yes |
| `shopping.*` | 42 | yes |
| `family.*` | 15 | yes |
| `sync.*` (extends Phase 1) | 4 added | yes |
| `pwa.*` (extends Phase 1) | 3 added | yes |
| **Total** | **95 leaves** | — |

**No new color tokens.** No new spacing tokens. No new motion durations. No new font families. No new radius tokens. No new shadows.

If a future Phase 2 plan needs a value not in this list, the proposal MUST amend Phase 1 §12 (revision bump) — silently adding a hardcoded one-off is forbidden (ESLint hex-ban + grep `text-[1` gate inherited).

---

## 13. Phase 2 Surface ↔ Component Map

Extension of Phase 1 §13. New surfaces and their consumed components:

| Surface | Components | Notes |
|---------|------------|-------|
| `/week` populated | `AppBar`, `WeekPicker`, `WeeklyMacroRing`, day section header (composed from `Card` + sticky position), `MealCard` (with VariantSelector slot + ShareToggleMenu owner-only + SharedBadge non-owner shared), `VariantSelector`, `BottomTabBar`, `SyncStatusPip` | Pre-fetch ±1 week; sticky day headers; vertical day stack mobile / horizontal day-tab desktop |
| `/week` empty (no plan) | `AppBar`, `EmptyStateWeek` (Phosphor `CalendarBlank` 240×240), `BottomTabBar` | "Carica piano" CTA → `/piano` |
| `/spesa` per categoria | `AppBar`, `ShoppingViewToggle`, `ShoppingCategorySection` × 5 (in fixed order: Frigo&Freschi → Frutta&Verdura → Dispensa → Condimenti → Integratori), `ShoppingItemRow`, sticky bottom `Button` row (Copia testo + Esporta PDF), `BottomTabBar`, `SyncStatusPip` | Reset settimana subwidget above sticky bottom row |
| `/spesa` per giorno | Same as per-categoria but `ShoppingDaySection` × 7 in place of category sections; ShoppingItemRow includes meal-context caption (`itemMealContextFormat`) | Same reset + export pattern |
| `/spesa` empty | `AppBar`, `EmptyStateShopping` (Phosphor `ShoppingCart` 200×200), `BottomTabBar` | "Vai alla settimana →" secondary link |
| Shopping list PDF | Jinja2 template `backend/app/templates/shopping_list.html` rendered by WeasyPrint (primary) or ReportLab (fallback per D-11 spike) | Brand contract via embedded `<style>` mirroring `theme.css` OKLCH coords; embedded woff2 base64 for italian-accent native rendering |
| Variant change flow | `VariantSelector` trigger pill on each MealCard → DropdownMenu open → `MacroDisplay compact` per menu item → optimistic update + sonner success/error toasts | Pattern: tap → dropdown 250ms → tap option → close 250ms + optimistic + sonner |
| Family sync — owner sees own meal | `MealCard` with `ShareToggleMenu` accessible via `⋯` icon | Owner toggles visibility per-meal; default per FAM-02 (cene+pranzi shared, colazione+spuntini private) |
| Family sync — partner sees shared meal | `MealCard` with `SharedBadge` inline next to slot-label caption + Radix Tooltip on tap | Read-only — partner cannot toggle visibility, only owner can |
| Conflict UX (409) | Sonner `info` variant via `ConflictToast` | Action button "Ricarica" → invalidate query + refetch |
| Reset settimana | `Button` (outlined ghost) → Radix AlertDialog → confirm POST `/api/shopping/{week_start}/reset` + sonner success | Auto-trigger Monday 00:00 user tz via APScheduler (D-09) shows `shopping.autoResetMonday` toast on next user focus |
| Remove shopping item | Swipe-left ShoppingItemRow → reveal delete button → tap → Radix AlertDialog → confirm DELETE | LWW + version int + 409 → conflict toast |
| `/today` (Phase 1 surface, Phase 2 extends) | `MealCard` extended with `SharedBadge` slot (when partner shared) and `ShareToggleMenu` (when owner) | Phase 1 layout preserved; only MealCard inner anatomy adds slots |
| Plan 02-03 deploy checklist | (markdown artifact, not a UI surface) | `02-03-DEPLOY-CHECKLIST.md` — Stefano + Marta sign-off table 12 sections |

---

## 14. Registry Safety — Phase 2 ADDED/EXTENDED registry blocks

**(inherited from Phase 1 UI-SPEC §14 verbatim — only shadcn official used; no third-party blocks)**

Phase 2 declares ZERO new third-party shadcn registries. All composites (`Dialog`, `AlertDialog`, `DropdownMenu`, `Popover`, `Switch`, `ToggleGroup`, `Tooltip`, `Tabs`, `Collapsible`) are pulled from shadcn official (`ui.shadcn.com`) via `npx shadcn add ...`.

| Registry | Phase 2 blocks added | Safety Gate |
|----------|----------------------|-------------|
| **shadcn official** (ui.shadcn.com) | Phase 1 already added: `dropdown-menu`, `dialog`, `sheet`, `tabs`. Phase 2 ADDS: `popover`, `tooltip`, `alert-dialog`, `collapsible`, `toggle-group` (5 net new). All others reused from Phase 1 §14 list. | not required (official registry, vetted upstream) |
| Third-party registries | **none declared for Phase 2** | not applicable |

If a Phase 2 plan emerges that needs a third-party block (e.g. specialty calendar/date-picker registry), gsd-ui-researcher must run the safety vetting protocol (`npx shadcn view` → scan for `fetch(`, `eval(`, `process.env`, dynamic external imports) BEFORE the registry entry can be merged into this UI-SPEC. See agent definition §registry-safety.

---

## 15. What Phase 3-5 Inherit from Phase 2

Beyond the Phase 1 §15 inheritance, Phase 3-5 also inherit:

- **VariantSelector** component pattern (Phase 5 may extend with AI-suggested variant — same component contract, new menu item type)
- **WeeklyMacroRing** SVG anatomy (Phase 3 may extend with adherence ring band — same 4-arc base, new outer band)
- **Shopping list PDF brand contract** (Phase 3+ PDF deliverables — meal plan PDF, weekly summary PDF — MUST mirror the same OKLCH coords + Plus Jakarta + Instrument Serif italic date-subtitle accent per §6.4)
- **SharedBadge** + **ShareToggleMenu** (Phase 4 admin gains group-merge UI — reuses same SharedBadge to indicate cross-merged meals)
- **ConflictToast** (Phase 4 admin operations + Phase 5 AI streaming may surface 409 conflicts — reuse the same component with extended copy keys)
- **Italian time-ago helper** (`italianTimeAgo`) — Phase 3 push notification copy reuses for "ultimo accesso" indicators
- **Tone audit gates §7.4** — applies to every new copy string in Phase 3-5

**Specifically forbidden to amend in Phase 3-5 without explicit revision bump:**
- Adding a new variant name beyond "Opzione A / B / Pasta speciale" (D-01 lock — Phase 5 AI feature must work within these names or amend with new lock decision)
- Replacing leaf-500 with coral on `/week` or `/spesa` primary CTAs (Phase 1 §4 reservation lock)
- Introducing a fifth typography size step (Phase 1 §3.6 lock)
- Adding lucide-react imports anywhere (Phosphor facade lock — Plan 09 propagation)
- Real-time WebSocket/SSE for FAM-* (D-16 polling lock — Phase 4 may revisit)

---

## 16. Phase 2 Exit Gate (UI-specific portion)

Cross-checked with ROADMAP Phase 2 pause gate:

- [ ] Tokens consumed everywhere (zero hardcoded hex grep on `frontend/src` + `backend/app/templates`)
- [ ] Dark-mode CI screenshot tests green on `/week`, `/spesa` (per-categoria + per-giorno), VariantSelector dropdown open state, ShareToggleMenu open state
- [ ] axe-core CI green on all Phase 2 PRs (every new surface from §11.1)
- [ ] Lighthouse a11y ≥ 95 on `/week` and `/spesa` production URLs
- [ ] Lighthouse PWA = 100/100 (D-28 — measured Plan 02-03 production deploy)
- [ ] `prefers-reduced-motion: reduce` test extends to `/week` + `/spesa` route — no animations fire
- [ ] All Phase 2 copy in `copy.it.ts`, no hardcoded strings (grep test extends Phase 1 list)
- [ ] Italian formatting verified — quantities `400 g` / `2 confezioni`, dates `lun 5 mag` short / `lunedì 5 maggio 2026` long, weekly kcal `12.320` thousand-separator
- [ ] iPhone install verified production URL on real iPhone (Stefano + Marta — D-27, Plan 02-03 checklist §8 + §9)
- [ ] Shopping list PDF Italian accents verified iPhone Safari + Mail.app (D-13, end-of-Plan-02-05)
- [ ] Family-sync authz matrix tests green (FAM-08 — 8 endpoints × 5 scenarios, Plan 02-06 verifier)
- [ ] Conflict 409 toast convergence ≤5s verified two-tab concurrent test (FAM-09, Plan 02-07)
- [ ] WeasyPrint GTK3 7-day stability spike verdict committed `.planning/phases/02-differentiators/02-01-GTK3-SPIKE.md` (D-11 — 5xx <2% locks WeasyPrint primary; >2% activates ReportLab fallback branch)
- [ ] **Stefano + Marta tone calibration sign-off** for §8.1 Phase 2 surface ratios — pending until Plan 02-07 final review (Phase 2 verifier goal-backward)
- [ ] **Plan 02-03 deploy checklist signed** by Stefano AND Marta with PASS verdict on all 12 sections (D-26)
- [ ] VoiceOver smoke pass on real iOS extends Phase 1 list with `/week` + `/spesa` + condiviso badge tooltip + variant selector dropdown
- [ ] Touch targets ≥ 44×44 verified by Playwright on Phase 2 surfaces (§11.5 list)
- [ ] Phosphor facade audit: grep `from '@phosphor-icons/react'` outside `frontend/src/components/icons/index.ts` returns 0 hits (extends Phase 1 lucide gate to Phosphor)
- [ ] No new tokens introduced in `theme.css` (diff against Phase 1 baseline — must be empty)

---

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS — §7 contains verb-first CTAs (Carica/Esporta/Resetta/Rimuovi/Ricarica/Mostra/Nascondi), no `!` in errors, no infantile copy, italian conventions enforced (Lunedì capital, kg/kcal lowercase, 24h time, thousand-separator `.`), destructive contracts present for reset and remove, plurals correctly rendered via `italianPlural` + `italianTimeAgo` helpers
- [ ] Dimension 2 Visuals: PASS — single icon system (Phosphor via facade extended with 12 net icons), zero new shadow levels, zero new radius values, motion budget enforced (≤250ms micro / ≤800ms celebration, none Phase 2), focal points declared per scene in §8.1, list-of-lists composition for `/spesa` rejects hero competition
- [ ] Dimension 3 Color: PASS — 60/30/10 reused per Phase 1 lock (leaf-500 primary on `/week`+`/spesa`, coral remains weight-CTA-only), accent reservations explicit, semantic colors reserved for semantic events (conflict toast = info NOT destructive), zero new color tokens, dark-mode parity verified across new surfaces
- [ ] Dimension 4 Typography: PASS — 4 base sizes inherited (12, 16, 22, 28), display-serif escape hatch FORBIDDEN on Phase 2 surfaces (`/today` only), 2 weights only (400/600 + 500 on escape hatch), KPI Mono reuses 28 step with Geist Mono font-family swap, italian formatting locked
- [ ] Dimension 5 Spacing: PASS — multiples of 4 inherited, exceptions documented and bounded (44×44 touch target + safe-area insets), container queries declared, sticky bottom export-row uses `env(safe-area-inset-bottom)` math
- [ ] Dimension 6 Registry Safety: PASS — only shadcn official used; net new blocks for Phase 2 (`dropdown-menu`, `popover`, `tooltip`, `alert-dialog`, `tabs`, `collapsible`, `toggle-group`) all from official registry; no third-party registries declared; vetting protocol noted for any future addition

**Approval:** pending — awaiting `gsd-ui-checker` validation, then Plan 02-07 Stefano+Marta tone review on rendered Phase 2 surfaces (`/week` + `/spesa` + shopping PDF + condiviso badge in production).
