// frontend/src/lib/persistStorage.ts
// FND-08, D-15, PITFALLS#1 — request browser persistent storage so iOS/Safari
// don't evict the IndexedDB after the 7-day inactivity window.
//
// Plan 03 ownership: this module ships the real surface. Plan 06's stub already
// matched this signature so callers (`useStoragePersist`, `Settings`) keep working
// without changes. Beyond Plan 06's stub, Plan 03 adds the denial-toast UX
// escalation per UI-SPEC §7.2 (`copy.pwa.persistDeniedHeading`).
//
// Public surface:
//   requestPersistentStorage(): Promise<boolean>
//   getStorageEstimate(): Promise<{ usage: number; quota: number } | null>

import { toast } from 'sonner';

import { copy } from '@/i18n/copy.it';

/**
 * Request persistent storage. Returns true if granted (already persisted or newly
 * granted), false if denied / unsupported.
 *
 * Side-effect on denial: surface a sonner toast warning with the locked italian
 * copy from `copy.pwa.persistDeniedHeading`. This is a UX nudge, not a blocker —
 * the app still works without persistence.
 */
export async function requestPersistentStorage(): Promise<boolean> {
  if (typeof navigator === 'undefined' || !navigator.storage?.persist) {
    return false;
  }
  try {
    const alreadyPersisted = await navigator.storage.persisted?.();
    if (alreadyPersisted) return true;
    const granted = await navigator.storage.persist();
    if (!granted) {
      toast.warning(copy.pwa.persistDeniedHeading, {
        description: copy.pwa.persistDeniedBody,
      });
    }
    return granted;
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
