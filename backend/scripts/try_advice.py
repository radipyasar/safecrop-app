"""Day 4: try the advice service on sample photos with the real Gemini key (from backend/.env; never printed).

Run in backend/:  python scripts/try_advice.py [photo ...] [--lang en|bn] [--no-key]
Prints CLIP's answer, the advice JSON and the time Gemini took. No photo is saved.
"""

import argparse
import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import photo_check  # noqa: E402
from app.advice import Advisor, photo_jpeg  # noqa: E402
from app.predict import Predictor  # noqa: E402

load_dotenv(ROOT / ".env")
p = argparse.ArgumentParser()
p.add_argument("photos", nargs="*", default=[str(ROOT / "tests/samples/potato_late_blight_007_clean_L0.png")])
p.add_argument("--lang", default="en")
p.add_argument("--no-key", action="store_true", help="pretend there is no key (shows the fallback)")
args = p.parse_args()

advisor = Advisor.from_env(ROOT / "data/diseases.json")
if args.no_key:
    advisor.api_key = None
print("model:", advisor.model, "| key set:", bool(advisor.api_key))
predictor = Predictor.load(ROOT / "models")

for path in args.photos:
    img = Image.open(path)
    img.load()
    check = predictor.run(photo_check.prepare_photo(img))
    r = check["result"]
    print(f"\n=== {Path(path).name}: CLIP -> {r['decision']} {r['disease_id']} (vote {r['vote_share']}), "
          f"photo {check['photo_check']['problem']} {check['photo_check']['level']}")
    t0 = time.perf_counter()
    out = advisor.advise(Path(path).stem, check, args.lang, photo_jpeg(img))
    print(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"advice took {time.perf_counter() - t0:.1f} s")
