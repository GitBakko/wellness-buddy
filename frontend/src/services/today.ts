// frontend/src/services/today.ts
// TanStack Query bindings for /api/today + meal complete.
// Source: TODAY-01..TODAY-08 + Plan 06 Dexie cache_today + offline fallback.

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { db } from '@/db/dexie';
import { useAuthStore } from '@/stores/auth';

export interface MealMacro {
  kcal: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
}

export interface TodayMeal {
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack' | string;
  variant_key: string;
  title: string;
  macros: MealMacro;
  completed: boolean;
  /** Plan 01-09 — optional Lifesum-style meal photo URL. Null when the parser
   * didn't find a `**Foto:** <url>` line in the section body. Frontend renders
   * a leaf-tinted gradient placeholder when null. */
  photo_url: string | null;
}

export interface TodayWeight {
  id: string;
  weight_kg: number;
}

export interface TodayWorkout {
  id: string;
  trained: boolean;
  duration_min: number | null;
  calories_burned: number | null;
  workout_type: string | null;
  notes: string | null;
}

export interface TodayResponse {
  date: string; // ISO YYYY-MM-DD
  day_of_week: number;
  greeting_period: 'morning' | 'afternoon' | 'evening' | 'night';
  meals: TodayMeal[];
  weight_today: TodayWeight | null;
  workout_today: TodayWorkout | null;
}

export const TODAY_QUERY_KEY = ['today'] as const;

export function useToday() {
  return useQuery<TodayResponse>({
    queryKey: TODAY_QUERY_KEY,
    queryFn: async () => {
      const resp = await apiClient.request<TodayResponse>({ url: '/api/today' });
      // Mirror to Dexie cache_today (PITFALLS#5 — opaque mirror, dropped on schema bump).
      const userId = useAuthStore.getState().user?.id ?? '';
      try {
        await db.cache_today.put({
          date: resp.date,
          user_id: userId,
          meals_completed: Object.fromEntries(
            resp.meals.map((m) => [m.meal_type, m.completed]),
          ),
          fetched_at: new Date().toISOString(),
        });
      } catch {
        // Dexie unavailable (e.g. Safari Private Mode) — fall through.
      }
      return resp;
    },
    // Offline-friendly: keep last good payload while a refetch is in flight.
    staleTime: 30_000,
  });
}

export function useCompleteMeal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (mealType: string) => {
      return apiClient.request<{ meal_type: string; completed: boolean; version: number }>({
        url: `/api/today/meal/${mealType}/complete`,
        method: 'POST',
      });
    },
    onMutate: async (mealType) => {
      await qc.cancelQueries({ queryKey: TODAY_QUERY_KEY });
      const prev = qc.getQueryData<TodayResponse>(TODAY_QUERY_KEY);
      if (prev) {
        qc.setQueryData<TodayResponse>(TODAY_QUERY_KEY, {
          ...prev,
          meals: prev.meals.map((m) =>
            m.meal_type === mealType ? { ...m, completed: true } : m,
          ),
        });
      }
      return { prev };
    },
    onError: (_e, _mealType, ctx) => {
      // Rollback optimistic update on error.
      if (ctx?.prev) {
        qc.setQueryData(TODAY_QUERY_KEY, ctx.prev);
      }
    },
    onSettled: () => {
      void qc.invalidateQueries({ queryKey: TODAY_QUERY_KEY });
    },
  });
}
