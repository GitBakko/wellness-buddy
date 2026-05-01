// frontend/src/db/migrations.ts
// Dexie schema migration contract (PITFALLS #5).
//
// Future schema bumps (v2+) MUST follow this DROP-and-refetch pattern:
//
//   db.version(2).stores({
//     cache_today: 'date, user_id, status_indicator',  // new field
//   }).upgrade(async (tx) => {
//     await tx.table('cache_today').clear();   // DROP, never migrate data in place
//   });
//
// Contract invariants:
//   - mutation_queue is OPAQUE — never has its shape changed across schema versions.
//     It stores HTTP {endpoint, method, body} so any pending writes survive
//     cache schema bumps and re-flush against whatever endpoint shape ships.
//   - cache_* tables are read-only mirrors of server data — server is canonical
//     truth. Migrations DROP cached rows and re-fetch on next access; do not
//     attempt to transform old rows into the new shape (silent corruption risk
//     when user types diverge between sessions).
//   - All IDs are server-generated UUIDs (string). Never use Dexie auto-increment.
//
// Phase 1 ships v1 only. This file documents the contract for Phase 2+ to
// keep PITFALLS #5 enforceable in code review.
export {};
