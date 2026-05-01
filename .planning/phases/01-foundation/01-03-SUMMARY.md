---
phase: 01-foundation
plan: 03
subsystem: auth
tags: [jwt, refresh-rotation, family-revocation, grace-window, invite, persist-storage]
requires:
  - 01-02a (User model, RefreshToken model, InviteToken model, AppException, security primitives)
  - 01-02b (auth router stub + DI scaffolding)
  - 01-05a (shadcn Button/Input/Card/Label/Form primitives, Tailwind 4 tokens)
  - 01-05b (i18n copy.it.ts, Zustand store stubs, vitest infra)
  - 01-06 (forward-compat stubs for auth/api/persistStorage — replaced here with real impls)
provides:
  - real JWT auth (15min access + 7d HttpOnly refresh, rotation, family revocation, 10s grace)
  - invite-only signup (24h single-use revocable tokens, AUTH-09/10)
  - frontend singleton refresh promise coalescing concurrent 401s (AUTH-07, PITFALLS#4)
  - Italian-only Login + Register pages
  - PersistStorageWelcome (D-15, FND-08)
  - test infrastructure: TRUNCATE-based test isolation + greenlet-aware coverage
affects:
  - backend/app/api/auth.py (replaced 02b 501 stubs)
  - backend/app/core/deps.py (replaced 02a stub get_current_user with real impl)
  - backend/tests/integration/test_ai_api.py (501→401 after auth wired)
  - backend/tests/integration/test_stub_endpoints.py (login stub now 422 validation envelope)
  - frontend/src/{services/api.ts,stores/auth.ts,lib/persistStorage.ts} (Plan 06 stubs replaced)
tech-stack:
  added:
    - freezegun (backend dev) — time-travel for grace-window tests
  patterns:
    - JWT refresh rotation with 10s idempotent grace window cached via row.cached_access/cached_refresh
    - Family revocation on reuse-outside-grace (UPDATE refresh_tokens SET revoked=true WHERE family_id = X)
    - Singleton in-flight Promise pattern for client-side refresh coalescing (resets via setTimeout(0) on settle)
    - HttpOnly + Secure + SameSite=Lax cookie scoped to /api/auth path
key-files:
  created:
    - backend/app/services/auth_service.py
    - backend/tests/integration/test_auth.py
    - backend/tests/integration/test_invite.py
    - frontend/src/lib/refreshTokenAtomic.ts
    - frontend/src/services/auth.ts
    - frontend/src/components/auth/LoginForm.tsx
    - frontend/src/components/auth/InviteSignupForm.tsx
    - frontend/src/tests/unit/refreshTokenAtomic.test.ts
    - frontend/src/tests/unit/auth.test.ts
    - docker-compose.override.yml (port 5434 to avoid 5432 conflict on dev box)
  modified:
    - backend/app/api/auth.py (501 stubs → real endpoints)
    - backend/app/core/deps.py (real get_current_user + require_admin)
    - backend/app/schemas/auth.py + invite.py (real shapes)
    - backend/pyproject.toml (bcrypt<4.1 pin, freezegun, greenlet coverage)
    - backend/tests/conftest.py (TRUNCATE-based isolation, ADMIN_EMAIL changed to test.example.com)
    - backend/tests/integration/test_ai_api.py + test_stub_endpoints.py (post-auth-wiring expectations)
    - frontend/src/services/api.ts (real client with 401 → singleton refresh → retry)
    - frontend/src/stores/auth.ts (real store with user + clear, back-compat with Plan 06 stub)
    - frontend/src/lib/persistStorage.ts (sonner toast on denial)
    - frontend/src/components/auth/PersistStorageWelcome.tsx (real welcome card)
    - frontend/src/pages/Login.tsx + Register.tsx (real form wrappers)
decisions:
  - Use docker-compose.override.yml to map WB postgres to port 5434 (mantis-postgres holds 5432); zero impact on production wiring
  - Pin bcrypt<4.1 because passlib 1.7.4 reads bcrypt.__about__ which was removed in 4.1+
  - Keep frontend store dual-API: setAccessToken accepts (string|null) for Plan 06 callers; clear() for Plan 03 spec; clearAccessToken() retained as deprecated alias
  - Test emails use *.example.com TLDs because email-validator rejects .local as special-use
  - Grace-window service-side, not middleware-side: simpler reasoning, single source of truth in auth_service.rotate_refresh
  - Welcome heading "Benvenuto in Wellness Buddy" not yet routed through copy.it.ts (no welcome namespace yet) — scope-bounded; copy.it.ts owned by Plan 05b
metrics:
  duration: ~20 min
  completed: 2026-05-01T17:23Z
---

# Phase 1 Plan 03: Auth System Summary

JWT auth with 15min access tokens, 7d refresh-cookie rotation, 10s idempotent grace window, family revocation on reuse, plus invite-gated signup — backend ships in 1 service module + 1 router + real `get_current_user`, frontend ships singleton refresh-coalescer + Zustand store + Italian-only Login/Register pages + PersistStorageWelcome.

## Truths Verified

- User can login with email + password and receives access token in body + HttpOnly refresh cookie scoped to `/api/auth`
- Access token expires in 15 minutes; refresh token expires in 7 days
- Refresh rotation issues new pair; reuse of revoked token within 10s grace returns cached pair (idempotent — `test_refresh_grace_window_returns_cached_pair`)
- Refresh reuse outside grace revokes entire family (`test_refresh_reuse_outside_grace_revokes_family`)
- Logout revokes the refresh family server-side (`test_logout_revokes_family`)
- `GET /api/auth/me` returns user profile when access token is valid (`test_me_returns_profile`)
- Admin can `POST /api/auth/invite` to generate single-use 24h-expiry token (`test_invite_create_admin_succeeds`)
- Invite-only signup: `POST /api/auth/register` requires valid token (4 separate tests for valid/expired/revoked/reused)
- Frontend singleton refresh promise coalesces 5 concurrent calls into 1 fetch (`refreshTokenAtomic.test.ts: coalesces 5 concurrent calls`)
- All auth API errors return JSON `{detail: string, code: string}` envelope (AUTH-12)
- Post-login welcome screen calls `navigator.storage.persist()` (FND-08, D-15)

## Test Counts

| Suite | Tests | Status |
|-------|-------|--------|
| backend `test_auth.py`   | 12 | all green |
| backend `test_invite.py` | 7  | all green |
| frontend `refreshTokenAtomic.test.ts` | 3 | all green (coalescing, clear-on-fail, reset-after-settle) |
| frontend `auth.test.ts` | 5 | all green (store set/clear, store user, persistStorage already-persisted/denied/granted) |
| backend total (full suite) | 56 | all green |
| frontend total (full suite) | 18 | all green |

## Coverage

| Module | Stmts | Cover | Notes |
|--------|-------|-------|-------|
| `app/api/auth.py`            | 58  | **100%** | every endpoint hit by tests |
| `app/services/auth_service.py` | 107 | **93%**  | misses are 3 defensive branches (jwt decode error, missing-row guard, audit_id flush already-set) |
| **Combined**                 | 165 | **96%**  | gate ≥80% |

## Manual Verification

Pending Phase 1 pause gate (real iPhone resume + 16min wait + offline /today). Plans 04-08 must land first to enable the end-to-end flow.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] passlib 1.7.4 + bcrypt 5.0.0 incompatible**
- **Found during:** Task 1 RED → first run
- **Issue:** `passlib.handlers.bcrypt._load_backend_mixin` reads `_bcrypt.__about__.__version__`, which bcrypt 4.1+ removed; this caused passlib to mis-detect the password length and raise `ValueError: password cannot be longer than 72 bytes`.
- **Fix:** Pin `bcrypt<4.1` in pyproject.toml. The hash format is identical, no migration needed.
- **Files modified:** `backend/pyproject.toml`, `backend/uv.lock`
- **Commit:** `aec53fc`

**2. [Rule 3 - Blocking] Local docker-compose port 5432 collision**
- **Found during:** Task 1 RED → conftest tried to connect
- **Issue:** Port 5432 is occupied by another project's container (`mantis-postgres`); WB's `docker-compose.yml` mapped 5432:5432 unconditionally.
- **Fix:** Add `docker-compose.override.yml` mapping 5434:5432 for WB only. Document via `DATABASE_URL` env override in test commands.
- **Files modified:** `docker-compose.override.yml` (new)
- **Commit:** `aec53fc`

**3. [Rule 1 - Bug] EmailStr rejects `.local` TLD**
- **Found during:** Task 1 GREEN → first run after impl
- **Issue:** `email-validator` (transitive dep of pydantic[email]) rejects `*.local` and other special-use TLDs, returning 422 instead of 200 for tests using `user@test.local`.
- **Fix:** Migrate test fixtures to `*@test.example.com` (the IANA-reserved example TLD).
- **Files modified:** `backend/tests/integration/test_auth.py`, `backend/tests/integration/test_invite.py`, `backend/tests/conftest.py` (ADMIN_EMAIL default)
- **Commit:** `fb3c6be`

**4. [Rule 1 - Bug] Test fixture isolation broken**
- **Found during:** Task 1 GREEN → second test (test_login_invalid_creds_returns_envelope) saw a duplicate-key error
- **Issue:** `db_session` fixture only does `rollback()` AFTER the test runs. Tests that COMMIT (seeding via fixtures) had their committed rows persist into the next test, breaking unique constraints.
- **Fix:** Add a `_truncate_all` helper that runs `TRUNCATE ... RESTART IDENTITY CASCADE` BEFORE each `db_session` yield. Lists the 10 mutable tables explicitly.
- **Files modified:** `backend/tests/conftest.py`
- **Commit:** `fb3c6be`

**5. [Rule 1 - Bug] Coverage tool reports 0% on lines that actually run**
- **Found during:** Task 1 GREEN → coverage report
- **Issue:** SQLAlchemy 2 async runs DB IO inside greenlets; coverage's default thread-only tracking misses lines executed under the greenlet bridge.
- **Fix:** Add `concurrency = ["thread", "greenlet"]` to `[tool.coverage.run]`. Coverage jumped 51% → 93% on `auth_service.py` with no test changes.
- **Files modified:** `backend/pyproject.toml`
- **Commit:** `fb3c6be`

**6. [Rule 1 - Bug] test_ai_api + test_stub_endpoints assumed 501 stubs**
- **Found during:** Task 1 full-suite verification
- **Issue:** Plans 02b's tests asserted that `/api/ai/*` and `/api/auth/login` returned 501. After Plan 03 wired real auth, those endpoints either gate on `Depends(get_current_user)` (now 401) or accept JSON validation (now 422 on empty body).
- **Fix:** Update assertions to match the new reality and rename test functions to be self-describing.
- **Files modified:** `backend/tests/integration/test_ai_api.py`, `backend/tests/integration/test_stub_endpoints.py`
- **Commit:** `fb3c6be`

### Architectural Deviations

None requested. Plan executed within scope.

## Threat Surface Status

All Plan 03 threats from `<threat_model>` have a verifying test or defensive code path:

| Threat | Mitigation | Verification |
|--------|------------|--------------|
| T-AUTH-01 (JWT forging)              | python-jose HS256 + SECRET_KEY≥32 chars + decode_token raises on tamper | `test_me_with_garbage_token_returns_envelope` |
| T-AUTH-02 (refresh storm)             | server 10s grace + client singleton promise | `test_refresh_grace_window_returns_cached_pair` + `coalesces 5 concurrent calls into a single fetch` |
| T-AUTH-03 (refresh reuse beyond grace) | family revocation in `rotate_refresh` | `test_refresh_reuse_outside_grace_revokes_family` |
| T-AUTH-04 (logout doesn't invalidate) | `revoke_family` on /logout | `test_logout_revokes_family` |
| T-AUTH-05 (login enumeration)         | identical envelope for unknown email vs wrong pwd | `test_login_unknown_email_same_envelope` |
| T-AUTH-06 (invite brute force)        | 256-bit token + 24h expiry + single-use + revocable | `test_register_expired/revoked/reuse/unknown` (4 tests) |
| T-AUTH-07 (iPhone resume DoS)         | server grace + client singleton (above) + manual gate | scheduled for Phase 1 pause gate |

## Auth Gates Encountered

None — Plan 03 did not require any external authentication or human-action checkpoints.

## Self-Check: PASSED

**Files exist (verified via filesystem):**
- backend/app/services/auth_service.py — FOUND
- backend/app/api/auth.py — FOUND
- backend/app/core/deps.py — FOUND
- backend/tests/integration/test_auth.py — FOUND
- backend/tests/integration/test_invite.py — FOUND
- frontend/src/lib/refreshTokenAtomic.ts — FOUND
- frontend/src/services/api.ts — FOUND
- frontend/src/services/auth.ts — FOUND
- frontend/src/stores/auth.ts — FOUND
- frontend/src/components/auth/LoginForm.tsx — FOUND
- frontend/src/components/auth/InviteSignupForm.tsx — FOUND
- frontend/src/components/auth/PersistStorageWelcome.tsx — FOUND
- frontend/src/pages/Login.tsx — FOUND
- frontend/src/pages/Register.tsx — FOUND
- frontend/src/tests/unit/refreshTokenAtomic.test.ts — FOUND
- frontend/src/tests/unit/auth.test.ts — FOUND
- docker-compose.override.yml — FOUND

**Commits exist (verified via git log):**
- aec53fc — RED tests + dep pins + docker override — FOUND
- fb3c6be — backend auth GREEN — FOUND
- 5c9a023 — frontend RED tests — FOUND
- 17966f4 — frontend auth GREEN — FOUND

**Verification commands:**
- backend: `cd backend && DATABASE_URL=... uv run pytest tests/integration/test_auth.py tests/integration/test_invite.py` — exits 0 (19/19)
- backend coverage: `--cov=app.services.auth_service --cov=app.api.auth` — 96% combined
- frontend: `cd frontend && pnpm vitest run src/tests/unit/refreshTokenAtomic.test.ts src/tests/unit/auth.test.ts` — exits 0 (8/8)
- frontend typecheck: `pnpm typecheck` — exits 0
- frontend lint: `pnpm lint --max-warnings=0` — exits 0
- requestPersistentStorage export: `grep -q 'export async function requestPersistentStorage' frontend/src/lib/persistStorage.ts` — match
- no hex in auth components: `grep -E '#[0-9a-fA-F]{3,8}' frontend/src/components/auth/* frontend/src/pages/{Login,Register}.tsx` — 0 matches
