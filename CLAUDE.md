# SafeCrop web app

SafeCrop is our CSE299 Junior Design project (North South University, Fall 2026, Section 13, Group 7;
supervisor Md. Salman Shamil). It recognises crop diseases from **noisy phone photos** and gives the
farmer advice. This repo is the **web app**: a React front end and a FastAPI back end that serves our
fine-tuned CLIP model and asks Gemini for advice.

The full project story and every result we rely on: @docs/PROJECT_STORY.md
Where the build is right now (what's done, what's next): @docs/PROGRESS.md
The day-by-day plan (17–26 Nov 2026) is in `docs/ROUTINE.md`. Before working on any app task,
read that day's section (`## Day N — …`). Day 1 = Tue 17 Nov, Day 2 = Wed 18–Thu 19, Day 3 = Sat 21 Nov,
Day 4 = Mon 23 Nov. **Plan shortened on 24 Nov:** Tue 24 = Day 5 + Day 6 Block B (disease pages) + Day 7;
Thu 26 = Day 6 Block A (real-photo test on the laptop app), then Days 9, 10, 11. **Day 8 (hosting) removed on 26 Nov:**
no Hugging Face Space, no Vercel, no phone test — the app runs and is demonstrated on the laptop. Week 10 update = Sun 22
Nov (work up to Day 3); Week 11 update = Mon 30 Nov. All nice-to-haves dropped; never drop a must-have.

## How to work with me (Nabil)

- Explain things in **plain, simple words**. Short sentences, no jargon without a one-line meaning.
- Before a change, say in one or two sentences what you will do. After it, tell me how to check it myself.
- Work in small steps: change → run the check or test → commit. Don't do several big changes at once.
- Ask before installing large packages, changing files outside this repo, or deleting anything.
- When a task needs something only I can do (make an account, run Colab on a GPU, take phone photos,
  paste a key), prepare everything and give me a short numbered list of what to click or run.
- After finishing a routine task, tick its box in `docs/ROUTINE.md` (`- [ ]` → `- [x]`).
- My supervisor wants **numbers and tables**, not descriptions. Write any measured number
  (time per check, real-photo results, test counts) into the "Numbers for slides" part of `docs/PROGRESS.md`.

## Hard rules

- **No card anywhere.** Only free services that don't ask for a credit or debit card (no Google Cloud
  trial). **No hosting** (26 Nov: HF Docker Spaces need PRO): the app runs on the laptop. Gemini = free AI Studio key.
- **Never put a key in code, git, logs or screenshots.** `GEMINI_API_KEY` and `HF_TOKEN` live only in
  `backend/.env` (git-ignored). Check `git status` before every commit.
- **Models:** only CLIP ViT-L/14 (our fine-tuned E4 version) and **Gemini 3.5 Flash-Lite**. No Gemma, no other models.
- **CLIP answers first; Gemini can replace the answer only when it says "no"** (decided by Nabil, 26 Nov 2026;
  replaces "Gemini does not change it"). Gemini sees the photo, CLIP's answer and the checked facts in
  `backend/data/diseases.json`, and returns `gemini_label` / `gemini_name` / `gemini_sure` + `agrees`.
  yes / unsure → CLIP's answer stays. no + sure high/medium → Gemini's answer (one of our 8 → that disease, advice
  from its facts; else "not in our list" with Gemini's words). no but can't name it → "not sure", `other_unknown`.
  Rules: `final_answer` in `backend/app/advice.py`, `docs/MODEL_CARD.md` ("Second check"). E5 (Gemini as the
  classifier) is still not measured: report CLIP, Gemini and final answers separately on real photos.
- **Learning from Gemini's "no"** only with `LEARN_FROM_GEMINI=true` (false during the real-photo test): the
  fingerprint + 15 noisy copies go to `backend/models/database_added.npz` (git-ignored). **`database.npz` (v1) is
  never changed.** Undo with `backend/scripts/undo_added.py`.
- **No chemical names with doses** in advice. Say "ask your local agriculture officer which product and dose to use".
- **Don't store farmers' photos** on the server. The SQLite log keeps only numbers and labels; `database_added.npz`
  keeps only 768-number fingerprints (the Check page says so).
- **Accuracy claims come from the 5-fold results** in the `NabilRafi/SafeCrop` repo, never from testing the
  app model on the 840 test images (it was trained on them). Real phone photos are the only fair new test.
- Never change the decision thresholds after looking at the real-photo test results.

## Tech stack

| Part | Tools |
| --- | --- |
| Front end | React 19 + Vite 6, `react-router-dom`, plain CSS (`frontend/src/styles.css`), Inter font |
| Back end | Python 3.11, FastAPI, Uvicorn, python-multipart, Pillow + pillow-heif |
| Model | PyTorch (CPU), transformers, `openai/clip-vit-large-patch14` + our fine-tuned last 4 blocks + projection (`clip_ft_delta.safetensors`) |
| Search | numpy cosine similarity over `database.npz` (clean + noisy copies + healthy / look-alike pictures) + `database_added.npz` (Gemini-labelled, since 26 Nov), k = 5 weighted vote |
| Photo check | 16 quality measurements + random forests (scikit-learn, joblib) — pin the Colab scikit-learn version |
| Advice | `google-genai`, Gemini 3.5 Flash-Lite, JSON output, 20 s timeout, fallback from `diseases.json` |
| History | browser localStorage (History page); SQLite log on the server for our own numbers |
| Hosting | None — runs on the laptop (decided 26 Nov); model files backed up in a private HF model repo + Drive |

## Folder layout

```
frontend/            React app (was safecrop-web)
  src/api.js         every call to the back end (reads VITE_API_URL)
  src/pages/         Home, Check, Result, Diseases, DiseaseDetail, History, Profile, NotFound
  src/components/    Sidebar, BottomNav, ScanCard, Leaf, Icons, ResultCard, AdviceBox ...
  src/lib/history.js save / read / delete checks in the browser (max 50, small thumbnails)
backend/
  app/main.py        FastAPI app, CORS, routes, load models once at start-up (lifespan)
  app/model.py       CLIP + fine-tuned weights → 768 numbers
  app/photo_check.py problem + level, resample fix
  app/predict.py     database search, vote, decision
  app/advice.py      Gemini prompt + its own answer + the final-answer rule + fallback
  app/learn.py       save Gemini-labelled fingerprints to database_added.npz (LEARN_FROM_GEMINI)
  app/noise.py       the Day 2 noise recipe (15 noisy copies), copied from the research repo
  app/db.py          SQLite log
  scripts/undo_added.py  remove added fingerprints (--list, --all, --date, --check-id)
  data/diseases.json checked facts (8 diseases + healthy + unknown) with sources
  models/            model files — NOT in git (download from the HF model repo)
  tests/             pytest + sample images
notebooks/           SafeCrop_app_model_export.ipynb (Colab, Day 2)
docs/                PROJECT_STORY, ROUTINE, PROGRESS, MODEL_CARD, DATA_CARD, API, TEST_RESULTS
```

## API

- `GET /api/health` → `{status, model_loaded, version, added_rows, learn_from_gemini}`
- `POST /api/check` (form field `image`, header `X-Device-Id`) → `check_id`, `photo_check`
  {problem, problem_words, level, sure, level_sure, signs, message, fix_applied}, `result` {decision, reason,
  disease_id, disease_name, crop, vote_share, confidence_words, runner_up, tip, best_similarity},
  `neighbours` [5 × {disease_id, disease_name, thumb_url (null for an added fingerprint), added, similarity}],
  `timing_ms` {read, photo_check, embed, search, total}. Errors: 400 empty, 413 too big, 415 not a photo, 503 still
  starting. Shapes: `app/schemas.py`.
- `POST /api/advice` (form fields `check_id`, `lang` = en|bn, optional `image` = the same photo again, used once and never stored) → `{source: gemini|fallback, agrees, gemini_label, gemini_name, gemini_sure, final {source: clip|gemini, decision (+ second_check), reason, disease_id, disease_name, crop, confidence_words}, learn: saved|off|duplicate|daily_limit|null, summary, steps[], see_expert_when, safety_note, lang, fallback_reason, cached, timing_ms}`. The front end shows `final` and saves it to History. 404 unknown `check_id`.
- `GET /api/diseases`, `GET /api/diseases/{id}`, static `/static/thumbs/…`
- Decisions: `sure`, `likely`, `not_sure`, `healthy`, `not_in_list`, `retake` (cut-offs in `backend/models/thresholds.json`).
  Option C (21 Nov): `healthy` / `not_in_list` only with vote ≥ the `sure` cut and a photo that is not L3; otherwise
  `not_sure` with the closest of our 8 diseases (rules: top of `backend/app/predict.py`, `docs/MODEL_CARD.md`).
- Uploads: JPEG, PNG, WebP, HEIC; max 10 MB; fix EXIF rotation. Show the **clean** thumbnail of each neighbour.

## Commands

```
# back end (in backend/)
python -m venv .venv  then  .venv\Scripts\activate   (Windows)  /  source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000        # test page: http://localhost:8000/docs
pytest -q

# front end (in frontend/)  —  frontend/.env.local: VITE_API_URL=http://localhost:8000
npm install
npm run dev            # http://localhost:5173
npm run build
```

## Related repo

The research code, data and all experiment results are in https://github.com/NabilRafi/SafeCrop
(fine-tuning kit, `finetune.py`, `noise.py`, results/). If it is cloned next to this repo, add it with
`/add-dir ../SafeCrop` when a task needs it (Day 2 notebook, photo-check feature code).
Detailed result tables: `docs/results/` (read only when needed).
