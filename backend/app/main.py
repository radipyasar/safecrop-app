"""SafeCrop back end: the FastAPI app.

Run (in backend/):  uvicorn app.main:app --reload --port 8000   → test page: http://localhost:8000/docs
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Read backend/.env (git-ignored) into environment variables. Real environment variables win.
load_dotenv()

VERSION = "0.1.0"

# Which front-end addresses may call this API. Comma-separated, no slash at the end.
ALLOWED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app = FastAPI(title="SafeCrop API", version=VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Device-Id"],
)


@app.get("/api/health")
def health():
    """Is the server up? model_loaded becomes true once the CLIP model is loaded (Day 3)."""
    return {"status": "ok", "model_loaded": False, "version": VERSION}
