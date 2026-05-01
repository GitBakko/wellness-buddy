// frontend/src/lib/mutationQueue.ts
// Outbox / mutation queue — FND-07.
// Source: 01-RESEARCH.md Pattern 5.
//
// Contract:
//   - enqueueMutation appends a Dexie row with crypto.randomUUID() id.
//   - flushQueue replays in created_at order:
//       * 200/204 → delete row.
//       * 409 conflict → delete row + sonner toast (last-write-wins per
//         CLAUDE.md convention #13). User refreshes to see latest.
//       * other failures → bump retries; stop the batch (preserve order);
//         dead-letter at retries >= 5 (toast + persist row for support).
//   - Auto-flushes on `online` event.

import { db } from '@/db/dexie';
import { apiClient } from '@/services/api';
import { toast } from 'sonner';
import { copy } from '@/i18n/copy.it';
import { useSyncStore } from '@/stores/sync';
import type { QueuedMutation } from '@/db/schema';

export async function enqueueMutation(
  m: Omit<QueuedMutation, 'id' | 'created_at' | 'retries' | 'last_error'>,
): Promise<void> {
  await db.mutation_queue.add({
    id: crypto.randomUUID(),
    created_at: Date.now(),
    retries: 0,
    last_error: null,
    ...m,
  });
  // Refresh UI pip count
  const count = await db.mutation_queue.count();
  useSyncStore.getState().setPending(count);
}

export async function flushQueue(): Promise<void> {
  const items = await db.mutation_queue.orderBy('created_at').toArray();
  for (const item of items) {
    try {
      await apiClient.request({
        url: item.endpoint,
        method: item.method,
        data: item.body,
      });
      await db.mutation_queue.delete(item.id);
    } catch (e: unknown) {
      const status =
        typeof e === 'object' && e !== null && 'response' in e
          ? ((e as { response?: { status?: number } }).response?.status ?? 0)
          : 0;
      if (status === 409) {
        await db.mutation_queue.delete(item.id);
        toast.error(copy.errors.conflict, {
          description: copy.errors.conflictHint,
        });
        continue;
      }
      if (item.retries >= 5) {
        await db.mutation_queue.update(item.id, {
          last_error: String(e),
          retries: item.retries + 1,
        });
        toast.error(copy.errors.syncFailed);
        break;
      }
      await db.mutation_queue.update(item.id, {
        retries: item.retries + 1,
        last_error: String(e),
      });
      break;
    }
  }
  // Update pip + lastSyncedAt if anything cleared
  const remaining = await db.mutation_queue.count();
  const sync = useSyncStore.getState();
  sync.setPending(remaining);
  if (remaining < items.length) {
    sync.setLastSyncedAt(Date.now());
  }
}

if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    void flushQueue();
  });
}
