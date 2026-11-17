# SafeCrop web app — progress

Update this at the end of every day (the `/wrapup` command does it for you).

## Status by day

| Day | Date | Goal | Status |
| --- | --- | --- | --- |
| 1 | Tue 17 Nov | Set up the project, connect all pages | almost done (Gemini key check, checklist, tell teammate left) |
| 2 | Wed 18 Nov | Make the app's model files in Colab | not started |
| 3 | Thu 19 Nov | Back end: photo in, disease out | not started |
| 4 | Fri 20 Nov | Back end: Gemini advice + disease facts | not started |
| 5 | Sat 21 Nov | Front end: the full check flow | not started |
| 6 | Sun 22 Nov | Real photos + Week 10 update + disease pages | not started |
| 7 | Mon 23 Nov | History, Profile, Home with real data | not started |
| 8 | Tue 24 Nov | Put it online (Hugging Face + Vercel) | not started |
| 9 | Wed 25 Nov | Test everything, fix bugs | not started |
| 10 | Thu 26 Nov | Polish, safety, documents | not started |
| 11 | Fri 27 Nov | Freeze, demo video, backups | not started |

## Where things are now (17 Nov, end of Day 1)

- Front end: routing works — 7 pages + "page not found"; menus highlight the current page; home buttons
  open `/check`. Only the home page has real content (sample data); other pages are titles.
  `src/api.js` has `getHealth()`; the sidebar shows a server online / offline dot.
- Back end: FastAPI skeleton with `GET /api/health` and CORS; 3 pytest tests pass. Python 3.11 venv in
  `backend/.venv` with the small packages only (torch / transformers not installed yet).
- Git: on GitHub (`radipyasar/safecrop-app`), `main` pushed. History checked 18 Nov: no key in any commit.
- Models: E4 works in the research repo (5-fold); the app's model files (Day 2) are not built yet.
- Accounts: Hugging Face account + write token, Vercel account (Hobby) — done 18 Nov.
  `GEMINI_API_KEY`, `HF_TOKEN`, `ALLOWED_ORIGINS` are set in `backend/.env` (git-ignored).
  Gemini key not yet tested with `scripts/check_gemini.py`.

## Daily log

### Day 1 — Tue 17 Nov
- **Done:** router + 8 pages, NavLink menus, `api.js` + online dot, FastAPI `/api/health` + CORS, `requirements.txt`, `.env.example`, 3 tests, first commit.
- **Left over:** Gemini key check, checklist, tell teammate. (HF + Vercel accounts, HF token, GitHub repo + push: done 18 Nov.)
- **Blockers:** none (Python 3.11 installed today).

<!-- one entry per day: done / left over / blockers -->

## Numbers for slides

| What | Value | Date measured |
| --- | --- | --- |
| Time per check, laptop CPU | | |
| Time per check, Hugging Face Space | | |
| Space start-up time after sleeping | | |
| Fold 0, E4 L3 with vs without healthy / look-alike pictures | | |
| Fold 0, compressed L3 with vs without resample | | |
| Real photos: right / wrong / not sure (of N) | | |
| Gemini agrees with CLIP (% of checks) | | |
| Fallback advice used (count) | | |
| Test plan passed (of 20) | | |
| Back-end automatic tests passing | 3 / 3 | 17 Nov 2026 |

## Bugs and ideas for later

- Vercel (Day 8): add a rewrite so deep links like `/history` don't give 404 (we use BrowserRouter).
- Gemini model ID `gemini-3.5-flash-lite` is a guess in `scripts/check_gemini.py` — confirm in AI Studio, set `GEMINI_MODEL` in `.env` if different.
- Day 2: pin `scikit-learn==<Colab version>` in `requirements.txt`. Day 3: ask Nabil, then install torch + transformers (~1 GB).
- The laptop's default Python is 3.14 — always use `backend/.venv` (3.11).
- Git shows LF/CRLF warnings on Windows; harmless. Could add a `.gitattributes` later.
