"""Learning from our second check (Gemini). Decision by Nabil, 26 Nov 2026.

When Gemini says "no" to CLIP's answer (see app/advice.py, final_answer), the photo's fingerprint (CLIP's 768
numbers) is saved with Gemini's label, so the next check of a similar photo can match it:

- 1 row right away: the check's own embedding (kept in memory since /api/check)
- 15 rows in the background: noisy copies (5 noise types x L1-L3, the Day 2 recipe in app/noise.py, seed family 2026)
  made from the photo sent with the advice call, then put through CLIP. The noisy pictures are thrown away at once.

Files (git-ignored, in LEARN_DIR, default backend/models):
- database_added.npz   emb, label, photo_id, name (Gemini's words), source, date, time, check_id, device_id,
                       noise, level, is_copy. database.npz (v1) is never changed.
- added_by_gemini.csv  one line per save: date, check_id, CLIP's answer, Gemini's answer + words + how sure.

Safety nets: LEARN_FROM_GEMINI=true/false (off -> nothing is saved), skip a fingerprint that is almost the same
(cosine > 0.99) as one already in the library, at most 20 saves per device per day. No cut-off changes.
Never saved: the photo itself. `scripts/undo_added.py` removes rows again.
"""

import csv
import logging
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

from .model import embed
from .noise import noisy_copies
from .predict import ADDED_FILE

log = logging.getLogger("safecrop.learn")

LOG_FILE = "added_by_gemini.csv"
DUPLICATE_COSINE = 0.99
MAX_PER_DEVICE_PER_DAY = 20
SOURCE = "gemini"

ROW_FIELDS = ["label", "photo_id", "name", "source", "date", "time", "check_id", "device_id", "noise", "level",
              "is_copy"]
CSV_FIELDS = ["date", "time", "check_id", "device_id", "clip_answer", "clip_decision", "gemini_label", "gemini_name",
              "gemini_sure", "saved_label"]


def env_flag(name, default=False):
    v = os.getenv(name)
    return default if v is None or not v.strip() else v.strip().lower() in ("1", "true", "yes", "on")


# ---------------------------------------------------------------- the two files

def read_added(path):
    """database_added.npz -> {"emb": N x 768, field: N values ...}; empty (N = 0) when the file is missing."""
    path = Path(path)
    if not path.exists():
        return {"emb": np.zeros((0, 768), np.float32), **{f: np.array([], dtype=str) for f in ROW_FIELDS}}
    with np.load(path) as a:
        return {"emb": a["emb"].astype(np.float32), **{f: a[f] for f in ROW_FIELDS}}


def write_added(path, rows):
    """Write database_added.npz safely (a half-written file never replaces the old one)."""
    path = Path(path)
    tmp = path.with_suffix(".tmp.npz")
    with open(tmp, "wb") as f:
        np.savez(f, emb=np.asarray(rows["emb"], np.float32),
                 **{k: np.asarray(rows[k]).astype(bool if k == "is_copy" else np.int8 if k == "level" else str)
                    for k in ROW_FIELDS})
    os.replace(tmp, path)


def append_rows(path, new):
    old = read_added(path)
    have = len(old["label"]) > 0
    out = {"emb": np.vstack([old["emb"], np.asarray(new["emb"], np.float32)])}
    for k in ROW_FIELDS:
        a = np.asarray(new[k])
        out[k] = np.concatenate([old[k].astype(a.dtype) if k in ("level", "is_copy") else old[k], a]) if have else a
    write_added(path, out)


def read_log(path):
    path = Path(path)
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_log(path, rows):
    path = Path(path)
    tmp = path.with_suffix(".tmp.csv")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def remove_rows(folder, everything=False, date=None, check_id=None):
    """Remove added rows: all of them, or those from one date (YYYY-MM-DD) or one check_id.
    Returns (photos removed, rows removed). Used by scripts/undo_added.py."""
    if not (everything or date or check_id):
        raise ValueError("say what to remove: everything, a date or a check_id")
    folder = Path(folder)
    rows = read_added(folder / ADDED_FILE)
    lines = read_log(folder / LOG_FILE)

    def gone(d, c):
        return everything or (date and d == date) or (check_id and c == check_id)

    drop = np.array([bool(gone(d, c)) for d, c in zip(rows["date"], rows["check_id"])], dtype=bool)
    photos = len({c for c, x in zip(rows["check_id"], drop) if x} | {r["check_id"] for r in lines
                                                                     if gone(r["date"], r["check_id"])})
    if len(rows["label"]):
        write_added(folder / ADDED_FILE, {k: rows[k][~drop] for k in ["emb", *ROW_FIELDS]})
    if lines:
        write_log(folder / LOG_FILE, [r for r in lines if not gone(r["date"], r["check_id"])])
    return photos, int(drop.sum())


# ---------------------------------------------------------------- saving

class Learner:
    """Saves fingerprints labelled by Gemini. get_predictor() returns the live Predictor (model + library)."""

    def __init__(self, folder, enabled, get_predictor):
        self.folder = Path(folder)
        self.enabled = enabled
        self.get_predictor = get_predictor
        self._lock = threading.Lock()
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="noisy-copies")
        self._jobs = []

    @property
    def added_path(self):
        return self.folder / ADDED_FILE

    @property
    def log_path(self):
        return self.folder / LOG_FILE

    def save(self, check_id, check, photo, final, gemini):
        """check: what /api/check remembered (needs `emb`, `device_id`, `result`). photo: 224 x 224 RGB uint8 of the
        photo sent with the advice call (or None: then only the 1 clean row). final: the final answer.
        gemini: {gemini_label, gemini_name, gemini_sure}.
        Returns "saved", "off", "duplicate" or "daily_limit"."""
        if not self.enabled:
            return "off"
        predictor = self.get_predictor()
        emb = np.asarray(check["emb"], np.float32)
        device = check.get("device_id") or "unknown"
        label = final["disease_id"]
        name = (gemini.get("gemini_name") or "").strip() or final["disease_name"] or "Not in our list"
        now = time.localtime()
        date, clock = time.strftime("%Y-%m-%d", now), time.strftime("%Y-%m-%dT%H:%M:%S", now)

        with self._lock:
            sims = predictor.lib.emb @ emb
            if len(sims) and float(sims.max()) > DUPLICATE_COSINE:
                return "duplicate"
            today = sum(1 for r in read_log(self.log_path) if r["device_id"] == device and r["date"] == date)
            if today >= MAX_PER_DEVICE_PER_DAY:
                return "daily_limit"

            photo_id = f"added_{check_id}"
            common = {"label": label, "photo_id": photo_id, "name": name, "source": SOURCE, "date": date,
                      "time": clock, "check_id": check_id, "device_id": device}
            self.folder.mkdir(parents=True, exist_ok=True)
            append_rows(self.added_path, {"emb": emb[None], **{k: [v] for k, v in common.items()},
                                          "noise": ["clean"], "level": [0], "is_copy": [False]})
            predictor.add_rows(emb[None], [label], [photo_id], [name])
            r = check["result"]
            lines = read_log(self.log_path)
            lines.append({"date": date, "time": clock, "check_id": check_id, "device_id": device,
                          "clip_answer": r.get("disease_id") or "", "clip_decision": r["decision"],
                          "gemini_label": gemini.get("gemini_label") or "", "gemini_name": name,
                          "gemini_sure": gemini.get("gemini_sure") or "", "saved_label": label})
            write_log(self.log_path, lines)

        if photo is not None:
            self._jobs.append(self._pool.submit(self._add_copies, photo, common, predictor))
        log.info("learned %s: %s (%s), copies %s", check_id[:8], label, name, "coming" if photo is not None else "none")
        return "saved"

    def _add_copies(self, photo, common, predictor):
        """Background: 15 noisy copies -> CLIP -> added rows. The noisy pictures are not kept."""
        try:
            t0 = time.perf_counter()
            copies = noisy_copies(photo, common["photo_id"])
            embs = np.stack([embed(predictor.model, a) for _, _, _, a in copies])
            n = len(copies)
            with self._lock:
                if common["check_id"] not in {r["check_id"] for r in read_log(self.log_path)}:
                    return  # undone in the meantime
                append_rows(self.added_path, {"emb": embs, **{k: [v] * n for k, v in common.items()},
                                              "noise": [c[0] for c in copies], "level": [c[1] for c in copies],
                                              "is_copy": [True] * n})
                predictor.add_rows(embs, [common["label"]] * n, [common["photo_id"]] * n, [common["name"]] * n)
            log.info("learned %s: %d noisy copies added in %.1f s", common["check_id"][:8], n, time.perf_counter() - t0)
        except Exception:
            log.exception("Could not make the noisy copies for %s", common["check_id"])

    def wait(self):
        """Wait until every background job has finished (for tests and shutdown)."""
        while self._jobs:
            self._jobs.pop(0).result()
