"""The Day 2 noise recipe, used to make 15 noisy copies (5 noise types x L1-L3) of a photo that our second check
(Gemini) labelled, exactly like the copies in database.npz.

Copied unchanged from the research repo NabilRafi/SafeCrop, src/safecrop/noise.py (commit d22d192, the one the
Day 2 notebook used). The four library effects come from imagecorruptions 1.1.2 (Apache License 2.0,
https://github.com/bethgelab/imagecorruptions); low_light is our own. tests/test_learn.py checks that this file
rebuilds the database.npz copies.

Copies use the seed family 2026 (COPY_SEED), never 299 (the test set's).
"""
from __future__ import annotations

import math
import zlib
from io import BytesIO

import cv2
import numpy as np
from PIL import Image

NOISE_TYPES = ["gaussian_noise", "motion_blur", "defocus_blur", "low_light", "jpeg_compression"]
NICE = {"gaussian_noise": "Sensor noise", "motion_blur": "Hand-shake blur", "defocus_blur": "Out of focus",
        "low_light": "Low light", "jpeg_compression": "Compression"}
LEVELS = {1: 1, 2: 3, 3: 5}          # our level -> library severity (low_light uses its own 1/2/3)
TEST_SEED = 299                      # seed family of the test set (never use it for training data)
IMAGE_SIZE = 224


# ----------------------------------------------------------------------------- imagecorruptions 1.1.2 (Apache-2.0)
def _disk(radius, alias_blur=0.1, dtype=np.float32):
    if radius <= 8:
        L = np.arange(-8, 8 + 1)
        ksize = (3, 3)
    else:
        L = np.arange(-radius, radius + 1)
        ksize = (5, 5)
    X, Y = np.meshgrid(L, L)
    aliased_disk = np.array((X ** 2 + Y ** 2) <= radius ** 2, dtype=dtype)
    aliased_disk /= np.sum(aliased_disk)
    return cv2.GaussianBlur(aliased_disk, ksize=ksize, sigmaX=alias_blur)


def _gauss_function(x, mean, sigma):
    return (np.exp(- x ** 2 / (2 * (sigma ** 2)))) / (np.sqrt(2 * np.pi) * sigma)


def _motion_kernel(width, sigma):
    k = _gauss_function(np.arange(width), 0, sigma)
    return k / np.sum(k)


def _shift(image, dx, dy):
    if dx < 0:
        shifted = np.roll(image, shift=image.shape[1] + dx, axis=1)
        shifted[:, dx:] = shifted[:, dx - 1:dx]
    elif dx > 0:
        shifted = np.roll(image, shift=dx, axis=1)
        shifted[:, :dx] = shifted[:, dx:dx + 1]
    else:
        shifted = image
    if dy < 0:
        shifted = np.roll(shifted, shift=image.shape[0] + dy, axis=0)
        shifted[dy:, :] = shifted[dy - 1:dy, :]
    elif dy > 0:
        shifted = np.roll(shifted, shift=dy, axis=0)
        shifted[:dy, :] = shifted[dy:dy + 1, :]
    return shifted


def _motion_blur_core(x, radius, sigma, angle):
    width = radius * 2 + 1
    kernel = _motion_kernel(width, sigma)
    point = (width * np.sin(np.deg2rad(angle)), width * np.cos(np.deg2rad(angle)))
    hypot = math.hypot(point[0], point[1])
    blurred = np.zeros_like(x, dtype=np.float32)
    for i in range(width):
        dy = -math.ceil(((i * point[0]) / hypot) - 0.5)
        dx = -math.ceil(((i * point[1]) / hypot) - 0.5)
        if np.abs(dy) >= x.shape[0] or np.abs(dx) >= x.shape[1]:
            break
        blurred = blurred + kernel[i] * _shift(x, dx, dy)
    return blurred


def _gaussian_noise(x, severity=1):
    c = [.08, .12, 0.18, 0.26, 0.38][severity - 1]
    x = np.array(x) / 255.
    return np.clip(x + np.random.normal(size=x.shape, scale=c), 0, 1) * 255


def _defocus_blur(x, severity=1):
    c = [(3, 0.1), (4, 0.5), (6, 0.5), (8, 0.5), (10, 0.5)][severity - 1]
    x = np.array(x) / 255.
    kernel = _disk(radius=c[0], alias_blur=c[1])
    channels = [cv2.filter2D(x[:, :, d], -1, kernel) for d in range(3)]
    return np.clip(np.array(channels).transpose((1, 2, 0)), 0, 1) * 255


def _motion_blur(x, severity=1):
    c = [(10, 3), (15, 5), (15, 8), (15, 12), (20, 15)][severity - 1]
    x = np.array(x)
    angle = np.random.uniform(-45, 45)
    return np.clip(_motion_blur_core(x, radius=c[0], sigma=c[1], angle=angle), 0, 255)


def _jpeg_compression(x, severity=1):
    c = [25, 18, 15, 10, 7][severity - 1]
    output = BytesIO()
    x.save(output, "JPEG", quality=c)
    return Image.open(output)


_LIBRARY = {"gaussian_noise": _gaussian_noise, "defocus_blur": _defocus_blur,
            "motion_blur": _motion_blur, "jpeg_compression": _jpeg_compression}


def corrupt(image: np.ndarray, corruption_name: str, severity: int) -> np.ndarray:
    """Same behaviour as imagecorruptions.corrupt for our four effects (uint8 HxWx3 in, uint8 out)."""
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("expected an RGB uint8 image (H x W x 3)")
    if severity not in (1, 2, 3, 4, 5):
        raise ValueError("severity must be 1..5")
    return np.uint8(_LIBRARY[corruption_name](Image.fromarray(image), severity))


# ----------------------------------------------------------------------------- our own effect
def low_light(img: np.ndarray, level: int, photons: int = 120) -> np.ndarray:
    light = {1: 0.30, 2: 0.12, 3: 0.05}[level]                    # share of light reaching the camera
    x = img.astype(np.float32) / 255.0
    signal = np.random.poisson(x * light * photons) / photons     # fewer photons -> grain
    out = signal * (1.0 / light) ** 0.5                           # the phone brightens it part of the way back
    grey = out.mean(axis=2, keepdims=True)
    out = grey + (out - grey) * {1: 0.90, 2: 0.75, 3: 0.60}[level]   # colours fade in the dark
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)


# ----------------------------------------------------------------------------- the test-set recipe
def make_noisy(img: np.ndarray, noise: str, level: int, seed: int) -> np.ndarray:
    """One noise type at one of our levels (1, 2, 3). Seeds NumPy's global generator, like the notebook."""
    np.random.seed(seed)
    if noise == "low_light":
        out = low_light(img, level)
    else:
        out = corrupt(img, corruption_name=noise, severity=LEVELS[level])
    return np.clip(out, 0, 255).astype(np.uint8)


def seed_for(photo_id: str, noise: str, level: int, base: int = TEST_SEED) -> int:
    """The fixed seed of one (photo, noise, level). base=299 rebuilds the test set."""
    return zlib.crc32(f"{base}/{photo_id}/{noise}/{level}".encode()) & 0x7FFFFFFF


# ----------------------------------------------------------------------------- the app's noisy copies
COPY_SEED = 2026                     # the database.npz copies' seed family (export_info.json: noisy_copy_seed)


def noisy_copies(img: np.ndarray, photo_id: str):
    """The 15 noisy copies of one 224 x 224 photo, in database.npz order: [(noise, level, seed, image), ...]."""
    out = []
    for noise in NOISE_TYPES:
        for level in (1, 2, 3):
            seed = seed_for(photo_id, noise, level, COPY_SEED)
            out.append((noise, level, seed, make_noisy(img, noise, level, seed)))
    return out
