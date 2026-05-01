// frontend/src/stores/auth.ts
// MERGE EXPECTED — Plan 03 owns the real auth store (login/logout flow,
// refresh rotation, 10s grace, family revocation). This file is a minimal
// forward-compat stub so Plan 06 can import { useAuthStore } without
// blocking on Plan 03 merge ordering.
//
// Public surface contract (must match what Plan 03 ships):
//   useAuthStore() → { accessToken, setAccessToken, clearAccessToken }
//
// Access token lives in memory (CLAUDE.md convention #3 — "JWT access 15 min
// in memory (Zustand)"). Never persisted; refresh cookie is HttpOnly + rotated.

import { create } from 'zustand';

export interface AuthState {
  accessToken: string | null;
  setAccessToken: (token: string | null) => void;
  clearAccessToken: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  setAccessToken: (token) => set({ accessToken: token }),
  clearAccessToken: () => set({ accessToken: null }),
}));
