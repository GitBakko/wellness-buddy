// frontend/src/lib/refreshTokenAtomic.ts
// AUTH-07, PITFALLS#4 — singleton refresh promise.
//
// Why this exists: when the access token expires (or the device wakes from
// background — iPhone resume), N parallel requests can each receive a 401 at
// nearly the same instant. Without coalescing, each tries to POST /api/auth/refresh
// with the SAME old refresh cookie. The server's 10s grace window handles the
// idempotency on the backend, but the network storm is wasteful (and exposes
// race-condition surface). Solution: cache the in-flight Promise and have all
// concurrent callers `await` the same one.
//
// Reset timing: the cached promise is cleared via `setTimeout(0)` after the
// fetch settles, so the NEXT batch of 401s gets a fresh fetch. We don't want
// to hold the cache forever — that would prevent legitimate re-refreshes
// later in the session.
//
// Source: 01-RESEARCH.md Pattern 9, PITFALLS.md#4 (iPhone resume logout storm).

import { useAuthStore } from '@/stores/auth';

let inflightRefresh: Promise<string> | null = null;

export function refreshTokenAtomic(): Promise<string> {
  if (inflightRefresh) return inflightRefresh;
  inflightRefresh = (async () => {
    try {
      const res = await fetch('/api/auth/refresh', {
        method: 'POST',
        credentials: 'include',
      });
      if (!res.ok) {
        // 401 / family_revoked / no_refresh_cookie → drop session client-side
        useAuthStore.getState().clear();
        throw new Error('refresh_failed');
      }
      const data = (await res.json()) as { access_token: string };
      useAuthStore.getState().setAccessToken(data.access_token);
      return data.access_token;
    } finally {
      // Reset on the next tick so concurrent awaiters of THIS promise still
      // see it (synchronous), but a brand-new batch of 401s lands a fresh fetch.
      setTimeout(() => {
        inflightRefresh = null;
      }, 0);
    }
  })();
  return inflightRefresh;
}

/** Test-only: reset the singleton between Vitest runs. */
export function __resetRefreshAtomic(): void {
  inflightRefresh = null;
}
