// frontend/src/db/__tests__/dexie.test.ts
// FND-07 — Dexie schema sanity (table count, UUID PKs, isEmpty heuristic,
// mutation_queue opacity).
//
// Uses fake-indexeddb/auto to give Dexie a real IDB in node.

import { describe, it, expect, beforeEach } from 'vitest';
import 'fake-indexeddb/auto';
import { db } from '@/db/dexie';

describe('Dexie schema v1 (FND-07)', () => {
  beforeEach(async () => {
    await db.delete();
    await db.open();
  });

  it('opens with all 7 tables', () => {
    const tableNames = db.tables.map((t) => t.name).sort();
    expect(tableNames).toEqual(
      [
        'cache_plans',
        'cache_today',
        'cache_users',
        'cache_weight_log',
        'cache_workout_log',
        'drafts',
        'mutation_queue',
      ].sort(),
    );
  });

  it('cache_users uses string id (server UUID, not auto-increment)', async () => {
    await db.cache_users.add({
      id: '11111111-1111-1111-1111-111111111111',
      email: 'a@b.it',
      username: 'a',
      role: 'user',
      group_id: null,
      timezone: 'Europe/Rome',
    });
    const row = await db.cache_users.get('11111111-1111-1111-1111-111111111111');
    expect(row?.email).toBe('a@b.it');
  });

  it('isEmptyButShouldHaveData returns true on empty DB', async () => {
    expect(await db.isEmptyButShouldHaveData()).toBe(true);
  });

  it('isEmptyButShouldHaveData returns false after user cached', async () => {
    await db.cache_users.add({
      id: '22222222-2222-2222-2222-222222222222',
      email: 'a@b.it',
      username: 'a',
      role: 'user',
      group_id: null,
      timezone: 'Europe/Rome',
    });
    expect(await db.isEmptyButShouldHaveData()).toBe(false);
  });

  it('mutation_queue stores opaque HTTP requests', async () => {
    await db.mutation_queue.add({
      id: crypto.randomUUID(),
      endpoint: '/api/weight',
      method: 'POST',
      body: { date: '2026-05-01', weight_kg: 75.3 },
      created_at: Date.now(),
      retries: 0,
      last_error: null,
    });
    const items = await db.mutation_queue.toArray();
    expect(items).toHaveLength(1);
    expect(items[0]!.endpoint).toBe('/api/weight');
    expect(items[0]!.method).toBe('POST');
  });

  it('cache_workout_log compound index [user_id+date] queryable', async () => {
    await db.cache_workout_log.bulkAdd([
      {
        id: 'w1',
        user_id: 'u1',
        date: '2026-05-01',
        trained: true,
        duration_min: 45,
        calories_burned: null,
        workout_type: 'corsa',
        notes: null,
        updated_at: '2026-05-01T10:00:00Z',
      },
      {
        id: 'w2',
        user_id: 'u1',
        date: '2026-05-02',
        trained: false,
        duration_min: null,
        calories_burned: null,
        workout_type: null,
        notes: null,
        updated_at: '2026-05-02T10:00:00Z',
      },
    ]);
    const day1 = await db.cache_workout_log
      .where('[user_id+date]')
      .equals(['u1', '2026-05-01'])
      .toArray();
    expect(day1).toHaveLength(1);
    expect(day1[0]!.workout_type).toBe('corsa');
  });
});
