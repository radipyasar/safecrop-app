"""POST /api/advice, GET /api/diseases and the SQLite log, through HTTP. Gemini is faked (no key, no quota)."""

import io
import sqlite3

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.db import COLUMNS
from app.main import ADVISOR, CHECK_LOG, HAVE_PHOTOS, app
from app.schemas import Advice
from tests.conftest import SAMPLES, needs_models
from tests.test_advice import GOOD, FakeGemini

plain = TestClient(app)  # no start-up needed for these
LEAF = SAMPLES / "potato_late_blight_007_clean_L0.png"


@pytest.fixture
def fake_gemini(monkeypatch):
    """Pretend a key is set and Gemini answers GOOD."""
    fake = FakeGemini(GOOD, GOOD, GOOD)
    monkeypatch.setattr(ADVISOR, "api_key", "test-key-not-real")
    monkeypatch.setattr(ADVISOR, "_client", fake)
    monkeypatch.setattr(ADVISOR, "_cache", type(ADVISOR._cache)())
    return fake


def new_check(client, path=LEAF):
    r = client.post("/api/check", files={"image": (path.name, path.read_bytes(), "image/png")},
                    headers={"X-Device-Id": "test-device"})
    assert r.status_code == 200
    return r.json()["check_id"]


# ------------------------------------------------------------------ /api/advice
def test_unknown_check_id_gives_clear_404():
    r = plain.post("/api/advice", data={"check_id": "no-such-check", "lang": "en"})
    assert r.status_code == 404
    assert "not found" in r.json()["detail"]


def test_wrong_language_is_rejected():
    assert plain.post("/api/advice", data={"check_id": "x", "lang": "fr"}).status_code == 422


@needs_models
def test_advice_from_gemini_is_valid_json(client, fake_gemini):
    check_id = new_check(client)
    r = client.post("/api/advice", data={"check_id": check_id, "lang": "en"})
    assert r.status_code == 200
    body = Advice.model_validate(r.json())
    assert body.source == "gemini" and body.steps
    assert body.agrees == "unsure"  # no photo sent


@needs_models
def test_advice_with_the_photo_lets_gemini_look(client, fake_gemini):
    check_id = new_check(client)
    r = client.post("/api/advice", data={"check_id": check_id, "lang": "en"},
                    files={"image": (LEAF.name, LEAF.read_bytes(), "image/png")})
    assert r.status_code == 200 and r.json()["agrees"] == "yes"
    sent = fake_gemini.calls[-1]
    assert len(sent) == 2 and sent[1].inline_data.mime_type == "image/jpeg"  # the prompt + a small JPEG


@needs_models
def test_advice_with_a_bad_photo_is_rejected(client, fake_gemini):
    check_id = new_check(client)
    r = client.post("/api/advice", data={"check_id": check_id},
                    files={"image": ("notes.txt", b"not a photo", "text/plain")})
    assert r.status_code == 415


@needs_models
def test_without_key_advice_is_the_fallback(client):
    assert not ADVISOR.api_key  # conftest removes the key for tests
    check_id = new_check(client)
    r = client.post("/api/advice", data={"check_id": check_id, "lang": "bn"})
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "fallback" and body["fallback_reason"] == "no_key" and body["agrees"] == "unsure"
    assert "16123" in body["safety_note"]


@needs_models
def test_second_call_is_cached(client, fake_gemini):
    check_id = new_check(client)
    first = client.post("/api/advice", data={"check_id": check_id}).json()
    second = client.post("/api/advice", data={"check_id": check_id}).json()
    assert first["cached"] is False and second["cached"] is True
    assert len(fake_gemini.calls) == 1


# ------------------------------------------------------------------ SQLite log
@needs_models
def test_every_check_is_logged_without_the_photo(client, fake_gemini):
    check_id = new_check(client)
    row = CHECK_LOG.get(check_id)
    assert row["decision"] == "sure" and row["label"] == "potato_late_blight" and row["device_id"] == "test-device"
    assert row["advice_source"] is None  # no advice asked yet

    client.post("/api/advice", data={"check_id": check_id}, files={"image": (LEAF.name, LEAF.read_bytes(), "image/png")})
    row = CHECK_LOG.get(check_id)
    assert row["advice_source"] == "gemini" and row["gemini_agrees"] == "yes" and row["advice_lang"] == "en"


@needs_models
def test_log_has_only_numbers_and_labels(client):
    new_check(client)
    con = sqlite3.connect(CHECK_LOG.path)
    cols = [r[1] for r in con.execute("PRAGMA table_info(checks)")]
    types = {t for (t,) in con.execute("SELECT DISTINCT typeof(v) FROM (" + " UNION ALL ".join(
        f"SELECT {c} AS v FROM checks" for c in cols) + ")")}
    con.close()
    assert cols == list(COLUMNS)
    assert not any(word in c for c in cols for word in ("photo", "image", "file", "thumb"))
    assert "blob" not in types  # no picture data of any kind


def test_log_write_failure_never_breaks_anything(tmp_path):
    from app.db import CheckLog

    log = CheckLog(tmp_path / "x.db")
    log.path = str(tmp_path / "missing_folder" / "x.db")  # writing now fails
    log.add_advice("abc", {"source": "fallback", "agrees": "unsure"})  # logs the error, does not raise


# ------------------------------------------------------------------ /api/diseases
def test_disease_list_has_our_8():
    r = plain.get("/api/diseases")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 8
    assert {d["kind"] for d in items} == {"disease", "pest"}
    assert all(d["name_en"] and d["name_bn"] and d["short"] for d in items)
    if HAVE_PHOTOS:
        assert all(d["thumb_url"].startswith("/static/thumbs/") for d in items)


def test_disease_detail_has_facts_and_sources():
    r = plain.get("/api/diseases/rice_stem_borer")
    assert r.status_code == 200
    d = r.json()
    assert d["kind"] == "pest" and "not a disease" in d["cause"]
    assert 3 <= len(d["signs"]) <= 5 and d["do_now"] and d["prevention"] and d["see_expert_when"]
    assert d["sources"] and all(s["url"].startswith("https://") for s in d["sources"])
    assert d["helpline"] == "16123"
    if HAVE_PHOTOS:
        assert 1 <= len(d["photos"]) <= 6 and d["photo_credit"]


@pytest.mark.parametrize("bad_id", ["no_such_disease", "healthy", "unknown", "healthy_potato"])
def test_disease_detail_404_for_anything_else(bad_id):
    assert plain.get(f"/api/diseases/{bad_id}").status_code == 404


@needs_models
def test_disease_thumbnail_is_served(client):
    url = plain.get("/api/diseases").json()[0]["thumb_url"]
    r = client.get(url)
    assert r.status_code == 200
    Image.open(io.BytesIO(r.content)).verify()
