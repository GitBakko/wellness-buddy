// frontend/src/services/workout.ts
// TanStack Query bindings for /api/workout CRUD.
// Source: WORK-01, WORK-02 + Plan 06 cache_workout_log + mutation_queue.

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { db } from '@/db/dexie';
import { enqueueMutation } from '@/lib/mutationQueue';
import { useAuthStore } from '@/stores/auth';
import { TODAY_QUERY_KEY } from '@/services/today';

export interface WorkoutLog {
  id: string;
  date: string;
  trained: boolean;
  duration_min: number | null;
  calories_burned: number | null;
  workout_type: string | null;
  notes: string | null;
}

export interface WorkoutInput {
  date: string;
  trained: boolean;
  duration_min?: number | null;
  calories_burned?: number | null;
  workout_type?: string | null;
  notes?: string | null;
}

export const WORKOUTS_QUERY_KEY = ['workouts'] as const;

export function useWorkouts(params?: { start?: string; end?: string }) {
  return useQuery<WorkoutLog[]>({
    queryKey: [...WORKOUTS_QUERY_KEY, params?.start ?? null, params?.end ?? null],
    queryFn: async () => {
      const list = await apiClient.request<WorkoutLog[]>({
        url: '/api/workout',
        params: {
          start: params?.start,
          end: params?.end,
        },
      });
      const userId = useAuthStore.getState().user?.id ?? '';
      try {
        await db.cache_workout_log.bulkPut(
          list.map((w) => ({
            ...w,
            user_id: userId,
            updated_at: new Date().toISOString(),
          })),
        );
      } catch {
        // Dexie unavailable — skip mirror.
      }
      return list;
    },
    staleTime: 30_000,
  });
}

export function useLogWorkout() {
  const qc = useQueryClient();
  return useMutation<WorkoutLog, Error, WorkoutInput>({
    mutationFn: async (input) => {
      try {
        return await apiClient.request<WorkoutLog>({
          url: '/api/workout',
          method: 'POST',
          data: input,
        });
      } catch (e: unknown) {
        if (typeof navigator !== 'undefined' && navigator.onLine === false) {
          await enqueueMutation({
            endpoint: '/api/workout',
            method: 'POST',
            body: input,
          });
          return {
            id: `pending-${crypto.randomUUID()}`,
            date: input.date,
            trained: input.trained,
            duration_min: input.duration_min ?? null,
            calories_burned: input.calories_burned ?? null,
            workout_type: input.workout_type ?? null,
            notes: input.notes ?? null,
          };
        }
        throw e instanceof Error ? e : new Error(String(e));
      }
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: WORKOUTS_QUERY_KEY });
      void qc.invalidateQueries({ queryKey: TODAY_QUERY_KEY });
    },
  });
}

export function useUpdateWorkout() {
  const qc = useQueryClient();
  return useMutation<
    WorkoutLog,
    Error,
    { id: string; patch: Partial<WorkoutInput> }
  >({
    mutationFn: async ({ id, patch }) => {
      return apiClient.request<WorkoutLog>({
        url: `/api/workout/${id}`,
        method: 'PATCH',
        data: patch,
      });
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: WORKOUTS_QUERY_KEY });
      void qc.invalidateQueries({ queryKey: TODAY_QUERY_KEY });
    },
  });
}

export function useDeleteWorkout() {
  const qc = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: async (id) => {
      await apiClient.request<void>({
        url: `/api/workout/${id}`,
        method: 'DELETE',
      });
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: WORKOUTS_QUERY_KEY });
      void qc.invalidateQueries({ queryKey: TODAY_QUERY_KEY });
    },
  });
}
