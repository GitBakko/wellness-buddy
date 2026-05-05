// frontend/src/components/today/MealCarousel.tsx
//
// Plan 02-05 follow-up — swipeable carousel for alternative meal options
// (e.g., snack pomeriggio Opzione A/B/C/D, snack serale Alternativa 1/2/3).
//
// Mobile-first interaction:
//   * Native horizontal scroll-snap, 1 card visible at a time
//   * Swipe left/right to traverse alternatives (no library, pure CSS)
//   * IntersectionObserver tracks the active card
//   * The card's existing check button doubles as "scelta + segna pasto" so
//     no separate select CTA is needed (one gesture: swipe to the alternative
//     you want, tap check to mark it eaten).
//   * Desktop ≥768px gets prev/next caret buttons that scroll programmatically.
//
// Honors UI-04 (motion ≤250ms) + UI-05 (prefers-reduced-motion via CSS
// scroll-behavior) + UI-13 (44×44 tap target on caret + check button).
//
// All copy from copy.it.ts, all icons via @/components/icons facade, no hex.

import { useCallback, useEffect, useId, useRef, useState } from 'react';
import { CaretLeft, CaretRight } from '@/components/icons';
import { MealCard } from '@/components/today/MealCard';
import { copy } from '@/i18n/copy.it';
import type { TodayMeal } from '@/services/today';

interface Props {
  /** ≥2 alternative options for the same logical meal slot. */
  options: TodayMeal[];
  /** Caption shown above the carousel (e.g., "Spuntino pomeriggio"). */
  slotLabel: string;
  /** Called when user taps the completion check on the active card. */
  onToggleComplete: (mealType: string) => void;
  /** Disabled state forwarded to the active card's check button. */
  disabled?: boolean;
}

function fillTemplate(template: string, vars: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (_match, key: string) =>
    vars[key] !== undefined ? String(vars[key]) : '',
  );
}

export function MealCarousel({
  options,
  slotLabel,
  onToggleComplete,
  disabled,
}: Props): React.ReactElement {
  const trackRef = useRef<HTMLDivElement>(null);
  const cardRefs = useRef<(HTMLDivElement | null)[]>([]);
  const [activeIdx, setActiveIdx] = useState(0);
  const headingId = useId();

  // Track which card is centered via IntersectionObserver.
  useEffect(() => {
    const track = trackRef.current;
    if (!track) return;
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (!visible) return;
        const idx = cardRefs.current.findIndex((el) => el === visible.target);
        if (idx >= 0) setActiveIdx(idx);
      },
      { root: track, threshold: [0.5, 0.75, 1] },
    );
    cardRefs.current.forEach((el) => {
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, [options.length]);

  const scrollTo = useCallback((idx: number) => {
    const el = cardRefs.current[idx];
    if (!el) return;
    el.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
  }, []);

  const goPrev = useCallback(() => {
    if (activeIdx > 0) scrollTo(activeIdx - 1);
  }, [activeIdx, scrollTo]);

  const goNext = useCallback(() => {
    if (activeIdx < options.length - 1) scrollTo(activeIdx + 1);
  }, [activeIdx, options.length, scrollTo]);

  return (
    <section
      aria-labelledby={headingId}
      className="flex flex-col gap-[var(--spacing-2)]"
    >
      {/* Caption + indicator + desktop carets */}
      <header className="flex items-center justify-between gap-[var(--spacing-2)]">
        <div className="flex flex-col gap-[2px] min-w-0">
          <h3
            id={headingId}
            className="text-[var(--text-base)] font-semibold text-[color:var(--color-text)] m-0 truncate"
          >
            {slotLabel}
          </h3>
          <p className="text-[var(--text-caption)] text-[color:var(--color-text-muted)] m-0 flex items-center gap-[var(--spacing-2)]">
            <span>{copy.today.alternativesHeading}</span>
            <span aria-hidden="true">·</span>
            <span className="tabular-nums" aria-live="polite">
              {fillTemplate(copy.today.alternativesIndicator, {
                current: activeIdx + 1,
                total: options.length,
              })}
            </span>
          </p>
        </div>
        {/* Desktop carets — hidden on mobile (touch swipe is the gesture). */}
        <div className="hidden md:flex items-center gap-[var(--spacing-1)] flex-shrink-0">
          <button
            type="button"
            onClick={goPrev}
            disabled={activeIdx === 0}
            aria-label={copy.today.alternativesPrev}
            className="w-11 h-11 rounded-[var(--radius-pill)] inline-flex items-center justify-center transition-transform duration-[var(--duration-instant)] ease-[var(--ease-out-soft)] active:scale-[0.97] disabled:opacity-40 disabled:cursor-default"
            style={{
              border: '1.5px solid var(--color-border)',
              background: 'var(--color-surface)',
              color: 'var(--color-text)',
            }}
          >
            <CaretLeft size={20} weight="bold" aria-hidden="true" />
          </button>
          <button
            type="button"
            onClick={goNext}
            disabled={activeIdx === options.length - 1}
            aria-label={copy.today.alternativesNext}
            className="w-11 h-11 rounded-[var(--radius-pill)] inline-flex items-center justify-center transition-transform duration-[var(--duration-instant)] ease-[var(--ease-out-soft)] active:scale-[0.97] disabled:opacity-40 disabled:cursor-default"
            style={{
              border: '1.5px solid var(--color-border)',
              background: 'var(--color-surface)',
              color: 'var(--color-text)',
            }}
          >
            <CaretRight size={20} weight="bold" aria-hidden="true" />
          </button>
        </div>
      </header>

      {/* Scroll-snap track. -mx + px restores edge padding to the page gutter. */}
      <div
        ref={trackRef}
        role="group"
        aria-roledescription="carousel"
        className="flex overflow-x-auto snap-x snap-mandatory gap-[var(--spacing-3)] -mx-[var(--spacing-4)] px-[var(--spacing-4)] pb-[var(--spacing-1)] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden touch-pan-x"
        style={{ scrollPaddingInline: 'var(--spacing-4)' }}
      >
        {options.map((meal, idx) => {
          const isActive = idx === activeIdx;
          return (
            <div
              key={meal.variant_key}
              ref={(el) => {
                cardRefs.current[idx] = el;
              }}
              className="snap-center shrink-0 w-full transition-transform duration-[var(--duration-base)] ease-[var(--ease-out-soft)]"
              style={{
                transform: isActive ? 'scale(1)' : 'scale(0.97)',
                opacity: isActive ? 1 : 0.78,
              }}
              aria-current={isActive ? 'true' : undefined}
              aria-roledescription="slide"
              aria-label={fillTemplate(copy.today.alternativesIndicator, {
                current: idx + 1,
                total: options.length,
              })}
            >
              <MealCard
                meal={meal}
                onToggle={() => onToggleComplete(meal.meal_type)}
                disabled={disabled}
              />
            </div>
          );
        })}
      </div>

      {/* Dots indicator */}
      <nav
        aria-label={copy.today.alternativesHeading}
        className="flex items-center justify-center gap-[var(--spacing-2)] mt-[var(--spacing-1)]"
      >
        {options.map((meal, idx) => {
          const isActive = idx === activeIdx;
          return (
            <button
              key={meal.variant_key}
              type="button"
              onClick={() => scrollTo(idx)}
              aria-label={fillTemplate(copy.today.alternativesIndicator, {
                current: idx + 1,
                total: options.length,
              })}
              aria-current={isActive ? 'true' : undefined}
              className="inline-flex items-center justify-center min-w-11 min-h-11 transition-transform duration-[var(--duration-instant)] ease-[var(--ease-out-soft)] active:scale-[0.97]"
            >
              <span
                aria-hidden="true"
                className="block rounded-[var(--radius-pill)] transition-all duration-[var(--duration-base)] ease-[var(--ease-out-soft)]"
                style={{
                  width: isActive ? 18 : 6,
                  height: 6,
                  background: isActive
                    ? 'var(--color-leaf-500)'
                    : 'var(--color-border)',
                }}
              />
            </button>
          );
        })}
      </nav>
    </section>
  );
}
