# Phase 2: Differentiators - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions captured in CONTEXT.md — this log preserves alternatives considered.

**Date:** 2026-05-02
**Phase:** 02-differentiators
**Mode:** discuss (auto)
**Areas analyzed:** Variant model · Shopping list aggregation · PDF export · Family sync · Authz · Migration · iOS Safari · Plan 08 T3 deferred · Performance · Visual baselines · AI widget · Italian copy · Wave structure

## Auto-mode summary

Most "gray areas" surfaced in the prompt were already pre-decided in `.planning/REQUIREMENTS.md`:
- Variant naming: "Opzione A / Opzione B / Pasta speciale" (WEEK-03 verbatim)
- Visibility defaults: cene+pranzi `group_shared`, colazione+spuntini `private` (FAM-02)
- Real-time strategy: TanStack Query polling 30s (FAM-09)
- Conflict UX: LWW + 409 + toast (FAM-04, FAM-05)
- Shopping categories: Frigo/Verdura/Dispensa/Condimenti/Integratori (SHOP-04)
- Reset trigger: lunedì 00:00 user tz (SHOP-08)
- Cross-user dependency: `get_user_with_group_access` (FAM-06)
- JWT exclusion: `group_id` MAI in JWT (FAM-07)
- WeasyPrint primary + ReportLab fallback (DEP-06)
- Authz test matrix in CI (FAM-08)

Auto-resolved decisions (recommended defaults selected):

| Question | Selected | Rationale |
|---|---|---|
| Ingredient unit normalization | Heuristic dictionary (no NLP) | Phase 2 ships pragmatic baseline; full NLP defer Phase 5 |
| Fuzzy name matching | NO Phase 2 | "pomodorini"/"pomodori" stay separate; synonym dict Phase 5 AI |
| Variant override granularity | per-meal-day | Bounded flexibility, simple persistence keying |
| Default variant | "Opzione A" everywhere | Predictable; user changes per slot |
| WeasyPrint spike timing | First plan of Phase 2 (Plan 02-01) | Gates subsequent PDF code; ROADMAP 7-day spike honored |
| ReportLab fallback wiring | Scaffolded via PdfExporter ABC | Only activated if spike fails; keeps code clean |
| Plan 08 T3 deferral position | Plan 02-03 mid-phase deploy | iPhone install + Lighthouse validated WITH Phase 2 features, not retrofitted |
| iOS multi-tab sync | BroadcastChannel API + focus-event fallback | Native browser, zero deps |
| Shopping list virtualization | NO (≤500 rows threshold) | iPhone perf adequate; revisit if scale grows |
| Visual baseline regen timing | First Phase 2 plan touching visual surfaces (Plan 02-02) | Locks new Lifesum Pure baseline |
| AI widget Phase 2 | locked placeholder unchanged | D-26 carry-forward Phase 1 |
| Wave structure | 7 waves linearized (spike → /week → deploy → shopping → PDF → family → closure) | Honor dependency locks; checkpoint mid-phase |

## Auto-mode pass cap

Single pass executed. CONTEXT.md written once. No re-pass triggered.

## Areas with no gray area (skipped)

- Italian copy expansion: pattern locked (FND-09, copy.it.ts) — Phase 2 extends namespaces only
- Variant naming: locked verbatim REQ
- Categories list: locked verbatim REQ

## Deferred ideas captured

- Phase 3: mascot, Lottie celebrations, dashboard KPI, push notifications
- Phase 4: admin panel group merge, RLS, stress test, virtualization
- Phase 5: fuzzy ingredient matching, AI shopping suggestions, AI plan editor

## External research

None performed — codebase + ROADMAP + Phase 1 CONTEXT carry sufficient evidence. WeasyPrint GTK3 stability uncertainty is explicitly addressed by Plan 02-01 spike (D-11), not by upfront research.

