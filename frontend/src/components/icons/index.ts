// frontend/src/components/icons/index.ts
// Plan 01-09 — Phosphor icon facade.
//
// Single import surface for ALL @phosphor-icons/react usage in the app.
// Reasons:
//   1. Future-proofing: a swap to lucide / hero-icons would touch this file only.
//   2. Tree-shaking discipline: re-exports keep bundlers honest about which
//      icons are actually used.
//   3. ESLint convention: components must `import { ... } from '@/components/icons'`,
//      never `from '@phosphor-icons/react'` directly. A grep gate verifies in CI:
//        grep -r "from '@phosphor-icons" frontend/src --include='*.tsx' --include='*.ts'
//          | grep -v "components/icons/index.ts"
//      MUST return empty.
//
// To add a new icon: add the export here, then import it via `@/components/icons`.
//
// Naming aliases:
//   Phosphor's `User` clashes with our `User` model type — re-export as `UserIcon`
//   to avoid noisy renames at every callsite.
export {
  Leaf,
  BowlFood,
  Fish,
  Cookie,
  OrangeSlice,
  PersonSimpleRun,
  Scales,
  House,
  CalendarBlank,
  CalendarDots,
  ShoppingCart,
  ClockCounterClockwise,
  User as UserIcon,
  CheckCircle,
  Check,
  Circle,
  Sparkle,
  ArrowDown,
  ArrowUp,
  UploadSimple,
  Plus,
  Sun,
  Moon,
  X,
  PencilSimple,
  Trash,
  CaretDown,
  CaretUp,
  CaretLeft,
  CaretRight,
  // Phase 2 (Plan 02-02) — /settimana additions
  ArrowsClockwise,
} from '@phosphor-icons/react';
