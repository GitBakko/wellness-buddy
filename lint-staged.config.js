// lint-staged config — runs on staged files only (D-09).
// `--no-warn-ignored` suppresses warnings when ESLint ignore patterns
// match a staged file (e.g., vite.config.ts is ignored by design but
// gets staged with src changes — the warning previously failed --max-warnings=0).
export default {
  'frontend/src/**/*.{ts,tsx}': [
    'pnpm --filter frontend exec eslint --fix --max-warnings=0 --no-warn-ignored',
    'prettier --write',
  ],
  'frontend/**/*.{css,md,json}': ['prettier --write'],
  'backend/**/*.py': [
    () => 'cd backend && uv run ruff check --fix',
    () => 'cd backend && uv run ruff format',
  ],
};
