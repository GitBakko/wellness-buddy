// frontend/src/services/weight.ts
// TanStack Query bindings for /api/weight CRUD.
// Source: WEIGHT-01, WEIGHT-02 + Plan 06 cache_weight_log + mutation_queue.

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { db } from '@/db/dexie';
import { enqueueMutation } from '@/lib/mutationQueue';
import { useAuthStore } from '@/stores/auth';
import { TODAY_QUERY_KEY } from '@/services/today';

export interface WeightLog {
  id: string;
  date: string;
  weight_kg: number;
}

export const WEIGHTS_QUERY_KEY = ['weights'] as const;

export function useWeights() {
  return useQuery<WeightLog[]>({
    queryKey: WEIGHTS_QUERY_KEY,
    queryFn: async () => {
      const list = await apiClient.request<WeightLog[]>({ url: '/api/weight' });
      const userId = useAuthStore.getState().user?.id ?? '';
      try {
        await db.cache_weight_log.bulkPut(
          list.map((w) => ({
            id: w.id,
            user_id: userId,
            date: w.date,
            weight_kg: Number(w.weight_kg),
            updated_at: new Date().toISOString(),
          })),
        );
      } catch {
        // Dexie unavailable — skip mirror.
      }
      return list.map((w) => ({ ...w, weight_kg: Number(w.weight_kg) }));
    },
    staleTime: 30_000,
  });
}

export interface WeightInput {
  date: string; // ISO YYYY-MM-DD
  weight_kg: number;
}

export function useLogWeight() {
  const qc = useQueryClient();
  return useMutation<WeightLog, Error, WeightInput>({
    mutationFn: async (input) => {
      try {
        return await apiClient.request<WeightLog>({
          url: '/api/weight',
          method: 'POST',
          data: input,
        });
      } catch (e: unknown) {
        if (typeof navigator !== 'undefined' && navigator.onLine === false) {
          await enqueueMutation({
            endpoint: '/api/weight',
            method: 'POST',
            body: input,
          });
          // Optimistic local row
          return {
            id: `pending-${crypto.randomUUID()}`,
            date: input.date,
            weight_kg: input.weight_kg,
          };
        }
        throw e instanceof Error ? e : new Error(String(e));
      }
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: WEIGHTS_QUERY_KEY });
      void qc.invalidateQueries({ queryKey: TODAY_QUERY_KEY });
    },
  });
}

export function useUpdateWeight() {
  const qc = useQueryClient();
  return useMutation<WeightLog, Error, { id: string; weight_kg: number; date: string }>({
    mutationFn: async ({ id, weight_kg, date }) => {
      return apiClient.request<WeightLog>({
        url: `/api/weight/${id}`,
        method: 'PATCH',
        data: { weight_kg, date },
      });
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: WEIGHTS_QUERY_KEY });
      void qc.invalidateQueries({ queryKey: TODAY_QUERY_KEY });
    },
  });
}

export function useDeleteWeight() {
  const qc = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: async (id) => {
      await apiClient.request<void>({
        url: `/api/weight/${id}`,
        method: 'DELETE',
      });
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: WEIGHTS_QUERY_KEY });
      void qc.invalidateQueries({ queryKey: TODAY_QUERY_KEY });
    },
  });
}
