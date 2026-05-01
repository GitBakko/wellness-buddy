// Class-name helper — combines clsx (conditional classes) with
// tailwind-merge (resolves Tailwind utility conflicts intelligently).
// shadcn/ui primitives import this as `@/lib/cn`.
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
