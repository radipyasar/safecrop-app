"""SafeCrop back end: the FastAPI app.

Run (in backend/):  uvicorn app.main:app --reload --port 8000   → test page: http://localhost:8000/docs
"""

import csv
import io
import logging
import os
import threading
import time
import uuid
import warnings
from collections import OrderedDict
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import pillow_heif
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image

from . import photo_check
from .advice import Advisor, photo_jpeg
from .db import CheckLog
from .predict import Predictor
from .schemas import Advice, CheckResponse, DiseaseDetail, DiseaseSummary, Health

BACKEND = Path(__file__).resolve().parents[1]
# Read backend/.env (git-ignored) into environment variables. Real environment variables win.
load_dotenv(BACKEND / ".env")
pillow_heif.register_heif_opener()  # lets Pillow open iPhone HEIC photos

VERSION = "0.4.0"
logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("safecrop")  # our own lines at INFO; other libraries only show warnings
log.setLevel(logging.INFO)

# Model files (git-ignored): backend/models, or MODELS_DIR from the environment
MODELS_DIR = Path(os.getenv("MODELS_DIR") or BACKEND / "models")
FACTS_PATH = BACKEND / "data" / "diseases.json"
DB_PATH = Path(os.getenv("DB_PATH") or BACKEND / "safecrop.db")  # git-ignored (*.db)
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
PHOTO_FORMATS = {"JPEG", "PNG", "WEBP", "HEIF"}  # what Pillow calls JPEG, PNG, WebP and HEIC files
KEEP_CHECKS = 1000  # the newest results kept in memory for /api/advice (Day 4); no photos are kept

# Which front-end addresses may call this API. Comma-separated, no slash at the end.
ALLOWED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]


class State:
    predictor: Predictor | None = None  # set once loading and the warm-up have finished
    load_seconds: float | None = None
    load_error: str | None = None  # set if loading failed (the details are in the server log)
    checks: "OrderedDict[str, dict]" = OrderedDict()
    lock = threading.Lock()


STATE = State()
ADVISOR = Advisor.from_env(FACTS_PATH)  # Gemini key from GEMINI_API_KEY; without it every answer is the fallback
CHECK_LOG = CheckLog(DB_PATH)


def load_photo_list(models_dir):
    """photos.csv -> {label: {"thumbs": [clean thumbnail URLs], "credit": "AppleLeaf9 (CC BY 4.0)"}}.
    Empty when the model files are missing (the disease pages then show no pictures)."""
    path = Path(models_dir) / "photos.csv"
    out = {}
    if not path.exists():
        return out
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            entry = out.setdefault(row["label"], {"thumbs": [], "credit": f"{row['source']} ({row['licence']})"})
            entry["thumbs"].append(f"/static/thumbs/{row['thumb']}")
    return out


PHOTOS = load_photo_list(MODELS_DIR)
HAVE_PHOTOS = bool(PHOTOS)


def load_everything():
    """Runs in a background thread at start-up: the server answers /api/health at once and /api/check says
    'starting' until this has finished."""
    t0 = time.perf_counter()
    try:
        predictor = Predictor.load(MODELS_DIR)
        predictor.warm_up()
    except Exception as e:
        log.exception("Could not load the model files from %s", MODELS_DIR)
        STATE.load_error = f"{type(e).__name__}: {e}"
        return
    STATE.load_seconds = time.perf_counter() - t0
    STATE.predictor = predictor
    log.info("Model loaded and warmed up in %.1f s", STATE.load_seconds)


@asynccontextmanager
async def lifespan(app):
    threading.Thread(target=load_everything, name="load-model", daemon=True).start()
    yield


app = FastAPI(title="SafeCrop API", version=VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Device-Id"],
)

# Clean thumbnails of the database photos, shown as the "similar pictures"
app.mount("/static/thumbs", StaticFiles(directory=MODELS_DIR / "thumbs", check_dir=False), name="thumbs")


@app.get("/api/health", response_model=Health)
def health():
    """Is the server up? model_loaded becomes true once the model is loaded and warmed up."""
    return {"status": "ok", "model_loaded": STATE.predictor is not None, "version": VERSION}


def read_photo(data):
    """Upload bytes -> 224 x 224 RGB photo (EXIF turn, central square) for CLIP and the photo check."""
    return photo_check.prepare_photo(open_photo(data))


def open_photo(data):
    """Upload bytes -> the opened Pillow photo. Judged by what is inside the file, not by its name.
    Raises a clear HTTP error for anything else."""
    if not data:
        raise HTTPException(400, "The file is empty. Choose a photo of a leaf.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "The photo is too big. The limit is 10 MB.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            img = Image.open(io.BytesIO(data))
            if img.format not in PHOTO_FORMATS:
                raise ValueError(f"not a photo format we take: {img.format}")
            img.load()
            return img
    except (Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise HTTPException(413, "The photo has too many pixels. Use a normal phone photo.")
    except Exception:
        raise HTTPException(415, "This file is not a photo SafeCrop can read. Use a JPEG, PNG, WebP or HEIC photo.")


@app.post("/api/check", response_model=CheckResponse)
def check(image: UploadFile = File(description="a photo of one leaf: JPEG, PNG, WebP or HEIC, up to 10 MB"),
          x_device_id: str | None = Header(default=None, max_length=100)):
    """Photo in, disease out: the photo check, the answer and the 5 most similar database pictures."""
    t0 = time.perf_counter()
    photo = read_photo(image.file.read(MAX_UPLOAD_BYTES + 1))
    read_ms = (time.perf_counter() - t0) * 1000
    predictor = STATE.predictor
    if predictor is None:
        raise HTTPException(503, "SafeCrop is starting. Try again in a minute.")
    out = predictor.run(photo)
    raw = out.pop("raw")
    out["timing_ms"] = {"read": round(read_ms, 1), **out["timing_ms"],
                        "total": round((time.perf_counter() - t0) * 1000, 1)}
    check_id = uuid.uuid4().hex
    with STATE.lock:  # remember the answer (never the photo) for the advice call
        STATE.checks[check_id] = {"time": time.time(), "device_id": x_device_id, **out, "raw": raw}
        while len(STATE.checks) > KEEP_CHECKS:
            STATE.checks.popitem(last=False)
    CHECK_LOG.add_check(check_id, x_device_id, out, raw)
    r = out["result"]
    log.info("check %s: %s %s (vote %.2f), photo %s %s, %.0f ms", check_id[:8], r["decision"], r["disease_id"],
             raw["share"], out["photo_check"]["problem"], out["photo_check"]["level"], out["timing_ms"]["total"])
    return {"check_id": check_id, **out}


@app.post("/api/advice", response_model=Advice)
def advice(check_id: str = Form(max_length=64, description="check_id from /api/check"),
           lang: Literal["en", "bn"] = Form("en", description="en = English, bn = Bangla"),
           image: UploadFile | None = File(None, description="optional: the same photo again, so Gemini can look "
                                                             "at it (used for this request only, never stored)")):
    """Advice for one check: written by Gemini from the checked facts, or the fallback from diseases.json.
    CLIP's answer never changes here; Gemini only gives a second opinion (`agrees`)."""
    with STATE.lock:
        check = STATE.checks.get(check_id)
    if check is None:
        raise HTTPException(404, "This check was not found. It may be too old or the server restarted; "
                                 "check the photo again.")
    photo = None
    if image is not None:
        photo = photo_jpeg(open_photo(image.file.read(MAX_UPLOAD_BYTES + 1)))
    out = ADVISOR.advise(check_id, check, lang, photo)
    del photo  # the photo is not kept anywhere
    if not out["cached"]:
        CHECK_LOG.add_advice(check_id, out)
    log.info("advice %s: %s (%s), agrees %s, %.0f ms", check_id[:8], out["source"], out["fallback_reason"] or lang,
             out["agrees"], out["timing_ms"] or 0)
    return out


def disease_summary(e):
    thumbs = PHOTOS.get(e["id"], {}).get("thumbs", [])
    return {k: e[k] for k in ("id", "kind", "group", "crop", "name_en", "name_bn", "short")} | {
        "thumb_url": thumbs[0] if thumbs else None}


OUR_DISEASES = [e for e in ADVISOR.facts.values() if e["kind"] in ("disease", "pest")]


@app.get("/api/diseases", response_model=list[DiseaseSummary])
def diseases():
    """The 8 problems SafeCrop knows (7 diseases + 1 insect pest), for the Diseases page."""
    return [disease_summary(e) for e in OUR_DISEASES]


@app.get("/api/diseases/{disease_id}", response_model=DiseaseDetail)
def disease(disease_id: str):
    """Full checked facts for one disease: signs, what to do now, prevention, when to call an expert, sources."""
    e = next((e for e in OUR_DISEASES if e["id"] == disease_id), None)
    if e is None:
        raise HTTPException(404, "SafeCrop has no page for this disease.")
    photos = PHOTOS.get(disease_id, {})
    return {**e, **disease_summary(e), "photos": photos.get("thumbs", [])[:6], "photo_credit": photos.get("credit"),
            "helpline": ADVISOR.about["helpline"]["number"]}
