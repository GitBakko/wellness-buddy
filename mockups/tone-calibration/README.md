# Tone Calibration Mockups — `/today`

Three standalone HTML/CSS mockups of the `/today` landing screen rendered at different elegant↔playful ratios. Output of **Phase 1 · Plan 08 · Task 1** — UI-SPEC §8 exit gate deliverable, UI-20 sign-off requirement.

## Variants

| File | Ratio | Treatment intensity |
|------|-------|---------------------|
| [`A-75-25-elegant.html`](./A-75-25-elegant.html) | 75% elegant / 25% playful | Geist Sans only (no Instrument Serif), illustration only on empty state, coral pixel-area only on primary CTA + active tab, smaller radius (12px) |
| [`B-50-50-balanced.html`](./B-50-50-balanced.html) | 50% / 50% (recommended) | Instrument Serif greeting (the §3 escape hatch), Storyset illustration on empty state, coral on CTA + completed-meal coral edge, 16px radius |
| [`C-25-75-playful.html`](./C-25-75-playful.html) | 25% elegant / 75% playful | Instrument Serif larger, illustrations also in populated header, decorative wavy underline on date, larger radius (22px), shadow-2 elevation |

Each variant shows four scenes in a CSS grid:

1. Mobile 390 · Light · Populated
2. Mobile 390 · Light · Empty (no plan)
3. Mobile 390 · Dark · Populated
4. Desktop 1280 · Light · Populated

## Locked focal points (UI-SPEC §8.3 revision 1)

Focal points are **constant across A/B/C** — only treatment intensity varies. Per surface:

- `/today` populated: Instrument Serif greeting at top + first incomplete `MealCard` directly below (eye lands on greeting, drops to next action).
- `/today` empty (no plan): centered hero illustration + `Carica piano` CTA.
- Meal-completion CTA: visually prominent on each `MealCard`.
- Weight log CTA: sub-prominent (below meals).
- AI widget: locked at bottom, lower visual weight.

## Open

### iPhone Safari (recommended for tone review)

Open `file://` URL directly in Safari (works on iOS) or:

```bash
cd mockups/tone-calibration
python -m http.server 8888
# Open http://<dev-ip>:8888/index.html on iPhone over LAN.
```

### Desktop

Open `index.html` in any modern browser (Chrome / Safari / Edge / Firefox). Use DevTools device toolbar to verify 390×844 layout for the mobile sections.

## Source of tokens (drift impossible by design)

`shared.css` mirrors `frontend/src/styles/theme.css` `@theme` block. Token names and values are **identical** to production — no fork, no overrides. If production tokens change, this file must be re-synced manually (verification step in Plan 08 ships a diff check).

The mockups intentionally do **not** compile from production code; they are the design contract artefact, kept readable in standalone HTML so non-engineers (Stefano + Marta) can open them on any browser without a build step.

## Conventions

- No hardcoded hex anywhere — all colours via `var(--color-*)`.
- Italian copy verbatim from `frontend/src/i18n/copy.it.ts` (UI-SPEC §7.2).
- 24h time, IT date format `lunedì 5 maggio`, IT decimal separator `75,3`.
- No `!` in copy; no infantile mascots; no emoji in chrome (UI-SPEC §7.1).

## Sign-off process

1. Stefano + Marta open `index.html` on iPhone Safari and on desktop Chrome.
2. For each scene listed in [`01-08-tone-calibration-checklist.md`](../../.planning/phases/01-foundation/01-08-tone-calibration-checklist.md), each reviewer independently picks A/B/C, then converges.
3. Fill the checklist with names + signatures + final per-scene ratios.
4. Phase 1 closes only when the checklist is fully signed.

## Focal points are LOCKED

Per UI-SPEC §8.3 revision 1, focal points are **locked across A/B/C**. Only treatment intensity varies. Any review feedback that wants to move a focal point requires amending UI-SPEC and bumping the design contract revision — not a silent change here.
