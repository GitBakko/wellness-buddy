// frontend/src/db/dexie.ts
// Dexie v1 schema — FND-07.
// Source: 01-RESEARCH.md Pattern 5.
//
// PITFALLS #5 contract (locked):
//   - mutation_queue stores OPAQUE HTTP requests {endpoint, method, body} —
//     never domain objects. Survives any cache_* schema migration.
//   - cache_* tables are read-only mirrors; schema bumps DROP + re-fetch
//     (never migrate data in place — see migrations.ts header comment).
//   - All IDs are server-generated UUIDs (never auto-increment).
//
// PITFALLS #1 (iOS storage eviction) mitigation hook:
//   - isEmptyButShouldHaveData() detects Dexie-empty-but-JWT-valid state.
//     Used by useDexieResync to trigger full server resync on app boot.

import Dexie, { type EntityTable } from 'dexie';
import type {
  CachedUser,
  CachedPlan,
  CachedToday,
  CachedWorkoutLog,
  CachedWeightLog,
  QueuedMutation,
  Draft,
} from './schema';

export class WellnessBuddyDB extends Dexie {
  cache_users!: EntityTable<CachedUser, 'id'>;
  cache_plans!: EntityTable<CachedPlan, 'id'>;
  cache_today!: EntityTable<CachedToday, 'date'>;
  cache_workout_log!: EntityTable<CachedWorkoutLog, 'id'>;
  cache_weight_log!: EntityTable<CachedWeightLog, 'id'>;
  mutation_queue!: EntityTable<QueuedMutation, 'id'>;
  drafts!: EntityTable<Draft, 'key'>;

  constructor() {
    super('wellness-buddy');
    this.version(1).stores({
      cache_users: 'id, email',
      cache_plans: 'id, user_id, is_active',
      cache_today: 'date, user_id',
      cache_workout_log: 'id, [user_id+date]',
      cache_weight_log: 'id, [user_id+date]',
      mutation_queue: 'id, created_at',
      drafts: 'key, updated_at',
    });
  }

  /**
   * FND-08, PITFALLS #1 — detect Dexie-empty-but-JWT-valid → trigger full resync.
   * Returns true when neither cached users nor cached plans exist (proxy for
   * "iOS evicted storage; restore from server").
   */
  async isEmptyButShouldHaveData(): Promise<boolean> {
    const userCount = await this.cache_users.count();
    const planCount = await this.cache_plans.count();
    return userCount === 0 && planCount === 0;
  }
}

export const db = new WellnessBuddyDB();
