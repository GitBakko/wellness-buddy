// frontend/src/lib/format.ts
// Italian formatting helpers (UI-18, UI-SPEC §7.1 conventions, CLAUDE.md UI rule 11):
//   - Numbers: Intl.NumberFormat('it-IT')         → "75,3" (comma decimal)
//   - Dates:   Intl.DateTimeFormat('it-IT')       → "lun 5 mag" / "lunedì 5 maggio"
//   - Time:    24h ("19:30")
//   - Sort:    Intl.Collator('it') sensitivity:'base'  → diacritic-insensitive
//   - NFC:     normalize on save for equality/sort parity
//
// All Intl objects are constructed once at module load (cheap to reuse, expensive to allocate).
// Per RESEARCH "Don't Hand-Roll" + STACK list — never `toLocaleString()` ad-hoc.

const NUMBER_FMT = new Intl.NumberFormat('it-IT', { maximumFractionDigits: 2 });
const NUMBER_FMT_WHOLE = new Intl.NumberFormat('it-IT', {
  maximumFractionDigits: 0,
});
const DATE_FMT_SHORT = new Intl.DateTimeFormat('it-IT', {
  weekday: 'short',
  day: 'numeric',
  month: 'short',
});
const DATE_FMT_LONG = new Intl.DateTimeFormat('it-IT', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
});
const TIME_FMT = new Intl.DateTimeFormat('it-IT', {
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
});
const COLLATOR = new Intl.Collator('it', { sensitivity: 'base' });

/** Format a number with up to 2 decimals, Italian locale (comma decimal): 75.3 → "75,3". */
export const italianNumber = (n: number): string => NUMBER_FMT.format(n);

/** Format an integer, Italian locale (thousands separator dot): 1250 → "1.250". */
export const italianNumberInt = (n: number): string => NUMBER_FMT_WHOLE.format(n);

/** Short Italian date: Date → "lun 5 mag". Accepts ISO string too. */
export const italianDateShort = (d: Date | string): string =>
  DATE_FMT_SHORT.format(typeof d === 'string' ? new Date(d) : d);

/** Long Italian date: Date → "lunedì 5 maggio". Accepts ISO string too. */
export const italianDateLong = (d: Date | string): string =>
  DATE_FMT_LONG.format(typeof d === 'string' ? new Date(d) : d);

/** 24h Italian time: Date → "19:30". Accepts ISO string too. */
export const italianTime = (d: Date | string): string =>
  TIME_FMT.format(typeof d === 'string' ? new Date(d) : d);

/** Italian collator (diacritic-insensitive). Use for `[...].sort(italianCollator.compare)`. */
export const italianCollator = COLLATOR;

/**
 * Parse a user-typed Italian decimal: "75,3" → 75.3.
 * Accepts both Italian comma and English dot. Returns NaN on invalid.
 * Used by input fields where the user types `75,3 kg`.
 */
export const parseItalianDecimal = (s: string): number => {
  const normalized = s.replace(',', '.').trim();
  if (normalized === '') return NaN;
  const n = Number(normalized);
  return Number.isFinite(n) ? n : NaN;
};

/**
 * NFC-normalize an Italian string for storage/equality/sorting parity.
 * Apply at save-time (form submit) so DB never has mixed forms ("caffè" vs "café").
 */
export const nfc = (s: string): string => s.normalize('NFC');

/** Convenience: format weight in kg with Italian comma decimal: 75.3 → "75,3 kg". */
export const formatWeight = (kg: number): string => `${italianNumber(kg)} kg`;

/** Convenience: format calories with Italian thousands separator: 1250 → "1.250 kcal". */
export const formatCalories = (kcal: number): string => `${italianNumberInt(kcal)} kcal`;
