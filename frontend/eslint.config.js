// ESLint 9 flat config — D-09
// Note: plugins (@eslint/js, typescript-eslint, eslint-plugin-react, eslint-plugin-react-hooks)
// are installed in Plan 05a alongside the rest of the frontend dev deps. This file
// declares the contract; lint commands will fail with module-not-found until then.
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import reactPlugin from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';

export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    plugins: { react: reactPlugin, 'react-hooks': reactHooks },
    settings: { react: { version: 'detect' } },
    languageOptions: {
      parserOptions: { ecmaFeatures: { jsx: true } },
      globals: { window: 'readonly', document: 'readonly', console: 'readonly' },
    },
    rules: {
      ...reactPlugin.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      'react/react-in-jsx-scope': 'off',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      // Pitfall #10 — ban hardcoded hex outside theme.css (FND-04, UI-01)
      'no-restricted-syntax': [
        'error',
        {
          selector:
            "Literal[value=/^#([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/]",
          message:
            'Hardcoded hex colors forbidden — use Tailwind 4 @theme tokens (UI-01).',
        },
      ],
    },
  },
  {
    ignores: [
      'dist/',
      'node_modules/',
      'src/styles/theme.css',
      // Config files using CommonJS conventions — not part of source ESM tree.
      '*.cjs',
      '.prettierrc.cjs',
      'lighthouserc.json',
    ],
  },
];
