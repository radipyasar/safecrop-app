"""SafeCrop back end: the FastAPI app.

Run (in backend/):  uvicorn app.main:app --reload --port 8000   → test page: http://localhost:8000/docs
"""

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

import pillow_heif
from dotenv import load_dotenv
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image

from . import photo_check
from .predict import Predictor
from .schemas import CheckResponse, Health

# Read backend/.env (git-ignored) into environment variables. Real environment variables win.
load_dotenv()
pillow_heif.register_heif_opener()  # lets Pillow open iPhone HEIC photos

VERSION = "0.3.0"
logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("safecrop")  # our own lines at INFO; other libraries only show warnings
log.setLevel(logging.INFO)

# Model files (git-ignored): backend/models, or MODELS_DIR from the environment
MODELS_DIR = Path(os.getenv("MODELS_DIR") or Path(__file__).resolve().parents[1] / "models")
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
    """Upload bytes -> 224 x 224 RGB photo (EXIF turn, central square). Judged by what is inside the file,
    not by its name. Raises a clear HTTP error for anything else."""
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
            return photo_check.prepare_photo(img)
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
    r = out["result"]
    log.info("check %s: %s %s (vote %.2f), photo %s %s, %.0f ms", check_id[:8], r["decision"], r["disease_id"],
             raw["share"], out["photo_check"]["problem"], out["photo_check"]["level"], out["timing_ms"]["total"])
    return {"check_id": check_id, **out}
