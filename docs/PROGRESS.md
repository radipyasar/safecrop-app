# SafeCrop web app — progress

Update this at the end of every day (the `/wrapup` command does it for you).

## Status by day

| Day | Date | Goal | Status |
| --- | --- | --- | --- |
| 1 | Tue 17 Nov | Set up the project, connect all pages | done (2 small to-dos: checklist, tell teammate) |
| 2 | Wed 18 Nov | Make the app's model files in Colab | done 19 Nov (Colab run 18 min; files in `backend/models/`, HF, Drive) |
| 3 | Thu 19 Nov | Back end: photo in, disease out | not started |
| 4 | Fri 20 Nov | Back end: Gemini advice + disease facts | not started |
| 5 | Sat 21 Nov | Front end: the full check flow | not started |
| 6 | Sun 22 Nov | Real photos + Week 10 update + disease pages | not started |
| 7 | Mon 23 Nov | History, Profile, Home with real data | not started |
| 8 | Tue 24 Nov | Put it online (Hugging Face + Vercel) | not started |
| 9 | Wed 25 Nov | Test everything, fix bugs | not started |
| 10 | Thu 26 Nov | Polish, safety, documents | not started |
| 11 | Fri 27 Nov | Freeze, demo video, backups | not started |

## Where things are now (18 Nov, end of Day 2)

- Front end: routing works — 7 pages + "page not found"; menus highlight the current page; home buttons
  open `/check`. Only the home page has real content (sample data); other pages are titles.
  `src/api.js` has `getHealth()`; the sidebar shows a server online / offline dot.
- Back end: FastAPI skeleton with `GET /api/health` and CORS; 3 pytest tests pass. Python 3.11 venv in
  `backend/.venv` with the small packages only (torch / transformers not installed yet).
- Git: on GitHub (`radipyasar/safecrop-app`), `main` pushed. History checked 18 Nov: no key in any commit.
- Models: E4 works in the research repo (5-fold); the app's model files (Day 2) are not built yet —
  no `backend/models/`, no Colab notebook yet. This is the next job.
- Accounts: Hugging Face account + write token, Vercel account (Hobby) — done 18 Nov.
  `GEMINI_API_KEY`, `HF_TOKEN`, `ALLOWED_ORIGINS` are set in `backend/.env` (git-ignored).
  Gemini key works: `backend/scripts/check_gemini.py` got a reply from `gemini-3.5-flash-lite` (18 Nov).

## Daily log

### Day 1 — Tue 17 Nov
- **Done:** router + 8 pages, NavLink menus, `api.js` + online dot, FastAPI `/api/health` + CORS, `requirements.txt`, `.env.example`, 3 tests, first commit.
- **Left over:** checklist, tell teammate. (HF + Vercel accounts, HF token, GitHub repo + push, Gemini key check: done 18 Nov.)
- **Blockers:** none (Python 3.11 installed today).

### Day 2 — Wed 18 Nov
- **Done:** finished Day 1: HF account + write token, Vercel account, GitHub repo + push, Gemini key works (`gemini-3.5-flash-lite`). Checked: no key in git history, 3/3 tests pass, front end builds.
- **Left over:** all of Day 2 (Colab notebook → model files, `database.npz`, photo check, thresholds, fold-0 checks, `MODEL_CARD.md`). Also from Day 1: checklist, tell teammate.
- **Blockers:** none — the day went to accounts and setup.

<!-- one entry per day: done / left over / blockers -->

## Numbers for slides

| What | Value | Date measured |
| --- | --- | --- |
| Time per check, laptop CPU | | |
| Time per check, Hugging Face Space | | |
| Space start-up time after sleeping | | |
| Fold 0, E4 L3 with vs without healthy / look-alike pictures | 85.4% (41/48) with vs 97.9% (47/48) without; McNemar 0 vs 6, p = 0.031 (all 6 → healthy / not in list) | 19 Nov 2026 |
| Fold 0, compressed L3 with vs without resample | 8/9 vs 8/9 (tie → resample kept) | 19 Nov 2026 |
| Fold 0, app database, answers by decision | sure 99.4% right (161/162), likely 85.7% (18/21), not sure 44.4% (4/9) | 19 Nov 2026 |
| Cut-offs (recipe-B out-of-fold E4 answers) | sure ≥ 0.902 (right 98.8%), not sure < 0.601 (right 41.0%) | 19 Nov 2026 |
| "Not a leaf" cut-off (fold 0) | 0.760: 192/192 held-out leaves kept, 44/44 non-leaf pictures rejected | 19 Nov 2026 |
| Photo check, fair test on 960 images | problem 98.0%, level 93.2% (within one level 99.7%) | 19 Nov 2026 |
| CLIP embedding only, laptop CPU (not a full check) | 0.83 s per photo | 19 Nov 2026 |
| Colab export run (T4): training / whole notebook | 176 s / 18 min | 19 Nov 2026 |
| Real photos: right / wrong / not sure (of N) | | |
| Gemini agrees with CLIP (% of checks) | | |
| Fallback advice used (count) | | |
| Test plan passed (of 20) | | |
| Back-end automatic tests passing | 3 / 3 | 18 Nov 2026 |

## Bugs and ideas for later

- Vercel (Day 8): add a rewrite so deep links like `/history` don't give 404 (we use BrowserRouter).
- ~~Gemini model ID `gemini-3.5-flash-lite` is a guess~~ — confirmed working 18 Nov (no `GEMINI_MODEL` needed in `.env`).
- Day 2: pin `scikit-learn==<Colab version>` in `requirements.txt`. Day 3: ask Nabil, then install torch + transformers (~1 GB).
  The notebook prints the exact line to pin ("PIN THESE": scikit-learn, numpy, opencv-python-headless); the back end
  also needs `opencv-python-headless` for `photo_check.py` (not in `requirements.txt` yet).
- Day 2 notebook: `notebooks/SafeCrop_app_model_export.ipynb`; its one input zip is made by
  `python notebooks/make_colab_inputs.py` (→ `dist/safecrop_app_inputs.zip`, git-ignored). Smoke-tested on the laptop
  (tiny fake CLIP, all 16 steps pass). Cut-offs it will pick (from recipe-B out-of-fold E4 answers): sure ≥ 0.902,
  not sure < 0.601.
- Plan is 1 day behind (Day 2 moved to Thu 19 Nov). Catch-up idea: run Day 2 Block A+B in Colab first; while the
  fold-0 checks run, start the Day 3 back end. If still behind by Day 7, drop nice-to-haves first
  (feedback button, Bangla, home-screen icon, webcam, stats page) — never must-haves.
- The Gemini check script is at `backend/scripts/check_gemini.py` (not `scripts/`).
- The laptop's default Python is 3.14 — always use `backend/.venv` (3.11).
- Git shows LF/CRLF warnings on Windows; harmless. Could add a `.gitattributes` later.
