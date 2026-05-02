// frontend/src/components/today/MacroRing.tsx
// Plan 01-09 — Lifesum-signature macro ring hero.
//
// Anatomy: 4 concentric SVG circles + 4 progress arcs at radii 86 / 68 / 54 / 40.
//   Outer (r=86, stroke=12): kcal — leaf-100 track, leaf-500 progress
//   Inner-1 (r=68, stroke=6): protein — blueberry-50 track, blueberry-500 progress
//   Inner-2 (r=54, stroke=6): carbs — carb-soft track, leaf-700 progress
//   Inner-3 (r=40, stroke=6): fat — amber-50 track, amber-500 progress
//
// Center: stacked text — kcal big (Plus Jakarta 800, NOT Instrument Serif —
// the serif escape hatch is reserved for the /today greeting, UI-SPEC §3.2).
//
// Accessibility:
//   role="img" + aria-label "{consumed} di {target} kcal oggi" so screen
//   readers get the headline metric. The 4 SVG arcs are aria-hidden via
//   parent role="img".
//
// All colors via tokens — zero hex.

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
  size?: number;
}

/** Clamp x into [lo, hi]. Returns lo if x is NaN. */
function clamp(x: number, lo: number, hi: number): number {
  if (!Number.isFinite(x)) return lo;
  return Math.min(Math.max(x, lo), hi);
}

/** Compute SVG stroke-dasharray "filled track" pair given radius + ratio in [0,1]. */
function dasharray(radius: number, ratio: number): string {
  const circ = 2 * Math.PI * radius;
  const filled = clamp(ratio, 0, 1) * circ;
  // Two-segment dasharray: filled portion, then a gap as long as the circumference
  // so the track wraps once. Rounded floats keep the SVG output stable for tests.
  return `${filled.toFixed(2)} ${circ.toFixed(2)}`;
}

export function MacroRing({
  kcalConsumed,
  kcalTarget,
  protein,
  carbs,
  fat,
  size = 220,
}: Props): React.ReactElement {
  // Compute ratios. Guard against 0-target → ratio 0 so we never divide by zero.
  const kcalRatio = kcalTarget > 0 ? kcalConsumed / kcalTarget : 0;
  const proteinRatio = protein.target > 0 ? protein.current / protein.target : 0;
  const carbsRatio = carbs.target > 0 ? carbs.current / carbs.target : 0;
  const fatRatio = fat.target > 0 ? fat.current / fat.target : 0;

  const consumedLabel = italianNumberInt(Math.max(0, Math.round(kcalConsumed)));
  const targetLabel = italianNumberInt(Math.max(0, Math.round(kcalTarget)));

  const ariaLabel = copy.today.macroRingAria
    .replace('{consumed}', consumedLabel)
    .replace('{target}', targetLabel);

  const subtitle = copy.today.macroKcalSubtitle.replace('{target}', targetLabel);

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

      {/* Center text — Plus Jakarta 800 for kcal value (NOT Instrument Serif) */}
      <div
        className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none gap-[2px]"
      >
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
          {copy.today.macroKcalSuffix}
        </div>
      </div>
    </div>
  );
}
