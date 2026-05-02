// frontend/src/pages/History.tsx
// Phase 1 /storico — WeightChart on top, then tabbed history (Peso / Allenamenti).
// Italian-only. All copy from copy.it.ts.

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { WeightChart } from '@/components/weight/WeightChart';
import { WeightHistoryTable } from '@/components/weight/WeightHistoryTable';
import { WorkoutHistoryTable } from '@/components/workout/WorkoutHistoryTable';
import { useWeights } from '@/services/weight';

export default function History(): React.ReactElement {
  const { data: weights, isLoading } = useWeights();

  return (
    <main className="p-[var(--spacing-4)] flex flex-col gap-[var(--spacing-6)] max-w-3xl mx-auto">
      <header className="flex flex-col gap-[var(--spacing-1)]">
        <h1 className="text-[length:var(--text-display)] font-bold tracking-tight text-[color:var(--color-text)] m-0">
          Storico
        </h1>
      </header>

      {!isLoading && weights && weights.length > 0 && (
        <section aria-label="Andamento peso">
          <WeightChart
            data={weights.map((w) => ({ date: w.date, weight_kg: w.weight_kg }))}
          />
        </section>
      )}

      <Tabs defaultValue="weight" className="w-full">
        <TabsList className="w-full">
          <TabsTrigger value="weight" className="flex-1">Peso</TabsTrigger>
          <TabsTrigger value="workout" className="flex-1">Allenamenti</TabsTrigger>
        </TabsList>
        <TabsContent value="weight">
          <WeightHistoryTable />
        </TabsContent>
        <TabsContent value="workout">
          <WorkoutHistoryTable />
        </TabsContent>
      </Tabs>
    </main>
  );
}
