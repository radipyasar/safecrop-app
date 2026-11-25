"""SQLite log of every check, for our own numbers (time per check, Gemini agreement, fallback count ...).

Privacy: only numbers and labels. No photo, no file name, no picture data of any kind is ever written here.
The file is backend/safecrop.db (git-ignored), or DB_PATH from the environment. The History page lives in the browser,
never in this log. A failed write is logged and never breaks a check.
"""

import logging
import sqlite3
import threading
import time
from contextlib import closing

log = logging.getLogger("safecrop.db")

COLUMNS = {  # name -> SQLite type
    "id": "TEXT PRIMARY KEY",       # check_id
    "time": "TEXT",                 # UTC, e.g. 2026-11-23T10:15:02Z
    "device_id": "TEXT",            # random id the browser makes; not a name or phone number
    "problem": "TEXT",              # photo check: clean, motion_blur ...
    "level": "TEXT",                # L0 ... L3
    "problem_sure": "REAL",
    "fix_applied": "TEXT",
    "label": "TEXT",                # the shown answer (disease_id), null for retake
    "winner": "TEXT",               # the raw vote winner (can be healthy_ / other_)
    "vote_share": "REAL",
    "best_similarity": "REAL",
    "decision": "TEXT",
    "reason": "TEXT",
    "timing_total_ms": "REAL",
    "timing_embed_ms": "REAL",
    "gemini_agrees": "TEXT",        # filled by /api/advice: yes / no / unsure
    "advice_source": "TEXT",        # gemini / fallback
    "fallback_reason": "TEXT",
    "advice_lang": "TEXT",
    "advice_ms": "REAL",
}


class CheckLog:
    def __init__(self, path):
        self.path = str(path)
        self._lock = threading.Lock()
        with self._connect() as con:
            con.execute(f"CREATE TABLE IF NOT EXISTS checks ({', '.join(f'{k} {v}' for k, v in COLUMNS.items())})")

    def _connect(self):
        return closing(sqlite3.connect(self.path, timeout=10))

    def _write(self, sql, values):
        try:
            with self._lock, self._connect() as con, con:  # the inner `con` commits
                con.execute(sql, values)
        except Exception:
            log.exception("Could not write to the check log")

    def add_check(self, check_id, device_id, out, raw):
        """out: the /api/check answer (photo_check, result, timing_ms); raw: {winner, share}."""
        pc, r, t = out["photo_check"], out["result"], out["timing_ms"]
        row = {"id": check_id, "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "device_id": device_id,
               "problem": pc["problem"], "level": pc["level"], "problem_sure": pc["sure"],
               "fix_applied": pc["fix_applied"], "label": r["disease_id"], "winner": raw["winner"],
               "vote_share": raw["share"], "best_similarity": r["best_similarity"], "decision": r["decision"],
               "reason": r["reason"], "timing_total_ms": t.get("total"), "timing_embed_ms": t.get("embed")}
        self._write(f"INSERT OR REPLACE INTO checks ({', '.join(row)}) VALUES ({', '.join('?' * len(row))})",
                    list(row.values()))

    def add_advice(self, check_id, advice):
        self._write("UPDATE checks SET gemini_agrees = ?, advice_source = ?, fallback_reason = ?, advice_lang = ?, "
                    "advice_ms = ? WHERE id = ?",
                    [advice["agrees"] if advice["source"] == "gemini" else None, advice["source"],
                     advice.get("fallback_reason"), advice.get("lang"), advice.get("timing_ms"), check_id])

    def get(self, check_id):
        with self._connect() as con:
            con.row_factory = sqlite3.Row
            row = con.execute("SELECT * FROM checks WHERE id = ?", [check_id]).fetchone()
        return dict(row) if row else None
