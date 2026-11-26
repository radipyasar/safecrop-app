"""Database search, vote and decision: from 768 numbers to an answer the farmer can read.

The vote is the research repo's `database_vote` (safecrop/evaluate.py): the 5 most similar database pictures vote,
each with its similarity, and the vote share is the winner's part of the total. The cut-offs in thresholds.json were
chosen on exactly this vote share, so it must not change.

Decision rules (checked in this order; option C chosen by Nabil on 21 Nov 2026):

1. best similarity < not_a_leaf                                   -> retake ("this doesn't look like a leaf")
2. photo check is sure (>= photo_check_sure) the photo is L3 and the vote share < not_sure
                                                                   -> retake ("too unclear")
3. the winner is a healthy leaf or a look-alike disease (not one of our 8):
   vote share >= sure AND the photo check does not say L3         -> healthy / not_in_list
   otherwise (option C)                                           -> not_sure: show the closest of our 8 diseases,
                                                                     the healthy / look-alike label as runner-up,
                                                                     and a retake tip
4. one of our 8 diseases: vote share >= sure -> sure; >= not_sure -> likely; else not_sure

"Closest disease" = the same 5-picture vote, but only over pictures of our 8 diseases.

The library = database.npz (v1, never changed) + database_added.npz (photos our second check, Gemini, labelled;
see app/learn.py). Added rows have no thumbnail (we never keep the photo) and carry Gemini's own words as their name.
"""

import csv
import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import photo_check
from .model import embed, load_model, set_threads

EXTRA_KINDS = ("healthy", "other")  # database pictures that are not one of our 8 diseases
OTHER_UNKNOWN = "other_unknown"     # label of added photos that Gemini said are not one of our 8
ADDED_FILE = "database_added.npz"

CONFIDENCE_WORDS = {"sure": "Very likely", "likely": "Likely", "not_sure": "Not sure", "healthy": "Looks healthy",
                    "not_in_list": "Not in our list", "retake": "Can't read this photo"}

# What to tell the farmer about the photo itself (one "blurry" message for both kinds of blur)
PHOTO_TIPS = {
    "motion_blur": "Your photo is blurry. Hold the phone steady and tap the leaf on the screen to focus.",
    "defocus_blur": "Your photo is blurry. Hold the phone steady and tap the leaf on the screen to focus.",
    "gaussian_noise": "Your photo is grainy. Take it in better light.",
    "low_light": "Your photo is too dark. Move to brighter light, but not harsh direct sun.",
    "jpeg_compression": "Your photo is blocky (too compressed). Use the original photo from the camera, "
                        "not a copy sent through a chat app.",
}
GENERIC_TIP = "Take a new photo of one leaf, close up, in good light."
NOT_A_LEAF_TIP = "This doesn't look like a leaf. Take a close photo of one leaf so that it fills most of the picture."


@dataclass(frozen=True)
class Library:
    """database.npz (+ database_added.npz) + names from photos.csv + thresholds.json. Never changed in place:
    adding rows makes a new Library, so a check that is already running keeps a consistent copy."""
    emb: np.ndarray          # N x 768, unit length
    label: np.ndarray        # N labels, e.g. "potato_late_blight", "healthy_potato", "other_potato_early_blight"
    photo_id: np.ndarray     # N photo ids (a clean picture and its 15 noisy copies share one id)
    is_disease: np.ndarray   # N booleans: one of our 8 diseases?
    names: dict              # label -> {"name", "crop", "kind"}
    thresholds: dict
    row_name: np.ndarray     # N display names: the label's name, or Gemini's own words for added rows
    added: np.ndarray        # N booleans: from database_added.npz (these have no thumbnail)

    def kind(self, label):
        return self.names[label]["kind"]

    def name(self, label):
        return self.names[label]["name"]

    @property
    def n_added(self):
        return int(self.added.sum())

    def extended(self, emb, label, photo_id, row_name):
        """A new Library with extra (added) rows at the end."""
        label = np.asarray(label, dtype=str)
        return Library(emb=np.ascontiguousarray(np.vstack([self.emb, np.asarray(emb, dtype=np.float32)])),
                       label=np.concatenate([self.label, label]),
                       photo_id=np.concatenate([self.photo_id, np.asarray(photo_id, dtype=str)]),
                       is_disease=np.concatenate([self.is_disease, [self.kind(x) == "disease" for x in label]]),
                       names=self.names, thresholds=self.thresholds,
                       row_name=np.concatenate([self.row_name, np.asarray(row_name, dtype=str)]),
                       added=np.concatenate([self.added, np.ones(len(label), dtype=bool)]))


def load_library(models_dir, added_path=None):
    """database.npz + photos.csv + thresholds.json, then the rows of database_added.npz if that file exists
    (added_path: where it is; default models_dir/database_added.npz)."""
    models_dir = Path(models_dir)
    db = np.load(models_dir / "database.npz")
    names = {}
    with open(models_dir / "photos.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            names.setdefault(row["label"], {"name": row["label_name"], "crop": row["crop"], "kind": row["kind"]})
    names[OTHER_UNKNOWN] = {"name": "Not in our list", "crop": None, "kind": "other"}
    thresholds = json.loads((models_dir / "thresholds.json").read_text(encoding="utf-8"))
    label = db["label"].astype(str)
    lib = Library(emb=np.ascontiguousarray(db["emb"], dtype=np.float32), label=label,
                  photo_id=db["photo_id"].astype(str), is_disease=np.array([names[x]["kind"] == "disease" for x in label]),
                  names=names, thresholds=thresholds, row_name=np.array([names[x]["name"] for x in label]),
                  added=np.zeros(len(label), dtype=bool))
    added_path = Path(added_path) if added_path else models_dir / ADDED_FILE
    if added_path.exists():
        with np.load(added_path) as a:
            if len(a["label"]):
                lib = lib.extended(a["emb"], a["label"].astype(str), a["photo_id"].astype(str), a["name"].astype(str))
    return lib


def weighted_vote(labels, similarities):
    """The research repo's vote: each picture adds its similarity (at least 0) to its label.
    Returns [(label, share), ...], biggest share first."""
    votes = {}
    for lab, s in zip(labels, similarities):
        votes[lab] = votes.get(lab, 0.0) + max(float(s), 0.0) + 1e-6
    total = sum(votes.values())
    return [(lab, v / total) for lab, v in sorted(votes.items(), key=lambda kv: -kv[1])]


def decide(winner_kind, share, best_similarity, level, level_sure, t):
    """The decision rules from the top of this file. Returns (decision, reason)."""
    if best_similarity < t["not_a_leaf"]:
        return "retake", "not_a_leaf"
    if level == "L3" and level_sure >= t["photo_check_sure"] and share < t["not_sure"]:
        return "retake", "too_unclear"
    if winner_kind in EXTRA_KINDS:
        if share >= t["sure"] and level != "L3":
            return ("healthy" if winner_kind == "healthy" else "not_in_list"), None
        return "not_sure", "healthy_or_other_unclear"  # option C
    if share >= t["sure"]:
        return "sure", None
    if share >= t["not_sure"]:
        return "likely", None
    return "not_sure", "weak_vote"


def photo_message(check):
    """The photo warning, or None when the photo looks fine."""
    if check["problem"] == "clean" or check["level"] == "L0":
        return None
    return PHOTO_TIPS.get(check["problem"], GENERIC_TIP)


def unique_neighbours(order, lib, n=5):
    """The n most similar pictures from n different photos (a photo's noisy copies count once)."""
    seen, out = set(), []
    for i in order:
        if lib.photo_id[i] not in seen:
            seen.add(lib.photo_id[i])
            out.append(i)
            if len(out) == n:
                break
    return out


class Predictor:
    """Everything one check needs, loaded once at start-up."""

    def __init__(self, model, lib, checker):
        self.model, self.lib, self.checker = model, lib, checker
        self.t = lib.thresholds
        self._add_lock = threading.Lock()

    @classmethod
    def load(cls, models_dir, added_path=None):
        models_dir = Path(models_dir)
        set_threads()
        lib = load_library(models_dir, added_path)
        checker = photo_check.load_checker(models_dir / "photo_check.joblib")
        model = load_model(models_dir / "clip_ft_delta.safetensors")
        return cls(model, lib, checker)

    def warm_up(self):
        """One made-up photo through every step, so the first real check is not slow."""
        rng = np.random.default_rng(0)
        fake = np.clip(rng.normal([90, 140, 70], 30, (224, 224, 3)), 0, 255).astype(np.uint8)
        self.run(fake)

    def add_rows(self, emb, label, photo_id, row_name):
        """Put newly added rows into the live library, so the next check can match them."""
        with self._add_lock:
            self.lib = self.lib.extended(emb, label, photo_id, row_name)

    def run(self, photo):
        """photo: 224 x 224 RGB uint8 from photo_check.prepare_photo. Returns photo_check, result, neighbours,
        timing_ms, `raw` (numbers for the server's own log) and `emb` (the 768 numbers, kept in memory only)."""
        t, ms = self.t, {}

        t0 = time.perf_counter()
        check = photo_check.check_photo(photo, self.checker)
        fix = None
        if t["use_resample"] and photo_check.needs_resample(check, t["photo_check_sure"]):
            photo, fix = photo_check.fix_resample(photo), "resample"
        ms["photo_check"] = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        q = embed(self.model, photo)
        ms["embed"] = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        out = self.answer(q, check)
        ms["search"] = (time.perf_counter() - t0) * 1000

        out["photo_check"] = {"problem": check["problem"], "problem_words": check["problem_words"],
                              "level": check["level"], "sure": round(check["problem_sure"], 3),
                              "level_sure": round(check["level_sure"], 3), "signs": check["signs"],
                              "message": photo_message(check), "fix_applied": fix}
        out["timing_ms"] = {k: round(v, 1) for k, v in ms.items()}
        out["emb"] = q
        return out

    def answer(self, q, check):
        """768 numbers + the photo check -> result, neighbours and raw vote (no CLIP needed, so tests can call it
        with an embedding saved in the database)."""
        t, lib = self.t, self.lib
        sims = lib.emb @ q
        order = np.argsort(-sims)
        top = order[: t["k"]]
        ranked = weighted_vote(lib.label[top], sims[top])
        winner, share = ranked[0]
        best = float(sims[order[0]])
        decision, reason = decide(lib.kind(winner), share, best, check["level"], check["level_sure"], t)

        def name_of(label):  # an added "not in our list" photo is named with Gemini's words for the closest one
            if label == OTHER_UNKNOWN:
                return str(lib.row_name[next(i for i in order if lib.label[i] == label)])
            return lib.name(label)

        def guess(label, s):
            return {"disease_id": str(label), "disease_name": name_of(label), "vote_share": round(float(s), 4)}

        shares = dict(ranked)
        if decision == "retake":
            shown, runner_up = None, None
        elif decision == "not_sure" and reason == "healthy_or_other_unclear":
            d_order = order[lib.is_disease[order]][: t["k"]]  # option C: the closest of our 8 diseases
            shown = weighted_vote(lib.label[d_order], sims[d_order])[0][0]
            runner_up = guess(winner, share)
        else:
            shown = winner
            runner_up = guess(*ranked[1]) if len(ranked) > 1 else None

        neighbours = [{"disease_id": str(lib.label[i]), "disease_name": str(lib.row_name[i]),
                       "thumb_url": None if lib.added[i] else f"/static/thumbs/{lib.photo_id[i]}.jpg",
                       "added": bool(lib.added[i]), "similarity": round(float(sims[i]), 4)}
                      for i in unique_neighbours(order, lib)]

        message = photo_message(check)
        if decision == "retake" and reason == "not_a_leaf":
            tip = NOT_A_LEAF_TIP
        elif decision in ("retake", "not_sure", "likely"):
            tip = message or GENERIC_TIP
        else:
            tip = None

        return {
            "result": {"decision": decision, "reason": reason, "disease_id": shown,
                       "disease_name": name_of(shown) if shown else None,
                       "crop": lib.names[shown]["crop"] if shown else None,
                       "vote_share": round(float(shares.get(shown, 0.0)), 4) if shown else round(float(share), 4),
                       "confidence_words": CONFIDENCE_WORDS[decision], "runner_up": runner_up, "tip": tip,
                       "best_similarity": round(best, 4)},
            "neighbours": neighbours,
            "raw": {"winner": winner, "share": round(float(share), 4)},
        }
