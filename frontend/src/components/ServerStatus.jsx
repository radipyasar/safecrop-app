import { useEffect, useState } from 'react';
import { getHealth } from '../api.js';

const CHECK_EVERY_MS = 30000;

// A small dot that says whether the back end answers. Asks once at the start, then every 30 seconds.
export default function ServerStatus() {
  const [state, setState] = useState({ status: 'checking', error: '' });

  useEffect(() => {
    let stopped = false;
    const check = () =>
      getHealth()
        .then(() => !stopped && setState({ status: 'online', error: '' }))
        .catch((err) => !stopped && setState({ status: 'offline', error: err.message }));

    check();
    const timer = setInterval(check, CHECK_EVERY_MS);
    return () => {
      stopped = true;
      clearInterval(timer);
    };
  }, []);

  const words = { checking: 'Checking server…', online: 'Server online', offline: 'Server offline' };

  return (
    <p className="server-status" data-status={state.status} title={state.error || undefined} role="status">
      <span className="server-dot" aria-hidden="true" />
      {words[state.status]}
    </p>
  );
}
