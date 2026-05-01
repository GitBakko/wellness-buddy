// frontend/src/services/api.ts
// MERGE EXPECTED — Plan 03 owns the real apiClient (axios instance + JWT
// refresh interceptor + 10s grace + family revocation). This file is a
// minimal forward-compat stub so Plan 06 can import { apiClient } without
// blocking on Plan 03 merge ordering.
//
// When Plan 03 merges, this file must be replaced with the full implementation.
// Public surface contract (must match):
//   apiClient.request<T>({ url, method?, data?, params?, headers? }): Promise<T>

interface RequestOptions {
  url: string;
  method?: 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE';
  data?: unknown;
  params?: Record<string, unknown>;
  headers?: Record<string, string>;
}

export const apiClient = {
  async request<T = unknown>(opts: RequestOptions): Promise<T> {
    const { url, method = 'GET', data, params, headers = {} } = opts;
    const qs = params
      ? '?' +
        Object.entries(params)
          .filter(([, v]) => v !== undefined && v !== null)
          .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
          .join('&')
      : '';
    const res = await fetch(url + qs, {
      method,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        ...headers,
      },
      body: data !== undefined ? JSON.stringify(data) : undefined,
    });
    if (!res.ok) {
      const err: Error & { response?: { status: number; data?: unknown } } = new Error(
        `HTTP ${res.status} on ${method} ${url}`,
      );
      let body: unknown = undefined;
      try {
        body = await res.json();
      } catch {
        /* non-JSON body */
      }
      err.response = { status: res.status, data: body };
      throw err;
    }
    if (res.status === 204) return undefined as T;
    return (await res.json()) as T;
  },
};
