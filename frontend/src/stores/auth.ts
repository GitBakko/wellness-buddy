// frontend/src/stores/auth.ts
// AUTH-04 — access token in memory only (Zustand). Refresh in HttpOnly cookie (server).
//
// Plan 03 owner. Compatible with Plan 06's stub surface:
//   - setAccessToken accepts (string | null) so Plan 06 callers passing null still work
//   - clearAccessToken alias kept; new clear() resets BOTH access token + user profile
//
// Keeping access token in memory (not localStorage / IndexedDB) is the AUTH-04
// contract — XSS reachability is bounded to the lifetime of the JS heap.
//
// Source: AUTH-04, RESEARCH Pattern 9 frontend section, CLAUDE.md convention #3.

import { create } from 'zustand';

export interface AuthUser {
  id: string;
  email: string;
  username: string;
  role: 'admin' | 'user';
  group_id: string | null;
  timezone: string;
}

export interface AuthState {
  accessToken: string | null;
  user: AuthUser | null;
  /** Set or clear the access token in memory. Null clears it. */
  setAccessToken: (token: string | null) => void;
  /** Set or clear the user profile in memory. */
  setUser: (user: AuthUser | null) => void;
  /** Clear both access token and user profile (logout, refresh failure, etc.). */
  clear: () => void;
  /**
   * Plan 06 forward-compat alias for clearing only the access token. New code
   * should prefer `clear()` which resets both fields atomically.
   * @deprecated use `clear()` instead.
   */
  clearAccessToken: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  setAccessToken: (accessToken) => set({ accessToken }),
  setUser: (user) => set({ user }),
  clear: () => set({ accessToken: null, user: null }),
  clearAccessToken: () => set({ accessToken: null }),
}));
