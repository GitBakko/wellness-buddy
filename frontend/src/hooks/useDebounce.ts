// frontend/src/hooks/useDebounce.ts
// Generic debounce hook — defers updating a value until `ms` ms after the last change.
// Used for search inputs, weight-input live preview, etc.

import { useEffect, useState } from 'react';

export function useDebounce<T>(value: T, ms: number): T {
  const [debounced, setDebounced] = useState<T>(value);

  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), ms);
    return () => clearTimeout(t);
  }, [value, ms]);

  return debounced;
}
