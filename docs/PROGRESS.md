# SafeCrop web app — progress

Update this at the end of every day (the `/wrapup` command does it for you).

## Status by day

| Day | Date | Goal | Status |
| --- | --- | --- | --- |
| 1 | Tue 17 Nov | Set up the project, connect all pages | done (checklist + teammate done 23 Nov) |
| 2 | Wed 18 Nov | Make the app's model files in Colab | done 19 Nov (Colab run 18 min; files in `backend/models/`, HF, Drive) |
| 3 | Sat 21 Nov | Back end: photo in, disease out | done (`/api/check` works, 79 tests, 0.82 s per check) |
| — | Sun 22 Nov | Week 10 update (shows work up to Day 3) | done (presented) |
| 4 | Mon 23 Nov | Back end: Gemini advice + disease facts | done (`/api/advice` + fallback, `/api/diseases`, SQLite log, 140 tests) |
| 5 | Tue 24 Nov | Front end: the full check flow | not started |
| 6 | Tue 24 (B) + Wed 25 (A) | Disease pages (Tue); real photos on the online app (Wed, after Day 8) | not started |
| 7 | Tue 24 Nov | History, Profile, Home with real data | not started |
| 8 | Wed 25 Nov | Put it online (Hugging Face + Vercel) | not started |
| 9 | Thu 26 Nov | Test everything, fix bugs | not started |
| 10 | Thu 26 Nov | Must-have polish, safety, documents | not started |
| 11 | Thu 26 Nov | Freeze, demo video, backups | not started |
| — | Mon 30 Nov | Week 11 update | not started |

Dates shifted by 2 days on 21 Nov, then 1 more day from Day 4. **Plan shortened on 24 Nov: everything finished by
Thu 26 Nov** (Tue 24 = Days 5, 6B, 7 · Wed 25 = Day 8, then 6A · Thu 26 = Days 9, 10, 11). Week 11 update stays Mon 30.

## Where things are now (23 Nov, end of Day 4 — on the shifted plan)

- Front end: routing works — 7 pages + "page not found"; menus highlight the current page; home buttons
  open `/check`. Only the home page has real content (sample data); other pages are titles.
  `src/api.js` has `getHealth()`; the sidebar shows a server online / offline dot. (Day 5 connects it to `/api/check`.)
- Back end: **`POST /api/check` works** — photo check (16 measurements + forests, resample for blocky photos),
  fine-tuned CLIP, 5-picture vote, option C decisions, 5 neighbours from different photos, clean thumbnails at
  `/static/thumbs/`, `timing_ms`. Model loads once in the background at start-up (`/api/health` → `model_loaded`;
  `/api/check` says "starting" with 503 until then). Uploads: JPEG / PNG / WebP / HEIC ≤ 10 MB, EXIF turn fixed,
  clear 400 / 413 / 415 errors. The newest 1,000 results (never photos) are kept in memory for `/api/advice`.
  Files: `app/main.py`, `model.py`, `predict.py`, `photo_check.py`, `schemas.py`.
  `scripts/time_checks.py` times start-up and checks (also `--url` for the Space on Day 8).
  All packages installed in `backend/.venv`; torch 2.14.1, transformers 5.22.1, Pillow 11.3.0 pinned to Colab.
- Back end, Day 4: **`POST /api/advice` works** (form: `check_id`, `lang` en/bn, optional `image` used once, never
  stored) — Gemini 3.5 Flash-Lite writes advice from the facts (JSON schema, 20 s timeout + 1 retry, cached by check +
  language, chemical / dose check), fallback from `diseases.json` with `fallback_reason`; retake answers never call
  Gemini. **`GET /api/diseases`** (8) and **`/api/diseases/{id}`** (facts, sources, 6 photos, credit, helpline 16123).
  **SQLite log** `app/db.py` → `backend/safecrop.db` (git-ignored; `DB_PATH` to move it): one row per check, advice
  added later; numbers and labels only. `data/diseases.json`: 8 diseases + healthy + unknown, all checked by Nabil.
  `scripts/try_advice.py` tries real Gemini on sample photos (`--lang bn`, `--no-key`). **140 tests pass** (110 s);
  tests blank the Gemini key and use a throw-away log, so they never spend quota. Version 0.4.0.
- Models: **done.** `backend/models/` (git-ignored) has `clip_ft_delta.safetensors`, `database.npz` (7,680 × 768),
  `thumbs/` (480), `photos.csv`, `photo_check.joblib` + `photo_check.py`, `thresholds.json`, `README.md`,
  `export_info.json`, `checks/`. Same files in the private HF repo `Radip/safecrop-models` and Drive
  `SafeCrop_app/app_model_files`. Checksums 10/10; all load with the pinned versions on Python 3.11; laptop CPU gives
  the same embeddings as the Colab database (cosine 1.000000). CLIP ViT-L/14 (1.7 GB) is in the laptop's HF cache.
- Docs: `docs/MODEL_CARD.md` written. Notebook `notebooks/SafeCrop_app_model_export.ipynb` + `make_colab_inputs.py`.
- Git: on GitHub (`radipyasar/safecrop-app`), everything pushed. Day 4 = `cd54d91`, `03871ab`, `503e559` (+ this
  wrap-up). No keys in git.
- Accounts: Hugging Face account + write token, Vercel account (Hobby) — done 18 Nov.
  `GEMINI_API_KEY`, `HF_TOKEN`, `ALLOWED_ORIGINS` are set in `backend/.env` (git-ignored); `HF_TOKEN` is also a
  Colab secret. Gemini key works: `backend/scripts/check_gemini.py` got a reply from `gemini-3.5-flash-lite` (18 Nov).

## Daily log

### Day 1 — Tue 17 Nov
- **Done:** router + 8 pages, NavLink menus, `api.js` + online dot, FastAPI `/api/health` + CORS, `requirements.txt`, `.env.example`, 3 tests, first commit.
- **Left over:** checklist, tell teammate. (HF + Vercel accounts, HF token, GitHub repo + push, Gemini key check: done 18 Nov.)
- **Blockers:** none (Python 3.11 installed today).

### Day 2 — Wed 18 Nov
- **Done:** finished Day 1: HF account + write token, Vercel account, GitHub repo + push, Gemini key works (`gemini-3.5-flash-lite`). Checked: no key in git history, 3/3 tests pass, front end builds.
- **Left over:** all of Day 2 (Colab notebook → model files, `database.npz`, photo check, thresholds, fold-0 checks, `MODEL_CARD.md`). Also from Day 1: checklist, tell teammate.
- **Blockers:** none — the day went to accounts and setup.

### Day 2 (finished) — Thu 19 Nov
- **Done:** Colab export notebook (laptop smoke test, then a real T4 run, 18 min); app model + database + thumbnails + photo check + cut-offs; fold-0 checks; files on HF + Drive + `backend/models/` (all load, checksums OK); `MODEL_CARD.md`; versions pinned; pushed.
- **Left over:** none from Day 2. Day 3 not started (plan still 1 day behind). From Day 1: checklist, tell teammate.
- **Blockers:** none. Finding to handle on Day 3: healthy / look-alike pictures cost 6/48 L3 images on fold 0 (p = 0.031).

### Day 3 — Sat 21 Nov (plan shifted by 2 days today)
- **Done:** option C decided and tested (sick L3 called healthy 6/48 → 0/48; healthy still recognised 96% → 56%); packages installed + pinned; model loads once (laptop = Colab, cosine 1.000000); photo check, vote, decisions, neighbours; `POST /api/check` with clear errors; 79 tests; time per check 0.82 s (on battery); Nabil checked everything in `/docs`.
- **Left over:** none from Day 3. Plugged-in timing skipped (battery number kept, labelled). From Day 1: checklist, tell teammate.
- **Blockers:** none.

### Week 10 update — Sun 22 Nov
- **Done:** slides presented (work up to Day 3). Day 1 leftovers (checklist, tell teammate) also done (ticked 23 Nov).

### Day 4 — Mon 23 Nov
- **Done:** `diseases.json` (8 + healthy + unknown, sources, no doses, helpline 16123; Nabil checked all); `advice.py` (Gemini + fallback + safety check + cache); `/api/advice`, `/api/diseases`, `/api/diseases/{id}`; SQLite log; 140 tests; real Gemini median 2.2 s; Nabil checked everything in `/docs`.
- **Left over:** none. Plan on schedule (Day 5 tomorrow, Tue 24 Nov).
- **Blockers:** none. Open points: no BRRI / BJRI / BARI / DAE web pages found as sources; jute dieback's cause not confirmed.

<!-- one entry per day: done / left over / blockers -->

## Numbers for slides

| What | Value | Date measured |
| --- | --- | --- |
| Time per check, laptop CPU (i5-13420H, 12 threads, **on battery**) | median **0.82 s** (48 checks; typical 0.80–0.84 s, one outlier 5.4 s that did not repeat); split: CLIP 0.71 s, photo check 0.05–0.11 s, read 3 ms, search 1 ms | 21 Nov 2026 |
| Laptop start-up until `model_loaded: true` | 11.2 s (7.6 s importing PyTorch etc. + 3.5 s loading the model and warm-up) | 21 Nov 2026 |
| PyTorch threads, laptop (median per check) | 12 threads 0.77 s vs 8 threads 0.94 s → keep 12 (all CPU threads) | 21 Nov 2026 |
| Time per check, Hugging Face Space | | |
| Space start-up time after sleeping | | |
| Fold 0, E4 L3 with vs without healthy / look-alike pictures | 85.4% (41/48) with vs 97.9% (47/48) without; McNemar 0 vs 6, p = 0.031 (all 6 → healthy / not in list) | 19 Nov 2026 |
| Fold 0, compressed L3 with vs without resample | 8/9 vs 8/9 (tie → resample kept) | 19 Nov 2026 |
| Fold 0, app database, answers by decision | sure 99.4% right (161/162), likely 85.7% (18/21), not sure 44.4% (4/9) | 19 Nov 2026 |
| Cut-offs (recipe-B out-of-fold E4 answers) | sure ≥ 0.902 (right 98.8%), not sure < 0.601 (right 41.0%) | 19 Nov 2026 |
| "Not a leaf" cut-off (fold 0) | 0.760: 192/192 held-out leaves kept, 44/44 non-leaf pictures rejected | 19 Nov 2026 |
| Photo check, fair test on 960 images | problem 98.0%, level 93.2% (within one level 99.7%) | 19 Nov 2026 |
| Option C: sick L3 photos called healthy / not in list (fold 0) | 6/48 before → **0/48** (all 6 had vote 0.40–0.80, below the 0.902 "sure" cut) | 21 Nov 2026 |
| Option C: healthy photos still called healthy (app model, own photo hidden, 1,440 images) | 96.0% → 56.0% (L0 100 → 96.7, L1 99.8 → 90.2, L2 97.3 → 69.8, L3 90.0 → 0%) | 21 Nov 2026 |
| Option C: look-alike photos still "not in our list" (1,920 images) | 93.1% → 39.2% | 21 Nov 2026 |
| Laptop vs Colab (torch 2.14.1 CPU) | embeddings cosine 1.000000 (8 clean photos); vote sanity 0.9917 = Colab's | 21 Nov 2026 |
| CLIP embedding only, laptop CPU (not a full check) | 0.83 s per photo | 19 Nov 2026 |
| Colab export run (T4): training / whole notebook | 176 s / 18 min | 19 Nov 2026 |
| Real photos: right / wrong / not sure (of N) | | |
| Gemini advice time, laptop (`scripts/try_advice.py`, 4 sample photos, with photo) | 2.0–4.3 s per answer (English 2.0, 2.3, 4.2 s; Bangla 4.3 s); fallback 0 s | 23 Nov 2026 |
| Gemini advice time through the real server (`/api/advice` over HTTP, photo sent, 4 sample photos) | 2.1–3.2 s (median 2.2 s); agrees yes on both L0 photos, unsure on both L3 photos; fallback without key 0 s | 23 Nov 2026 |
| Gemini agrees with CLIP (% of checks) | | |
| Fallback advice used (count) | | |
| Test plan passed (of 20) | | |
| Back-end automatic tests passing | 140 / 140 (110 s, includes loading the model once; Gemini faked, no quota) | 23 Nov 2026 |

## Bugs and ideas for later

- Vercel (Day 8): add a rewrite so deep links like `/history` don't give 404 (we use BrowserRouter).
- ~~Gemini model ID `gemini-3.5-flash-lite` is a guess~~ — confirmed working 18 Nov (no `GEMINI_MODEL` needed in `.env`).
- ~~Day 2: pin scikit-learn~~ — done 19 Nov (scikit-learn 1.6.1, numpy 2.4.6, joblib 1.6.0, opencv-python-headless
  4.14.0.*). Installed in `backend/.venv` on 21 Nov, with torch 2.14.1 (CPU), transformers 5.22.1 and Pillow 11.3.0
  also pinned to the Colab versions.
- ~~Day 3 (`predict.py`): apply the "not sure" cut-off to healthy / not-in-list answers too~~ — done 21 Nov as
  **option C** (stricter: healthy / not in list only with vote ≥ 0.902 and a photo that is not L3). Rules in
  `docs/MODEL_CARD.md` and the ROUTINE decision table.
- ~~Day 3 (`model.py`): hide transformers' "LOAD REPORT"~~ — done 21 Nov (also loads CLIP from the local cache first,
  so start-up needs no internet).
- ~~Day 3: copy `backend/models/photo_check.py` into `backend/app/photo_check.py`~~ — done 21 Nov (identical copy).
- ~~Day 4 (advice): how Gemini sees the photo~~ — done 23 Nov (option a): `/api/advice` is a form with `check_id`, `lang`
  and an optional `image`. **Day 5:** the Result page sends the same photo file again with the advice call (FormData);
  the server uses it once and keeps nothing. Advice for a check is only available while the server remembers the check
  (newest 1,000, lost on restart) → on 404 show "check the photo again".
- Day 5 (Result page), option C answers (`reason: healthy_or_other_unclear`): `disease_id` is the closest of our 8
  diseases (its vote share can be 0) and `runner_up` is the healthy / look-alike label that won the vote. Word it like
  "Not sure: this could be a healthy leaf, or Potato late blight. Retake a clearer photo."
- On Windows the photo-check measurements differ very slightly from Colab/Linux for 6/840 images (same answers);
  the HF Space runs Linux like Colab.
- `dist/safecrop_app_inputs.zip` (88.5 MB, git-ignored) is only needed to rerun the Colab notebook; can be deleted.
- "Not a leaf" gap is narrow at L3 (worst held-out leaf 0.790 vs most leaf-like non-leaf photo 0.730; cut 0.760):
  watch it on real photos (Day 6) but don't change the cut-off after seeing them.
- **24 Nov: plan shortened — everything finished by Thu 26 Nov.** Tue 24 = Day 5 + Day 6 Block B (disease pages) +
  Day 7 (must-haves). Wed 25 = Day 8 (Space + Vercel + `vercel.json` rewrite + phone test), then Day 6 Block A: the
  real-photo test **on the online app** (label the photos before running them). Thu 26 = Day 9, Day 10 (must-have
  polish, safety, docs only), Day 11 (freeze, v1.0, demo video, backups). Week 11 update stays Mon 30 Nov. **All
  nice-to-haves dropped** (feedback button, Bangla switch, home-screen icon, webcam, stats page); no must-have dropped.
  Cut-offs stay fixed after the real-photo results. The older shift notes below are kept for the record.
- Plan shifted by 2 days on 21 Nov, then 1 more day from Day 4 (also 21 Nov): Day 3 = Sat 21, Day 4 = Mon 23, …
  Day 11 = Mon 30. The Week 10 update stays on Sun 22 (own section, no build work) and shows work up to Day 3 only, before the real-photo
  test (Day 6, Wed 25) — show the Day 2 tables + the laptop time per check; real-photo results go into the Week 11
  update (Day 11, Mon 30). If still behind by Day 7, drop nice-to-haves first (feedback button, Bangla, home-screen icon, webcam, stats page) —
  never must-haves.
- `backend/data/diseases.json` (23 Nov): Nabil checked every entry, source and Bangla name on 23 Nov (`checked: true`).
  No BRRI / BJRI / BARI / DAE pages were found online for most diseases (we used
  university extension, PhilRice / IRRI, TNAU and BanglaJOL papers instead); add Bangladesh institute sources if you
  have them. Jute dieback's cause is not confirmed (written as "a later stage of fungus attacks on the stem; ask an
  expert"). Helpline 16123 (DAE Krishi Call Centre) confirmed active by a BSS report, July 2026.
- The Gemini check script is at `backend/scripts/check_gemini.py` (not `scripts/`).
- The laptop's default Python is 3.14 — always use `backend/.venv` (3.11).
- Git shows LF/CRLF warnings on Windows; harmless. Could add a `.gitattributes` later.
- Day 6 (before the real-photo test): delete `backend/safecrop.db` (8 test rows from 23 Nov on sample photos), so
  "Gemini agrees with CLIP" and "Fallback advice used" count only real photos.
- The fallback advice is English only (`diseases.json` has only Bangla names). If the Bangla nice-to-have is done,
  add Bangla text to `diseases.json`; Gemini already answers in Bangla (`lang=bn`).
- Free Gemini quota: when it runs out, `/api/advice` gives the fallback (`fallback_reason: quota`), so the demo still
  works. Watch it on demo day (Day 11).
- Testing the fallback on Windows: in PowerShell `$env:GEMINI_API_KEY = ""` deletes the variable (then `.env` is read
  again), so use `--no-key` in `scripts/try_advice.py` or a fake key (`fallback_reason: client_error`).
- Sources: add BRRI / BJRI / BARI / DAE pages or booklets to `diseases.json` if found; confirm jute dieback's cause.
