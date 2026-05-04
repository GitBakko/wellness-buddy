# Deferred items — Phase 02 (discovered during 02-04 execution)

Out-of-scope discoveries logged per gsd-executor SCOPE BOUNDARY rule. Do NOT
fix as part of 02-04. Track here for follow-up plans.

## 2026-05-04 (Plan 02-04 execution)

### Pre-existing frontend test failures (uncommitted in-flight modifications)

Three test failures present BEFORE Plan 02-04 started — confirmed via `git stash`
+ test re-run showing the same failures on the prior commit (b97cbc1 + earlier):

1. **`src/components/__tests__/WorkoutForm.test.tsx`** — "uses italian toggle label
   (Hai allenato oggi?)". Test expects `^Hai allenato/`; copy.it.ts contains
   `Ti sei allenato oggi?`. Either the test was authored against an older copy
   string or the copy was recently changed without updating the test. Fix in a
   follow-up `fix(...)` commit (one-line copy update or test update — reviewer
   chooses canonical wording).

2. **`src/tests/unit/plans/PlanDiffView.test.tsx`** — two assertions reference
   `copy.plans.diffAddedHeading` / `diffRemovedHeading` / `diffChangedHeading`.
   The component or the copy keys may have been refactored leaving the tests
   stale. Fix in a follow-up commit aligning test fixture to current component
   markup.

These do NOT block Plan 02-04 commits because:
- They are not regressions from 02-04 changes.
- 02-04's WIN REQUISITE is grid parser + per-day variants — neither touches
  WorkoutForm copy or PlanDiffView markup.

**Recommendation:** open issue / mini-plan to triage all three (~30 min).
