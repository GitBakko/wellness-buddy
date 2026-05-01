// frontend/src/hooks/useTheme.ts
// Re-export the Zustand theme store + applyTheme helper from `@/stores/theme`.
// Lets components import theme bindings via `import { useTheme } from '@/hooks/useTheme'`
// without reaching into the stores layer directly (UI-07 manual data-theme override).

export { useThemeStore, applyTheme, type ThemeMode, type ThemeState } from '@/stores/theme';

import { useThemeStore } from '@/stores/theme';

/**
 * Convenience hook: returns the entire theme store state (mode + setMode).
 * Most components only need `mode` — use `useThemeStore((s) => s.mode)` directly
 * for narrow re-render scope.
 */
export function useTheme() {
  return useThemeStore();
}
