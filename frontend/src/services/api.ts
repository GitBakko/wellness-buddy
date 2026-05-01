// frontend/src/services/api.ts
// AUTH-12 envelope-aware API client + AUTH-07 401-driven refresh interceptor.
//
// Behavior:
//   1. Inject `Authorization: Bearer ${accessToken}` from Zustand store.
//   2. On 401 response (only when an access token was attached), call
//      `refreshTokenAtomic()` once, then retry the request with the new token.
//   3. On non-OK final response, throw an Error decorated with
//      `.response = { status, data: { detail, code } }` so callers can
//      inspect AUTH-12 envelope.
//   4. 204 No Content returns undefined.
//
// Source: 01-RESEARCH.md Pattern 9, AUTH-12, PITFALLS#4 (refresh-storm coalescing).

import { refreshTokenAtomic } from '@/lib/refreshTokenAtomic';
import { useAuthStore } from '@/stores/auth';

export interface ApiErrorBody {
  detail: string;
  code: string;
}

export interface ApiError extends Error {
  response: { status: number; data: ApiErrorBody };
}

interface RequestOptions {
  url: string;
  method?: 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE';
  data?: unknown;
  params?: Record<string, unknown>;
  headers?: Record<string, string>;
  signal?: AbortSignal;
}

function buildUrl(url: string, params?: Record<string, unknown>): string {
  if (!params) return url;
  const qs = Object.entries(params)
    .filter(([, v]) => v !== undefined && v !== null)
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
    .join('&');
  return qs ? `${url}?${qs}` : url;
}

async function executeFetch(
  fullUrl: string,
  opts: RequestOptions,
  accessToken: string | null,
): Promise<Response> {
  return fetch(fullUrl, {
    method: opts.method ?? 'GET',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...(opts.headers ?? {}),
    },
    body: opts.data !== undefined ? JSON.stringify(opts.data) : undefined,
    signal: opts.signal,
  });
}

async function parseError(res: Response): Promise<ApiErrorBody> {
  try {
    const body = (await res.json()) as Partial<ApiErrorBody>;
    return {
      detail: typeof body.detail === 'string' ? body.detail : 'Errore',
      code: typeof body.code === 'string' ? body.code : 'unknown',
    };
  } catch {
    return { detail: 'Errore', code: 'unknown' };
  }
}

export const apiClient = {
  async request<T = unknown>(opts: RequestOptions): Promise<T> {
    const fullUrl = buildUrl(opts.url, opts.params);
    const access = useAuthStore.getState().accessToken;
    let res = await executeFetch(fullUrl, opts, access);

    // AUTH-07: 401 only triggers refresh if we had an access token to begin with.
    // /api/auth/refresh itself is excluded — failure there means the session is dead.
    if (res.status === 401 && access && opts.url !== '/api/auth/refresh') {
      try {
        const newAccess = await refreshTokenAtomic();
        res = await executeFetch(fullUrl, opts, newAccess);
      } catch {
        // refreshTokenAtomic clears the auth store; surface the original 401
      }
    }

    if (!res.ok) {
      const data = await parseError(res);
      const err = new Error(`HTTP ${res.status} on ${opts.method ?? 'GET'} ${opts.url}`) as ApiError;
      err.response = { status: res.status, data };
      throw err;
    }

    if (res.status === 204) return undefined as T;
    return (await res.json()) as T;
  },
};
