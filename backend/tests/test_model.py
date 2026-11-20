"""The laptop's CLIP must give the same 768 numbers as the Colab database (database.npz)."""

import numpy as np
from PIL import Image

from app.model import embed
from tests.conftest import needs_models, sample_photos

pytestmark = needs_models


def test_laptop_embeddings_match_the_database(predictor):
    lib = predictor.lib
    for path, disease, _ in sample_photos("L0"):
        photo_id = path.stem[: -len("_clean_L0")]
        q = embed(predictor.model, np.asarray(Image.open(path).convert("RGB")))
        assert q.shape == (768,) and abs(float(np.linalg.norm(q)) - 1) < 1e-4
        row = np.flatnonzero(lib.photo_id == photo_id)[0]  # the photo's clean picture comes first
        assert lib.label[row] == disease
        assert float(lib.emb[row] @ q) > 0.9999, photo_id
