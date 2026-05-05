// frontend/src/components/family/SharedBadge.tsx
// Plan 02-07 — Phosphor UsersThree pill + partner name + Radix tooltip.
//
// Shown ONLY when:
//   - meal.visibility === 'group_shared'
//   - meal.owner_user_id !== current_user_id
// (i.e. caller is reading a partner's shared meal — render the badge so the
//  user knows the source of truth is the partner, not themselves.)
//
// Anatomy (UI-SPEC §6.2):
//   ┌──────────────────┐
//   │ ⊙⊙⊙ {Marta}      │  ← UsersThree 14px + name (12px), tap for tooltip
//   └──────────────────┘   "Aggiornato da Marta · 2 minuti fa"
//
// Tone: NO `!`, no panic. Tap-scale 0.97/80ms (UI-13). All tokens (CLAUDE.md UI rule 1).

import { UsersThree } from '@/components/icons';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { copy } from '@/i18n/copy.it';
import { italianTimeAgo } from '@/lib/format';

interface SharedBadgeProps {
  partnerName: string;
  /** ISO timestamp of the most-recent variant write — used by tooltip. */
  updatedAt: string | null;
}

export function SharedBadge({ partnerName, updatedAt }: SharedBadgeProps): React.ReactElement {
  const ariaLabel = copy.family.sharedBadgeAria.replace('{partnerName}', partnerName);
  const tooltipText = updatedAt
    ? copy.family.sharedBadgeTooltipFormat
        .replace('{partnerName}', partnerName)
        .replace('{timeAgo}', italianTimeAgo(updatedAt))
    : ariaLabel;

  return (
    <TooltipProvider delayDuration={150}>
      <Tooltip>
        <TooltipTrigger asChild>
          <span
            role="img"
            aria-label={ariaLabel}
            data-testid="shared-badge"
            className="inline-flex items-center gap-[var(--spacing-1)] rounded-[var(--radius-pill)] bg-[var(--color-surface-muted)] px-[var(--spacing-2)] py-[2px] cursor-default transition-transform duration-[var(--duration-instant)] ease-[var(--ease-out-soft)] active:scale-[0.97]"
          >
            <UsersThree
              size={14}
              weight="regular"
              aria-hidden="true"
              className="text-[color:var(--color-text-muted)]"
            />
            <span className="text-[12px] font-medium text-[color:var(--color-text-muted)] truncate max-w-[12ch] leading-none">
              {partnerName}
            </span>
          </span>
        </TooltipTrigger>
        <TooltipContent side="top" sideOffset={4}>
          {tooltipText}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
