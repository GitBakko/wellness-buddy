// frontend/src/hooks/useStoragePersist.ts
// FND-08 hooks for storage persistence + Dexie resync (PITFALLS #1).
//
// Plan 03 owns the user-facing PersistStorageWelcome page (D-15) which
// invokes requestPersistentStorage on first login. This module provides
// the secondary boot-time guard:
//
//   useDexieResync()
//     If JWT is valid (accessToken present in memory) but Dexie has zero
//     cached users + zero cached plans, iOS likely evicted storage during
//     the 7-day inactivity window. Refetch from /api/auth/me + /api/plans
//     to reconstruct the cache before the user notices missing data.

import { useEffect } from 'react';
import { useAuthStore } from '@/stores/auth';
import { db } from '@/db/dexie';
import { apiClient } from '@/services/api';
import type { CachedUser, CachedPlan } from '@/db/schema';

export function useDexieResync(): void {
  const accessToken = useAuthStore((s) => s.accessToken);
  useEffect(() => {
    if (!accessToken) return;
    void (async () => {
      const empty = await db.isEmptyButShouldHaveData();
      if (!empty) return;
      try {
        const me = await apiClient.request<CachedUser>({ url: '/api/auth/me' });
        await db.cache_users.put(me);
        const plans = await apiClient.request<CachedPlan[]>({ url: '/api/plans' });
        await db.cache_plans.bulkPut(plans);
      } catch {
        // Offline — next online event triggers mutationQueue flush, not us.
        // This branch fails silently; the SyncStatusPip still says "Offline".
      }
    })();
  }, [accessToken]);
}

/**
 * Re-export of the persistStorage helper for components that want to invoke
 * it directly (Settings panel, advanced flows). Plan 03 ships the welcome
 * UX that calls this on first login.
 */
export { requestPersistentStorage } from '@/lib/persistStorage';
