// Every call to the SafeCrop back end goes through this file.
// The back end's address comes from VITE_API_URL (frontend/.env.local on your laptop, Vercel settings online).

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

// Send a request and return the JSON answer, or throw an Error with a message a person can read.
async function request(path, { timeoutMs = 10000, ...options } = {}) {
  let response;
  try {
    response = await fetch(API_URL + path, { ...options, signal: AbortSignal.timeout(timeoutMs) });
  } catch (err) {
    if (err.name === 'TimeoutError') {
      throw new Error(`The server did not answer in ${timeoutMs / 1000} seconds. It may be starting up — try again in a minute.`);
    }
    throw new Error('Cannot reach the server. Check your internet connection, or that the back end is running.');
  }

  let body = null;
  try {
    body = await response.json();
  } catch {
    // the answer was not JSON; handled below
  }

  if (!response.ok) {
    const detail = body && typeof body.detail === 'string' ? body.detail : `error ${response.status}`;
    throw new Error(`The server could not do this (${detail}).`);
  }
  if (body === null) {
    throw new Error('The server sent an answer we could not read.');
  }
  return body;
}

// GET /api/health → { status: "ok", ... }
export function getHealth() {
  return request('/api/health');
}

export { API_URL };
