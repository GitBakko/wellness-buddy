// frontend/src/tests/unit/plans/plansService.test.ts
// Plan 01-04 Task 3: services/plans.ts unit tests.
//
// Covers: listPlans + uploadPlan + activatePlan + diffPlan response shapes
// and that uploadPlan uses FormData + multipart semantics.

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { useAuthStore } from '@/stores/auth';

describe('services/plans', () => {
  let originalFetch: typeof globalThis.fetch;

  beforeEach(() => {
    originalFetch = globalThis.fetch;
    useAuthStore.setState({ accessToken: 'test-access-token', user: null });
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
    useAuthStore.setState({ accessToken: null, user: null });
    vi.restoreAllMocks();
  });

  it('listPlans returns array of plans', async () => {
    const mockPlans = [
      { id: 'p1', name: 'Plan A', uploaded_at: '2026-05-01T10:00:00Z', is_active: false },
      { id: 'p2', name: 'Plan B', uploaded_at: '2026-05-02T10:00:00Z', is_active: true },
    ];
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockPlans,
    } as Response);

    const { listPlans } = await import('@/services/plans');
    const plans = await listPlans();
    expect(plans).toHaveLength(2);
    expect(plans[0]?.name).toBe('Plan A');
  });

  it('uploadPlan sends multipart FormData with file + name + bearer', async () => {
    const mockResponse = {
      id: 'new-plan-id',
      name: 'Test',
      uploaded_at: '2026-05-01T10:00:00Z',
      is_active: false,
      parse_warnings: [],
      unrecognized_headings: [],
    };
    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => mockResponse,
    } as Response);
    globalThis.fetch = fetchSpy;

    const { uploadPlan } = await import('@/services/plans');
    const file = new File(['# Piano test'], 'plan.md', { type: 'text/markdown' });
    const result = await uploadPlan(file, 'Test');

    expect(result.id).toBe('new-plan-id');
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    const callArgs = fetchSpy.mock.calls[0];
    expect(callArgs?.[0]).toBe('/api/plans/upload');
    const init = callArgs?.[1] as RequestInit;
    expect(init.method).toBe('POST');
    expect(init.body).toBeInstanceOf(FormData);
    const fd = init.body as FormData;
    expect(fd.get('name')).toBe('Test');
    expect(fd.get('file')).toBeInstanceOf(File);
    const headers = init.headers as Record<string, string>;
    expect(headers.Authorization).toBe('Bearer test-access-token');
  });

  it('uploadPlan throws shaped error on non-OK response', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({ detail: 'Solo file .md sono supportati.', code: 'bad_file_type' }),
    } as Response);

    const { uploadPlan } = await import('@/services/plans');
    const file = new File(['x'], 'plan.txt', { type: 'text/plain' });
    await expect(uploadPlan(file, 'Test')).rejects.toMatchObject({
      response: {
        status: 400,
        data: { code: 'bad_file_type' },
      },
    });
  });

  it('activatePlan POSTs to /api/plans/{id}/activate', async () => {
    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ id: 'p1', name: 'A', is_active: true }),
    } as Response);
    globalThis.fetch = fetchSpy;

    const { activatePlan } = await import('@/services/plans');
    const result = await activatePlan('p1');
    expect(result.is_active).toBe(true);
    const url = fetchSpy.mock.calls[0]?.[0] as string;
    expect(url).toBe('/api/plans/p1/activate');
  });

  it('diffPlan returns added/removed/changed shape', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        added: ['dinners'],
        removed: ['lunches'],
        changed: ['breakfast'],
      }),
    } as Response);

    const { diffPlan } = await import('@/services/plans');
    const result = await diffPlan('p1');
    expect(result.added).toEqual(['dinners']);
    expect(result.removed).toEqual(['lunches']);
    expect(result.changed).toEqual(['breakfast']);
  });
});
