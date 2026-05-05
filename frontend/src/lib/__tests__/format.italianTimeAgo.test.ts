// frontend/src/lib/__tests__/format.italianTimeAgo.test.ts
// Plan 02-07 — italianTimeAgo helper covers the SharedBadge tooltip + 409 toast.
// Locks Italian copy + plural agreement (1 minuto vs 2 minuti, 1 ora vs ore).

import { describe, expect, it } from 'vitest';

import { italianTimeAgo } from '@/lib/format';

describe('italianTimeAgo (Plan 02-07)', () => {
  const now = new Date('2026-05-05T12:00:00Z');

  it("returns 'adesso' for diffs under one minute", () => {
    expect(italianTimeAgo(new Date('2026-05-05T11:59:30Z'), now)).toBe('adesso');
    // Future-tense (clock skew) collapses to 'adesso' so toasts never read 'tra X'.
    expect(italianTimeAgo(new Date('2026-05-05T12:00:30Z'), now)).toBe('adesso');
  });

  it("returns '1 minuto fa' singular at exactly 1 min", () => {
    expect(italianTimeAgo(new Date('2026-05-05T11:59:00Z'), now)).toBe('1 minuto fa');
  });

  it("returns '2 minuti fa' plural at 2 minutes", () => {
    expect(italianTimeAgo(new Date('2026-05-05T11:58:00Z'), now)).toBe('2 minuti fa');
  });

  it("returns '5 minuti fa' plural at 5 minutes", () => {
    expect(italianTimeAgo(new Date('2026-05-05T11:55:00Z'), now)).toBe('5 minuti fa');
  });

  it("returns '1 ora fa' singular at exactly 1 hour", () => {
    expect(italianTimeAgo(new Date('2026-05-05T11:00:00Z'), now)).toBe('1 ora fa');
  });

  it("returns '5 ore fa' plural at 5 hours", () => {
    expect(italianTimeAgo(new Date('2026-05-05T07:00:00Z'), now)).toBe('5 ore fa');
  });

  it("returns 'ieri' for diffs in the 24..47h window", () => {
    expect(italianTimeAgo(new Date('2026-05-04T11:00:00Z'), now)).toBe('ieri');
  });

  it("returns '3 giorni fa' for 3-day-old timestamps", () => {
    expect(italianTimeAgo(new Date('2026-05-02T12:00:00Z'), now)).toBe('3 giorni fa');
  });

  it('accepts ISO string input as well as Date', () => {
    expect(italianTimeAgo('2026-05-05T11:55:00Z', now)).toBe('5 minuti fa');
  });

  it("returns 'adesso' on garbage input (NaN diff)", () => {
    expect(italianTimeAgo('not-a-date', now)).toBe('adesso');
  });
});
