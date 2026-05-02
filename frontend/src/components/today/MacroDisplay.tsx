// frontend/src/components/today/MacroDisplay.tsx
// Plan 01-09 Lifesum Pure macro pills (3-up grid: Prot · Carb · Grassi).
//
// Replaces the chip-row variant with the locked Lifesum layout — head row
// (color dot + uppercase short label) + value (Geist Mono tabular nums) +
// thin progress bar tinted with the macro family's color.
//
// Used in /today, sitting BELOW the MacroRing inside the same hero card.

import { copy } from '@/i18n/copy.it';
import { italianNumberInt } from '@/lib/format';

interface MacroValue {
  current: number;
  target: number;
}

interface Props {
  protein: MacroValue;
  carbs: MacroValue;
  fat: MacroValue;
}

interface PillSpec {
  label: string;
  dotVar: string;
  fillVar: string;
  current: number;
  target: number;
}

function pct(current: number, target: number): number {
  if (target <= 0) return 0;
  return Math.min(100, Math.max(0, (current / target) * 100));
}

function MacroPill({ spec }: { spec: PillSpec }): React.ReactElement {
  const widthPct = pct(spec.current, spec.target);
  return (
    <div
      className="flex flex-col gap-[var(--spacing-1)] p-[var(--spacing-3)] rounded-[var(--radius-sm)] bg-[var(--color-surface-muted)] min-w-0"
    >
      <div className="text-[var(--text-caption)] font-semibold uppercase tracking-[0.04em] text-[color:var(--color-text-muted)] flex items-center gap-[var(--spacing-1)]">
        <span
          aria-hidden="true"
          className="w-2 h-2 rounded-[var(--radius-pill)] flex-shrink-0"
          style={{ background: `var(${spec.dotVar})` }}
        />
        <span>{spec.label}</span>
      </div>
      <div className="text-[var(--text-base)] font-semibold tabular-nums text-[color:var(--color-text)]">
        {italianNumberInt(Math.round(spec.current))} / {italianNumberInt(Math.round(spec.target))} g
      </div>
      <div
        aria-hidden="true"
        className="h-1 rounded-[var(--radius-pill)] overflow-hidden bg-[var(--color-surface-muted)]"
        style={{ background: 'var(--color-neutral-100)' }}
      >
        <div
          className="h-full rounded-[var(--radius-pill)]"
          style={{
            width: `${widthPct.toFixed(2)}%`,
            background: `var(${spec.fillVar})`,
          }}
        />
      </div>
    </div>
  );
}

export function MacroDisplay({
  protein,
  carbs,
  fat,
}: Props): React.ReactElement {
  const pills: PillSpec[] = [
    {
      label: copy.today.macroProtShort,
      dotVar: '--color-blueberry-500',
      fillVar: '--color-blueberry-500',
      current: protein.current,
      target: protein.target,
    },
    {
      label: copy.today.macroCarbShort,
      dotVar: '--color-leaf-700',
      fillVar: '--color-leaf-700',
      current: carbs.current,
      target: carbs.target,
    },
    {
      label: copy.today.macroFatShort,
      dotVar: '--color-amber-500',
      fillVar: '--color-amber-500',
      current: fat.current,
      target: fat.target,
    },
  ];
  return (
    <div
      className="grid grid-cols-3 gap-[var(--spacing-2)] w-full"
      aria-label="Macronutrienti"
    >
      {pills.map((spec) => (
        <MacroPill key={spec.label} spec={spec} />
      ))}
    </div>
  );
}
