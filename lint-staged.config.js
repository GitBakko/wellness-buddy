// lint-staged config — runs on staged files only (D-09)
export default {
  'frontend/**/*.{ts,tsx}': [
    'pnpm --filter frontend lint --fix --max-warnings=0',
    'prettier --write',
  ],
  'frontend/**/*.{css,md,json}': ['prettier --write'],
  'backend/**/*.py': [
    () => 'cd backend && uv run ruff check --fix',
    () => 'cd backend && uv run ruff format',
  ],
};
