---
phase: 02-differentiators
plan: 07
subsystem: backend-authz + frontend-family-sync
tags:
  - family-sync
  - cross-user
  - authz-matrix
  - alembic-data-migration
  - radix-tooltip
  - phosphor-icons
  - tanstack-query
  - lww-conflict
  - v13
  - fam-08

# Dependency graph
requires:
  - phase: 01-foundation
    provides: User + Group + WeeklyPlanVariant.visibility schema (D-31); auth_service.consume_invite_and_register; AppException envelope; Visibility enum
  - phase: 02-differentiators
    provides: Plan 02-04 per-day variants (8137b2e24001 head); variant_service.upsert_variant LWW; sync.conflictToast* italian copy
provides:
  - Alembic 0002_activate_groups idempotent data migration (per-user household backfill)
  - auth_service ensure_personal_group call (PITFALL #16 mitigation — no NULL group_id post-deploy)
  - get_user_with_group_access dependency (FAM-06 + FAM-07; group_id NEVER from JWT — DB re-look-up; cross-group → 404 V13)
  - Cross-user ?user_id={partner} on /api/today, /api/weekly/{w}, /api/weekly/{w}/summary, /api/shopping/{w}, /api/shopping/{w}/export-pdf
  - PATCH /api/family/share/{variant_id} (owner-only; non-owner → 404)
  - 13 family API tests + 40 authz matrix tests + 6 alembic/register tests = 59 new backend tests
  - Frontend SharedBadge (UsersThree pill + Radix tooltip) + ShareToggleMenu (DotsThreeOutline + Switch)
  - useShareToggle hook (sonner success/info/error toasts; cache invalidation)
  - copy.it.ts gains 15 family.* keys (sharedBadge*, sharePerMeal*, timeAgo*)
  - italianTimeAgo helper (1 min / N minuti / 1 ora / N ore / ieri / N giorni)
  - Phosphor facade exports UsersThree + DotsThreeOutline
  - Radix Tooltip primitive (net-new shadcn-style)
affects:
  - 02-08 (Phase 2 closure pause-gate verifier)
  - 03-pwa-shell-polish (push notifications: family share toggle hooks into Phase 3 reminders)
  - 04-admin (group merge admin tooling consumes the same get_user_with_group_access guard)

# Tech tracking
tech-stack:
  added:
    - "@radix-ui/react-tooltip ^1.2.8 (Radix Tooltip primitive)"
  patterns:
    - "Cross-user authz: re-look-up group_id from DB on every request; group_id NEVER claimed in JWT (FAM-07 lock)"
    - "404 V13 envelope for cross-group/non-owner reads + writes (info-disclosure mitigation)"
    - "Negative-authz parametrized matrix (8 endpoints × 5 scenarios = 40 tests; pytest @parametrize stack)"
    - "Idempotent Alembic data migration via reflective SQL (no app.models import); upgrade re-runs are no-op"
    - "PITFALL #16 fix: ensure_personal_group called from register flow so users.group_id never NULL post-deploy"
    - "Mutation hook + 409 handler reuse: useShareToggle inherits sync.conflictToast* italian copy from Plan 02-02"

key-files:
  created:
    - "backend/alembic/versions/0002_activate_groups.py (data-only migration; idempotent)"
    - "backend/app/services/group_service.py (ensure_personal_group helper)"
    - "backend/app/services/family_service.py (toggle_share with V13 404)"
    - "backend/app/api/family.py (PATCH /api/family/share/{variant_id})"
    - "backend/app/schemas/family.py (Pydantic v2 Literal['private','group_shared'] strict body)"
    - "backend/tests/integration/test_alembic_0002.py (4 tests: backfill / idempotent / downgrade / chain)"
    - "backend/tests/integration/test_auth_register_creates_group.py (2 tests; PITFALL #16 verify)"
    - "backend/tests/integration/test_family_api.py (13 tests: toggle / non-owner 404 / convergence)"
    - "backend/tests/integration/test_family_authz_matrix.py (40 tests: 8 endpoints × 5 scenarios)"
    - "frontend/src/components/family/SharedBadge.tsx"
    - "frontend/src/components/family/ShareToggleMenu.tsx"
    - "frontend/src/components/family/__tests__/SharedBadge.test.tsx (3 tests)"
    - "frontend/src/components/family/__tests__/ShareToggleMenu.test.tsx (4 tests)"
    - "frontend/src/components/ui/tooltip.tsx (shadcn-style Radix primitive)"
    - "frontend/src/lib/__tests__/format.italianTimeAgo.test.ts (10 tests)"
    - "frontend/src/services/family.ts (useShareToggle TanStack mutation)"
  modified:
    - "backend/app/services/auth_service.py (call ensure_personal_group post-flush in register)"
    - "backend/app/core/deps.py (+ get_user_with_group_access dependency)"
    - "backend/app/api/today.py (?user_id= cross-user with meal filter; weight + workout nulled)"
    - "backend/app/api/weekly.py (?user_id= on GET / + GET /summary; cross-user filtered totals)"
    - "backend/app/api/shopping.py (?user_id= on GET / + POST /export-pdf)"
    - "backend/app/services/today_service.py (_attach_variant_meta surfaces visibility/owner_user_id/variant_id/updated_at)"
    - "backend/app/schemas/today.py (MealEntry + visibility/owner_user_id/variant_id/updated_at fields)"
    - "backend/app/main.py (include family.router → 42 routes total)"
    - "frontend/src/components/today/MealCard.tsx (currentUserId/partnerName/weekStart props; SharedBadge + ShareToggleMenu render slots)"
    - "frontend/src/pages/Today.tsx (passes currentUserId from auth store + week_start derived from /today date)"
    - "frontend/src/components/icons/index.ts (+UsersThree, +DotsThreeOutline)"
    - "frontend/src/i18n/copy.it.ts (+15 family.* keys)"
    - "frontend/src/lib/format.ts (+italianTimeAgo helper)"
    - "frontend/src/services/today.ts (+optional visibility/owner_user_id/variant_id/updated_at on TodayMeal)"
    - "frontend/package.json + pnpm-lock.yaml (+@radix-ui/react-tooltip)"

key-decisions:
  - "(Plan 02-07) Migration filename corrected to 0002_activate_groups.py (not 0001) — Plan 02-04 already owns 0001-prefix slot via 8137b2e24001"
  - "(Plan 02-07) Down-revision targets 8137b2e24001 (Plan 02-04 head), keeping a clean linear chain baseline → 02-04 → 02-07"
  - "(Plan 02-07) Cross-user reads on /today filter meals to visibility=group_shared AND null weight_today/workout_today (CONV-14 — those are always private, never shared)"
  - "(Plan 02-07) GET /api/weekly/{w}/summary cross-user uses _summary_from_filtered helper to recompute totals from filtered days so private meals are not counted in partner kcal totals"
  - "(Plan 02-07) PATCH /api/weekly/{w}/variant + PATCH /api/shopping/{w}/check + POST /api/shopping/{w}/reset stay own-user only (no ?user_id= surface) — cross-user mutation has no API surface; matrix locks the contract for future regression detection"
  - "(Plan 02-07) family_share_patch matrix scenarios use DIFFERENT callers per row (Marta for shared/private_other, Outsider for non_family, Ex-member for ex_member) so each row asserts 'non-owner ⇒ 404'"
  - "(Plan 02-07) Radix Tooltip primitive shipped net-new (no pre-existing shadcn block) — followed dropdown-menu.tsx pattern; tokens-only (CLAUDE.md UI rule 1)"

patterns-established:
  - "Pattern: Cross-user dependency — `get_user_with_group_access(target_id, current, session)` returns own-user or partner User; raises 404 V13 otherwise; group_id re-fetched from DB every request"
  - "Pattern: Cross-user query string — endpoints expose `user_id: UUID | None = Query(None)` and swap target user via the dependency when present; response filtered to visibility=group_shared"
  - "Pattern: Idempotent data migration — reflective SQL via `sa.table()`; check 'rows where group_id IS NULL' before mutating; re-run is no-op"
  - "Pattern: PITFALL #16 mitigation — always call ensure_personal_group from auth_service.consume_invite_and_register so post-deploy users never miss the migration backfill"
  - "Pattern: Negative-authz matrix via @pytest.parametrize × 2 — endpoints param × scenarios param; expected dict per (endpoint, scenario) lock contract"
  - "Pattern: Pydantic v2 strict enum for share toggle body — `Literal['private', 'group_shared']`; invalid values surface as 422 RequestValidationError"

requirements-completed:
  - FAM-01
  - FAM-02
  - FAM-03
  - FAM-04
  - FAM-05
  - FAM-06
  - FAM-07
  - FAM-08
  - FAM-09
  - UI-01
  - UI-03
  - UI-15
  - UI-17

# Metrics
duration: 43m44s
completed: 2026-05-05
---

# Phase 2 Plan 07: Family Sync Activation Summary

**Multi-user family sync end-to-end: idempotent Group backfill, cross-user authz dependency with V13 404 envelope, 40-test negative-authz matrix, owner-only share toggle, partner-aware MealCard with Radix tooltip + Phosphor pill — Stefano sees Marta's pranzi/cene as `condiviso con Marta`, both can flip per-meal visibility, conflicts surface via named-partner toast.**

## Performance

- **Duration:** 43m44s
- **Started:** 2026-05-05T09:17:16Z
- **Completed:** 2026-05-05T10:00:58Z
- **Tasks:** 3 / 3
- **Files created:** 16 · **Files modified:** 14

## Accomplishments

- **Migration 0002_activate_groups** backfills `users.group_id` for every existing user (one `{username} · household` Group per user). Idempotent — re-running is a no-op (verified). Round-trip clean (downgrade nulls + deletes households; upgrade re-creates). Live dev DB upgraded successfully; `dev` user now linked to `dev · household`.
- **PITFALL #16 fix** — `auth_service.consume_invite_and_register` calls `ensure_personal_group(session, user)` after `session.flush()`. Verified by 2 register tests: every new user post-deploy lands in their own household; `users.group_id` never stays NULL.
- **`get_user_with_group_access`** dependency wired (V13 404 envelope; group_id NEVER from JWT — DB re-fetch every request). 5 endpoints accept `?user_id={partner}` (today / weekly / weekly summary / shopping / shopping export-pdf). Partner reads filter to `visibility=group_shared`; weight + workout nulled cross-user (CONV-14).
- **`PATCH /api/family/share/{variant_id}`** owner-only toggle. Non-owner → 404 with `not_found` code. Visibility enum locked via `Literal['private','group_shared']`; invalid → 422.
- **40-test authz matrix** — 8 endpoints × 5 scenarios. All 4 read-mutation endpoints (today / weekly / weekly summary / shopping / shopping export-pdf) return 404 for non_family + ex_member. share_toggle returns 404 for every non-owner caller (S2/S3/S4/S5). Self-write endpoints (variant patch / shopping check) lock the "no future cross-user mutation" contract.
- **13 family API tests** including FAM-09 convergence smoke (Stefano flips lunch private → Marta refetches → lunch disappears).
- **Frontend SharedBadge** — Phosphor `UsersThree` 14px pill + truncated partner name + Radix tooltip "Aggiornato da {nome} · 2 minuti fa". `aria-label="Condiviso con {nome}"` italian; tap-scale 0.97/80ms.
- **Frontend ShareToggleMenu** — `DotsThreeOutline` 44×44 button → Radix DropdownMenu → `UsersThree` + label + Switch. Optimistic state with rollback on error. Owner-only render.
- **MealCard extension** — three new optional props (`currentUserId`, `partnerName`, `weekStart`). Badge renders when `visibility==='group_shared' && owner_user_id !== currentUserId`; toggle renders when `owner_user_id === currentUserId && variant_id` set.
- **`useShareToggle`** TanStack mutation: 200 → italian success toast + invalidate `['today']` + `['weekly']` (FAM-09 ≤5s convergence with `staleTime: 30_000` + `refetchOnFocus: true` already in `useToday`); 409 → named-partner info toast (reuses `sync.conflictToast*` from Plan 02-02); other errors → italian `sharePerMealError`.
- **`copy.it.ts`** gains 15 family.* keys verbatim per UI-SPEC §7.1: `sharedBadgeLabel/Aria/TooltipFormat`, `sharePerMealMenuAria/ToggleLabel/OnSuccess/OffSuccess/Error`, `timeAgoJustNow/Minutes/MinutesSingular/Hours/HoursSingular/Yesterday/Days`.
- **`italianTimeAgo`** helper covers all 7 buckets (adesso / 1 minuto / N minuti / 1 ora / N ore / ieri / N giorni); 10 unit tests including singular vs plural agreement and clock-skew (future timestamp → `adesso`).
- **Phosphor facade** gains `UsersThree` + `DotsThreeOutline` — preserves the CLAUDE.md grep gate "icons via @/components/icons facade only".
- **Radix Tooltip primitive** shipped net-new in `frontend/src/components/ui/tooltip.tsx` — pattern matches existing shadcn dropdown-menu.tsx; tokens-only.

## Task Commits

1. **Task 1: Alembic 0002_activate_groups + auth register auto-creates household + idempotence tests** — `9267884` (feat)
2. **Task 2: get_user_with_group_access dep + cross-user wiring + family share endpoint + 40-test authz matrix** — `26d21ca` (feat)
3. **Task 3: SharedBadge + ShareToggleMenu + MealCard extension + family.* copy + italianTimeAgo** — `1be1a58` (feat)

## Files Created/Modified

### Backend (created)

- `backend/alembic/versions/0002_activate_groups.py` — Idempotent data migration; per-user `{username} · household` Group; reflective SQL (no app.models import).
- `backend/app/services/group_service.py` — `ensure_personal_group(session, user)` helper.
- `backend/app/services/family_service.py` — `toggle_share(session, user, variant_id, visibility)` with V13 404 envelope on non-owner.
- `backend/app/schemas/family.py` — Pydantic v2 `Literal['private','group_shared']` body + response.
- `backend/app/api/family.py` — `PATCH /api/family/share/{variant_id}` router.
- `backend/tests/integration/test_alembic_0002.py` (4 tests).
- `backend/tests/integration/test_auth_register_creates_group.py` (2 tests).
- `backend/tests/integration/test_family_api.py` (13 tests including convergence smoke).
- `backend/tests/integration/test_family_authz_matrix.py` (40 parametrized tests).

### Backend (modified)

- `backend/app/services/auth_service.py` — register flow now calls `ensure_personal_group` post-flush.
- `backend/app/core/deps.py` — `get_user_with_group_access(target_user_id, current_user, session)` added; group_id re-look-up + V13 404.
- `backend/app/api/today.py` — `?user_id=` accepted; cross-user filter (visibility=group_shared); weight_today/workout_today nulled cross-user.
- `backend/app/api/weekly.py` — `?user_id=` accepted on GET + GET /summary; `_summary_from_filtered` recomputes totals from filtered days.
- `backend/app/api/shopping.py` — `?user_id=` accepted on GET + POST /export-pdf.
- `backend/app/services/today_service.py` — `_attach_variant_meta` surfaces visibility/owner_user_id/variant_id/updated_at on every MealEntry.
- `backend/app/schemas/today.py` — `MealEntry` gains those 4 optional fields.
- `backend/app/main.py` — family router included → **42 routes total**.

### Frontend (created)

- `frontend/src/components/family/SharedBadge.tsx`
- `frontend/src/components/family/ShareToggleMenu.tsx`
- `frontend/src/components/family/__tests__/SharedBadge.test.tsx` (3 tests)
- `frontend/src/components/family/__tests__/ShareToggleMenu.test.tsx` (4 tests; uses `userEvent.setup()` for Radix DropdownMenu pointer events)
- `frontend/src/components/ui/tooltip.tsx` (Radix primitive, shadcn-style)
- `frontend/src/lib/__tests__/format.italianTimeAgo.test.ts` (10 tests)
- `frontend/src/services/family.ts` (useShareToggle TanStack mutation)

### Frontend (modified)

- `frontend/src/components/today/MealCard.tsx` — currentUserId/partnerName/weekStart props; SharedBadge in slot caption row, ShareToggleMenu before check button.
- `frontend/src/pages/Today.tsx` — passes currentUserId from auth store + weekStart derived from /today date.
- `frontend/src/components/icons/index.ts` — +UsersThree, +DotsThreeOutline.
- `frontend/src/i18n/copy.it.ts` — +15 family.* keys.
- `frontend/src/lib/format.ts` — +italianTimeAgo helper.
- `frontend/src/services/today.ts` — +visibility/owner_user_id/variant_id/updated_at optional fields on TodayMeal.
- `frontend/package.json` + `pnpm-lock.yaml` — +@radix-ui/react-tooltip ^1.2.8.

## Decisions Made

- **Migration filename correction (Deviation #1):** Plan frontmatter specified `0001_activate_groups.py`, but Plan 02-04 already created `0001_weekly_variant_per_day.py` (revision `8137b2e24001`). The migration was renamed to `0002_activate_groups.py` with `down_revision = "8137b2e24001"` so the chain stays linear: baseline → 02-04 → 02-07. Verified by `alembic upgrade head` + downgrade -1 + upgrade head round trip + re-run idempotency.
- **Cross-user weight + workout hidden (CONV-14):** today_service surfaces weight + workout from the partner's row; the API explicitly nulls them on cross-user response. Weight + workout are listed as "always private" in CONV-14 — the partner has no business reading them.
- **/weekly/{w}/summary recomputes totals from filtered days:** Without this, partner's private meals would still count toward kcal totals shown to the caller. The new `_summary_from_filtered` helper aggregates from the already-filtered `payload['days']`.
- **Own-only mutations (variant patch / shopping check / shopping reset) stay own-only:** No `?user_id=` surface added — by construction these mutations only ever target the authenticated user's row. The matrix locks the contract so a future regression that adds cross-user mutation MUST be denied with 404.
- **`family_share_patch` matrix uses different callers per scenario:** Each row tests a different non-owner attempting to mutate Stefano's variant — Marta (shared/private_other), Outsider (non_family), Ex-member (ex_member). Stefano stays the owner who succeeds in S1.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Migration filename collision with Plan 02-04**

- **Found during:** Task 1 setup (load existing alembic versions)
- **Issue:** Plan 02-07 frontmatter listed `backend/alembic/versions/0001_activate_groups.py`. Plan 02-04 already shipped `0001_weekly_variant_per_day.py` (revision `8137b2e24001`). Creating a second `0001_*` file would collide on disk; using `revision = "0001"` would clash with Plan 02-04's revision and break the chain.
- **Fix:** Renamed migration file to `0002_activate_groups.py`, set `revision = "0002"` and `down_revision = "8137b2e24001"`. Updated all references in tests + acceptance criteria.
- **Files modified:** `backend/alembic/versions/0002_activate_groups.py`, `backend/tests/integration/test_alembic_0002.py`.
- **Verification:** `alembic current` → `0002 (head)`; `alembic upgrade head` no-op on second run; `alembic downgrade -1` → `8137b2e24001`; `alembic upgrade head` → `0002`. All 4 test_alembic_0002 tests green.
- **Committed in:** `9267884` (Task 1).

**2. [Rule 2 - Missing Critical] today_service did not surface visibility / owner_user_id / variant_id**

- **Found during:** Task 2 wiring of `?user_id=` filter on `/api/today`.
- **Issue:** The plan acceptance criterion required filtering meals by `visibility === 'group_shared'`. But `today_service.build_today_payload` only returned `MealEntry` rows from the parsed plan with no visibility annotation. Without surfacing `visibility`, `owner_user_id`, `variant_id`, `updated_at` on every entry, the cross-user filter had nothing to filter by, the SharedBadge couldn't tell owner from partner, and the ShareToggleMenu had no variant id to PATCH.
- **Fix:** Added 4 optional fields to `MealEntry` schema; added `_attach_variant_meta` helper that fills them from `variant_by_meal[meal_type]` (or default visibility per `_default_visibility_for(meal_type)` when no variant exists yet). Mirrored fields on the frontend `TodayMeal` interface.
- **Files modified:** `backend/app/schemas/today.py`, `backend/app/services/today_service.py`, `frontend/src/services/today.ts`.
- **Verification:** All today API tests still green (no regression); cross-user `?user_id=` filter has data to operate on; FAM-09 convergence test verifies (Marta's view drops the lunch when Stefano flips it private).
- **Committed in:** `26d21ca` (Task 2).

**3. [Rule 3 - Blocking] Radix Tooltip primitive missing**

- **Found during:** Task 3 SharedBadge component — needed `Tooltip + TooltipProvider + TooltipTrigger + TooltipContent`.
- **Issue:** `@radix-ui/react-tooltip` was not in `frontend/package.json`; `frontend/src/components/ui/tooltip.tsx` did not exist (Plan 02-05 added DropdownMenu primitives but no tooltip). Without it the SharedBadge had no place to render the "Aggiornato da {nome} · 2 minuti fa" tooltip text.
- **Fix:** `pnpm add @radix-ui/react-tooltip` (^1.2.8) + created `frontend/src/components/ui/tooltip.tsx` matching the existing shadcn dropdown-menu.tsx style (tokens-only, CLAUDE.md UI rule 1).
- **Files modified:** `frontend/package.json`, `pnpm-lock.yaml`, `frontend/src/components/ui/tooltip.tsx` (new).
- **Verification:** `pnpm tsc --noEmit` clean; `pnpm lint` clean; SharedBadge tests render without errors.
- **Committed in:** `1be1a58` (Task 3).

---

**Total deviations:** 3 auto-fixed (1 bug, 1 missing critical, 1 blocking).
**Impact on plan:** All three were necessary for plan correctness. Migration filename was a hard prerequisite (collision); visibility surfacing was the data the cross-user filter operates on; tooltip primitive was a hard dependency of the SharedBadge anatomy. No scope creep.

## Issues Encountered

- **JSDOM + Radix DropdownMenu pointer events** — initial ShareToggleMenu test used `fireEvent.click(trigger)`, which doesn't open the dropdown because Radix listens to pointer events. Switched to `userEvent.setup()` (already used by `VariantSelector.test.tsx` + `WorkoutForm.test.tsx`) and the menu opens correctly. All 4 tests green.
- **Test fixture day_of_week alignment** — first version of `family_world` fixture seeded variants for `day_of_week=0` (Monday matching `week_start`). Real `today_service` queries variants for `today's day_of_week` in the user's IANA tz, which on `2026-05-05` is Tuesday (dow=1). Fixed by deriving `day_of_week` at fixture build time via `datetime.now(ZoneInfo("Europe/Rome")).weekday()`. Convergence test now correctly observes the partner's flip.

## User Setup Required

None — the migration self-applies on next deploy via `alembic upgrade head`. Production deploy checklist:

- [ ] Backup PostgreSQL `WellnessBuddy` DB before applying migration (Phase 2 first data-only migration; downgrade IS destructive).
- [ ] Run `cd backend && uv run alembic upgrade head` on production server.
- [ ] Verify `SELECT count(*) FROM users WHERE group_id IS NULL` returns 0.
- [ ] Verify `SELECT count(*) FROM groups WHERE name LIKE '% · household'` matches user count.

## Threat Surface Scan

No new threat surface beyond what Plan 02-07 explicitly mitigates in `<threat_model>` (T-02-07-01..10). The 40-test matrix locks all 10 STRIDE entries.

## Live Test Results

Backend live calls were not executed (dev backend not running on `:8002` at execution time). All endpoint contracts validated via the comprehensive 366-test pytest suite, including:

- Migration round-trip: `alembic upgrade head` (0002 head) → `downgrade -1` (back to 8137b2e24001) → `upgrade head` (0002 head) — all green.
- Idempotency: re-running `alembic upgrade head` after head produces no SQL output (verified manually).
- 40-test matrix S1..S5 per endpoint: all green (test_family_authz_matrix.py).
- 13 family API tests including `test_today_with_outsider_user_id_returns_404` (404 not 403), `test_today_with_unknown_user_id_returns_404`, `test_share_toggle_non_owner_returns_404`, FAM-09 convergence.
- Live dev DB: `dev` user backfilled to `dev · household` group post-upgrade.

## Test Counts

| Surface  | Before                        | After                                 | Delta      |
| -------- | ----------------------------- | ------------------------------------- | ---------- |
| Backend  | 307                           | 366                                   | +59 (+19%) |
| Frontend | ~120 (3 pre-existing failing) | 137 (3 pre-existing failing — same 3) | +17 (+14%) |

**Backend breakdown:** 4 alembic + 2 register + 13 family API + 40 matrix = 59 new tests.
**Frontend breakdown:** 10 italianTimeAgo + 3 SharedBadge + 4 ShareToggleMenu = 17 new tests.

## Next Phase Readiness

- **Plan 02-08 (Phase 2 closure):** Family sync surface ready for the closure pause-gate verifier. iPhone smoke test of SharedBadge + ShareToggleMenu deferred to Wave 8 per execution prompt — visual baselines NOT regenerated this run.
- **Phase 4 admin:** `get_user_with_group_access` dependency is the canonical pattern for admin-side cross-user reads with group authz; admin merge-gruppi and ex-member move tooling can reuse the helper.
- **Phase 3 push notifications:** PATCH /api/family/share/{variant_id} bumps `version` so the LWW + 409 toast continues to work for cross-user concurrent edits when push reminders land. PITFALL #18 (silent loss when both partners edit same second) handled by the named-partner info toast (already shipped Plan 02-02).
- **Pre-existing frontend failures unchanged:** PlanDiffView ×2 + WorkoutForm ×1 vitest failures + 3 PlanDiffView TS errors — all explicitly out of scope per execution prompt.

---

## Self-Check: PASSED

- `backend/alembic/versions/0002_activate_groups.py` ✓
- `backend/app/services/group_service.py` ✓
- `backend/app/services/family_service.py` ✓
- `backend/app/api/family.py` ✓
- `backend/tests/integration/test_family_authz_matrix.py` ✓
- `frontend/src/components/family/SharedBadge.tsx` ✓
- `frontend/src/components/family/ShareToggleMenu.tsx` ✓
- `frontend/src/services/family.ts` ✓
- `frontend/src/components/ui/tooltip.tsx` ✓
- Commit `9267884` (Task 1) ✓
- Commit `26d21ca` (Task 2) ✓
- Commit `1be1a58` (Task 3) ✓

---

*Phase: 02-differentiators*
*Completed: 2026-05-05*
