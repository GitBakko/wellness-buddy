// frontend/src/components/plans/PlanPreviewMd.tsx
// Plan 04 Task 3 — render parsed markdown safely.
//
// react-markdown is safe-by-default: <script> / <iframe> never render. We use
// remark-gfm so tables in the plan render with semantic HTML. This component
// MUST never use `dangerouslySetInnerHTML` (T-XSS-01).

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface PlanPreviewMdProps {
  markdown: string;
}

export function PlanPreviewMd({ markdown }: PlanPreviewMdProps): React.ReactElement {
  return (
    <div className="flex flex-col gap-[var(--spacing-3)] text-[length:var(--text-base)] leading-[var(--leading-base)] text-[var(--color-text)]">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h1 className="text-[length:var(--text-display)] font-semibold leading-[var(--leading-display)] mt-[var(--spacing-4)]">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-[length:var(--text-heading)] font-semibold leading-[var(--leading-heading)] mt-[var(--spacing-4)]">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-[length:var(--text-base)] font-semibold mt-[var(--spacing-3)]">
              {children}
            </h3>
          ),
          ul: ({ children }) => (
            <ul className="flex flex-col gap-[var(--spacing-1)] pl-[var(--spacing-5)] list-disc">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="flex flex-col gap-[var(--spacing-1)] pl-[var(--spacing-5)] list-decimal">
              {children}
            </ol>
          ),
          p: ({ children }) => (
            <p className="text-[length:var(--text-base)]">{children}</p>
          ),
        }}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  );
}
