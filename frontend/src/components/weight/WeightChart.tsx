// frontend/src/components/weight/WeightChart.tsx
// UI-08 + PITFALLS#8 — Recharts in dark mode requires CSS variable colors
// (the library bakes the resolved color into SVG attributes at render time;
// hex literals would freeze at the value sampled in light mode and never flip
// when the user toggles dark). Stroke / fill / grid all reference @theme tokens.
//
// Phase 1 chart: simple line of weight_kg over date. Domain auto-clamps to
// [min-1, max+1] so the line is centered (not pinned to chart edge). Tolerance
// band (±0.5 kg/week) and projection dotted line are deferred to Phase 3
// alongside the trend overlay (WEIGHT-02 lives there).

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { italianDateShort, italianNumber } from '@/lib/format';

export interface WeightPoint {
  date: string; // ISO YYYY-MM-DD
  weight_kg: number;
}

interface Props {
  data: WeightPoint[];
  height?: number;
}

export function WeightChart({ data, height = 280 }: Props): React.ReactElement {
  const sorted = [...data].sort((a, b) => a.date.localeCompare(b.date));

  return (
    <div
      style={{ width: '100%', height }}
      role="img"
      aria-label="Andamento del peso nel tempo"
    >
      <ResponsiveContainer>
        <LineChart data={sorted} margin={{ top: 16, right: 16, bottom: 8, left: 8 }}>
          <CartesianGrid
            stroke="var(--color-neutral-200)"
            strokeDasharray="3 3"
          />
          <XAxis
            dataKey="date"
            stroke="var(--color-neutral-500)"
            tickFormatter={(d) => italianDateShort(String(d))}
            tick={{ fill: 'var(--color-text-muted)', fontSize: 12 }}
          />
          <YAxis
            stroke="var(--color-neutral-500)"
            tickFormatter={(n) => italianNumber(Number(n))}
            domain={['dataMin - 1', 'dataMax + 1']}
            tick={{ fill: 'var(--color-text-muted)', fontSize: 12 }}
          />
          <Tooltip
            contentStyle={{
              background: 'var(--color-bg-elev)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--color-text)',
            }}
            formatter={(v) => [`${italianNumber(Number(v))} kg`, 'Peso']}
            labelFormatter={(d) => italianDateShort(String(d))}
          />
          <Line
            type="monotone"
            dataKey="weight_kg"
            stroke="var(--color-neutral-700)"
            strokeWidth={2}
            dot={{ fill: 'var(--color-neutral-700)', r: 3 }}
            activeDot={{ r: 5, fill: 'var(--color-coral-500)' }}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
