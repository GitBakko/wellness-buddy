// frontend/src/components/ai/AIWidget.tsx
// AI-05 (locked placeholder Phase 1) + AI-06 (WebSocket/SSE scaffold for Phase 5).
// UI-SPEC §6.3 AIWidgetPlaceholder + §7.2 ai copy.
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
import { Card } from '@/components/ui/card';
import { copy } from '@/i18n/copy.it';
import { Bot } from 'lucide-react';

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
    <Card
      className="p-[var(--spacing-4)] flex items-center gap-[var(--spacing-3)]"
      aria-label={copy.ai.placeholderHeading}
      role="region"
    >
      <Bot
        size={24}
        strokeWidth={1.75}
        aria-hidden="true"
        className="text-[var(--color-neutral-500)]"
      />
      <div className="flex flex-col">
        <span className="text-[var(--text-base)] font-[600]">
          {copy.ai.placeholderHeading}
        </span>
        <span className="text-[var(--text-caption)] text-[color:var(--color-text-muted)]">
          {copy.ai.placeholderBody}
        </span>
      </div>
    </Card>
  );
}
