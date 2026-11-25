// Every call to the SafeCrop back end goes through this file.
// The back end's address comes from VITE_API_URL (frontend/.env.local on the laptop; default http://localhost:8000).

import { getDeviceId } from './lib/profile.js';

const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

// The messages a person sees. `kind` lets a page pick a picture or a button; `message` is what it shows.
const MESSAGES = {
  offline: 'No internet connection. Check your mobile data or Wi-Fi, then try again.',
  unreachable: "Can't reach SafeCrop. If it was asleep it is starting now — try again in a minute.",
  starting: 'SafeCrop is starting, try again in a minute.',
  server: 'Something went wrong on the SafeCrop server. Try again; if it keeps happening, try another photo.',
  bad_answer: 'The server sent an answer we could not read. Try again.',
};

// An error with a `kind`: offline, unreachable, starting, empty, too_big, not_photo, not_found, server, bad_answer.
export class ApiError extends Error {
  constructor(kind, message, status = 0) {
    super(message || MESSAGES[kind] || MESSAGES.server);
    this.kind = kind;
    this.status = status;
  }
}

const KIND_BY_STATUS = { 400: 'empty', 404: 'not_found', 413: 'too_big', 415: 'not_photo', 503: 'starting' };

// Send a request and return the JSON answer, or throw an ApiError with a message a person can read.
async function request(path, { timeoutMs = 10000, ...options } = {}) {
  let response;
  try {
    response = await fetch(API_URL + path, { ...options, signal: AbortSignal.timeout(timeoutMs) });
  } catch (err) {
    if (typeof navigator !== 'undefined' && navigator.onLine === false) throw new ApiError('offline');
    // a timeout usually means the back end is still starting (loading the model)
    throw new ApiError(err.name === 'TimeoutError' ? 'starting' : 'unreachable');
  }

  let body = null;
  try {
    body = await response.json();
  } catch {
    // the answer was not JSON (for example the hosting service's own "starting" page); handled below
  }

  if (!response.ok) {
    const kind = KIND_BY_STATUS[response.status] || (response.status === 502 || response.status === 504 ? 'starting' : 'server');
    // our back end's own messages are already written for farmers; use them when there is one
    const detail = body && typeof body.detail === 'string' ? body.detail : '';
    throw new ApiError(kind, kind === 'server' ? '' : detail, response.status);
  }
  if (body === null) throw new ApiError('bad_answer');
  return body;
}

// GET /api/health → { status: "ok", model_loaded, version }
export function getHealth() {
  return request('/api/health');
}

// POST /api/check: the photo in, the photo check + answer + 5 similar pictures out.
export function checkPhoto(file) {
  const form = new FormData();
  form.append('image', file, file.name || 'photo.jpg');
  return request('/api/check', {
    method: 'POST',
    body: form,
    headers: { 'X-Device-Id': getDeviceId() },
    timeoutMs: 60000, // the first check right after start-up can be slow
  });
}

// POST /api/advice: advice for one check. The same photo is sent again (used once, never stored) so Gemini can
// give its second opinion; without it the advice still comes, with agrees = "unsure".
export function getAdvice(checkId, { file = null, lang = 'en' } = {}) {
  const form = new FormData();
  form.append('check_id', checkId);
  form.append('lang', lang);
  if (file) form.append('image', file, file.name || 'photo.jpg');
  // the server waits up to 20 s for Gemini and tries once more, then falls back
  return request('/api/advice', { method: 'POST', body: form, timeoutMs: 60000 });
}

// GET /api/diseases → the 8 problems SafeCrop knows
export function getDiseases() {
  return request('/api/diseases');
}

// GET /api/diseases/{id} → facts, sources and photos for one disease
export function getDisease(id) {
  return request('/api/diseases/' + encodeURIComponent(id));
}

// Pictures from the back end (thumb_url is a path like /static/thumbs/apple_scab_001.jpg)
export function fileUrl(path) {
  return path ? API_URL + path : '';
}

export { API_URL };
