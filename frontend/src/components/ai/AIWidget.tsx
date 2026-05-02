// frontend/src/components/ai/AIWidget.tsx
// AI-05 (locked placeholder Phase 1) + AI-06 (WebSocket/SSE scaffold for Phase 5).
// UI-SPEC §6.3 AIWidgetPlaceholder + §7.2 ai copy.
// Plan 01-09 — Lifesum Pure restyle: Phosphor Sparkle in leaf-100 round chip,
// soft dashed border (mockup A `.lp-ai`), Plus Jakarta 600 title (NOT serif —
// the display-serif escape hatch is reserved for the /today greeting per
// UI-SPEC §3.2 "max 1 display-serif per page").
//
// T-AI-01 mitigation:
//   - ZERO data interpolation; only static copy.ai.* strings
//   - WebSocket scaffold is COMMENTED, never instantiated
//   - No /api/ai/* network calls fire in Phase 1
//
// Phase 5 unlock plan:
//   - Replace placeholder body with chat widget
//   - Detect capabilities via GET /api/ai/capabilities (returns 501 in Sprint 1)
//   - Stream tokens via SSE EventSource('/api/ai/chat/stream')
import { Sparkle } from '@/components/icons';
import { copy } from '@/i18n/copy.it';

export function AIWidget() {
  // Phase 5 stub — connection scaffold, kept commented so lint stays clean
  // and no network calls fire in Phase 1.
  // useEffect(() => {
  //   if (!aiCapabilities.streaming) return;
  //   const es = new EventSource('/api/ai/chat/stream');
  //   es.onmessage = (ev) => { /* render token */ };
  //   return () => es.close();
  // }, []);

  return (
    <section
      className="bg-[var(--color-surface)] rounded-[var(--radius-sheet)] p-[var(--spacing-4)] flex items-center gap-[var(--spacing-3)] opacity-[0.78]"
      style={{
        border: '1px dashed var(--color-border)',
      }}
      aria-label={copy.ai.placeholderHeading}
      role="region"
    >
      <span
        className="w-10 h-10 rounded-[var(--radius-pill)] inline-flex items-center justify-center flex-shrink-0 bg-[var(--color-leaf-100)] text-[color:var(--color-leaf-700)]"
        aria-hidden="true"
      >
        <Sparkle size={20} weight="fill" aria-hidden="true" />
      </span>
      <div className="flex flex-col gap-[2px] min-w-0">
        <h3 className="text-[var(--text-base)] font-semibold text-[color:var(--color-text)] m-0">
          {copy.ai.placeholderHeading}
        </h3>
        <p className="text-[var(--text-caption)] text-[color:var(--color-text-muted)] m-0 font-medium">
          {copy.ai.placeholderBody}
        </p>
      </div>
    </section>
  );
}
