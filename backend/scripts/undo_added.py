"""Remove fingerprints that our second check (Gemini) added to backend/models/database_added.npz.

database.npz (v1) is never touched. Run in backend/ with the server STOPPED (or restart it afterwards: the server
reads database_added.npz only at start-up).

    python scripts/undo_added.py --list                 # what is in there
    python scripts/undo_added.py --all                  # remove every added row
    python scripts/undo_added.py --date 2026-11-27      # remove the rows saved on one day
    python scripts/undo_added.py --check-id 1a2b3c...   # remove one saved photo (its clean row + 15 copies)

--folder: another folder than LEARN_DIR / backend/models (used by the tests).
"""

import argparse
import os
import sys
from collections import Counter
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.learn import LOG_FILE, read_added, read_log, remove_rows  # noqa: E402
from app.predict import ADDED_FILE  # noqa: E402


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    what = p.add_mutually_exclusive_group(required=True)
    what.add_argument("--list", action="store_true", help="show what is saved, change nothing")
    what.add_argument("--all", action="store_true", help="remove every added row")
    what.add_argument("--date", help="remove the rows saved on this day (YYYY-MM-DD)")
    what.add_argument("--check-id", help="remove the rows of one check")
    p.add_argument("--folder", type=Path, default=None, help="where database_added.npz is (default: LEARN_DIR or "
                                                             "backend/models)")
    args = p.parse_args(argv)

    folder = args.folder or Path(os.getenv("LEARN_DIR") or BACKEND / "models")
    rows = read_added(folder / ADDED_FILE)
    lines = read_log(folder / LOG_FILE)
    if args.list:
        print(f"{folder / ADDED_FILE}: {len(rows['label'])} rows from {len(set(rows['check_id']))} photos")
        for (date, label), n in sorted(Counter(zip(rows["date"], rows["label"])).items()):
            print(f"  {date}  {label:28s} {n} rows")
        print(f"{folder / LOG_FILE}: {len(lines)} saves")
        for r in lines:
            print(f"  {r['date']}  {r['check_id']}  CLIP {r['clip_answer'] or '-'} -> Gemini {r['gemini_label']} "
                  f"({r['gemini_sure']}): {r['gemini_name']}")
        return 0

    photos, removed = remove_rows(folder, everything=args.all, date=args.date, check_id=args.check_id)
    print(f"Removed {removed} rows ({photos} photos) from {folder / ADDED_FILE} and {folder / LOG_FILE}.")
    print(f"Left: {len(read_added(folder / ADDED_FILE)['label'])} rows. Restart the server to use the new library.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
