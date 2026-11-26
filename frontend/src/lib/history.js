// Past checks, saved in this browser only (localStorage). At most 50; the oldest go first.
// Each entry: { id, date, thumb, decision, disease_id, disease_name, crop, confidence_words, check, advice }
//   check  = the whole /api/check answer (so the result can be shown again without the server)
//   advice = the /api/advice answer, added when it arrives (null until then)
// No full-size photos are kept: only a 160 x 160 thumbnail.

const KEY = 'safecrop.history';
export const MAX_CHECKS = 50;

const listeners = new Set();

export function readHistory() {
  try {
    const list = JSON.parse(localStorage.getItem(KEY) || '[]');
    return Array.isArray(list) ? list : [];
  } catch {
    return [];
  }
}

function writeHistory(list) {
  let keep = list.slice(0, MAX_CHECKS);
  // if the browser's storage is full, drop the oldest checks until it fits
  for (;;) {
    try {
      localStorage.setItem(KEY, JSON.stringify(keep));
      break;
    } catch (err) {
      if (keep.length <= 1) throw err;
      keep = keep.slice(0, -1);
    }
  }
  listeners.forEach((fn) => fn(keep));
  return keep;
}

export function getCheck(id) {
  return readHistory().find((c) => c.id === id) || null;
}

// Save a finished check (newest first).
export function saveCheck(check, thumb) {
  const r = check.result;
  const entry = {
    id: check.check_id,
    date: new Date().toISOString(),
    thumb: thumb || null,
    decision: r.decision,
    disease_id: r.disease_id,
    disease_name: r.disease_name,
    crop: r.crop,
    confidence_words: r.confidence_words,
    check,
    advice: null,
  };
  try {
    writeHistory([entry, ...readHistory().filter((c) => c.id !== entry.id)]);
  } catch {
    // storage blocked (private mode) or full: the result still shows, it just isn't saved
  }
  return entry;
}

// Add the advice. If our second check (Gemini) said no, its answer becomes the check's answer in History too.
export function saveAdvice(id, advice) {
  const f = advice && advice.final;
  const answer =
    f && f.source === 'gemini'
      ? {
          decision: f.decision,
          disease_id: f.disease_id,
          disease_name: f.disease_name,
          crop: f.crop,
          confidence_words: f.confidence_words,
        }
      : {};
  try {
    writeHistory(readHistory().map((c) => (c.id === id ? { ...c, ...answer, advice } : c)));
  } catch {
    // see saveCheck
  }
}

export function deleteCheck(id) {
  writeHistory(readHistory().filter((c) => c.id !== id));
}

export function clearHistory() {
  writeHistory([]);
}

// Let a page re-draw when the history changes.
export function onHistoryChange(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}
