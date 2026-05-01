// frontend/src/services/auth.ts
// Auth service helpers — wraps apiClient calls and pushes results into the Zustand store.
//
// `login` is exported as both a named export and a default export so callers
// can import either shape. `logout` is forgiving: client-side state is cleared
// even if the server call fails (offline, 401, etc.).
//
// Source: AUTH-04 (access in memory), AUTH-12 (envelope), Plan 03 <action>.

import { apiClient } from '@/services/api';
import type { AuthUser } from '@/stores/auth';
import { useAuthStore } from '@/stores/auth';

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const tokenRes = await apiClient.request<TokenResponse>({
    url: '/api/auth/login',
    method: 'POST',
    data: { email, password },
  });
  useAuthStore.getState().setAccessToken(tokenRes.access_token);
  // Eagerly populate the user profile so the post-login UI renders without spinner.
  const me = await apiClient.request<AuthUser>({ url: '/api/auth/me' });
  useAuthStore.getState().setUser(me);
  return tokenRes;
}

export async function logout(): Promise<void> {
  try {
    await apiClient.request<void>({ url: '/api/auth/logout', method: 'POST' });
  } finally {
    useAuthStore.getState().clear();
  }
}

export async function fetchMe(): Promise<AuthUser> {
  const me = await apiClient.request<AuthUser>({ url: '/api/auth/me' });
  useAuthStore.getState().setUser(me);
  return me;
}

export async function registerWithInvite(
  token: string,
  email: string,
  username: string,
  password: string,
): Promise<TokenResponse> {
  const tokenRes = await apiClient.request<TokenResponse>({
    url: '/api/auth/register',
    method: 'POST',
    data: { token, email, username, password },
  });
  useAuthStore.getState().setAccessToken(tokenRes.access_token);
  await fetchMe();
  return tokenRes;
}
