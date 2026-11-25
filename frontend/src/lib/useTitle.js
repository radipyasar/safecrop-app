import { useEffect } from 'react';

// The browser tab's title for a page: "Check a leaf · SafeCrop" (just "SafeCrop" on the home page).
export function useTitle(title) {
  useEffect(() => {
    document.title = title ? `${title} · SafeCrop` : 'SafeCrop';
  }, [title]);
}
