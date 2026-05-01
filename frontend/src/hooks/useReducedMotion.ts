// frontend/src/hooks/useReducedMotion.ts
// UI-05 (CLAUDE.md UI rule 3): honor prefers-reduced-motion: reduce.
//
// Returns `true` when the OS-level reduce-motion setting is active.
// theme.css (Plan 05a) sets `--motion-scale: 0` globally under
// `@media (prefers-reduced-motion: reduce)`, plus an !important rule
// zeroing animation/transition durations. This hook is for component-level
// branching (e.g. swap a Motion `<motion.div>` for a static one).
//
// Threat model: T-MOTION-01 — animations not respecting prefers-reduced-motion.

import { useEffect, useState } from 'react';

const QUERY = '(prefers-reduced-motion: reduce)';

export function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState<boolean>(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return false;
    return window.matchMedia(QUERY).matches;
  });

  useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return;
    const mql = window.matchMedia(QUERY);
    const handler = (e: MediaQueryListEvent) => setReduced(e.matches);
    // Modern API; addListener is deprecated since Safari 14.
    mql.addEventListener('change', handler);
    return () => mql.removeEventListener('change', handler);
  }, []);

  return reduced;
}
