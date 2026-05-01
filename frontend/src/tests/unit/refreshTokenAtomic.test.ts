// AUTH-07, PITFALLS#4 — singleton refresh promise behavior under concurrent 401 race.
//
// These tests assert that:
//   1. Five concurrent calls to refreshTokenAtomic() coalesce to a single fetch.
//   2. On refresh failure (401 from /api/auth/refresh), the auth store is cleared.
//   3. After settle, the cached promise resets so a NEW batch hits a fresh fetch.
//
// Source: 01-RESEARCH.md Pattern 9 (frontend section), Plan 01-03 <behavior>.

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import {
  __resetRefreshAtomic,
  refreshTokenAtomic,
} from '@/lib/refreshTokenAtomic';
import { useAuthStore } from '@/stores/auth';

describe('refreshTokenAtomic — singleton coalescing (AUTH-07, PITFALLS#4)', () => {
  beforeEach(() => {
    __resetRefreshAtomic();
    useAuthStore.setState({ accessToken: null, user: null });
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it('coalesces 5 concurrent calls into a single fetch', async () => {
    const fetchSpy = vi.fn(
      async () =>
        new Response(JSON.stringify({ access_token: 'new-token' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
    );
    vi.stubGlobal('fetch', fetchSpy);

    const results = await Promise.all([
      refreshTokenAtomic(),
      refreshTokenAtomic(),
      refreshTokenAtomic(),
      refreshTokenAtomic(),
      refreshTokenAtomic(),
    ]);

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/auth/refresh',
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
      }),
    );
    expect(results.every((t) => t === 'new-token')).toBe(true);
    expect(useAuthStore.getState().accessToken).toBe('new-token');
  });

  it('clears the auth store when refresh returns non-200', async () => {
    useAuthStore.setState({ accessToken: 'old-token' });
    const fetchSpy = vi.fn(
      async () => new Response('{"detail":"...","code":"family_revoked"}', { status: 401 }),
    );
    vi.stubGlobal('fetch', fetchSpy);

    await expect(refreshTokenAtomic()).rejects.toThrow();
    expect(useAuthStore.getState().accessToken).toBeNull();
  });

  it('resets after settle so a subsequent batch fetches fresh', async () => {
    const fetchSpy = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ access_token: 't1' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ access_token: 't2' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
      );
    vi.stubGlobal('fetch', fetchSpy);

    const t1 = await refreshTokenAtomic();
    expect(t1).toBe('t1');
    // Allow the setTimeout(0) microtask to flip inflightRefresh back to null
    await new Promise((r) => setTimeout(r, 5));
    const t2 = await refreshTokenAtomic();

    expect(fetchSpy).toHaveBeenCalledTimes(2);
    expect(t2).toBe('t2');
  });
});
