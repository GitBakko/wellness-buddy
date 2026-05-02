// frontend/src/lib/ifUnmodifiedSince.ts
// LWW (Last-Write-Wins) precondition helpers — D-17, FAM-04, FAM-05.
//
// Pattern (RESEARCH 02 Pattern 4): the client sends `If-Unmodified-Since:
// <updated_at ISO>` header derived from the variant version it last fetched.
// The server compares to the row's `updated_at` and either proceeds (200) or
// raises AppException(409, "Aggiornato da {nome}", "version_conflict").
//
// Frontend responsibilities:
//   1. attachIfUnmodifiedSince — append the header when an updated_at is known
//   2. is409Conflict           — detect the AUTH-12 envelope code='version_conflict'
//   3. extractConflictPartner  — pull "{partnerName}" out of detail or extras
//
// Pairs with apiClient (services/api.ts) which decorates errors with `.response.data`.

import type { ApiError } from '@/services/api';

export interface ConflictError {
  code: 'version_conflict';
  detail: string;
  conflicting_user?: string;
  partnerName: string;
}

/**
 * Append the `If-Unmodified-Since` header when a precondition is available.
 * No-op when the value is null/undefined/empty (skips LWW gate server-side).
 */
export function attachIfUnmodifiedSince(
  headers: Record<string, string>,
  ifUnmodifiedSince?: string | null,
): Record<string, string> {
  if (!ifUnmodifiedSince) return headers;
  return { ...headers, 'If-Unmodified-Since': ifUnmodifiedSince };
}

/**
 * Returns true when the error is a 409 with code='version_conflict'.
 * Accepts either:
 *   - The thrown apiClient error: { response: { status: 409, data: { code, detail } } }
 *   - The error body itself: { code, detail }
 */
export function is409Conflict(err: unknown): boolean {
  if (!err || typeof err !== 'object') return false;
  // apiClient ApiError shape
  const e = err as Partial<ApiError> & {
    code?: string;
    detail?: string;
  };
  if (e.response) {
    const data = e.response.data;
    return e.response.status === 409 && data?.code === 'version_conflict';
  }
  // Direct envelope shape
  return e.code === 'version_conflict';
}

/**
 * Extract the partner name (the user who beat us in the LWW race).
 * Source order: explicit `conflicting_user` field → "Aggiornato da {nome}" parse → fallback.
 */
export function extractConflictPartner(err: unknown): string {
  if (!err || typeof err !== 'object') return 'un familiare';
  const apiErr = err as Partial<ApiError> & {
    conflicting_user?: string;
    detail?: string;
  };
  // Look at error body first, then at the wrapped response payload
  const body = apiErr.response?.data ?? apiErr;
  const data = body as { conflicting_user?: string; detail?: string };
  if (data.conflicting_user && data.conflicting_user.trim()) {
    return data.conflicting_user.trim();
  }
  if (data.detail) {
    const m = /Aggiornato da ([^.]+)\./i.exec(data.detail);
    if (m) return m[1].trim();
  }
  return 'un familiare';
}
