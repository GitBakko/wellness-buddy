// Unit tests for Plan 01-03 frontend auth surface:
//   - Zustand auth store (accessToken in memory, user profile, clear)
//   - persistStorage helper (FND-08, D-15)
//
// Source: AUTH-04, FND-08, RESEARCH Pattern 9 frontend section.

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { requestPersistentStorage } from '@/lib/persistStorage';
import { useAuthStore } from '@/stores/auth';

describe('useAuthStore (AUTH-04)', () => {
  beforeEach(() => {
    useAuthStore.setState({ accessToken: null, user: null });
  });

  it('sets and clears the access token', () => {
    useAuthStore.getState().setAccessToken('abc');
    expect(useAuthStore.getState().accessToken).toBe('abc');
    useAuthStore.getState().clear();
    expect(useAuthStore.getState().accessToken).toBeNull();
    expect(useAuthStore.getState().user).toBeNull();
  });

  it('stores the authenticated user profile', () => {
    useAuthStore.getState().setUser({
      id: 'u1',
      email: 'a@example.com',
      username: 'alice',
      role: 'user',
      group_id: null,
      timezone: 'Europe/Rome',
    });
    expect(useAuthStore.getState().user?.email).toBe('a@example.com');
  });
});

describe('requestPersistentStorage (FND-08, D-15)', () => {
  let originalStorage: StorageManager | undefined;

  beforeEach(() => {
    originalStorage = (navigator as Navigator & { storage?: StorageManager }).storage;
  });

  afterEach(() => {
    Object.defineProperty(navigator, 'storage', {
      configurable: true,
      writable: true,
      value: originalStorage,
    });
    vi.restoreAllMocks();
  });

  function setStorage(impl: Partial<StorageManager>): void {
    Object.defineProperty(navigator, 'storage', {
      configurable: true,
      writable: true,
      value: impl,
    });
  }

  it('returns true when storage is already persisted (no persist() call)', async () => {
    const persistSpy = vi.fn().mockResolvedValue(true);
    const persistedSpy = vi.fn().mockResolvedValue(true);
    setStorage({ persist: persistSpy, persisted: persistedSpy });

    const granted = await requestPersistentStorage();

    expect(granted).toBe(true);
    expect(persistSpy).not.toHaveBeenCalled();
    expect(persistedSpy).toHaveBeenCalled();
  });

  it('returns false when persist is denied', async () => {
    const persistSpy = vi.fn().mockResolvedValue(false);
    const persistedSpy = vi.fn().mockResolvedValue(false);
    setStorage({ persist: persistSpy, persisted: persistedSpy });

    const granted = await requestPersistentStorage();

    expect(granted).toBe(false);
    expect(persistSpy).toHaveBeenCalled();
  });

  it('returns true when persist is granted', async () => {
    const persistSpy = vi.fn().mockResolvedValue(true);
    const persistedSpy = vi.fn().mockResolvedValue(false);
    setStorage({ persist: persistSpy, persisted: persistedSpy });

    const granted = await requestPersistentStorage();

    expect(granted).toBe(true);
    expect(persistSpy).toHaveBeenCalled();
  });
});
