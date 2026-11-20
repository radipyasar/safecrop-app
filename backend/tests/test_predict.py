"""Photo check, search and decision with the real model files.

Note: the app model and the photo check were trained on the sample photos, so these tests only show that the code
works. They are not accuracy results (those come from the 5-fold tests in the research repo).
"""

import csv
import json

import numpy as np
import pytest

from app import photo_check
from app.main import MODELS_DIR
from app.predict import load_library, weighted_vote
from tests.conftest import needs_models, sample_photos

pytestmark = needs_models
BLUR = {"motion_blur", "defocus_blur"}


def test_vote_gives_the_same_number_as_colab():
    """Day 2 sanity check: each clean test photo, with all its own pictures hidden, voted to its own disease.
    Colab saved this number in export_info.json; the same vote on the laptop must give it exactly."""
    lib = load_library(MODELS_DIR)
    db = np.load(MODELS_DIR / "database.npz")
    with open(MODELS_DIR / "photos.csv", encoding="utf-8") as f:
        test_photos = {r["photo_id"] for r in csv.DictReader(f) if r["in_test_set"] == "True"}
    q = np.flatnonzero(np.isin(lib.photo_id, list(test_photos)) & ~db["is_copy"])
    S = lib.emb[q] @ lib.emb.T
    S[lib.photo_id[q][:, None] == lib.photo_id[None, :]] = -np.inf
    nn = np.argsort(-S, axis=1)[:, :5]
    own = np.mean([weighted_vote(lib.label[nn[i]], S[i, nn[i]])[0][0] == lib.label[q[i]] for i in range(len(q))])
    colab = json.loads((MODELS_DIR / "export_info.json").read_text())["numbers"]["database"]
    assert len(q) == 240
    assert round(float(own), 4) == colab["sanity_clean_photos_own_disease"]


@pytest.mark.parametrize("path, disease, noise", sample_photos("L0") + sample_photos("L3"),
                         ids=lambda x: getattr(x, "stem", None))
def test_photo_check_names_problem_and_level(path, disease, noise):
    checker = photo_check.load_checker(MODELS_DIR / "photo_check.joblib")
    result = photo_check.check_photo(photo_check.prepare_photo(path), checker)
    level = path.stem[-2:]
    assert result["level"] == level
    if noise == "clean":
        assert result["problem"] == "clean"
    elif noise in BLUR:
        assert result["problem"] in BLUR  # the app says "blurry" for both kinds
    else:
        assert result["problem"] == noise


def test_resample_only_for_the_blocky_photo():
    t = json.loads((MODELS_DIR / "thresholds.json").read_text())
    checker = photo_check.load_checker(MODELS_DIR / "photo_check.joblib")
    for path, _, noise in sample_photos("L0") + sample_photos("L3"):
        result = photo_check.check_photo(photo_check.prepare_photo(path), checker)
        assert photo_check.needs_resample(result, t["photo_check_sure"]) == (noise == "jpeg_compression"), path.name


def test_clean_healthy_and_look_alike_leaves(predictor):
    healthy = predictor.run(photo_check.prepare_photo(MODELS_DIR / "thumbs" / "pv_potato_healthy_01.jpg"))
    assert healthy["result"]["decision"] == "healthy"
    assert healthy["result"]["disease_id"] == "healthy_potato"
    other = predictor.run(photo_check.prepare_photo(MODELS_DIR / "thumbs" / "pv_potato_early_blight_01.jpg"))
    assert other["result"]["decision"] == "not_in_list"
    assert other["result"]["disease_id"] == "other_potato_early_blight"


def test_option_c_unclear_healthy_leaf_is_not_called_healthy(predictor):
    """A very strong 'healthy' vote: the saved clean picture of a healthy potato leaf (its own picture and copies
    are in the database, so the vote is 1.0). If the photo check says L3, option C must show 'not sure' with the
    closest of our 8 diseases and healthy as the runner-up; with L1 the answer is 'healthy'."""
    lib = predictor.lib
    db = np.load(MODELS_DIR / "database.npz")
    row = np.flatnonzero((lib.photo_id == "pv_potato_healthy_01") & ~db["is_copy"])[0]
    q = lib.emb[row]
    l3 = {"problem": "low_light", "level": "L3", "level_sure": 0.95}
    out = predictor.answer(q, l3)
    r = out["result"]
    assert out["raw"]["winner"] == "healthy_potato" and out["raw"]["share"] >= 0.90235
    assert r["decision"] == "not_sure" and r["reason"] == "healthy_or_other_unclear"
    assert lib.kind(r["disease_id"]) == "disease"
    assert r["runner_up"]["disease_id"] == "healthy_potato"
    assert r["tip"] and r["confidence_words"] == "Not sure"

    l1 = {"problem": "low_light", "level": "L1", "level_sure": 0.95}
    assert predictor.answer(q, l1)["result"]["decision"] == "healthy"


@pytest.mark.parametrize("name", ["grey", "checkerboard"])
def test_not_a_leaf_asks_for_a_retake(predictor, name):
    yy, xx = np.mgrid[0:224, 0:224]
    pictures = {"grey": np.full((224, 224, 3), 128, np.uint8),
                "checkerboard": (((yy // 28 + xx // 28) % 2) * 255).astype(np.uint8)[..., None].repeat(3, 2)}
    r = predictor.run(pictures[name])["result"]
    assert r["decision"] == "retake" and r["reason"] == "not_a_leaf"
    assert r["disease_id"] is None and "leaf" in r["tip"]


def test_neighbours_are_five_different_clean_photos(predictor):
    path, disease, _ = sample_photos("L3")[0]
    out = predictor.run(photo_check.prepare_photo(path))
    urls = [n["thumb_url"] for n in out["neighbours"]]
    assert len(urls) == 5 and len(set(urls)) == 5
    for n in out["neighbours"]:
        assert (MODELS_DIR / "thumbs" / n["thumb_url"].rsplit("/", 1)[-1]).exists()
        assert n["disease_name"]
    sims = [n["similarity"] for n in out["neighbours"]]
    assert sims == sorted(sims, reverse=True)
