// frontend/src/db/schema.ts
// Dexie v1 table types (FND-07).
// Source: 01-RESEARCH.md Pattern 5.
//
// Contract (PITFALLS #5):
//   - All IDs are server-generated UUIDs (string), never auto-increment.
//   - cache_* tables are read-only mirrors of server data; bumps DROP + re-fetch.
//   - mutation_queue stores OPAQUE HTTP requests {endpoint, method, body} —
//     never domain shapes. Survives any cache_* schema migration.

export interface CachedUser {
  id: string;
  email: string;
  username: string;
  role: 'admin' | 'user';
  group_id: string | null;
  timezone: string;
}

export interface CachedPlan {
  id: string;
  user_id: string;
  name: string;
  parsed_json: unknown;
  uploaded_at: string;
  is_active: boolean;
}

export interface CachedToday {
  date: string;
  user_id: string;
  meals_completed: Record<string, boolean>;
  fetched_at: string;
}

export interface CachedWorkoutLog {
  id: string;
  user_id: string;
  date: string;
  trained: boolean;
  duration_min: number | null;
  calories_burned: number | null;
  workout_type: string | null;
  notes: string | null;
  updated_at: string;
}

export interface CachedWeightLog {
  id: string;
  user_id: string;
  date: string;
  weight_kg: number;
  updated_at: string;
}

export interface QueuedMutation {
  id: string;
  endpoint: string;
  method: 'POST' | 'PATCH' | 'DELETE';
  body: unknown;
  created_at: number;
  retries: number;
  last_error: string | null;
}

export interface Draft {
  key: string;
  payload: unknown;
  updated_at: number;
}
