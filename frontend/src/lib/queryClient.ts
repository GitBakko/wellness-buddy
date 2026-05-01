// frontend/src/lib/queryClient.ts
// TanStack Query client + persistQueryClient (FND-07 + Phase 1 stretch).
//
// Phase 1 ships sync localStorage persister (24h maxAge). Phase 2 hard
// requirement upgrades to a Dexie-backed async persister to cache larger
// query payloads (plans, weekly history) without 5MB localStorage cap.
//
// Why persist queries at all? — Cold boot offline must show last-known
// /today + /piano without spinner. PITFALLS #1 ("data deleted my app")
// trust signal in SyncStatusPip uses `lastSyncedAt` from successful refetch.

import { QueryClient } from '@tanstack/react-query';
import { persistQueryClient } from '@tanstack/react-query-persist-client';
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      refetchOnWindowFocus: true,
      retry: 1,
    },
    mutations: {
      retry: 0,
    },
  },
});

// SSR / test guard — `window.localStorage` not defined in node.
if (typeof window !== 'undefined') {
  const persister = createSyncStoragePersister({
    storage: window.localStorage,
    key: 'wb-tanstack-cache',
  });
  void persistQueryClient({
    queryClient,
    persister,
    maxAge: 24 * 60 * 60 * 1000,
    dehydrateOptions: {
      shouldDehydrateQuery: (q) => q.state.status === 'success',
    },
  });
}
