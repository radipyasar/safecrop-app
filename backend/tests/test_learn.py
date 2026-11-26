"""26 Nov: learning from our second check (Gemini). app/learn.py, app/noise.py and scripts/undo_added.py.
Gemini is faked (no key, no quota); every file goes to a throw-away LEARN_DIR (see conftest.py)."""

import io
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from PIL import Image

from app import learn as learn_mod
from app.learn import LOG_FILE, Learner, read_added, read_log, remove_rows
from app.main import ADVISOR, CHECK_LOG, LEARN_DIR, LEARNER, MODELS_DIR, STATE
from app.model import embed
from app.noise import noisy_copies
from app.predict import ADDED_FILE
from tests.conftest import SAMPLES, needs_models
from tests.test_advice import GOOD, FakeGemini

BACKEND = Path(__file__).resolve().parents[1]

# Gemini says "no": this is jute dieback (one of our 8), sure
NO_DIEBACK = {**GOOD, "gemini_label": "jute_dieback", "gemini_name": "jute stem with dark dieback",
              "gemini_sure": "high", "agrees": "no", "summary": "This looks like jute dieback, not the app's answer.",
              "steps": ["Show the leaf to your local agriculture officer."]}
# the second call: advice about jute dieback
SECOND = {**GOOD, "summary": "SafeCrop's second check thinks this is Jute dieback. Look at the stems.",
          "steps": ["Pull out dead plants.", "Keep the field clean.", "Check the stems each week."]}
NO_CANT_NAME = {**NO_DIEBACK, "gemini_label": "other", "gemini_name": "something odd", "gemini_sure": "low"}
NO_OTHER = {**NO_DIEBACK, "gemini_label": "other", "gemini_name": "a grape leaf seen again", "gemini_sure": "high"}


def new_photo():
    """A leaf photo that is not in database.npz (a grape sample turned 30 degrees: closest library picture 0.955)."""
    img = Image.open(SAMPLES / "grape_leaf_blight_001_clean_L0.png").convert("RGB").rotate(30)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def check(client, data, device="test-device"):
    r = client.post("/api/check", files={"image": ("leaf.png", data, "image/png")}, headers={"X-Device-Id": device})
    assert r.status_code == 200
    return r.json()


def advise(client, check_id, data, lang="en"):
    r = client.post("/api/advice", data={"check_id": check_id, "lang": lang},
                    files={"image": ("leaf.png", data, "image/png")})
    assert r.status_code == 200
    return r.json()


@pytest.fixture
def gemini(monkeypatch):
    def use(*replies):
        fake = FakeGemini(*replies)
        monkeypatch.setattr(ADVISOR, "api_key", "test-key-not-real")
        monkeypatch.setattr(ADVISOR, "_client", fake)
        monkeypatch.setattr(ADVISOR, "_cache", type(ADVISOR._cache)())
        return fake
    return use


@pytest.fixture
def learning(client, monkeypatch):
    """LEARN_FROM_GEMINI on for one test; afterwards the live library and the files are as before."""
    predictor = STATE.predictor
    before = predictor.lib
    monkeypatch.setattr(LEARNER, "enabled", True)
    yield LEARNER
    LEARNER.wait()
    predictor.lib = before
    for f in (LEARN_DIR / ADDED_FILE, LEARN_DIR / LOG_FILE):
        f.unlink(missing_ok=True)


# ------------------------------------------------------------------ the noise recipe
@needs_models
def test_noise_rebuilds_the_database_copies(predictor):
    """Same noise code as Day 2: the copies of a sample photo give exactly the database.npz rows."""
    db = np.load(MODELS_DIR / "database.npz")
    img = np.array(Image.open(SAMPLES / "apple_scab_001_clean_L0.png").convert("RGB"))
    copies = noisy_copies(img, "apple_scab_001")
    assert [(n, lv) for n, lv, _, _ in copies][:3] == [("gaussian_noise", 1), ("gaussian_noise", 2), ("gaussian_noise", 3)]
    assert len(copies) == 15
    rows = np.flatnonzero(db["photo_id"] == "apple_scab_001")
    for n, lv, seed, a in (copies[0], copies[5], copies[13]):  # 3 noise types, 3 levels
        r = next(i for i in rows if db["noise"][i] == n and db["level"][i] == lv)
        assert seed == db["seed"][r]
        assert float(db["emb"][r] @ embed(predictor.model, a)) > 0.9999


# ------------------------------------------------------------------ the decision through the API
@needs_models
def test_override_shows_geminis_answer(client, gemini):
    data = new_photo()
    c = check(client, data)
    assert c["result"]["disease_id"] == "grape_leaf_blight"  # CLIP's closest match
    gemini(NO_DIEBACK, SECOND)
    a = advise(client, c["check_id"], data)
    f = a["final"]
    assert f["source"] == "gemini" and f["decision"] == "second_check" and f["disease_id"] == "jute_dieback"
    assert a["summary"] == SECOND["summary"] and a["gemini_name"] == "jute stem with dark dieback"
    row = CHECK_LOG.get(c["check_id"])
    assert row["label"] == "grape_leaf_blight" and row["gemini_label"] == "jute_dieback"
    assert row["final_source"] == "gemini" and row["final_label"] == "jute_dieback"


@needs_models
def test_cant_name_it_gives_other_unknown(client, gemini):
    data = new_photo()
    c = check(client, data)
    gemini(NO_CANT_NAME)
    f = advise(client, c["check_id"], data)["final"]
    assert f["decision"] == "not_sure" and f["disease_id"] == "other_unknown"


@needs_models
def test_with_the_setting_off_nothing_is_saved(client, gemini):
    assert LEARNER.enabled is False  # conftest sets LEARN_FROM_GEMINI=false
    data = new_photo()
    c = check(client, data)
    gemini(NO_DIEBACK, SECOND)
    a = advise(client, c["check_id"], data)
    assert a["final"]["source"] == "gemini" and a["learn"] == "off"
    assert not (LEARN_DIR / ADDED_FILE).exists() and not (LEARN_DIR / LOG_FILE).exists()
    assert STATE.predictor.lib.n_added == 0


@needs_models
def test_agreeing_saves_nothing(client, gemini, learning):
    c = check(client, new_photo())
    gemini({**GOOD, "gemini_label": "grape_leaf_blight", "gemini_name": "grape leaf with blight"})
    a = advise(client, c["check_id"], new_photo())
    assert a["final"]["source"] == "clip" and a["learn"] is None
    assert not (LEARN_DIR / ADDED_FILE).exists()


# ------------------------------------------------------------------ saving, matching, duplicates
@needs_models
def test_saved_check_is_matched_next_time(client, gemini, learning):
    data = new_photo()
    c = check(client, data)
    gemini(NO_DIEBACK, SECOND)
    a = advise(client, c["check_id"], data)
    assert a["learn"] == "saved"
    learning.wait()  # the 15 noisy copies are made in the background

    rows = read_added(LEARN_DIR / ADDED_FILE)
    assert len(rows["label"]) == 16 and rows["is_copy"].sum() == 15
    assert set(rows["label"]) == {"jute_dieback"} and set(rows["source"]) == {"gemini"}
    assert set(rows["check_id"]) == {c["check_id"]} and set(rows["device_id"]) == {"test-device"}
    assert set(rows["name"]) == {"jute stem with dark dieback"}
    assert sorted(set(rows["noise"])) == ["clean", "defocus_blur", "gaussian_noise", "jpeg_compression", "low_light",
                                          "motion_blur"]
    log = read_log(LEARN_DIR / LOG_FILE)
    assert len(log) == 1 and log[0]["clip_answer"] == "grape_leaf_blight" and log[0]["gemini_sure"] == "high"
    assert client.get("/api/health").json()["added_rows"] == 16

    again = check(client, data)  # the same photo, a new check: CLIP now finds the saved fingerprint
    # (the vote can still include a few v1 grape pictures, so "likely" is fine; the cut-offs are not changed)
    assert again["result"]["disease_id"] == "jute_dieback" and again["result"]["decision"] in ("sure", "likely")
    first = again["neighbours"][0]
    assert first["added"] is True and first["thumb_url"] is None
    assert first["disease_name"] == "jute stem with dark dieback" and first["similarity"] > 0.999

    # the same photo again with another "no": almost identical fingerprint -> not saved twice
    gemini(NO_OTHER)
    assert advise(client, again["check_id"], data)["learn"] == "duplicate"
    assert len(read_added(LEARN_DIR / ADDED_FILE)["label"]) == 16

    # asking again for the first check (another language) does not save again
    gemini(NO_DIEBACK, SECOND)
    assert advise(client, c["check_id"], data, lang="bn")["learn"] == "saved"
    assert len(read_log(LEARN_DIR / LOG_FILE)) == 1


@needs_models
def test_nothing_from_the_photo_is_kept_but_numbers(client, gemini, learning):
    data = new_photo()
    c = check(client, data)
    gemini(NO_DIEBACK, SECOND)
    advise(client, c["check_id"], data)
    learning.wait()
    files = {p.name for p in LEARN_DIR.iterdir()}
    assert files == {ADDED_FILE, LOG_FILE}  # no picture files
    with np.load(LEARN_DIR / ADDED_FILE) as f:
        assert f["emb"].shape == (16, 768)
        assert all(f[k].ndim == 1 for k in f.files if k != "emb")


# ------------------------------------------------------------------ the safety nets, without the model
class FakePredictor:
    def __init__(self):
        self.lib = SimpleNamespace(emb=np.zeros((0, 768), np.float32))
        self.model = None

    def add_rows(self, emb, label, photo_id, row_name):
        self.lib = SimpleNamespace(emb=np.vstack([self.lib.emb, emb]))


def fake_check(seed, device="phone-1"):
    v = np.random.default_rng(seed).normal(size=768).astype(np.float32)
    return {"emb": v / np.linalg.norm(v), "device_id": device,
            "result": {"decision": "sure", "disease_id": "apple_scab"}}


FINAL = {"disease_id": "other_unknown", "disease_name": "pumpkin leaf"}
OPINION = {"gemini_label": "other", "gemini_name": "pumpkin leaf", "gemini_sure": "high"}


def test_setting_off_saves_nothing(tmp_path):
    learner = Learner(tmp_path, enabled=False, get_predictor=FakePredictor)
    assert learner.save("c1", fake_check(1), None, FINAL, OPINION) == "off"
    assert list(tmp_path.iterdir()) == []


def test_at_most_20_saves_per_device_per_day(tmp_path, monkeypatch):
    monkeypatch.setattr(learn_mod, "MAX_PER_DEVICE_PER_DAY", 2)
    p = FakePredictor()
    learner = Learner(tmp_path, enabled=True, get_predictor=lambda: p)
    assert [learner.save(f"c{i}", fake_check(i), None, FINAL, OPINION) for i in range(3)] == \
        ["saved", "saved", "daily_limit"]
    assert learner.save("c9", fake_check(9, device="phone-2"), None, FINAL, OPINION) == "saved"
    assert learn_mod.MAX_PER_DEVICE_PER_DAY == 2 and len(read_log(tmp_path / LOG_FILE)) == 3


def test_duplicate_is_skipped(tmp_path):
    p = FakePredictor()
    learner = Learner(tmp_path, enabled=True, get_predictor=lambda: p)
    assert learner.save("c1", fake_check(1), None, FINAL, OPINION) == "saved"
    assert learner.save("c2", fake_check(1), None, FINAL, OPINION) == "duplicate"
    assert len(read_added(tmp_path / ADDED_FILE)["label"]) == 1


def test_undo_by_check_id_date_and_all(tmp_path):
    p = FakePredictor()
    learner = Learner(tmp_path, enabled=True, get_predictor=lambda: p)
    for i in range(3):
        learner.save(f"c{i}", fake_check(i), None, FINAL, OPINION)
    assert remove_rows(tmp_path, check_id="c1") == (1, 1)
    assert list(read_added(tmp_path / ADDED_FILE)["check_id"]) == ["c0", "c2"]
    assert [r["check_id"] for r in read_log(tmp_path / LOG_FILE)] == ["c0", "c2"]
    assert remove_rows(tmp_path, date="2000-01-01") == (0, 0)
    with pytest.raises(ValueError):
        remove_rows(tmp_path)  # must say what to remove

    script = [sys.executable, str(BACKEND / "scripts" / "undo_added.py"), "--folder", str(tmp_path)]
    listed = subprocess.run(script + ["--list"], capture_output=True, text=True, check=True).stdout
    assert "2 rows from 2 photos" in listed and "pumpkin leaf" in listed
    today = time.strftime("%Y-%m-%d")
    out = subprocess.run(script + ["--date", today], capture_output=True, text=True, check=True).stdout
    assert "Removed 2 rows" in out
    assert len(read_added(tmp_path / ADDED_FILE)["label"]) == 0 and read_log(tmp_path / LOG_FILE) == []
    learner.save("c7", fake_check(7), None, FINAL, OPINION)
    subprocess.run(script + ["--all"], capture_output=True, text=True, check=True)
    assert len(read_added(tmp_path / ADDED_FILE)["label"]) == 0
