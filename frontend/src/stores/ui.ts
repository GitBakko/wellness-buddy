// frontend/src/stores/ui.ts
// Minimal UI store — currently tracks the user's selected week start in /storico.
// Plans 03/06/07 will extend with toast queue, modal stack, sidebar state, etc.
//
// Default week start = current ISO week's Monday (CLAUDE.md UI rule 11: lunedì pesata ritual).

import { create } from 'zustand';

export interface UiState {
  /** ISO date string `YYYY-MM-DD` of the Monday whose week is currently shown in /storico. */
  currentWeekStart: string;
  setCurrentWeekStart: (date: string) => void;
}

/** Returns the Monday of the current ISO week as YYYY-MM-DD (UTC-safe). */
function defaultWeekStart(): string {
  const now = new Date();
  const day = now.getUTCDay(); // 0 (Sun) ... 6 (Sat)
  // ISO week: Monday is 1; Sunday is treated as previous week's day 7.
  const offset = day === 0 ? -6 : 1 - day;
  const monday = new Date(
    Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate() + offset),
  );
  return monday.toISOString().slice(0, 10);
}

export const useUiStore = create<UiState>((set) => ({
  currentWeekStart: defaultWeekStart(),
  setCurrentWeekStart: (date) => set({ currentWeekStart: date }),
}));
