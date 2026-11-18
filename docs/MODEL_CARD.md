# SafeCrop model card (app model, v1 — made 19 Nov 2026)

What the SafeCrop web app uses to name a crop disease from a phone photo, how it was made, and how well we know it works.
All numbers come from the Day 2 export (`backend/models/README.md` and `export_info.json`) and from the 5-fold
results in the research repo [NabilRafi/SafeCrop](https://github.com/NabilRafi/SafeCrop) (commit `d22d192`).

## In one paragraph

The app runs **E4**: CLIP ViT-L/14 with its last 4 blocks fine-tuned on our photos plus noisy copies, and a
**picture database** of 7,680 pictures. A photo is turned into 768 numbers, compared with every database picture, and
the **5 most similar pictures vote** (weighted by similarity). CLIP's vote names the disease. Gemini only writes the
advice and gives a second opinion; it never changes the label. Before that, a **photo check** (16 measurements + two
random forests) says what is wrong with the photo (blur, grain, dark, blocky) and how badly (L0–L3).

## How accurate is it? (the numbers to report)

**Only the 5-fold results count as accuracy.** The app model trained on every test photo, so testing it on the 840 /
960 test images would be unfair, and we never do it. Real phone photos (Day 6) are the only fair new test.

| E4, 5 folds by photo (research repo) | L0 | L1 | L2 | L3 | All |
| --- | ---: | ---: | ---: | ---: | ---: |
| Test images, 7 diseases (840) | 100 | 100 | 99.5 | **97.1** | 99.2 |
| Recipe B (noise made a different way), 7 diseases | – | – | – | **85.2** | 95.4 |
| Black gram (8th disease), test images / recipe B | – | – | – | 90.0 / 76.7 | – |

On recipe B, L3: info-rich group A 95.3% vs info-scarce group B 78.4% (Fisher p = 0.0006); weakest is jute mosaic (53.3%).

## Files (`backend/models/`, private Hugging Face repo `Radip/safecrop-models`, Drive `SafeCrop_app/app_model_files`)

| File | What it is | Size |
| --- | --- | ---: |
| `clip_ft_delta.safetensors` | the fine-tuned weights only (last 4 blocks + final norm + projection, 51.2 M numbers), put on top of `openai/clip-vit-large-patch14` | 204.7 MB |
| `database.npz` | 7,680 pictures × 768 numbers (unit length, float32) + label, photo_id, kind, noise, level, thumbnail | 27.0 MB |
| `thumbs/` + `photos.csv` | 480 clean 200-px photos (the app shows the clean one) + source and licence of each | 5.7 MB |
| `photo_check.joblib` + `photo_check.py` | two random forests (problem, level) + normal ranges, and the 16-measurement code | 2.4 MB |
| `thresholds.json` | the cut-offs below | 1 KB |

Every file has a SHA-256 checksum in `export_info.json`; the downloaded copies matched 10/10 (19 Nov).

## How it was made

**Training data:** all **240 photos** of the 8 diseases (30 each; pear leaf spot 35, potato late blight 25), clean
224 × 224 pictures. Noisy views are made on the fly (5 noise types, L1–L3, fresh seeds, never the test set's 299).

| Setting (same as E3/E4) | Value |
| --- | --- |
| Base model | `openai/clip-vit-large-patch14` (frozen except the parts below) |
| Trained parts | last 4 of 24 blocks + final layer norm + projection (51.2 M weights) |
| Epochs, photos per step | 15, 16 (each: 1 clean + 1 noisy view, random flips / quarter turns) |
| Optimiser | AdamW, lr 1e-5 (classifier head 1e-3), weight decay 0.05, 1 warm-up epoch, cosine schedule |
| Loss | cross-entropy + 1.0 × (1 − cosine(noisy view, clean view)) |
| Seed | 299 (database noisy copies: seed family 2026) |
| Training loss | 0.840 (epoch 1) → 0.152 (epoch 15) |
| Hardware, time | free Colab Tesla T4: training 176 s, whole export 18 min |

**Database:** each of 480 photos gives 1 clean picture + 15 noisy copies (5 noise types × L1–L3) = 7,680 pictures.

| Photos in the database | Photos | Label in the app |
| --- | ---: | --- |
| Our 8 diseases (the test-set photos) | 240 | the disease |
| PlantVillage apple scab (a second photo source; allowed by the research rules) | 30 | `apple_scab` |
| PlantVillage healthy apple, grape, potato | 3 × 30 | `healthy_…` → "This leaf looks healthy" |
| PlantVillage cedar apple rust, grape black rot, grape esca, potato early blight | 4 × 30 | `other_…` → "Not in our list" |

The database is embedded in plain float32, exactly as the back end embeds a farmer's photo on the CPU: the same photo
gives cosine 1.000000 on the Colab GPU and on a CPU (largest difference 2.4 × 10⁻⁷).

## Cut-offs (`thresholds.json`)

Chosen **before** any real-photo test; they must not be changed after looking at real-photo results.

| Cut-off | Value | Meaning | How it was chosen |
| --- | ---: | --- | --- |
| `sure` | 0.902 | vote share ≥ this → "Very likely" | isotonic fit of right/wrong on vote share, research repo's out-of-fold E4 answers on recipe B (960): where answers are right ≥ 95% |
| `not_sure` | 0.601 | vote share < this → "Not sure" (between: "Likely") | same fit: below it answers are right < 70% |
| `not_a_leaf` | 0.760 | best similarity < this → "We can't read this photo" | fold-0 model: 192 held-out leaf images vs 44 non-leaf pictures (30 phone photos + 14 sample pictures) |
| `photo_check_sure` | 0.6 | trust the photo check's main problem only at ≥ 60% | research photo-check notebook |
| `use_resample` | true | shrink + enlarge blocky (JPEG) photos before CLIP | fold-0 check below (helps or ties → keep) |
| `k` | 5 | the 5 most similar pictures vote | research (Step 2 onwards) |

"Sure" in practice means **all 5 similar pictures agree**. How the out-of-fold answers split (research repo, E4):

| Answers (out of fold) | Sure | Likely | Not sure |
| --- | --- | --- | --- |
| Recipe B (used to choose) | 98.8% right (846/856) | 76.9% (50/65) | 41.0% (16/39) |
| Test images | 99.9% (912/913) | 81.8% (27/33) | 50.0% (7/14) |

## The fair checks (fold 0: a second model trained without 48 photos, same seed)

**1. Do the healthy / look-alike pictures hurt?** The same 192 held-out images, three databases:

| Database | L0 | L1 | L2 | L3 | L3 answered healthy / other |
| --- | --- | --- | --- | --- | ---: |
| Our 8 diseases only (E4, as in the repo) | 100% (48/48) | 97.9% (47/48) | 97.9% (47/48) | **97.9% (47/48)** | 0 |
| + 210 healthy / look-alike pictures | 100% (48/48) | 97.9% (47/48) | 97.9% (47/48) | 85.4% (41/48) | 6 |
| + all 240 extras (**the app**) | 100% (48/48) | 97.9% (47/48) | 97.9% (47/48) | **85.4% (41/48)** | 6 |

- Our "ours only" row reproduces the research repo's own E4 fold-0 run exactly (L3 47/48).
- The extras cost **6 of 48 L3 images** (McNemar: 0 vs 6, p = 0.031); all 6 were answered "healthy" or "not in our
  list", none a wrong disease. L0–L2 are unchanged. (Frozen noisy album, for comparison: 95.2% → 88.1% at L3.)
- All 6 are **grape leaf blight or potato late blight**, our two PlantVillage-sourced diseases, pulled towards
  PlantVillage healthy / look-alike leaves (photo style). 5 of the 6 had a vote share below the "not sure" cut-off
  (0.40–0.60), so the app would mostly say "not sure" for them, not a confident wrong answer.
- This is the price of being able to say "healthy" or "not in our list". With the cut-offs, the app's answers on fold 0
  were: **sure 99.4% right (161/162; L3 31/31)**, likely 85.7% (18/21), not sure 44.4% (4/9).

**2. Does resample help compressed photos?** (app database)

| Level | Compressed images | Right without | Right with | Fixed | Broken |
| --- | ---: | ---: | ---: | ---: | ---: |
| L1 | 9 | 9 | 9 | 0 | 0 |
| L2 | 9 | 9 | 9 | 0 | 0 |
| L3 | 9 | 8 | 8 | 0 | 0 |

A tie, so resample stays (rule fixed in advance: keep if it helps or ties). 9 images are too few to show a difference;
the reason to keep it is the frozen-model result (57% → 79% on compressed L3).

**3. Not a leaf.** Best similarity to any database picture:

| Pictures | Best similarity | Called "not a leaf" (cut-off 0.760) |
| --- | --- | --- |
| Held-out leaves L0 / L1 / L2 / L3 | 0.919–0.990 / 0.881–0.981 / 0.871–0.975 / **0.790**–0.958 | 0 of 192 |
| Non-leaf phone photos (desk, hand, sky, food …) | 0.448–**0.730** | 30 of 30 |
| Built-in sample pictures | 0.407–0.606 | 14 of 14 |

Perfect separation, but the gap is narrow at L3 (0.790 vs 0.730): a very bad leaf photo can come close to the cut-off.
The app model with the same cut-off also rejects 30/30 + 14/14 non-leaf pictures.

## Photo check

Fair test on all 960 images (5 folds by photo): **problem right 98.0%, level right 93.2%** (within one level 99.7%);
problem right at L0 100%, L1 95.0%, L2 99.6%, L3 97.5%. Its only mistakes: telling hand-shake blur from out of focus
(8 + 8 images) and calling 3 hand-shake photos clean. The 16 measurements equal the research notebook's for
840/840 images on Colab (Linux). On a Windows laptop with the same OpenCV, 6/840 differ very slightly (edge count,
one bright pixel); the forests give the same answers for all 6 (largest probability change 0.004).

## Versions (pinned in `backend/requirements.txt`)

| Library | Colab (made the files) | Pinned for the back end |
| --- | --- | --- |
| scikit-learn | 1.6.1 | `==1.6.1` (the forests only load with this version) |
| numpy | 2.4.6 | `==2.4.6` |
| OpenCV | 4.14.0 | `opencv-python-headless==4.14.0.*` (measurements can shift between versions) |
| joblib | 1.6.0 | `==1.6.0` |
| torch / transformers | 2.14.1 (CUDA 13.0) / 5.22.1 | not pinned (the weights are plain tensors) |
| Python | 3.13 | back end runs 3.11 |

## Known limits (say these in reports)

- All noise is computer-made, one problem per photo. **Real phone photos are not tested yet** (Day 6).
- Each disease comes from one photo source (apple scab: two), so CLIP can partly match photo **style**. Potato late
  blight and grape leaf blight are PlantVillage lab photos.
- The healthy / look-alike pictures lower L3 accuracy on fold 0 by 6 of 48 images (see above); those photos get
  "healthy" or "not in our list" instead of the disease.
- The fold-0 checks use 48 photos (192 images): about ±7 points of chance variation per level.
- Black gram rests on 30 photos. Only the default fine-tuning settings were tried.
- The "not a leaf" check was set with 30 phone photos and 14 sample pictures; unusual objects may still pass.
- The app model must never be scored on the test images (it trained on them).
