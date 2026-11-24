import { useCallback, useEffect, useState } from 'react';

// Load something from the back end once per key and keep it in memory while the tab is open
// (the disease facts don't change, so the Home and Diseases pages share one copy).
const cache = new Map();

export function useLoad(key, load) {
  const [state, setState] = useState(() =>
    cache.has(key) ? { data: cache.get(key), error: null, loading: false } : { data: null, error: null, loading: true },
  );
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (cache.has(key)) {
      setState({ data: cache.get(key), error: null, loading: false });
      return undefined;
    }
    let stopped = false;
    setState({ data: null, error: null, loading: true });
    load()
      .then((data) => {
        cache.set(key, data);
        if (!stopped) setState({ data, error: null, loading: false });
      })
      .catch((error) => !stopped && setState({ data: null, error, loading: false }));
    return () => {
      stopped = true;
    };
    // `load` is a new function on every render; the key says what is loaded
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, attempt]);

  const retry = useCallback(() => setAttempt((n) => n + 1), []);
  return { ...state, retry };
}
