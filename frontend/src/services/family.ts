// frontend/src/services/family.ts
// TanStack Query bindings for Plan 02-07 family-share toggle.
//
// PATCH /api/family/share/{variantId} — owner-only visibility toggle. On success
// invalidates the `today` and `weekly` caches so the SharedBadge / toggle state
// re-renders immediately. On 409 conflict (CONV-13 LWW) shows the named-partner
// info toast already used by Plan 02-02 variant patches.
//
// Source: FAM-02, FAM-03, FAM-09, D-15.

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import { copy } from '@/i18n/copy.it';
import { extractConflictPartner, is409Conflict } from '@/lib/ifUnmodifiedSince';
import { apiClient } from '@/services/api';

export interface ShareToggleInput {
  variantId: string;
  visibility: 'private' | 'group_shared';
}

export interface ShareToggleResponse {
  id: string;
  visibility: 'private' | 'group_shared';
  version: number;
  updated_at: string;
}

/**
 * Owner-only mutation. ``weekStart`` (optional) lets us invalidate the
 * specific weekly query so /settimana rerenders without a stale cache.
 */
export function useShareToggle(weekStart?: string) {
  const qc = useQueryClient();
  return useMutation<ShareToggleResponse, unknown, ShareToggleInput>({
    mutationFn: async (input) =>
      apiClient.request<ShareToggleResponse>({
        url: `/api/family/share/${input.variantId}`,
        method: 'PATCH',
        data: { visibility: input.visibility },
      }),
    onSuccess: (_data, input) => {
      toast.success(
        input.visibility === 'group_shared'
          ? copy.family.sharePerMealOnSuccess
          : copy.family.sharePerMealOffSuccess,
        { duration: 4000 },
      );
      // FAM-09 — invalidate the surfaces a SharedBadge / ShareToggleMenu lives in.
      void qc.invalidateQueries({ queryKey: ['today'] });
      if (weekStart) {
        void qc.invalidateQueries({ queryKey: ['weekly', undefined, weekStart] });
      } else {
        void qc.invalidateQueries({ queryKey: ['weekly'] });
      }
    },
    onError: (err) => {
      if (is409Conflict(err)) {
        const partner = extractConflictPartner(err);
        toast.info(copy.sync.conflictToastHeading.replace('{partnerName}', partner), {
          description: copy.sync.conflictToastBody,
          duration: 6000,
        });
      } else {
        toast.error(copy.family.sharePerMealError, { duration: 4000 });
      }
    },
  });
}
