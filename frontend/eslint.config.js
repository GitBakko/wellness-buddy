// ESLint 9 flat config — D-09 + Pitfall #10 (hex-ban).
// Plugins installed via frontend devDependencies (Plan 05a).
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import reactPlugin from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import globals from 'globals';

export default [
  // Ignore generated/vendor & non-source files
  {
    ignores: [
      'dist/',
      'node_modules/',
      'src/styles/theme.css',
      'src/styles/globals.css',
      'public/',
      // Config files using CommonJS conventions — not part of source ESM tree.
      '*.config.js',
      '*.config.ts',
      '*.config.cjs',
      '*.config.mjs',
      '*.cjs',
      '.prettierrc.cjs',
      '.prettierrc.js',
      'lighthouserc.json',
      'vite.config.ts',
      'tsconfig*.json',
    ],
  },

  // Base JS rules
  js.configs.recommended,

  // TypeScript strict
  ...tseslint.configs.recommended,

  // App source rules
  {
    files: ['src/**/*.{ts,tsx}'],
    plugins: {
      react: reactPlugin,
      'react-hooks': reactHooks,
    },
    settings: {
      react: { version: 'detect' },
    },
    languageOptions: {
      ecmaVersion: 2023,
      sourceType: 'module',
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
      globals: {
        ...globals.browser,
        ...globals.es2023,
      },
    },
    rules: {
      ...reactPlugin.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      'react/react-in-jsx-scope': 'off',
      'react/prop-types': 'off',
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
      '@typescript-eslint/no-explicit-any': 'warn',
      // Pitfall #10 — ban hardcoded hex outside theme.css/globals.css (UI-01).
      // Matches #abc, #abcd, #abcdef, #abcdef12 only. Tokens must come from @theme.
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
];
