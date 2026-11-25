# SafeCrop web app — 11-day build routine (17–26 Nov 2026, Week 11 update 30 Nov)

> Markdown copy of `SafeCrop_webapp_routine_17-27Nov2026.pdf`. Tick a box by changing `- [ ]` to `- [x]`.
> **Dates shifted by 2 days on 21 Nov, then by 1 more day from Day 4** (Day 3 = Sat 21, Day 4 = Mon 23 … Day 11 = Mon 30).
> The Week 10 update stays on **Sun 22** (its own short section after Day 3; slides show work up to Day 3 only) and the
> Week 11 update is on Day 11 (Mon 30).
> **Plan shortened on 24 Nov: everything is finished by Thu 26 Nov.** Tue 24 = Day 5, Day 6 Block B (disease pages),
> Day 7 · ~~Wed 25 = Day 8 (online), then Day 6 Block A (real-photo test on the online app)~~ · Thu 26 = Days 9, 10, 11.
> All nice-to-haves are dropped; no must-have is dropped. The Week 11 update stays on **Mon 30 Nov** (own section after Day 11).
> **26 Nov: no hosting.** Hugging Face now needs a paid PRO plan for Docker Spaces on the free CPU (the Space was refused
> on 26 Nov), free hosts without a card give at most 512 MB (our model needs about 2 GB), and Nabil chose to demo on the
> laptop. So **Day 8 is removed**: no Hugging Face Space, no Vercel, no phone test. The app runs on the laptop (back end +
> front end); the Hugging Face model repo stays as the backup of the model files. Thu 26 = Day 6 Block A (real photos,
> uploaded on the laptop) → Day 9 → Day 10 → Day 11.
> The PDF still has the old dates.

Tuesday 17 November to Thursday 26 November 2026 (Week 11 update on Monday 30 November). Every task, in order, with a clear "done when" check for each day, so that by 26 November SafeCrop works end to end on the laptop.

**Where you are today (16 Nov) and where you will be on 26 Nov**

**Today:** the React home page runs on `localhost:5173` with sample data. The models work in Colab and in the `NabilRafi/SafeCrop` repo (E4, fine-tuned CLIP + noisy copies, is the most robust: 97.1% at L3 on the test images, 85.2% on recipe B). There is no back end yet.

**26 Nov:** on the laptop, a leaf photo (taken with a phone) is uploaded and the app gives: a photo-quality check, the disease from fine-tuned CLIP, the 5 most similar reference pictures, and advice written by Gemini from checked disease facts. Past checks are saved in History. A demo video is recorded (by 26 Nov) and shown at the Week 11 update (Mon 30 Nov).

### The 11 days at a glance

| Day | Date          | Main goal                                                  | Done when                                                        |
|-----|---------------|------------------------------------------------------------|------------------------------------------------------------------|
| 1   | Tue 17 Nov    | Set up the project, connect all pages                      | Every menu item opens a page; back end says “ok”                 |
| 2   | Wed 18–Thu 19 | Make the app's model files in Colab                        | Fine-tuned CLIP, database, photo check and thresholds saved      |
| 3   | Sat 21 Nov    | Back end: photo in, disease out                            | `/api/check` names the disease for 8 sample photos               |
| —   | Sun 22 Nov    | **Week 10 update** (shows work up to Day 3)                | Week 10 slides presented                                         |
| 4   | Mon 23 Nov    | Back end: Gemini advice + disease facts                    | `/api/advice` works, with a fallback                             |
| 5   | Tue 24 Nov    | Front end: the full check flow                             | Upload → result → advice works on the laptop                     |
| 6   | Tue 24 (B) + Thu 26 (A) | Disease pages (Tue) + real photos on the laptop app (Thu) | Disease pages filled; real-photo table done |
| 7   | Tue 24 Nov    | History, Profile, Home with real data                      | No sample data left anywhere                                     |
| 8   | —             | ~~Put it online~~ **removed 26 Nov** (laptop demo only)     | —                                                                |
| 9   | Thu 26 Nov    | Test everything, fix bugs                                  | All tests in the test plan pass                                  |
| 10  | Thu 26 Nov    | Must-have polish, safety, documents                        | A teammate can run it from the README                            |
| 11  | Thu 26 Nov    | Freeze, demo video, backups                                | v1.0 tagged, video recorded, link works                          |
| —   | Mon 30 Nov    | **Week 11 update**                                         | Week 11 update given                                             |

Order of work: **Tue 24** Day 5 → Day 6 Block B → Day 7 · **Thu 26** Day 6 Block A → Day 9 → Day 10 → Day 11 (Day 8 removed).

## Before you start

**How to use this routine**

- Each day has 3 blocks of about 1.5 to 2 hours (about 5–6 hours a day). Do the blocks in order; tick each box when it is done.
- Every task is small enough to give to Claude Code in VS Code as one request. Paste the task, then check the result yourself before ticking.
- Commit to GitHub at the end of every block (for example `git commit -m "Day 3: /api/check returns disease"`).
- Spend 10 minutes at the end of each day writing 3 lines: what got done, what is left, what is blocking you.
- If a day runs late, cut from the “nice to have” list, never from the must-haves.

**Three rules that keep the app honest**

- **CLIP (E4) names the disease; Gemini does not change it.** E4 is the method you tested (97.1% at L3, 85.2% on recipe B). Gemini + fine-tuned neighbours (E5) is not tested yet, so in the app Gemini only writes the advice and gives a second opinion. If it disagrees, the app says so and suggests a retake or an expert.
- **Advice comes from checked facts.** Gemini rewrites the facts in `diseases.json` in plain words; it does not invent treatments. The app never gives chemical doses; it tells the farmer to ask the local agriculture officer.
- **The app's own numbers are not accuracy results.** The app model is trained on all photos, so testing it on the 840 test images would be unfair. Accuracy for the report stays the 5-fold numbers from the repo. The only fair new test is real phone photos (Day 6).

## What “fully functional” means (the target)

These are the features SafeCrop must have by 26 November. Use this list as the finish line: the app is done when every must-have works on the laptop.

| \#  | Must-have feature                                                                                                                                       | Where it lives         |
|-----|---------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------|
| 1   | Upload a photo (file picker or drag-and-drop on the laptop)                                                                                             | Check page             |
| 2   | Photo check: names the problem (blur, grain, dark, blocky) and the level (L0–L3); warns when the photo is bad; asks for a retake when it is too unclear | Back end + Result page |
| 3   | Disease answer from fine-tuned CLIP (E4) with a confidence word (Very likely / Likely / Not sure) and the next best guess                               | Back end + Result page |
| 4   | Handles a healthy leaf, a disease not in our list, and a photo that is not a leaf                                                                       | Back end + Result page |
| 5   | Shows the 5 most similar reference pictures, so the farmer can compare by eye                                                                           | Result page            |
| 6   | Advice written by Gemini from checked disease facts, plus a fallback when Gemini is slow, out of quota or offline                                       | Back end + Result page |
| 7   | Disease list and a detail page for each of the 8 diseases (symptoms, what to do, prevention, sources)                                                   | Diseases pages         |
| 8   | History of past checks: open, delete one, clear all                                                                                                     | History page           |
| 9   | Profile: name, district, crops, language                                                                                                                | Profile page           |
| 10  | Runs on the laptop (back end + front end) for the demo; no API key in the code (no hosting, decided 26 Nov)                                             | Laptop                 |
| 11  | Clear messages for: no internet, server still starting, wrong file type, file too big, server error                                                     | Every page             |
| 12  | README, model card, data card and test results written                                                                                                  | `docs/` folder         |

| Nice to have — **all dropped on 24 Nov** (plan shortened to 26 Nov)       | Why it is optional                                          |
|--------------------------------------------------------------------------|-------------------------------------------------------------|
| “Was this right?” button that saves feedback                             | Useful data for the report, but the app works without it    |
| Bangla language switch (main screens + disease names + advice in Bangla) | Good for farmers; the English app is complete without it    |
| Add-to-home-screen icon (web app manifest)                               | Looks like a real app on the phone; not needed for the demo |
| Laptop webcam capture (not just file upload)                             | Phones already open the camera with the upload button       |
| A small stats page (checks per day, average time, Gemini agreement)      | Numbers for slides; can be read from the log instead        |

## How the finished app works

**Flow of one check:** photo (browser) → `POST /api/check` → photo check (problem + level) → resample if blocky (only if Day 2 says it helps) → fine-tuned CLIP (E4) → search the database (clean + noisy copies + healthy / look-alikes) → decision (sure / likely / not sure / healthy / not in list / retake) → result screen with 5 similar pictures → `POST /api/advice` → Gemini 3.5 Flash-Lite writes advice from `diseases.json` facts (fallback to `diseases.json` text if Gemini fails) → saved to History in the browser.

One check, start to finish. Steps 2–3 happen in one request (`/api/check`), so the disease shows quickly; the advice (step 5) is a second request, so a slow Gemini answer never blocks the result.

| Part            | Tools (all free, no card needed)                                                                     | Notes                                                                            |
|-----------------|------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| Front end       | React 19 + Vite 6 (your `safecrop-web`), `react-router-dom` for pages                                | Runs on the laptop (`npm run dev`); no hosting (26 Nov)                          |
| Back end        | Python 3.11, FastAPI, Uvicorn, python-multipart                                                      | Swagger test page at `/docs` for free                                            |
| Image reading   | Pillow + pillow-heif (iPhone HEIC photos), EXIF rotation fix                                         | Uploads up to 10 MB                                                              |
| Disease model   | PyTorch (CPU), transformers, CLIP ViT-L/14 with your fine-tuned last 4 blocks (E4)                   | Only the changed weights are saved (~100–200 MB)                                 |
| Database search | numpy: cosine similarity, 5 nearest pictures, weighted vote                                          | Clean + noisy copies + healthy / look-alike pictures                             |
| Photo check     | Your 16 measurements + random forests (scikit-learn, joblib)                                         | Pin the same scikit-learn version as in Colab                                    |
| Advice          | google-genai with Gemini 3.5 Flash-Lite (free AI Studio key)                                         | Key kept only in `backend/.env` (git-ignored)                                    |
| History         | Browser storage (localStorage) for the History page; SQLite log on the server for your own numbers   | History does not depend on the server                                            |
| Hosting         | **None (26 Nov):** back end and front end run on the laptop; model files backed up in a Hugging Face model repo + Drive | HF Docker Spaces need PRO; free no-card hosts give ≤ 512 MB          |

## The API (what the front end and back end say to each other)

| Call                     | Sends                                                | Gets back                                                                                                                                                                                                                                   |
|--------------------------|------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `GET /api/health`        | nothing                                              | `{status, model_loaded, version}`                                                                                                                                                                                                           |
| `POST /api/check`        | the photo (form field `image`); header `X-Device-Id` | `check_id`; `photo_check` {problem, level, sure, message, fix_applied}; `result` {decision, disease_id, disease_name, crop, vote_share, confidence_words, runner_up}; `neighbours` \[5 × {disease_id, thumb_url, similarity}\]; `timing_ms` |
| `POST /api/advice`       | form: `check_id`, `lang`, optional `image` (not stored)| `{source: gemini | fallback, agrees, summary, steps[], see_expert_when, safety_note}`                                                                                                                                                       |
| `GET /api/diseases`      | nothing                                              | list of the 8 diseases (id, crop, names, short description, thumbnail)                                                                                                                                                                      |
| `GET /api/diseases/{id}` | nothing                                              | full facts: symptoms, what to do now, prevention, when to call an expert, sources                                                                                                                                                           |
| `GET /static/thumbs/…`   | nothing                                              | small reference pictures shown on the Result and Disease pages                                                                                                                                                                              |

| Decision        | When (thresholds chosen on Day 2)                                                                           | What the farmer sees                                                                     |
|-----------------|-------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| **sure**        | one of our 8 diseases with vote share at or above the “sure” cut (also at L3: fold 0 L3 sure 31/31 right; the photo warning still shows) | “Very likely: Potato late blight” + similar pictures + advice                            |
| **likely**      | vote share between the two cuts                                                                             | “Likely: X. Could also be Y.” + a tip to retake a clearer photo                          |
| **not sure**    | vote share below the lower cut; **or (option C)** a healthy / look-alike winner whose vote is below the “sure” cut or whose photo is L3 | “SafeCrop is not sure.” Top 2 guesses (option C: the closest of our 8 diseases + the healthy / look-alike label), a retake tip, and a nudge to ask an expert |
| **healthy**     | the winning label is a healthy leaf, vote share at or above the “sure” cut, and the photo check does not say L3 (option C, chosen 21 Nov) | “This leaf looks healthy.” + what to watch for                                           |
| **not in list** | the winning label is a look-alike disease SafeCrop does not cover, with the same option C conditions as “healthy” | “This may be a disease SafeCrop doesn't know yet.” + ask an expert                       |
| **retake**      | best similarity below the “not a leaf” cut, or the photo check is sure (≥ 60%) the photo is L3 and the vote share is below the lower cut | “We can't read this photo.” + exactly what to fix (hold steady, more light, move closer) |

### Folder layout (one GitHub repo: `safecrop-app`)

    safecrop-app/
      frontend/                 (your current safecrop-web, moved here)
        src/api.js              all calls to the back end in one place
        src/pages/              one file per page (Home, Check, Result, Diseases, History ...)
        src/components/         Sidebar, BottomNav, ScanCard, ResultCard, AdviceBox ...
        src/lib/history.js      save / read / delete checks in the browser
      backend/
        app/main.py             FastAPI app, CORS, routes, start-up loading
        app/model.py            load CLIP + fine-tuned weights; photo to 768 numbers
        app/photo_check.py      16 measurements + random forests, resample fix
        app/predict.py          database search, vote, decision (sure, healthy, retake ...)
        app/advice.py           Gemini prompt, timeout, fallback
        app/db.py               SQLite log
        app/schemas.py          the JSON shapes (pydantic)
        data/diseases.json      checked facts: 8 diseases + healthy + unknown
        models/                 model files (NOT in git; from Hugging Face)
        tests/                  pytest tests + sample images
        requirements.txt, .env.example
      notebooks/SafeCrop_app_model_export.ipynb
      docs/MODEL_CARD.md, DATA_CARD.md, API.md, TEST_RESULTS.md

## Day 1 — Tuesday 17 November: Set up the project and connect every page

**Goal:** one repo with the front end and an empty back end, both running, and every menu item opening its own page.

#### Block A · Plan and accounts (≈ 1.5 h)

- [x] Read this routine once from start to finish. Copy the must-have list into a checklist you will tick (GitHub Issues, a GitHub Project board, or Notion).
- [x] Make a **Hugging Face** account (free, no card). Create an access token with *write* rights (Settings → Access Tokens). Save it in a password manager, not in a file.
- [x] Make a **Vercel** account by signing in with GitHub (Hobby plan, no card).
- [x] Check the Gemini key still works: a 5-line Python script that asks Gemini 3.5 Flash-Lite “say hi”. Keep the key in an environment variable only.
- [x] Tell your teammate the plan and split work if possible (for example: teammate writes `diseases.json` on Day 4 and collects real photos for Day 6).

#### Block B · Repo and back-end skeleton (≈ 2 h)

- [x] Create a new GitHub repo `safecrop-app`. Move `safecrop-web` into `frontend/`.
- [x] Create `backend/` with a Python 3.11 virtual environment and `requirements.txt` (fastapi, uvicorn\[standard\], python-multipart, pillow, pillow-heif, numpy, scikit-learn, joblib, torch (CPU), transformers, safetensors, huggingface_hub, google-genai, python-dotenv, pytest, httpx).
- [x] Write `app/main.py` with `GET /api/health` returning `{"status": "ok"}` and CORS allowing `http://localhost:5173`.
- [x] Add `.gitignore` (`.env`, `.venv/`, `node_modules/`, `backend/models/`, `*.db`) and `.env.example` (`GEMINI_API_KEY=`, `HF_TOKEN=`, `ALLOWED_ORIGINS=`).
- [x] Run `uvicorn app.main:app --reload`, open `http://localhost:8000/docs`, try the health call. First commit and push.

#### Block C · Front-end pages and links (≈ 2 h)

- [x] Install `react-router-dom`. Add routes: `/`, `/check`, `/result/:id`, `/diseases`, `/diseases/:id`, `/history`, `/profile`, and a “page not found” route.
- [x] Create one simple page file per route (a title is enough for now). Make the sidebar and bottom bar use `NavLink` so the current page is highlighted.
- [x] Make “Upload a photo” and “Use camera” on the home page go to `/check`.
- [x] Create `src/api.js`: reads `VITE_API_URL` (from `frontend/.env.local`), has a `getHealth()` function with a 10-second timeout and clear error messages.
- [x] Show a small “server online / offline” dot in the sidebar footer using `getHealth()` (helps you all week).

**Done when**

- [x] Both servers start with one command each (`npm run dev`, `uvicorn …`).
- [x] Clicking every menu item opens the right page; a wrong address shows “page not found”.
- [x] The front end shows “server online” when the back end runs and “offline” when it doesn't.
- [x] Code is on GitHub; `.env` is not.

**If you get stuck**

If CORS blocks the call (red error in the browser console), check that the back end's allowed origin is exactly `http://localhost:5173` with no slash at the end.

## Day 2 — Wednesday 18 November: Make the app's model files in Colab

**Goal:** every file the back end needs to make a prediction, built once in Colab and saved: the fine-tuned CLIP weights, the picture database, the photo check, and the decision thresholds.

#### Block A · Train the app model (E4 settings, all photos) (≈ 2 h)

- [x] Make `SafeCrop_app_model_export.ipynb` from the repo's `finetune.py` (ask Claude Code to write it). Use the same default settings as E3/E4: last 4 blocks + projection, 15 epochs, lr 1e-5 (head 1e-3), consistency weight 1.0, fixed seed.
- [x] Train on **all 240 photos** of the 8 diseases (no folds this time, because the app should learn from everything). On a T4 this takes about 3–5 minutes.
- [x] Save **only the changed weights** (last 4 blocks, final norm, visual projection) as `clip_ft_delta.safetensors`. The app loads the normal CLIP ViT-L/14 from Hugging Face and puts these on top. Check that loading them back gives the same embedding for one photo, and note the seed and library versions.

#### Block B · Build the picture database (≈ 1.5 h)

- [x] For every one of the 240 photos: the clean photo + 15 noisy copies (5 noise types × L1–L3, seed family 2026, not 299). Embed all with the fine-tuned model.
- [x] Add the 240 PlantVillage extras (4 look-alike diseases + 3 healthy leaves) and their noisy copies, labelled `healthy_…` or `other_…`, so the app can say “healthy” or “not in our list”.
- [x] Save `database.npz`: embeddings (normalised), label, photo_id, is_copy, noise type, level. About 7,700 × 768 numbers, roughly 25 MB.
- [x] Save a 200-pixel JPEG thumbnail of every **clean** photo in `thumbs/`. The app always shows the clean picture, even when a noisy copy was the match.

#### Block C · Photo check, thresholds and checks (≈ 2 h)

- [x] Retrain the photo-check forests on all 960 noisy test images; save `photo_check.joblib` + the feature code as `photo_check.py`; note the scikit-learn version.
- [x] **Pick the “sure” and “not sure” cuts** from the repo's out-of-fold E4 predictions (not the new model): the vote share at which answers are right at least 95% of the time (“sure”), and the one below which they are right less than 70% (“not sure”). Save them in `thresholds.json`.
- [x] **Pick the “not a leaf” cut:** embed 30 non-leaf photos (desk, hand, sky, food); choose the best-similarity value that separates them from leaves.
- [x] **Check the healthy pictures don't hurt too much:** on fold 0 (out-of-fold), compare E4 at L3 with and without the healthy / look-alike pictures in the database. Write both numbers down for your slides (in the frozen noisy album it was 95.2% vs 88.1%).
- [x] **Check the resample fix on E4:** compressed L3 photos with and without resample (fold 0). Keep the fix in the app only if it helps or ties.
- [x] Upload all files to a **private Hugging Face model repo** (e.g. `NabilRafi/safecrop-models`) and to Drive; download them into `backend/models/`.

**Done when**

- [x] `backend/models/` has `clip_ft_delta.safetensors`, `database.npz`, `thumbs/`, `photo_check.joblib`, `thresholds.json`.
- [x] A short `docs/MODEL_CARD.md` lists: training data, settings, seed, versions, thresholds, and the two fold-0 checks.
- [x] The same files are safe in the Hugging Face model repo and on Drive.

## Day 3 — Saturday 21 November: Back end: photo in, disease out

**Goal:** `POST /api/check` takes a photo and returns the photo-check result, the disease, the confidence and the 5 similar pictures.

#### Block A · Load the model once at start-up (≈ 2 h)

- [x] `app/model.py`: load `openai/clip-vit-large-patch14` (vision part + processor), put the fine-tuned weights on top, switch to eval mode, use `torch.inference_mode()`, set `torch.set_num_threads` to the CPU count.
- [x] Load `database.npz` and `thresholds.json` into memory once.
- [x] Use FastAPI's start-up (lifespan) to load everything and run one warm-up photo, so the first real check is not slow.
- [x] Make `/api/health` report `model_loaded: true` only after loading has finished.

#### Block B · Photo check and prediction (≈ 2 h)

- [x] `app/photo_check.py`: same 16 measurements as in Colab, then the two forests → problem, level, how sure. Apply resample to blocky photos only if Day 2 said it helps.
- [x] `app/predict.py`: embed → cosine similarity with every database picture → top 5 → weighted vote → winning label, vote share, runner-up.
- [x] Turn the numbers into one **decision** (sure / likely / not sure / healthy / not in list / retake) using `thresholds.json` and the decision table (after the API table).
- [x] For the 5 neighbours, return the **clean** photo's thumbnail URL (`/static/thumbs/…`) and remove duplicates (two copies of the same photo count once).

#### Block C · The endpoint and its tests (≈ 1.5 h)

- [x] `POST /api/check`: accept JPEG, PNG, WebP and HEIC up to 10 MB; reject other files with a clear message (HTTP 415 / 413). Fix EXIF rotation, convert to RGB.
- [x] Give every check a `check_id` and remember the result in memory for the advice call (and later in the SQLite log).
- [x] Add `timing_ms` (photo check, embedding, search) to every answer.
- [x] Write pytest tests: 8 sample photos (one per disease, clean and L3) give the right disease; a text file is rejected; an empty file is rejected; a 15 MB file is rejected.
- [x] Measure the time per check on your laptop CPU (write it down for the slides).

**Done when**

- [x] In `/docs`, uploading each of the 8 clean sample photos returns the right disease.
- [x] Bad files get a clear error, never a crash. All pytest tests pass.
- [x] You know the time per check on your laptop (target: under 5 seconds).

**If you get stuck**

If a check takes much longer than 5 seconds on the laptop, check that the model loads only once (not per request) and that gradients are off. If memory is short, load the model in half precision only for the database step, not for live checks.

## Week 10 update — Sunday 22 November (after Day 3, before Day 4)

**Goal:** Week 10 slides ready and presented. No build work today.

The supervisor wants tables and numbers. The slides show the work **up to Day 3** only (advice, front end and real photos come later). Lead with the Day 2 tables and the time per check (Day 3), not with descriptions. Real photos are tested on Day 6 (Wed 25 Nov), so say their results come in the Week 11 update.

#### Week 10 slides (supervisor update today — do this before the meeting) (≈ 1.5 h)

- [x] Slide: how the app works (the “How the finished app works” diagram) and the tech stack table.
- [x] Slide: the API table and the decision table.
- [x] Slide: numbers — time per check on the laptop, the two Day 2 fold-0 checks (with / without healthy pictures, resample), answers by decision, the cut-offs, photo check on 960 images (all in “Numbers for slides” in `docs/PROGRESS.md`).
- [x] Slide: screenshots of `/api/check` working in `/docs` (the front-end screens come on Day 5).
- [x] Slide: plan for 23–30 Nov (Days 4–11 of this routine), with the real-photo test on Wed 25 Nov.

**Done when**

- [x] Week 10 slides are in the deck and presented.

## Day 4 — Monday 23 November: Back end: Gemini advice and disease facts

**Goal:** the back end can explain each result in plain words, using facts you checked, and still answers when Gemini fails.

#### Block A · Write the disease facts (≈ 2 h)

- [x] Create `data/diseases.json` with one entry for each of the 8 diseases, plus `healthy` and `unknown`.
- [x] For each disease: id, crop, English name, Bangla name, what causes it (fungus, virus, insect…), 3–5 signs to look for, what to do now, how to prevent it, when to call an expert, and 1–3 source links.
- [x] Use trusted sources: Bangladesh research institutes and extension services (for example BRRI for rice, BJRI for jute, BARI for potato and black gram, DAE), and university extension pages for apple, pear and grape. Write down every source you used.
- [x] Do **not** write chemical names with doses. Write “ask your local agriculture officer which product and dose to use”. Add the local agriculture helpline number after checking it is current.
- [x] Note: rice stem borer is an insect pest, not a disease. Say so on its page.

#### Block B · The advice service (≈ 2 h)

- [x] `app/advice.py`: use `google-genai` with Gemini 3.5 Flash-Lite. Send: the farmer's photo, the predicted disease, its facts from `diseases.json`, and the photo-check result.
- [x] Ask for a JSON answer with a fixed shape: `agrees` (yes / no / unsure), `summary` (2 sentences), `steps` (3–5 short steps), `see_expert_when`, `safety_note`. Tell Gemini to use only the given facts and simple words, and to answer in the requested language (English or Bangla).
- [x] Timeout of 20 seconds and one retry. Cache the answer by `check_id` so a page refresh doesn't spend quota.
- [x] **Fallback:** if Gemini fails, times out or the daily quota is used up, build the same JSON from `diseases.json` with `source: "fallback"`.

#### Block C · Endpoints, log and tests (≈ 1.5 h)

- [x] `POST /api/advice`, `GET /api/diseases`, `GET /api/diseases/{id}`.
- [x] `app/db.py`: SQLite table `checks` (id, time, device_id, problem, level, label, vote_share, decision, gemini_agrees, advice_source, timing). Do **not** store photos (privacy).
- [x] Tests: advice returns valid JSON; with the key removed it returns the fallback; an unknown `check_id` gives a clear 404.
- [x] Put the key only in `backend/.env`. Run `git status` and make sure `.env` is not listed.

**Done when**

- [x] `/api/advice` returns Gemini's advice in about 10 seconds or less, and fallback advice when the key is removed.
- [x] `/api/diseases` returns all 8 diseases with checked facts and sources.
- [x] Every check is written to the SQLite log; no photos are stored.

**If you get stuck**

If Gemini returns text that is not valid JSON, use the SDK's structured-output option (a response schema) instead of asking for JSON in words, and still wrap the parse in a try/except that falls back.

## Day 5 — Tuesday 24 November: Front end: the full check flow

**Goal:** on the laptop, a user can upload a photo, watch the steps, see the result with similar pictures, and read the advice.

#### Block A · The Check page (≈ 2 h)

- [x] Upload button (file picker), “Use camera” button (`<input type="file" accept="image/*" capture="environment">`, which opens the back camera on phones) and drag-and-drop on laptops.
- [x] Show a preview of the chosen photo with “Check this leaf” and “Choose another” buttons.
- [x] Only shrink the photo in the browser if it is larger than 2048 pixels or 5 MB (shrinking adds compression, which could change the photo check). Test that the photo check gives the same answer for 5 test images with and without this step.
- [x] Disable the button while a check runs so it can't be sent twice.

#### Block B · Progress and the Result page (≈ 2.5 h)

- [x] Progress steps tied to real calls: “Photo check” and “Compare” while `/api/check` runs, “Get advice” while `/api/advice` runs.
- [x] Result card: disease name and crop, the confidence word (Very likely / Likely / Not sure), and the runner-up when it is close.
- [x] Photo warning banner when the photo check finds a problem (for example “Your photo is blurry. Hold the phone steady and retake if you can.”). Use one simple “blurry” message for both blur types.
- [x] “Similar pictures from our library”: the 5 thumbnails with their disease names.
- [x] Advice box that fills in when `/api/advice` returns; if Gemini disagrees, show “Our second check is not sure about this answer. Retake the photo or ask an expert.”
- [x] Buttons: Retake, Learn about this disease, See history.

#### Block C · Special results and errors (≈ 1.5 h)

- [x] Screens for: healthy leaf, not in our list, retake needed, not sure. Each says what happened and what to do next.
- [x] Error messages: no internet, server waking up (“SafeCrop is starting, try again in a minute”), wrong file, file too big, server error.
- [x] Save every finished check to History in the browser (`src/lib/history.js`): id, date, small thumbnail, disease, confidence word, decision, advice. Keep at most 50 checks.

**Done when**

- [x] Upload → steps → result → advice works for 8 sample photos on the laptop.
- [x] You can trigger every special screen and every error message on purpose (for example stop the back end to see “offline”).
- [x] Each check appears in the browser's saved history.

**If you get stuck**

To trigger the special screens without hunting for photos, add a hidden test option in development only (for example `?force=healthy`) that the back end ignores in production.

## Day 6 — Tuesday 24 (Block B) and Thursday 26 November (Block A): Real photos and the disease pages

**Goal:** the first fair test of the app on real phone photos, and the Diseases pages filled with real facts. (The Week 10 update was on Sun 22.)

**Plan:** Block B (disease pages) was done on Tue 24 with the rest of the front end. Block A (real-photo test) is done
on **Thu 26 on the laptop app** (no hosting since 26 Nov): the photos are taken with a phone, copied to the laptop and
uploaded there.

#### Block A · Real-photo test (Thu 26, on the laptop) (≈ 2 h)

- [ ] Before the test, delete `backend/safecrop.db` (8 test rows from 23 Nov), so the log counts only real photos.
- [ ] Gather 20–30 real phone photos with a known disease (from the field trip or new ones), including a few healthy leaves and a few bad photos. Copy them to the laptop. Write the true label of each in a sheet **before** running them.
- [ ] Run each through the app on the laptop (upload on the Check page). Record: photo, true label, app answer, decision, photo-check problem and level, Gemini agrees?, time.
- [ ] Count: right / wrong / not sure, and how often the photo check warned. Do **not** change any threshold after seeing these results (that would make the test unfair); write ideas down for later.
- [ ] Save the table as `docs/TEST_RESULTS.md` (real-photo section).

#### Block B · Diseases pages (Tue 24) (≈ 1.5 h)

- [x] Diseases page: cards from `/api/diseases` (photo, crop, name), grouped by crop.
- [x] Detail page: signs to look for, what to do now, prevention, when to call an expert, sources (as links), and 4 example pictures from the database.
- [x] Link from the Result page (“Learn about this disease”) and from the home page cards.

**Done when**

- [ ] Real-photo results table written, with the true labels recorded before the test.
- [x] Diseases list and all 8 detail pages show real facts and sources.

**If you get stuck**

If you don't have labelled real photos yet, take 3–4 photos each of whatever leaves you can find (healthy leaves count) and ask your teammate for field-trip photos; even 15 photos give a useful first table.

## Day 7 — Tuesday 24 November: History, Profile and a home page with real data

**Goal:** every screen uses real data; the sample data file is deleted.

#### Block A · History page (≈ 2 h)

- [x] List of past checks from browser storage: date, thumbnail, disease, confidence word, newest first.
- [x] Tap a check to open its full result again (from storage, no new server call).
- [x] Delete one check; “Clear all” with a confirmation inside the page (not a browser pop-up).
- [x] Empty state: “No checks yet. Check your first leaf.” with a button to `/check`.

#### Block B · Profile page (≈ 1.5 h)

- [x] Fields: name, district, main crops, language (English / Bangla). Saved in browser storage; a Save button with a “Saved” message.
- [x] Create a device id once (`crypto.randomUUID()`), keep it in storage, send it as `X-Device-Id` with every check (for the server log only).
- [x] A short “About SafeCrop” section: what it can and cannot do, and the safety note.

#### Block C · Home page with real data (≈ 2 h)

- [x] Greeting uses the profile name (“Good evening, Nabil”), with the right greeting for the time of day.
- [x] “Recent checks” row from History (hidden when empty). Disease cards come from `/api/diseases` and open the detail pages.
- [x] Delete `src/data/sample.js` and fix anything that still used it.
- ~~Nice to have, only if time is left: Bangla switch — one strings file for English and Bangla, Bangla disease names, advice requested with `lang: "bn"`.~~ **Dropped 24 Nov.**

**Done when**

- [x] History opens, deletes and clears checks; Profile saves and reloads after a page refresh.
- [x] The home page shows real recent checks and real disease cards.
- [x] `sample.js` is gone and nothing breaks.

**If you get stuck**

Browser storage holds about 5 MB. Keep the history thumbnail small (about 160 pixels wide, JPEG) or 50 checks will not fit.

## Day 8 — removed on 26 November (no hosting; the app is demonstrated on the laptop)

Day 8 was "put SafeCrop online" (back end on a free Hugging Face Space, front end on Vercel, phone test). On 26 Nov
Hugging Face refused to create the Space: Docker (and Gradio) Spaces on the free CPU now need a paid PRO subscription,
which needs a card. Free hosts that ask for no card give at most 512 MB of memory; fine-tuned CLIP ViT-L/14 needs
about 2 GB. Nabil decided not to host the app at all and to demonstrate it on the laptop. No Space was created and no
hosting files were kept. For the report: "The app runs locally; free hosting without a card could not run the model."

## Day 9 — Thursday 26 November: Test everything and fix bugs

**Goal:** every test in the plan below passes on the laptop app, and every bug found so far is fixed.

#### Block A · Run the test plan (≈ 2.5 h)

- [x] Run every row of the test plan (next page) on the laptop app (back end + front end running locally). Mark pass or fail and note what happened.
- [x] Run the back-end tests (`pytest`) once more against the local server.

#### Block B · Fix bugs (≈ 2 h)

- [x] Fix the failed tests one at a time, most serious first (crashes and wrong answers before looks). (26 Nov: no test failed; 3 polish fixes.)
- [x] After each fix, run that test again and the tests next to it (a fix can break something else).
- [x] Commit and push to GitHub; recheck in the browser.

#### Block C · Speed and limits (≈ 1 h)

- [ ] Time per check on the laptop is already measured (0.82 s median); recheck it once plugged in with `scripts/time_checks.py`.
- [x] Check what happens with 3 checks at the same time (open 3 tabs): nothing should crash; slower is fine.
- [x] Count Gemini calls in the log; make sure caching stops repeat calls.

**Done when**

- [x] Every must-have test in the plan passes on the laptop app.
- [x] The bug list is empty or only has nice-to-have items left.
- [x] `docs/TEST_RESULTS.md` has the full test table.

## Day 10 — Thursday 26 November: Polish, safety and documents

**Goal:** the app looks finished, is safe to show to farmers, and a teammate can run it from the README alone.

**24 Nov plan:** only the polish a must-have needs (phone and laptop sizes, readable text, clear messages), then the safety checks and the docs.

#### Block A · Look and feel (≈ 2 h)

- [x] Loading placeholders instead of empty boxes; visible keyboard focus; text at least 16 px on phones; buttons at least 44 px tall. (26 Nov: placeholders, focus on every Tab stop and 44–50 px buttons checked; main text is 15–16 px, small captions 12–14 px — kept, since the demo is on the laptop.)
- [x] Check every page at 390, 820, 1366 and 1920 pixels wide. Nothing should spill sideways.
- [x] Page titles and the browser tab icon; a friendly “page not found” page.
- [ ] Run Lighthouse in Chrome DevTools on the home and result pages; fix anything below 90 in Accessibility.

#### Block B · Safety, privacy and security (≈ 1.5 h)

- [x] The safety note on every result: “SafeCrop gives a best guess, not a final diagnosis. Ask your local agriculture officer before using any chemical.”
- [x] Privacy line on the Check page: photos are checked and not stored.
- [x] Security check: search the whole repo history for the key (`git log -p | grep -i AIza`); upload size limit works; CORS allows only localhost.
- [x] If the key was ever committed, make a new key in AI Studio and delete the old one. (Not needed: 0 keys in the git history, 26 Nov.)

#### Block C · Documents (≈ 2 h)

- [ ] `README.md`: what SafeCrop does, a screenshot, how to run it locally (back end and front end; this is also how it is demonstrated), how to get the model files from the Hugging Face model repo, the environment variables.
- [ ] `docs/API.md` (or a link to `/docs`), `docs/MODEL_CARD.md`, and `docs/DATA_CARD.md`: where each disease's photos come from, how many, the licences, the noise recipe, and the known limits (one source per disease, synthetic noise).
- [ ] Ask your teammate to follow the README on their own laptop. Fix every step they get stuck on.

**Done when**

- [ ] Every page looks right on phone and laptop sizes; Lighthouse Accessibility ≥ 90.
- [ ] Safety and privacy notes are on screen; no secret in the repo history.
- [ ] Your teammate ran the app from the README without your help.

## Day 11 — Thursday 26 November: Freeze, demo video and backups

**Goal:** version 1.0 runs on the laptop, a demo video is recorded, and everything is backed up — ready for the Week 11 update on Mon 30 Nov.

**The Week 11 update is on Mon 30 Nov** (section below). The supervisor wants a working app, the demo video and numbers, so have the video and the Block C numbers ready by the end of today.

#### Block A · Freeze (≈ 1.5 h)

- [ ] Only fix bugs that break a must-have. No new features today.
- [ ] Final run of both parts on the laptop (`pytest`, `npm run build`, one full check). Tag the release in git: `git tag v1.0` and push the tag.
- [ ] Before any demo: start the back end and the front end 5 minutes early and wait for "Server online" (start-up about 11 s).

#### Block B · Demo script and video (≈ 2.5 h)

- [ ] Write a 2–3 minute demo script on the laptop: home → upload a real phone photo of a sick leaf → photo check warning → result with similar pictures → advice (and Bangla advice from Profile) → History → disease page → a short look at `/docs`.
- [ ] Practise it twice. Then record it: screen recording of the laptop.
- [ ] Keep the video as a backup in case the live demo fails (no internet for Gemini, laptop problem).

#### Block C · Numbers, backups and notes (≈ 1.5 h)

- [ ] Numbers for the Week 11 slides: real-photo results, time per check (laptop), start-up time, Gemini agreement rate, fallback count, tests passed.
- [ ] Backups: model files on Hugging Face and Drive; repo pushed; `.env` saved safely offline (never in Drive folders you share).
- [ ] Write “known limits” for the report: synthetic noise in training, one photo source per disease, real-photo test size, Gemini not tested as a classifier (E5), not hosted online (runs on the laptop; free hosting without a card can't run the model).
- [ ] Write the next steps: E5 (Gemini + fine-tuned neighbours), more real photos, the “Was this right?” button.

**Done when**

- [ ] `v1.0` is tagged and the app works end to end on the laptop.
- [ ] The demo video is recorded and saved in two places.
- [ ] Week 11 numbers and the known-limits list are written.

## Week 11 update — Monday 30 November (after Day 11)

**Goal:** show the working app on the laptop, the demo video and the numbers. No build work today. Start the back end
and the front end 5 minutes before the meeting; keep the video ready in case the live demo fails.

**Done when**

- [ ] Week 11 update given (live demo or the video).

## Test plan (Day 9; reuse for the final check on Day 11)

| \#  | Test                                                                 | Expected result                                          | Pass? |
|-----|----------------------------------------------------------------------|----------------------------------------------------------|-------|
| 1   | Clean photo of each of the 8 diseases (laptop upload)                | Right disease, “Very likely”, 5 similar pictures, advice |       |
| 2   | L3 photo of each noise type (5 photos)                               | Answer + the right photo warning                         |       |
| 3   | Healthy leaf                                                         | “Looks healthy” screen                                   |       |
| 4   | Look-alike disease not in our list (for example potato early blight) | “May be a disease SafeCrop doesn't know yet”             |       |
| 5   | Not a leaf (desk, face, wall)                                        | “We can't read this photo” + retake                      |       |
| 6   | Very dark photo; very blurry photo                                   | Warning; retake suggested when too unclear               |       |
| 7   | Drag a photo onto the Check page and onto the home card              | Preview shows; check works                               |       |
| 8   | iPhone HEIC photo uploaded on the laptop (if anyone has an iPhone)   | Accepted and checked                                     |       |
| 9   | Huge photo (over 10 MB) and a PDF                                    | Clear “too big” / “not a photo” message                  |       |
| 10  | Turn off the internet during a check                                 | “No internet” message, no crash                          |       |
| 11  | Check right after starting the back end (model still loading)        | “SafeCrop is starting” message, then it works            |       |
| 12  | Gemini key removed or quota used up                                  | Fallback advice shown; result still shown                |       |
| 13  | Refresh the browser on `/result/…`, `/history`, `/diseases/…`        | Page loads (no 404)                                      |       |
| 14  | History: open, delete one, clear all, then reload                    | Works and stays correct after reload                     |       |
| 15  | Profile: save name and language, reload                              | Name in greeting; settings kept                          |       |
| 16  | 3 checks at the same time (3 tabs)                                   | All finish; nothing crashes                              |       |
| 17  | Page widths 390 / 820 / 1366 / 1920 px                               | No sideways scrolling; everything readable               |       |
| 18  | Keyboard only (Tab, Enter) on laptop                                 | Every button reachable and visible when focused          |       |
| 19  | Search the built front end and the repo for the API key              | Not found                                                |       |
| 20  | Back-end `pytest`                                                    | All pass                                                 |       |

## Risks and what to do if they happen

| Risk                                        | Sign                                    | What to do                                                                                                                               |
|---------------------------------------------|-----------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| The laptop fails on demo day                | Won't start, or the back end won't load | Keep the demo video ready; model files are backed up on Hugging Face + Drive; README steps let a teammate's laptop run it               |
| No internet at the demo                     | Advice says it is the fallback          | Fine: the check runs fully on the laptop; advice falls back to `diseases.json`; show the video for the Gemini part                      |
| Gemini is slow, out of quota or down        | Advice takes \> 20 s or errors          | Fallback advice from `diseases.json` (built on Day 4); cache answers                                                                     |
| Checks are slow on battery                  | More than about 2 s per check           | Plug the laptop in for the demo; close other heavy programs                                                                              |
| Real photos give many wrong answers         | Day 6 table below about 70%             | Report it honestly (it is a real finding); the “not sure” screen protects farmers; plan more real photos for Week 11                     |
| scikit-learn version mismatch               | Error when loading `photo_check.joblib` | Pin the exact version used in Colab in `requirements.txt`                                                                                |
| Model files too big for GitHub              | Push rejected                           | Keep them only in the Hugging Face model repo (and Drive); `models/` is in `.gitignore`                                                  |
| Running out of days                         | A day's “done when” is not met          | Cut nice-to-haves (in the order of the “nice to have” table), never the must-haves; use Day 11's buffer                                  |

## Commands you will use every day

### Back end (in `backend/`)

    python -m venv .venv
    .venv\Scripts\activate        (Windows)
    source .venv/bin/activate      (Mac/Linux)
    pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000
    pytest -q

Test page: `http://localhost:8000/docs`

### Front end (in `frontend/`)

    npm install
    npm run dev
    npm run build
    npm run preview

`frontend/.env.local`: `VITE_API_URL=http://localhost:8000`

### Git (end of every block)

    git add -A
    git status                      (check .env and models/ are NOT listed)
    git commit -m "Day 5: result page with similar pictures"
    git push

### Release (no hosting since 26 Nov; the app runs on the laptop)

    git tag v1.0 && git push --tags

**Good habits for the whole 11 days**

- Never paste the Gemini key or the Hugging Face token into code, chat screenshots or slides.
- One change at a time: change, test, commit. If something breaks, `git diff` shows what changed.
- Keep a running “numbers” note (time per check, real-photo results, fold-0 checks) for the Week 10 and Week 11 slides.

## Master checklist for 26 November

Tick these on the last day. If every box is ticked, SafeCrop is fully functional.

### Model and back end

- [ ] Fine-tuned CLIP (E4 settings) trained on all photos and saved
- [ ] Database with clean + noisy copies + healthy / look-alikes
- [ ] Photo check exported; resample decision made
- [ ] Thresholds chosen from out-of-fold results (sure, not sure, not a leaf)
- [ ] `/api/health`, `/api/check`, `/api/advice`, `/api/diseases` work
- [ ] Gemini advice from checked facts, with fallback
- [ ] SQLite log without photos
- [ ] pytest tests pass
- [ ] Model card written

### Running on the laptop (no hosting since 26 Nov)

- [ ] Back end and front end start from the README commands; "Server online" shows
- [ ] Page refresh works on every route
- [ ] CORS limited to localhost; keys only in `backend/.env`
- [ ] Model files backed up on Hugging Face + Drive

### Front end

- [ ] Every menu item opens a working page
- [ ] Upload and drag-and-drop
- [ ] Progress steps tied to real calls
- [ ] Result: disease, confidence word, runner-up, photo warning
- [ ] 5 similar pictures
- [ ] Advice box + “second check disagrees” notice
- [ ] Healthy, not in list, not sure, retake screens
- [ ] Error messages (offline, waking up, wrong file, too big)
- [ ] Diseases list + 8 detail pages with sources
- [ ] History (open, delete, clear) and Profile
- [ ] No sample data left
- [ ] Safety and privacy notes on screen

### Proof and documents

- [ ] Real-photo test table
- [ ] Full test plan table
- [ ] README tested by a teammate
- [ ] API, model card, data card
- [ ] Week 10 slides done (22 Nov)
- [ ] Demo video recorded; v1.0 tagged
- [ ] Week 11 numbers and known limits written

