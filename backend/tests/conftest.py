"""Shared test helpers. Tests that need the model files (backend/models, not in git) are skipped without them."""

import os
import tempfile
import time
from pathlib import Path

import pytest

# Before the app is imported: tests never use the real Gemini key (no quota spent; tests that want Gemini use a fake)
# and write to a throw-away log instead of backend/safecrop.db.
os.environ["GEMINI_API_KEY"] = ""
os.environ["DB_PATH"] = str(Path(tempfile.mkdtemp(prefix="safecrop_test_")) / "test.db")

from app.main import MODELS_DIR  # noqa: E402

SAMPLES = Path(__file__).resolve().parent / "samples"
HAVE_MODELS = all((MODELS_DIR / f).exists() for f in
                  ["clip_ft_delta.safetensors", "database.npz", "photo_check.joblib", "thresholds.json"])
needs_models = pytest.mark.skipif(not HAVE_MODELS, reason="model files are not in backend/models (see README)")


def sample_photos(level):
    """The sample photos of one level ('L0' or 'L3') as (path, true disease, true noise)."""
    out = []
    for p in sorted(SAMPLES.glob(f"*_{level}.png")):
        stem = p.stem[: -len(f"_{level}")]  # e.g. apple_scab_001_gaussian_noise
        photo_id = next(stem[:i] for i in range(len(stem), 0, -1) if stem[:i].rsplit("_", 1)[-1].isdigit())
        disease = photo_id.rsplit("_", 1)[0]
        noise = stem[len(photo_id) + 1:]
        out.append((p, disease, noise))
    return out


@pytest.fixture(scope="session")
def client():
    """The real app with its real start-up (background loading + warm-up), shared by every test that needs it."""
    if not HAVE_MODELS:
        pytest.skip("model files are not in backend/models")
    from fastapi.testclient import TestClient

    from app.main import STATE, app

    with TestClient(app) as c:
        deadline = time.time() + 300
        while STATE.predictor is None:
            if STATE.load_error:
                pytest.fail(f"the model did not load: {STATE.load_error}")
            if time.time() > deadline:
                pytest.fail("the model did not load within 5 minutes")
            time.sleep(0.2)
        yield c


@pytest.fixture(scope="session")
def predictor(client):
    from app.main import STATE

    return STATE.predictor
