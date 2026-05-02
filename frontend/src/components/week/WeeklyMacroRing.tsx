// frontend/src/components/week/WeeklyMacroRing.tsx
// Plan 02-02 — weekly aggregator hero ring (replicates MacroRing.tsx for /settimana).
//
// UI-SPEC §6.2 anatomy:
//   - 4 concentric SVG rings (radii 86 / 68 / 54 / 40):
//       outer  kcal     — leaf-100 track, leaf-500 progress
//       inner1 protein  — blueberry-50 track, blueberry-500 progress
//       inner2 carbs    — carb-soft track, leaf-700 progress
//       inner3 fat      — amber-50 track, amber-500 progress
//   - Center: italianNumberInt(consumedKcal) (Plus Jakarta 800, NOT Instrument Serif)
//             + caption "kcal · settimana" (uppercase, --color-text-muted)
//             + subtitle "su {target}" (Plus Jakarta 500 13px)
//   - ARIA: role="img" + aria-label using copy.week.weeklyMacroRingAria
//
// All copy from copy.it.ts week.* namespace; all colors via @theme tokens.

import { copy } from '@/i18n/copy.it';
import { italianNumberInt } from '@/lib/format';

interface MacroValue {
  current: number;
  target: number;
}

interface Props {
  kcalConsumed: number;
  kcalTarget: number;
  protein: MacroValue;
  carbs: MacroValue;
  fat: MacroValue;
  /** Completed meals this week (for ARIA label "{done} pasti su {total} completati"). */
  completedMeals: number;
  /** Total meals this week (typically 28 = 7 × 4). */
  totalMeals: number;
  size?: number;
}

function clamp(x: number, lo: number, hi: number): number {
  if (!Number.isFinite(x)) return lo;
  return Math.min(Math.max(x, lo), hi);
}

function dasharray(radius: number, ratio: number): string {
  const circ = 2 * Math.PI * radius;
  const filled = clamp(ratio, 0, 1) * circ;
  return `${filled.toFixed(2)} ${circ.toFixed(2)}`;
}

export function WeeklyMacroRing({
  kcalConsumed,
  kcalTarget,
  protein,
  carbs,
  fat,
  completedMeals,
  totalMeals,
  size = 220,
}: Props): React.ReactElement {
  const kcalRatio = kcalTarget > 0 ? kcalConsumed / kcalTarget : 0;
  const proteinRatio =
    protein.target > 0 ? protein.current / protein.target : 0;
  const carbsRatio = carbs.target > 0 ? carbs.current / carbs.target : 0;
  const fatRatio = fat.target > 0 ? fat.current / fat.target : 0;

  const consumedLabel = italianNumberInt(Math.max(0, Math.round(kcalConsumed)));
  const targetLabel = italianNumberInt(Math.max(0, Math.round(kcalTarget)));

  const ariaLabel = copy.week.weeklyMacroRingAria
    .replace('{consumed}', consumedLabel)
    .replace('{target}', targetLabel)
    .replace('{done}', String(completedMeals))
    .replace('{total}', String(totalMeals));

  const subtitle = copy.week.weeklyTotalSubtitle.replace(
    '{target}',
    targetLabel,
  );

  return (
    <div
      role="img"
      aria-label={ariaLabel}
      style={{ width: size, height: size }}
      className="relative"
    >
      <svg
        viewBox="0 0 200 200"
        className="block w-full h-full"
        aria-hidden="true"
      >
        {/* Outer track + arc — kcal */}
        <circle
          cx="100"
          cy="100"
          r="86"
          fill="none"
          stroke="var(--color-leaf-100)"
          strokeWidth="12"
        />
        <circle
          cx="100"
          cy="100"
          r="86"
          fill="none"
          stroke="var(--color-leaf-500)"
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={dasharray(86, kcalRatio)}
          transform="rotate(-90 100 100)"
        />

        {/* Protein ring */}
        <circle
          cx="100"
          cy="100"
          r="68"
          fill="none"
          stroke="var(--color-blueberry-50)"
          strokeWidth="6"
        />
        <circle
          cx="100"
          cy="100"
          r="68"
          fill="none"
          stroke="var(--color-blueberry-500)"
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={dasharray(68, proteinRatio)}
          transform="rotate(-90 100 100)"
        />

        {/* Carbs ring */}
        <circle
          cx="100"
          cy="100"
          r="54"
          fill="none"
          stroke="var(--color-carb-soft)"
          strokeWidth="6"
        />
        <circle
          cx="100"
          cy="100"
          r="54"
          fill="none"
          stroke="var(--color-leaf-700)"
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={dasharray(54, carbsRatio)}
          transform="rotate(-90 100 100)"
        />

        {/* Fat ring */}
        <circle
          cx="100"
          cy="100"
          r="40"
          fill="none"
          stroke="var(--color-amber-50)"
          strokeWidth="6"
        />
        <circle
          cx="100"
          cy="100"
          r="40"
          fill="none"
          stroke="var(--color-amber-500)"
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={dasharray(40, fatRatio)}
          transform="rotate(-90 100 100)"
        />
      </svg>

      {/* Center text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none gap-[2px]">
        <div
          className="font-extrabold tabular-nums leading-none text-[color:var(--color-text)]"
          style={{
            fontSize: '2.75rem',
            letterSpacing: '-0.03em',
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          {consumedLabel}
        </div>
        <div
          className="text-[color:var(--color-text-muted)] tabular-nums font-medium"
          style={{
            fontSize: '0.8125rem',
            marginTop: '4px',
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          {subtitle}
        </div>
        <div
          className="text-[color:var(--color-text-muted)] uppercase font-semibold"
          style={{
            fontSize: '0.6875rem',
            letterSpacing: '0.08em',
            marginTop: '2px',
          }}
        >
          {copy.week.weeklyKcalSuffix}
        </div>
      </div>
    </div>
  );
}
