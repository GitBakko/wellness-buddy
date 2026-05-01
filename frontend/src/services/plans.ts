// frontend/src/services/plans.ts
// Plan 04 Task 3 — TanStack Query data layer for nutrition plans.
//
// Why a hand-rolled fetch for `uploadPlan`: the apiClient sets
// `Content-Type: application/json` for every request which clobbers the
// boundary that a multipart upload needs. The browser sets the multipart
// boundary itself when you pass a FormData body and DON'T set Content-Type —
// so we drop the apiClient layer for this single endpoint.
//
// Source: PLAN-07..PLAN-10, AUTH-12 envelope (we throw a shaped ApiError on
// non-OK so callers can switch on `.response.data.code`).

import { apiClient, type ApiError } from '@/services/api';
import { useAuthStore } from '@/stores/auth';

export interface PlanListItem {
  id: string;
  name: string;
  uploaded_at: string;
  is_active: boolean;
}

export interface PlanUploadResponse extends PlanListItem {
  parse_warnings: string[];
  unrecognized_headings: string[];
}

export interface PlanDiffResponse {
  added: string[];
  removed: string[];
  changed: string[];
}

export interface PlanResponse {
  id: string;
  name: string;
  is_active: boolean;
}

/** GET /api/plans — current user's plans, latest first. */
export async function listPlans(): Promise<PlanListItem[]> {
  return apiClient.request<PlanListItem[]>({ url: '/api/plans' });
}

/** POST /api/plans/upload — multipart upload of a markdown plan file. */
export async function uploadPlan(
  file: File,
  name: string,
): Promise<PlanUploadResponse> {
  const access = useAuthStore.getState().accessToken;
  const fd = new FormData();
  fd.append('file', file);
  fd.append('name', name);

  // Hand-rolled fetch: do NOT set Content-Type so the browser injects the
  // correct multipart boundary header. apiClient unconditionally sets JSON
  // headers, which would corrupt the upload.
  const res = await fetch('/api/plans/upload', {
    method: 'POST',
    body: fd,
    credentials: 'include',
    headers: access ? { Authorization: `Bearer ${access}` } : {},
  });

  if (!res.ok) {
    let body: { detail?: string; code?: string } = {};
    try {
      body = (await res.json()) as { detail?: string; code?: string };
    } catch {
      // body parse failed — leave empty, error message below stays generic
    }
    const err = new Error(`HTTP ${res.status} on POST /api/plans/upload`) as ApiError;
    err.response = {
      status: res.status,
      data: {
        detail: typeof body.detail === 'string' ? body.detail : 'Errore',
        code: typeof body.code === 'string' ? body.code : 'unknown',
      },
    };
    throw err;
  }

  return (await res.json()) as PlanUploadResponse;
}

/** POST /api/plans/{id}/activate — atomically deactivate previous + activate this. */
export async function activatePlan(planId: string): Promise<PlanResponse> {
  return apiClient.request<PlanResponse>({
    url: `/api/plans/${planId}/activate`,
    method: 'POST',
  });
}

/** GET /api/plans/{id}/diff — section-level diff vs the user's active plan. */
export async function diffPlan(planId: string): Promise<PlanDiffResponse> {
  return apiClient.request<PlanDiffResponse>({
    url: `/api/plans/${planId}/diff`,
  });
}
