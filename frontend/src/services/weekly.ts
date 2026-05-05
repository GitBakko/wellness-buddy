// frontend/src/services/weekly.ts
// TanStack Query bindings for /api/weekly + variant LWW mutation.
// Source: WEEK-01..05, FAM-04, D-17, RESEARCH 02 Pattern 4.
//
// Pattern:
//   useWeekly(weekStart)        → GET /api/weekly/{weekStart}, mirrored to Dexie cache_weekly
//   useWeeklySummary(weekStart) → GET /api/weekly/{weekStart}/summary
//   useSetVariant(weekStart)    → PATCH /api/weekly/{weekStart}/variant with optional
//                                  If-Unmodified-Since header; on 409 surfaces a sonner
//                                  ConflictToast with "Ricarica" action that invalidates the
//                                  query (FAM-05 UX), on success a "Variante aggiornata" toast.

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import { apiClient } from '@/services/api';
import { db } from '@/db/dexie';
import { useAuthStore } from '@/stores/auth';
import { copy } from '@/i18n/copy.it';
import {
  attachIfUnmodifiedSince,
  extractConflictPartner,
  is409Conflict,
} from '@/lib/ifUnmodifiedSince';

export interface WeeklyMacros {
  kcal: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
}

export interface WeeklyMealOption {
  /** Backend variant key — e.g. 'opzione_a', 'opzione_b', 'piatto'. */
  key: string;
  title: string;
  macros: Partial<WeeklyMacros>;
}

/** Plan 02-04 gap-closure — ingredient rows surfaced from grid-cell composition
 *  text (split on `+`) or from legacy ingredient tables. */
export interface WeeklyMealIngredient {
  name: string;
  quantity?: string | null;
}

export interface WeeklyMealEntry {
  slot: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  title: string;
  variant_key: string;
  visibility: 'private' | 'group_shared';
  version: number;
  updated_at: string | null;
  completed: boolean;
  owner_user_id: string;
  macros: WeeklyMacros;
  ingredients: WeeklyMealIngredient[];
  /** Plan 02-04: per-day variant options the user can pick between. Empty for
   *  breakfast/snack slots; lunch + dinner usually have 1-3 options per day. */
  options: WeeklyMealOption[];
  /** Plan 02-05: temporal slot for snacks ('afternoon' | 'evening'). Backend
   *  emits TWO snack entries per day when the plan has both pomeriggio and
   *  serale sections. Null for non-snack rows. */
  snack_slot?: 'afternoon' | 'evening' | null;
}

export interface WeeklyDay {
  date: string;
  day_of_week: number;
  meals: WeeklyMealEntry[];
}

export interface WeeklyResponse {
  week_start: string;
  days: WeeklyDay[];
  totals: WeeklyMacros;
}

export interface WeeklySummaryDay {
  date: string;
  kcal: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
}

export interface WeeklySummaryResponse {
  week_start: string;
  kcal_total: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  days: WeeklySummaryDay[];
}

export interface VariantResponse {
  id: string;
  user_id: string;
  week_start: string;
  day_of_week: number;
  meal_type: string;
  variant_key: string;
  visibility: string;
  version: number;
  updated_at: string;
  completed: boolean;
}

export interface PatchVariantInput {
  plan_id: string;
  day_of_week: number;
  meal_type: string;
  variant_key: string;
  visibility?: string;
  /** Optional `If-Unmodified-Since` precondition (ISO of row.updated_at). */
  ifUnmodifiedSince?: string | null;
}

export const weeklyQueryKey = (userId: string, weekStart: string) =>
  ['weekly', userId, weekStart] as const;

export const weeklySummaryQueryKey = (userId: string, weekStart: string) =>
  ['weekly', userId, weekStart, 'summary'] as const;

/**
 * Fetch the weekly aggregator payload + mirror to Dexie cache_weekly.
 * staleTime 30s + refetchOnWindowFocus reflect D-16 (lightweight realtime).
 */
export function useWeekly(weekStart: string) {
  const userId = useAuthStore.getState().user?.id ?? '';
  return useQuery<WeeklyResponse>({
    queryKey: weeklyQueryKey(userId, weekStart),
    queryFn: async () => {
      const resp = await apiClient.request<WeeklyResponse>({
        url: `/api/weekly/${weekStart}`,
      });
      try {
        await db.cache_weekly.put({
          user_id: userId,
          week_start: weekStart,
          payload: resp,
          fetched_at: new Date().toISOString(),
        });
      } catch {
        // Dexie unavailable (Safari Private Mode etc.) — fall through.
      }
      return resp;
    },
    staleTime: 30_000,
    refetchOnWindowFocus: true,
  });
}

export function useWeeklySummary(weekStart: string) {
  const userId = useAuthStore.getState().user?.id ?? '';
  return useQuery<WeeklySummaryResponse>({
    queryKey: weeklySummaryQueryKey(userId, weekStart),
    queryFn: async () =>
      apiClient.request<WeeklySummaryResponse>({
        url: `/api/weekly/${weekStart}/summary`,
      }),
    staleTime: 30_000,
  });
}

/**
 * PATCH /api/weekly/{weekStart}/variant with LWW precondition + optimistic UI.
 *
 *   - onMutate: optimistically swap variant_key in the TanStack cache + snapshot.
 *   - onError: rollback the cache; if 409, render the FAM-05 ConflictToast with a
 *              "Ricarica" action that invalidates the query (server canonical truth).
 *              For any other failure, render a generic italian error toast.
 *   - onSuccess: render "Variante aggiornata" toast and invalidate the query so the
 *                authoritative version + updated_at land in the cache.
 */
export function useSetVariant(weekStart: string) {
  const userId = useAuthStore.getState().user?.id ?? '';
  const qc = useQueryClient();
  return useMutation<
    VariantResponse,
    unknown,
    PatchVariantInput,
    { prev: WeeklyResponse | undefined }
  >({
    mutationFn: async (input) => {
      const headers = attachIfUnmodifiedSince({}, input.ifUnmodifiedSince);
      return apiClient.request<VariantResponse>({
        url: `/api/weekly/${weekStart}/variant`,
        method: 'PATCH',
        data: {
          plan_id: input.plan_id,
          day_of_week: input.day_of_week,
          meal_type: input.meal_type,
          variant_key: input.variant_key,
          visibility: input.visibility,
        },
        headers,
      });
    },
    onMutate: async (input) => {
      await qc.cancelQueries({ queryKey: weeklyQueryKey(userId, weekStart) });
      const prev = qc.getQueryData<WeeklyResponse>(
        weeklyQueryKey(userId, weekStart),
      );
      if (prev) {
        const next: WeeklyResponse = {
          ...prev,
          days: prev.days.map((d) =>
            d.day_of_week !== input.day_of_week
              ? d
              : {
                  ...d,
                  meals: d.meals.map((m) =>
                    m.slot !== input.meal_type
                      ? m
                      : { ...m, variant_key: input.variant_key },
                  ),
                },
          ),
        };
        qc.setQueryData(weeklyQueryKey(userId, weekStart), next);
      }
      return { prev };
    },
    onError: (err, _input, ctx) => {
      if (ctx?.prev) {
        qc.setQueryData(weeklyQueryKey(userId, weekStart), ctx.prev);
      }
      if (is409Conflict(err)) {
        const partner = extractConflictPartner(err);
        toast.info(
          copy.sync.conflictToastHeading.replace('{partnerName}', partner),
          {
            description: copy.sync.conflictToastBody,
            action: {
              label: copy.sync.conflictToastAction,
              onClick: () =>
                qc.invalidateQueries({
                  queryKey: weeklyQueryKey(userId, weekStart),
                }),
            },
            duration: 6000,
          },
        );
      } else {
        toast.error(copy.week.variantUpdateError);
      }
    },
    onSuccess: () => {
      toast.success(copy.week.variantUpdateSuccess, { duration: 4000 });
      void qc.invalidateQueries({
        queryKey: weeklyQueryKey(userId, weekStart),
      });
    },
  });
}
