// frontend/src/hooks/useMediaQuery.ts
// Generic media query hook with addEventListener('change').
// Used for responsive container queries, dark-mode detection in components,
// `(min-width: 768px)` checks for mobile vs desktop layout decisions.

import { useSyncExternalStore } from 'react';

/**
 * useMediaQuery — React 19-friendly via `useSyncExternalStore`.
 *
 * Why useSyncExternalStore over useState+useEffect:
 *   - No setState-in-effect cascade (react-hooks/set-state-in-effect)
 *   - SSR-safe (getServerSnapshot returns false)
 *   - Re-evaluates correctly when `query` changes (subscribe re-runs)
 */
function getSnapshotForQuery(query: string): () => boolean {
  return () => {
    if (typeof window === 'undefined' || !window.matchMedia) return false;
    return window.matchMedia(query).matches;
  };
}

function subscribeForQuery(query: string): (cb: () => void) => () => void {
  return (cb) => {
    if (typeof window === 'undefined' || !window.matchMedia) return () => {};
    const mql = window.matchMedia(query);
    mql.addEventListener('change', cb);
    return () => mql.removeEventListener('change', cb);
  };
}

export function useMediaQuery(query: string): boolean {
  return useSyncExternalStore(subscribeForQuery(query), getSnapshotForQuery(query), () => false);
}
