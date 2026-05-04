// frontend/src/services/shopping.ts
// TanStack Query bindings for /api/shopping CRUD + Dexie cache mirror +
// offline-first mutation queue + BroadcastChannel multi-tab sync (D-25).
//
// Source: SHOP-01..06, SHOP-08, Pattern 4 (offline-first), Pattern 10
// (BroadcastChannel iOS Safari fallback).

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import { db } from '@/db/dexie';
import { copy } from '@/i18n/copy.it';
import { postSyncMessage } from '@/lib/broadcastChannel';
import { enqueueMutation } from '@/lib/mutationQueue';
import { apiClient } from '@/services/api';
import { useAuthStore } from '@/stores/auth';

export interface ShoppingItem {
  canonical_name: string;
  name_display: string;
  amount: number | null;
  unit: string | null;
  quantity_it: string;
  category: string;
  checked: boolean;
  /** Source tags like ``"lunch_d0"`` recorded for the per-day view. */
  sources: string[];
}

export interface ShoppingCategorySectionData {
  name: string;
  items: ShoppingItem[];
}

export interface ShoppingResponse {
  week_start: string;
  categories: ShoppingCategorySectionData[];
  version: number;
}

/** Multi-tab sync channel name (D-25). */
export const SHOPPING_CHANNEL = 'wb-shopping-sync';

export const shoppingQueryKey = (userId: string, weekStart: string) =>
  ['shopping', userId, weekStart] as const;

/**
 * Fetch the categorized aggregated shopping list + mirror to Dexie.
 * staleTime 30s + refetchOnWindowFocus reflect D-16 (lightweight realtime).
 */
export function useShopping(weekStart: string) {
  const userId = useAuthStore.getState().user?.id ?? '';
  return useQuery<ShoppingResponse>({
    queryKey: shoppingQueryKey(userId, weekStart),
    queryFn: async () => {
      const resp = await apiClient.request<ShoppingResponse>({
        url: `/api/shopping/${weekStart}`,
      });
      try {
        await db.cache_shopping.put({
          user_id: userId,
          week_start: weekStart,
          payload: resp,
          fetched_at: new Date().toISOString(),
        });
      } catch {
        // Dexie unavailable (Safari Private mode etc.) — fall through.
      }
      return resp;
    },
    staleTime: 30_000,
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  });
}

export interface ToggleItemInput {
  canonical_name: string;
  unit: string | null;
  checked: boolean;
}

/**
 * PATCH /api/shopping/{weekStart}/check with optimistic UI + offline queue.
 *
 * - onMutate: optimistically swap the item's ``checked`` state in the cache.
 * - onError: rollback + toast (unless we already enqueued offline).
 * - onSuccess: invalidate the query, broadcast a sync message to other tabs.
 */
export function useToggleItem(weekStart: string) {
  const userId = useAuthStore.getState().user?.id ?? '';
  const qc = useQueryClient();
  return useMutation<
    ShoppingResponse | null,
    unknown,
    ToggleItemInput,
    { prev: ShoppingResponse | undefined }
  >({
    mutationFn: async (input) => {
      try {
        return await apiClient.request<ShoppingResponse>({
          url: `/api/shopping/${weekStart}/check`,
          method: 'PATCH',
          data: input,
        });
      } catch (e: unknown) {
        if (typeof navigator !== 'undefined' && navigator.onLine === false) {
          await enqueueMutation({
            endpoint: `/api/shopping/${weekStart}/check`,
            method: 'PATCH',
            body: input,
          });
          // Optimistic UI keeps the change locally; queued mutation will
          // replay when navigator.onLine flips back to true.
          return null;
        }
        throw e;
      }
    },
    onMutate: async (input) => {
      await qc.cancelQueries({ queryKey: shoppingQueryKey(userId, weekStart) });
      const prev = qc.getQueryData<ShoppingResponse>(shoppingQueryKey(userId, weekStart));
      if (prev) {
        const next: ShoppingResponse = {
          ...prev,
          categories: prev.categories.map((c) => ({
            ...c,
            items: c.items.map((it) =>
              it.canonical_name === input.canonical_name && it.unit === input.unit
                ? { ...it, checked: input.checked }
                : it,
            ),
          })),
        };
        qc.setQueryData(shoppingQueryKey(userId, weekStart), next);
      }
      return { prev };
    },
    onError: (_err, _input, ctx) => {
      if (ctx?.prev) {
        qc.setQueryData(shoppingQueryKey(userId, weekStart), ctx.prev);
      }
      toast.error(copy.errors.syncFailed);
    },
    onSuccess: (data) => {
      // No success toast — UI-SPEC §10.2: toggling 336 rows can't generate
      // 336 toasts. Silence is golden.
      postSyncMessage(SHOPPING_CHANNEL, { weekStart, type: 'check_changed' });
      // If the server returned a fresh payload (online path), seed the
      // cache with it so the version increments correctly.
      if (data) {
        qc.setQueryData(shoppingQueryKey(userId, weekStart), data);
      } else {
        void qc.invalidateQueries({ queryKey: shoppingQueryKey(userId, weekStart) });
      }
    },
  });
}

/**
 * POST /api/shopping/{weekStart}/reset — clear all check state for the week.
 * Always refetches afterward so the UI reflects server truth (no optimistic
 * update because the bulk-reset surface area is the whole list).
 */
export function useResetShopping(weekStart: string) {
  const userId = useAuthStore.getState().user?.id ?? '';
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async () =>
      apiClient.request<{ week_start: string; reset_at: string }>({
        url: `/api/shopping/${weekStart}/reset`,
        method: 'POST',
      }),
    onSuccess: () => {
      toast.success(copy.shopping.resetSuccess);
      void qc.invalidateQueries({ queryKey: shoppingQueryKey(userId, weekStart) });
      postSyncMessage(SHOPPING_CHANNEL, { weekStart, type: 'reset' });
    },
    onError: () => {
      toast.error(copy.errors.syncFailed);
    },
  });
}

/**
 * Compose a plain-text shopping list for the "Copia testo" CTA. Italian
 * formatting matches the WeasyPrint PDF template (Plan 02-06) so users can
 * paste into messages / notes / share apps.
 */
export function composeTextExport(payload: ShoppingResponse): string {
  const lines: string[] = [];
  lines.push(`Lista spesa — settimana del ${payload.week_start}`);
  lines.push('');
  for (const cat of payload.categories) {
    if (cat.items.length === 0) continue;
    lines.push(`## ${cat.name}`);
    for (const it of cat.items) {
      const tick = it.checked ? '[x]' : '[ ]';
      const qty = it.quantity_it ? ` — ${it.quantity_it}` : '';
      lines.push(`${tick} ${it.name_display}${qty}`);
    }
    lines.push('');
  }
  return lines.join('\n').trim();
}
