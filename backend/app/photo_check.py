"""SafeCrop photo check: what is wrong with a leaf photo (blur, grain, dark, blocky) and how bad (L0-L3).

Made by notebooks/SafeCrop_app_model_export.ipynb (Day 2). The 16 measurements are copied unchanged from the
research notebook SafeCrop_photo_check.ipynb (NabilRafi/SafeCrop, notebooks/previous/), so the two random forests
in photo_check.joblib see exactly the kind of numbers they learned from.

Needs numpy, opencv-python-headless, pillow and joblib, plus the SAME scikit-learn version that trained the
forests (see export_info.json).

    from photo_check import prepare_photo, load_checker, check_photo, needs_resample, fix_resample
    checker = load_checker("photo_check.joblib")
    a = prepare_photo("leaf.jpg")          # central square, 224 x 224, RGB uint8 (CLIP uses the same picture)
    result = check_photo(a, checker)       # {"problem", "problem_words", "problem_sure", "level", "level_sure", "signs"}
"""
import os

import cv2
import numpy as np
from PIL import Image, ImageOps

SIZE = 224
FEATURES = ["brightness", "dark_share", "bright_share", "contrast", "dynamic_range", "saturation", "colourfulness",
            "grain", "grain_relative", "colour_grain", "sharpness", "fine_detail", "edges",
            "blur_direction", "blockiness", "leaf_cover"]
PROBLEM_WORDS = {"clean": "clean", "gaussian_noise": "grain", "low_light": "low light",
                 "jpeg_compression": "compression", "motion_blur": "hand-shake blur", "defocus_blur": "out of focus"}
SIGNS = [   # measurement, which side is bad, what it means (outside the range of 98% of our clean photos)
    ("brightness", "low", "too dark"), ("brightness", "high", "too bright"),
    ("dark_share", "high", "large very dark areas"), ("grain", "high", "grainy (sensor noise)"),
    ("colour_grain", "high", "coloured speckles"), ("sharpness", "low", "blurry"),
    ("fine_detail", "low", "little fine detail"), ("blur_direction", "high", "smeared in one direction (hand shake)"),
    ("blockiness", "high", "blocky (JPEG compression)"), ("saturation", "low", "faded colours"),
    ("dynamic_range", "low", "low contrast (washed out)"), ("leaf_cover", "low", "the leaf fills little of the photo"),
]


def prepare_photo(img, size=SIZE):
    """Any photo (file path, PIL image or array) -> its central square at size x size, RGB uint8.
    The same way the test photos were made: turned by EXIF, central square, bicubic resize."""
    if isinstance(img, (str, os.PathLike)):
        img = Image.open(img)
    if isinstance(img, Image.Image):
        img = ImageOps.exif_transpose(img).convert("RGB")
    else:
        img = Image.fromarray(to_array(img))
    w, h = img.size
    s = min(w, h)
    left, top = (w - s) // 2, (h - s) // 2
    img = img.crop((left, top, left + s, top + s)).resize((size, size), Image.BICUBIC)
    return np.asarray(img, dtype=np.uint8).copy()


# ---------------------------------------------------------------- copied unchanged from the research notebook
def to_array(img):
    """PIL image or array -> uint8 RGB array."""
    if isinstance(img, Image.Image):
        img = np.asarray(img.convert("RGB"))
    a = np.asarray(img)
    if a.ndim == 2:
        a = np.stack([a] * 3, axis=2)
    return np.ascontiguousarray(a[..., :3]).astype(np.uint8)


def luminance(a):
    """brightness of every pixel, 0 (black) to 1 (white)"""
    return (a.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)) / 255.0


def noise_sigma(g):
    """Immerkaer's fast estimate of random noise (same as the loop notebook's), 0 to 1 scale"""
    k = np.array([[1, -2, 1], [-2, 4, -2], [1, -2, 1]], np.float32)
    conv = cv2.filter2D(g.astype(np.float32), -1, k, borderType=cv2.BORDER_REFLECT)[1:-1, 1:-1]
    H, W = g.shape
    return float(np.sqrt(np.pi / 2) * np.abs(conv).sum() / (6 * (W - 2) * (H - 2)))


def fix_resample(a, factor=0.5):
    """shrink then enlarge: each small square of pixels is averaged, which cancels some grain"""
    H, W = a.shape[:2]
    small = cv2.resize(a, (max(8, int(W * factor)), max(8, int(H * factor))), interpolation=cv2.INTER_AREA)
    return cv2.resize(small, (W, H), interpolation=cv2.INTER_CUBIC)


def measure(img):
    """16 numbers that describe what is wrong (or right) with a photo"""
    a = to_array(img)
    if max(a.shape[:2]) != 224:
        a = cv2.resize(a, (224, 224), interpolation=cv2.INTER_AREA)
    f = a.astype(np.float32) / 255.0
    g = luminance(a)
    out = {}
    out["brightness"] = float(g.mean())
    out["dark_share"] = float((g < 0.12).mean())
    out["bright_share"] = float((g > 0.95).mean())
    out["contrast"] = float(g.std())
    p2, p98 = np.percentile(g, [2, 98])
    out["dynamic_range"] = float(p98 - p2)
    mx, mn = f.max(2), f.min(2)
    out["saturation"] = float(np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0).mean())
    rg, yb = f[..., 0] - f[..., 1], 0.5 * (f[..., 0] + f[..., 1]) - f[..., 2]
    out["colourfulness"] = float(np.hypot(rg.std(), yb.std()) + 0.3 * np.hypot(rg.mean(), yb.mean()))
    s = noise_sigma(g)
    out["grain"] = s
    out["grain_relative"] = float(s / max(g.mean(), 0.02))
    ycc = cv2.cvtColor(a, cv2.COLOR_RGB2YCrCb).astype(np.float32) / 255.0
    out["colour_grain"] = float((noise_sigma(ycc[..., 1]) + noise_sigma(ycc[..., 2])) / 2)
    lap = cv2.Laplacian(g, cv2.CV_32F)
    out["sharpness"] = float(np.log(lap.var() + 1e-8))
    P = np.abs(np.fft.fftshift(np.fft.fft2(g - g.mean()))) ** 2
    H, W = g.shape
    yy, xx = np.mgrid[-H // 2:H - H // 2, -W // 2:W - W // 2]
    r = np.hypot(yy / (H / 2), xx / (W / 2))
    band = (r > 0.02) & (r <= 1)
    out["fine_detail"] = float(P[(r > 0.35) & (r <= 1)].sum() / (P[band].sum() + 1e-12))
    u8 = (g * 255).astype(np.uint8)
    med = float(np.median(u8))
    out["edges"] = float((cv2.Canny(u8, int(max(0, 0.66 * med)), int(min(255, 1.33 * med + 1))) > 0).mean())
    # motion blur smears in one direction: compare spectral energy across 12 directions (middle frequencies)
    ang = np.mod(np.arctan2(yy, xx), np.pi)
    mid = (r > 0.08) & (r < 0.5)
    e = np.array([P[mid & (ang >= k * np.pi / 12) & (ang < (k + 1) * np.pi / 12)].mean() for k in range(12)])
    out["blur_direction"] = float(np.log((e.max() + 1e-12) / (e.min() + 1e-12)))
    dh = np.abs(np.diff(g, axis=1))
    dv = np.abs(np.diff(g, axis=0))
    bh = dh[:, 7::8].mean() / (np.delete(dh, np.s_[7::8], axis=1).mean() + 1e-6)
    bv = dv[7::8, :].mean() / (np.delete(dv, np.s_[7::8], axis=0).mean() + 1e-6)
    out["blockiness"] = float((bh + bv) / 2)
    exg = 2 * f[..., 1] - f[..., 0] - f[..., 2]
    out["leaf_cover"] = float((exg > 0.05).mean())
    return out


# ---------------------------------------------------------------- the check, for the app
def load_checker(path):
    """The forests + normal ranges saved by the notebook (needs the same scikit-learn version)."""
    import joblib
    return joblib.load(path)


def signs_of(m, ranges):
    """Plain words for every measurement outside the range of 98% of our clean photos."""
    out = []
    for k, side, words in SIGNS:
        lo, hi = ranges[k]["low"], ranges[k]["high"]
        if (side == "low" and m[k] < lo) or (side == "high" and m[k] > hi):
            out.append(words)
    return out


def check_photo(a, checker):
    """a: 224 x 224 RGB uint8 from prepare_photo. The main problem and its level, how sure, and plain-word signs."""
    m = measure(a)
    x = np.array([[m[k] for k in checker["features"]]], dtype=np.float64)
    pp = checker["problem"].predict_proba(x)[0]
    lp = checker["level"].predict_proba(x)[0]
    i, j = int(pp.argmax()), int(lp.argmax())
    problem = str(checker["problem"].classes_[i])
    return {"problem": problem, "problem_words": PROBLEM_WORDS.get(problem, problem), "problem_sure": float(pp[i]),
            "level": str(checker["level"].classes_[j]), "level_sure": float(lp[j]),
            "signs": signs_of(m, checker["ranges"]), "measurements": m}


def needs_resample(result, sure_cut=0.6):
    """The research rule: resample only blocky (JPEG-compressed) photos. When the forest is unsure, the plain-word
    signs decide. (The app uses it only if thresholds.json says use_resample.)"""
    if result["problem_sure"] >= sure_cut:
        return result["problem"] == "jpeg_compression"
    return "blocky (JPEG compression)" in result["signs"]
