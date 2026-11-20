"""POST /api/check through HTTP: good photos, bad files, EXIF rotation, privacy.

The rejection tests need no model files: the upload is checked before the model is used.
The app model was trained on the sample photos, so the "right disease" tests only show that the code works.
"""

import io

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app import photo_check
from app.main import STATE, app, read_photo
from tests.conftest import needs_models, sample_photos

plain = TestClient(app)  # no start-up: enough for files that are rejected before the model is used


def post(client, data, name="leaf.jpg", mime="image/jpeg", headers=None):
    return client.post("/api/check", files={"image": (name, data, mime)}, headers=headers or {})


def png_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ------------------------------------------------------------------ bad files: a clear error, never a crash
def test_text_file_is_rejected():
    r = post(plain, b"this is not a photo", name="notes.txt", mime="text/plain")
    assert r.status_code == 415
    assert "JPEG, PNG, WebP or HEIC" in r.json()["detail"]


def test_text_file_named_jpg_is_rejected():
    r = post(plain, b"this is not a photo either", name="leaf.jpg")
    assert r.status_code == 415


def test_pdf_is_rejected():
    r = post(plain, b"%PDF-1.4\n1 0 obj << /Type /Catalog >> endobj\n%%EOF\n", name="report.pdf",
             mime="application/pdf")
    assert r.status_code == 415


def test_gif_is_rejected():
    buf = io.BytesIO()
    Image.new("RGB", (64, 64), (40, 160, 60)).save(buf, format="GIF")
    assert post(plain, buf.getvalue(), name="leaf.gif", mime="image/gif").status_code == 415


def test_empty_file_is_rejected():
    r = post(plain, b"")
    assert r.status_code == 400
    assert "empty" in r.json()["detail"]


def test_15_mb_file_is_rejected():
    r = post(plain, b"\0" * (15 * 1024 * 1024))
    assert r.status_code == 413
    assert "10 MB" in r.json()["detail"]


def test_photo_with_too_many_pixels_is_rejected():
    huge = png_bytes(Image.new("1", (10_000, 9_000)))  # 90 million pixels, but only a few KB as a file
    assert len(huge) < 1024 * 1024
    assert post(plain, huge, name="huge.png", mime="image/png").status_code == 413


def test_good_photo_while_starting_says_try_again(monkeypatch):
    monkeypatch.setattr(STATE, "predictor", None)
    path = sample_photos("L0")[0][0]
    r = post(plain, path.read_bytes(), name=path.name, mime="image/png")
    assert r.status_code == 503
    assert "starting" in r.json()["detail"]


def test_exif_rotation_is_fixed():
    """A phone held sideways stores the picture turned and says so in EXIF; we must turn it back."""
    upright = Image.open(sample_photos("L0")[0][0]).convert("RGB")
    stored = upright.transpose(Image.Transpose.ROTATE_90)  # what the camera saved
    exif = Image.Exif()
    exif[0x0112] = 6  # EXIF orientation 6 = "turn 90° clockwise to show"
    buf = io.BytesIO()
    stored.save(buf, format="PNG", exif=exif)
    assert np.array_equal(read_photo(buf.getvalue()), photo_check.prepare_photo(upright))
    assert not np.array_equal(read_photo(png_bytes(stored)), photo_check.prepare_photo(upright))  # without EXIF


# ------------------------------------------------------------------ good photos (need the model files)
@needs_models
def test_health_says_model_loaded(client):
    assert client.get("/api/health").json()["model_loaded"] is True


@needs_models
@pytest.mark.parametrize("path, disease, noise", sample_photos("L0") + sample_photos("L3"),
                         ids=lambda x: getattr(x, "stem", None))
def test_sample_photo_gives_the_right_disease(client, path, disease, noise):
    r = post(client, path.read_bytes(), name=path.name, mime="image/png")
    assert r.status_code == 200
    j = r.json()
    assert j["result"]["disease_id"] == disease
    if noise == "clean":
        assert j["result"]["decision"] == "sure" and j["photo_check"]["message"] is None
    else:
        assert j["result"]["decision"] in ("sure", "likely", "not_sure")
        assert j["photo_check"]["level"] == "L3" and j["photo_check"]["message"]
    assert len(j["neighbours"]) == 5
    assert set(j["timing_ms"]) == {"read", "photo_check", "embed", "search", "total"}
    assert j["timing_ms"]["total"] >= j["timing_ms"]["embed"] > 0


@needs_models
@pytest.mark.parametrize("fmt, mime", [("JPEG", "image/jpeg"), ("WEBP", "image/webp"), ("HEIF", "image/heic")])
def test_jpeg_webp_and_heic_are_accepted(client, fmt, mime):
    path, disease, _ = sample_photos("L0")[0]
    buf = io.BytesIO()
    Image.open(path).save(buf, format=fmt, quality=95)
    r = post(client, buf.getvalue(), name=f"leaf.{fmt.lower()}", mime=mime)
    assert r.status_code == 200
    assert r.json()["result"]["disease_id"] == disease


@needs_models
def test_check_is_remembered_without_the_photo(client):
    path = sample_photos("L3")[0][0]
    r = post(client, path.read_bytes(), name=path.name, mime="image/png", headers={"X-Device-Id": "test-device"})
    check_id = r.json()["check_id"]
    saved = STATE.checks[check_id]
    assert saved["device_id"] == "test-device"
    assert saved["result"] == r.json()["result"]

    def no_pictures(x):  # privacy: no photo bytes or pixel arrays anywhere in what we keep
        if isinstance(x, dict):
            return all(no_pictures(v) for v in x.values())
        if isinstance(x, (list, tuple)):
            return all(no_pictures(v) for v in x)
        return not isinstance(x, (bytes, bytearray, np.ndarray))

    assert no_pictures(saved)


@needs_models
def test_neighbour_thumbnails_are_served(client):
    path = sample_photos("L0")[0][0]
    url = post(client, path.read_bytes(), name=path.name, mime="image/png").json()["neighbours"][0]["thumb_url"]
    r = client.get(url)
    assert r.status_code == 200 and r.headers["content-type"] == "image/jpeg"
