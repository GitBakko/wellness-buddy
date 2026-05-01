// frontend/src/stores/theme.ts
// UI-07 + manual data-theme override + persist middleware.
//
// Theme modes:
//   - 'system' (default): defer to @media (prefers-color-scheme: dark) — no data-theme attr set
//   - 'light' | 'dark': manual override via document.documentElement[data-theme]
//
// theme.css (Plan 05a) carries dual logic:
//   @media (prefers-color-scheme: dark) { :root { /* dark tokens */ } }
//   :root[data-theme="dark"] { /* dark tokens */ }
//   :root[data-theme="light"] { /* light tokens — wins over media query */ }
//
// Persisted to localStorage key 'wb-theme'. On boot, `applyTheme(mode)` syncs
// the data-theme attr; `useThemeStore.subscribe` keeps it in sync on change.

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type ThemeMode = 'light' | 'dark' | 'system';

export interface ThemeState {
  mode: ThemeMode;
  setMode: (mode: ThemeMode) => void;
}

/**
 * Apply the theme to the DOM by mutating `document.documentElement[data-theme]`.
 * - 'system' → remove data-theme (defer to @media query)
 * - 'light' / 'dark' → set data-theme=mode
 */
export function applyTheme(mode: ThemeMode): void {
  if (typeof document === 'undefined') return;
  const root = document.documentElement;
  if (mode === 'system') {
    root.removeAttribute('data-theme');
  } else {
    root.setAttribute('data-theme', mode);
  }
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      mode: 'system',
      setMode: (mode) => {
        applyTheme(mode);
        set({ mode });
      },
    }),
    {
      name: 'wb-theme',
      // On rehydrate, sync the DOM to the persisted value.
      onRehydrateStorage: () => (state) => {
        if (state) applyTheme(state.mode);
      },
    },
  ),
);
