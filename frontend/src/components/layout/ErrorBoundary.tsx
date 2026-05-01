// frontend/src/components/layout/ErrorBoundary.tsx
// D-18 + UI-SPEC §6.2 — global error boundary with Italian fallback.
// Logs to /api/errors (best-effort, T-XSS-02 — no tokens, no payload data).
import { Component, type ReactNode } from 'react';
import { Button } from '@/components/ui/button';
import { copy } from '@/i18n/copy.it';
import { apiClient } from '@/services/api';

interface State {
  hasError: boolean;
  message: string;
}

export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { hasError: false, message: '' };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message };
  }

  componentDidCatch(error: Error): void {
    void apiClient
      .request({
        url: '/api/errors',
        method: 'POST',
        data: {
          message: error.message,
          stack: error.stack,
          url: window.location.href,
          user_agent: navigator.userAgent,
        },
      })
      .catch(() => {
        /* silent — error logging best-effort */
      });
  }

  render() {
    if (!this.state.hasError) return this.props.children;
    return (
      <main className="min-h-dvh flex items-center justify-center p-[var(--spacing-6)]">
        <div
          className="max-w-md flex flex-col gap-[var(--spacing-4)]"
          role="alert"
        >
          <h1 className="text-[var(--text-heading)] font-[600]">
            {copy.errors.boundaryHeading}
          </h1>
          <p className="text-[color:var(--color-text-muted)]">
            {copy.errors.boundaryBody}
          </p>
          <div className="flex gap-[var(--spacing-3)]">
            <Button onClick={() => window.location.reload()}>
              {copy.errors.boundaryReloadCta}
            </Button>
            <Button
              variant="ghost"
              onClick={() => {
                window.location.href = '/today';
              }}
            >
              {copy.errors.boundaryHomeCta}
            </Button>
          </div>
        </div>
      </main>
    );
  }
}
