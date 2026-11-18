"""Make the one zip the Day 2 Colab notebook needs: dist/safecrop_app_inputs.zip (about 90 MB).

It copies, from the research repo (NabilRafi/SafeCrop, cloned next to this repo):
  * the research code (src/safecrop) and its settings (configs/default.yaml)
  * the 960 test images (840 + 120 black gram) and the 240 PlantVillage extras
  * the tables: manifests, labels, extra_references, the saved photo-check measurements
  * the E4 out-of-fold answers (test images and recipe B), used for the "sure" / "not sure" cut-offs

Run it on the laptop (any Python 3.9+, no packages needed), from the safecrop-app folder:
    python notebooks/make_colab_inputs.py                  # research repo at ../SafeCrop
    python notebooks/make_colab_inputs.py --repo D:/SafeCrop
Then upload dist/safecrop_app_inputs.zip to My Drive/SafeCrop_app/ (see the notebook's first cell).
"""
from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]           # the safecrop-app folder
ROOT_IN_ZIP = "safecrop_research"                        # the notebook expects this folder inside the zip

E4_RUNS = {   # E4 (fine-tuned CLIP + noisy copies), 8 diseases, 5 folds by photo: out-of-fold answers
    "test": "results/finetune/20261111-153945_clip-vit-large-patch14_e4_8d",
    "recipe_b": "results/finetune/20261111-160258_clip-vit-large-patch14_e4_8d_rb",
}
TABLES = [
    "configs/default.yaml",
    "data/manifest.csv",
    "data/manifest_black_gram.csv",
    "data/manifest_recipe_b.csv",
    "data/labels.csv",
    "data/extra_references.csv",
    "data/baselines/photo_check_quality_measurements.csv",
]


def image_list(repo: Path) -> list[str]:
    """Exactly the image files the notebook reads, taken from the manifests (relative to the repo)."""
    out = []
    for manifest, folder, n in [("data/manifest.csv", "data/images", 840),
                                ("data/manifest_black_gram.csv", "data/images_black_gram", 120)]:
        rows = list(csv.DictReader(open(repo / manifest, encoding="utf-8")))
        if len(rows) != n:
            sys.exit(f"{manifest} has {len(rows)} rows, expected {n}")
        out += [f"{folder}/{r['image']}" for r in rows]
    extras = list(csv.DictReader(open(repo / "data/extra_references.csv", encoding="utf-8")))
    if len(extras) != 240:
        sys.exit(f"data/extra_references.csv has {len(extras)} rows, expected 240")
    out += [f"data/{r['path']}" for r in extras]
    return out


def git_commit(repo: Path) -> tuple[str, bool]:
    try:
        commit = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True,
                                check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"], capture_output=True, text=True,
                               check=True).stdout.strip()
        return commit, not dirty
    except Exception:                       # git missing or not a git folder: still make the zip
        return "unknown", False


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=str(APP_ROOT.parent / "SafeCrop"), help="the research repo folder")
    ap.add_argument("--out", default=str(APP_ROOT / "dist" / "safecrop_app_inputs.zip"), help="the zip to write")
    args = ap.parse_args()
    repo, out = Path(args.repo).resolve(), Path(args.out).resolve()
    if not (repo / "src" / "safecrop" / "finetune.py").is_file():
        sys.exit(f"No research repo at {repo} (expected src/safecrop/finetune.py). Use --repo PATH.")

    files = [f"src/safecrop/{p.name}" for p in sorted((repo / "src" / "safecrop").glob("*.py"))]
    files += TABLES
    for run in E4_RUNS.values():
        files += [f"{run}/{name}" for name in ("predictions_database.csv", "config.yaml", "summary.md")]
    images = image_list(repo)
    missing = [f for f in files + images if not (repo / f).is_file()]
    if missing:
        sys.exit(f"{len(missing)} files are missing in {repo}, for example {missing[:3]}")

    commit, clean = git_commit(repo)
    info = {
        "made": datetime.datetime.now().isoformat(timespec="seconds"),
        "made_by": "safecrop-app/notebooks/make_colab_inputs.py",
        "research_repo": "https://github.com/NabilRafi/SafeCrop",
        "research_commit": commit,
        "research_repo_unchanged": clean,
        "e4_out_of_fold": {k: f"{v}/predictions_database.csv" for k, v in E4_RUNS.items()},
        "counts": {"code_and_tables": len(files), "test_images": 840, "black_gram_images": 120,
                   "plantvillage_extras": 240},
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w") as z:
        z.writestr(f"{ROOT_IN_ZIP}/BUNDLE_INFO.json", json.dumps(info, indent=1), compress_type=zipfile.ZIP_DEFLATED)
        for f in files:                                   # text: compress
            z.write(repo / f, f"{ROOT_IN_ZIP}/{f}", compress_type=zipfile.ZIP_DEFLATED)
        for f in images:                                  # PNG / JPG are already compressed: store as they are
            z.write(repo / f, f"{ROOT_IN_ZIP}/{f}", compress_type=zipfile.ZIP_STORED)

    h = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"Wrote {out}")
    print(f"  {len(files)} code/table files + {len(images)} images "
          f"(840 test + 120 black gram + 240 PlantVillage extras)")
    print(f"  size {out.stat().st_size / 1e6:.1f} MB, sha256 {h[:12]}...")
    print(f"  research repo commit {commit[:7]}" + ("" if clean else "  (WARNING: the research repo has uncommitted changes)"))
    print("Next: upload this zip to My Drive/SafeCrop_app/ in Google Drive.")


if __name__ == "__main__":
    main()
