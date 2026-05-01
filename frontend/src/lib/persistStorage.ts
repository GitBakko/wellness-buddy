// frontend/src/lib/persistStorage.ts
// MERGE EXPECTED — Plan 03 owns the real persistStorage helpers (Welcome flow,
// FND-08 invocation timing, persistDenied toast escalation). This file is a
// minimal forward-compat stub so Plan 06 can call requestPersistentStorage /
// getStorageEstimate without blocking on Plan 03 merge ordering.
//
// Public surface contract (must match what Plan 03 ships):
//   requestPersistentStorage(): Promise<boolean>
//   getStorageEstimate(): Promise<{ usage: number; quota: number } | null>

/**
 * Request persistent storage (FND-08, D-15 — PITFALLS #1 mitigation).
 * Returns true if granted (or already persisted), false if denied / unsupported.
 *
 * Browsers grant persistence based on heuristics: site bookmarked, frequent
 * use, PWA installed. iOS grants implicitly when added to Home Screen.
 */
export async function requestPersistentStorage(): Promise<boolean> {
  if (typeof navigator === 'undefined' || !navigator.storage?.persist) {
    return false;
  }
  try {
    const alreadyPersisted = await navigator.storage.persisted?.();
    if (alreadyPersisted) return true;
    return await navigator.storage.persist();
  } catch {
    return false;
  }
}

/** Fetch current storage usage/quota for diagnostics (Settings panel, debug). */
export async function getStorageEstimate(): Promise<{ usage: number; quota: number } | null> {
  if (typeof navigator === 'undefined' || !navigator.storage?.estimate) {
    return null;
  }
  try {
    const est = await navigator.storage.estimate();
    return { usage: est.usage ?? 0, quota: est.quota ?? 0 };
  } catch {
    return null;
  }
}
