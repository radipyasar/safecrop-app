# SafeCrop web app — 11-day build routine (17–27 Nov 2026)

> Markdown copy of `SafeCrop_webapp_routine_17-27Nov2026.pdf`. Tick a box by changing `- [ ]` to `- [x]`.

Tuesday 17 November to Friday 27 November 2026. Every task, in order, with a clear "done when" check for each day, so that by 27 November SafeCrop works end to end and is online.

**Where you are today (16 Nov) and where you will be on 27 Nov**

**Today:** the React home page runs on `localhost:5173` with sample data. The models work in Colab and in the `NabilRafi/SafeCrop` repo (E4, fine-tuned CLIP + noisy copies, is the most robust: 97.1% at L3 on the test images, 85.2% on recipe B). There is no back end yet.

**27 Nov:** a farmer opens one public link on a phone, takes a photo of a leaf, and gets: a photo-quality check, the disease from fine-tuned CLIP, the 5 most similar reference pictures, and advice written by Gemini from checked disease facts. Past checks are saved in History. A demo video is recorded for the Week 11 update (29 Nov).

### The 11 days at a glance

| Day | Date       | Main goal                                        | Done when                                                   |
|-----|------------|--------------------------------------------------|-------------------------------------------------------------|
| 1   | Tue 17 Nov | Set up the project, connect all pages            | Every menu item opens a page; back end says “ok”            |
| 2   | Wed 18 Nov | Make the app's model files in Colab              | Fine-tuned CLIP, database, photo check and thresholds saved |
| 3   | Thu 19 Nov | Back end: photo in, disease out                  | `/api/check` names the disease for 8 sample photos          |
| 4   | Fri 20 Nov | Back end: Gemini advice + disease facts          | `/api/advice` works, with a fallback when Gemini fails      |
| 5   | Sat 21 Nov | Front end: the full check flow                   | Upload → result → advice works on the laptop                |
| 6   | Sun 22 Nov | Real photos + **Week 10 update** + disease pages | Real-photo table done; Week 10 slides added                 |
| 7   | Mon 23 Nov | History, Profile, Home with real data            | No sample data left anywhere                                |
| 8   | Tue 24 Nov | Put it online (Hugging Face + Vercel)            | The public link works on a phone                            |
| 9   | Wed 25 Nov | Test everything, fix bugs                        | All tests in the test plan pass                             |
| 10  | Thu 26 Nov | Polish, safety, documents                        | A teammate can run it from the README                       |
| 11  | Fri 27 Nov | Freeze, demo video, backups                      | v1.0 tagged, video recorded, link works                     |

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

These are the features SafeCrop must have by 27 November. Use this list as the finish line: the app is done when every must-have works on the public link.

| \#  | Must-have feature                                                                                                                                       | Where it lives         |
|-----|---------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------|
| 1   | Upload a photo, or take one with the phone camera                                                                                                       | Check page             |
| 2   | Photo check: names the problem (blur, grain, dark, blocky) and the level (L0–L3); warns when the photo is bad; asks for a retake when it is too unclear | Back end + Result page |
| 3   | Disease answer from fine-tuned CLIP (E4) with a confidence word (Very likely / Likely / Not sure) and the next best guess                               | Back end + Result page |
| 4   | Handles a healthy leaf, a disease not in our list, and a photo that is not a leaf                                                                       | Back end + Result page |
| 5   | Shows the 5 most similar reference pictures, so the farmer can compare by eye                                                                           | Result page            |
| 6   | Advice written by Gemini from checked disease facts, plus a fallback when Gemini is slow, out of quota or offline                                       | Back end + Result page |
| 7   | Disease list and a detail page for each of the 8 diseases (symptoms, what to do, prevention, sources)                                                   | Diseases pages         |
| 8   | History of past checks: open, delete one, clear all                                                                                                     | History page           |
| 9   | Profile: name, district, crops, language                                                                                                                | Profile page           |
| 10  | Works on phone and laptop; online at a public link; no API key in the code                                                                              | Vercel + Hugging Face  |
| 11  | Clear messages for: no internet, server waking up, wrong file type, file too big, server error                                                          | Every page             |
| 12  | README, model card, data card and test results written                                                                                                  | `docs/` folder         |

| Nice to have (only if time is left, in this order)                       | Why it is optional                                          |
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
| Front end       | React 19 + Vite 6 (your `safecrop-web`), `react-router-dom` for pages                                | Hosted on Vercel (Hobby plan, sign in with GitHub)                               |
| Back end        | Python 3.11, FastAPI, Uvicorn, python-multipart                                                      | Swagger test page at `/docs` for free                                            |
| Image reading   | Pillow + pillow-heif (iPhone HEIC photos), EXIF rotation fix                                         | Uploads up to 10 MB                                                              |
| Disease model   | PyTorch (CPU), transformers, CLIP ViT-L/14 with your fine-tuned last 4 blocks (E4)                   | Only the changed weights are saved (~100–200 MB)                                 |
| Database search | numpy: cosine similarity, 5 nearest pictures, weighted vote                                          | Clean + noisy copies + healthy / look-alike pictures                             |
| Photo check     | Your 16 measurements + random forests (scikit-learn, joblib)                                         | Pin the same scikit-learn version as in Colab                                    |
| Advice          | google-genai with Gemini 3.5 Flash-Lite (free AI Studio key)                                         | Key kept in `.env` locally and as a Space secret online                          |
| History         | Browser storage (localStorage) for the History page; SQLite log on the server for your own numbers   | Free Spaces lose their disk on restart, so History must not depend on the server |
| Hosting         | Hugging Face Space (Docker, CPU basic: 2 vCPU, 16 GB RAM) + model files in a Hugging Face model repo | Free Spaces sleep when unused; wake it before a demo                             |

## The API (what the front end and back end say to each other)

| Call                     | Sends                                                | Gets back                                                                                                                                                                                                                                   |
|--------------------------|------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `GET /api/health`        | nothing                                              | `{status, model_loaded, version}`                                                                                                                                                                                                           |
| `POST /api/check`        | the photo (form field `image`); header `X-Device-Id` | `check_id`; `photo_check` {problem, level, sure, message, fix_applied}; `result` {decision, disease_id, disease_name, crop, vote_share, confidence_words, runner_up}; `neighbours` \[5 × {disease_id, thumb_url, similarity}\]; `timing_ms` |
| `POST /api/advice`       | `{check_id, lang}`                                   | `{source: gemini | fallback, agrees, summary, steps[], see_expert_when, safety_note}`                                                                                                                                                       |
| `GET /api/diseases`      | nothing                                              | list of the 8 diseases (id, crop, names, short description, thumbnail)                                                                                                                                                                      |
| `GET /api/diseases/{id}` | nothing                                              | full facts: symptoms, what to do now, prevention, when to call an expert, sources                                                                                                                                                           |
| `GET /static/thumbs/…`   | nothing                                              | small reference pictures shown on the Result and Disease pages                                                                                                                                                                              |

| Decision        | When (thresholds chosen on Day 2)                                                                           | What the farmer sees                                                                     |
|-----------------|-------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| **sure**        | vote share at or above the “sure” cut, photo check OK or L1–L2                                              | “Very likely: Potato late blight” + similar pictures + advice                            |
| **likely**      | vote share between the two cuts                                                                             | “Likely: X. Could also be Y.” + a tip to retake a clearer photo                          |
| **not sure**    | vote share below the lower cut                                                                              | “SafeCrop is not sure.” Top 2 guesses, a retake button, and a nudge to ask an expert     |
| **healthy**     | the winning label is a healthy leaf                                                                         | “This leaf looks healthy.” + what to watch for                                           |
| **not in list** | the winning label is a look-alike disease SafeCrop does not cover                                           | “This may be a disease SafeCrop doesn't know yet.” + ask an expert                       |
| **retake**      | best similarity below the “not a leaf” cut, or the photo check is sure the photo is L3 and the vote is weak | “We can't read this photo.” + exactly what to fix (hold steady, more light, move closer) |

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
        requirements.txt, Dockerfile, .env.example
      notebooks/SafeCrop_app_model_export.ipynb
      docs/MODEL_CARD.md, DATA_CARD.md, API.md, TEST_RESULTS.md

## Day 1 — Tuesday 17 November: Set up the project and connect every page

**Goal:** one repo with the front end and an empty back end, both running, and every menu item opening its own page.

#### Block A · Plan and accounts (≈ 1.5 h)

- [ ] Read this routine once from start to finish. Copy the must-have list into a checklist you will tick (GitHub Issues, a GitHub Project board, or Notion).
- [x] Make a **Hugging Face** account (free, no card). Create an access token with *write* rights (Settings → Access Tokens). Save it in a password manager, not in a file.
- [x] Make a **Vercel** account by signing in with GitHub (Hobby plan, no card).
- [x] Check the Gemini key still works: a 5-line Python script that asks Gemini 3.5 Flash-Lite “say hi”. Keep the key in an environment variable only.
- [ ] Tell your teammate the plan and split work if possible (for example: teammate writes `diseases.json` on Day 4 and collects real photos for Day 6).

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

- [ ] Make `SafeCrop_app_model_export.ipynb` from the repo's `finetune.py` (ask Claude Code to write it). Use the same default settings as E3/E4: last 4 blocks + projection, 15 epochs, lr 1e-5 (head 1e-3), consistency weight 1.0, fixed seed.
- [ ] Train on **all 240 photos** of the 8 diseases (no folds this time, because the app should learn from everything). On a T4 this takes about 3–5 minutes.
- [ ] Save **only the changed weights** (last 4 blocks, final norm, visual projection) as `clip_ft_delta.safetensors`. The app loads the normal CLIP ViT-L/14 from Hugging Face and puts these on top. Check that loading them back gives the same embedding for one photo, and note the seed and library versions.

#### Block B · Build the picture database (≈ 1.5 h)

- [ ] For every one of the 240 photos: the clean photo + 15 noisy copies (5 noise types × L1–L3, seed family 2026, not 299). Embed all with the fine-tuned model.
- [ ] Add the 240 PlantVillage extras (4 look-alike diseases + 3 healthy leaves) and their noisy copies, labelled `healthy_…` or `other_…`, so the app can say “healthy” or “not in our list”.
- [ ] Save `database.npz`: embeddings (normalised), label, photo_id, is_copy, noise type, level. About 7,700 × 768 numbers, roughly 25 MB.
- [ ] Save a 200-pixel JPEG thumbnail of every **clean** photo in `thumbs/`. The app always shows the clean picture, even when a noisy copy was the match.

#### Block C · Photo check, thresholds and checks (≈ 2 h)

- [ ] Retrain the photo-check forests on all 960 noisy test images; save `photo_check.joblib` + the feature code as `photo_check.py`; note the scikit-learn version.
- [ ] **Pick the “sure” and “not sure” cuts** from the repo's out-of-fold E4 predictions (not the new model): the vote share at which answers are right at least 95% of the time (“sure”), and the one below which they are right less than 70% (“not sure”). Save them in `thresholds.json`.
- [ ] **Pick the “not a leaf” cut:** embed 30 non-leaf photos (desk, hand, sky, food); choose the best-similarity value that separates them from leaves.
- [ ] **Check the healthy pictures don't hurt too much:** on fold 0 (out-of-fold), compare E4 at L3 with and without the healthy / look-alike pictures in the database. Write both numbers down for your slides (in the frozen noisy album it was 95.2% vs 88.1%).
- [ ] **Check the resample fix on E4:** compressed L3 photos with and without resample (fold 0). Keep the fix in the app only if it helps or ties.
- [ ] Upload all files to a **private Hugging Face model repo** (e.g. `NabilRafi/safecrop-models`) and to Drive; download them into `backend/models/`.

**Done when**

- [ ] `backend/models/` has `clip_ft_delta.safetensors`, `database.npz`, `thumbs/`, `photo_check.joblib`, `thresholds.json`.
- [ ] A short `docs/MODEL_CARD.md` lists: training data, settings, seed, versions, thresholds, and the two fold-0 checks.
- [ ] The same files are safe in the Hugging Face model repo and on Drive.

## Day 3 — Thursday 19 November: Back end: photo in, disease out

**Goal:** `POST /api/check` takes a photo and returns the photo-check result, the disease, the confidence and the 5 similar pictures.

#### Block A · Load the model once at start-up (≈ 2 h)

- [ ] `app/model.py`: load `openai/clip-vit-large-patch14` (vision part + processor), put the fine-tuned weights on top, switch to eval mode, use `torch.inference_mode()`, set `torch.set_num_threads` to the CPU count.
- [ ] Load `database.npz` and `thresholds.json` into memory once.
- [ ] Use FastAPI's start-up (lifespan) to load everything and run one warm-up photo, so the first real check is not slow.
- [ ] Make `/api/health` report `model_loaded: true` only after loading has finished.

#### Block B · Photo check and prediction (≈ 2 h)

- [ ] `app/photo_check.py`: same 16 measurements as in Colab, then the two forests → problem, level, how sure. Apply resample to blocky photos only if Day 2 said it helps.
- [ ] `app/predict.py`: embed → cosine similarity with every database picture → top 5 → weighted vote → winning label, vote share, runner-up.
- [ ] Turn the numbers into one **decision** (sure / likely / not sure / healthy / not in list / retake) using `thresholds.json` and the decision table (after the API table).
- [ ] For the 5 neighbours, return the **clean** photo's thumbnail URL (`/static/thumbs/…`) and remove duplicates (two copies of the same photo count once).

#### Block C · The endpoint and its tests (≈ 1.5 h)

- [ ] `POST /api/check`: accept JPEG, PNG, WebP and HEIC up to 10 MB; reject other files with a clear message (HTTP 415 / 413). Fix EXIF rotation, convert to RGB.
- [ ] Give every check a `check_id` and remember the result in memory for the advice call (and later in the SQLite log).
- [ ] Add `timing_ms` (photo check, embedding, search) to every answer.
- [ ] Write pytest tests: 8 sample photos (one per disease, clean and L3) give the right disease; a text file is rejected; an empty file is rejected; a 15 MB file is rejected.
- [ ] Measure the time per check on your laptop CPU (write it down for the slides).

**Done when**

- [ ] In `/docs`, uploading each of the 8 clean sample photos returns the right disease.
- [ ] Bad files get a clear error, never a crash. All pytest tests pass.
- [ ] You know the time per check on your laptop (target: under 5 seconds).

**If you get stuck**

If a check takes much longer than 5 seconds on the laptop, check that the model loads only once (not per request) and that gradients are off. If memory is short, load the model in half precision only for the database step, not for live checks.

## Day 4 — Friday 20 November: Back end: Gemini advice and disease facts

**Goal:** the back end can explain each result in plain words, using facts you checked, and still answers when Gemini fails.

#### Block A · Write the disease facts (≈ 2 h)

- [ ] Create `data/diseases.json` with one entry for each of the 8 diseases, plus `healthy` and `unknown`.
- [ ] For each disease: id, crop, English name, Bangla name, what causes it (fungus, virus, insect…), 3–5 signs to look for, what to do now, how to prevent it, when to call an expert, and 1–3 source links.
- [ ] Use trusted sources: Bangladesh research institutes and extension services (for example BRRI for rice, BJRI for jute, BARI for potato and black gram, DAE), and university extension pages for apple, pear and grape. Write down every source you used.
- [ ] Do **not** write chemical names with doses. Write “ask your local agriculture officer which product and dose to use”. Add the local agriculture helpline number after checking it is current.
- [ ] Note: rice stem borer is an insect pest, not a disease. Say so on its page.

#### Block B · The advice service (≈ 2 h)

- [ ] `app/advice.py`: use `google-genai` with Gemini 3.5 Flash-Lite. Send: the farmer's photo, the predicted disease, its facts from `diseases.json`, and the photo-check result.
- [ ] Ask for a JSON answer with a fixed shape: `agrees` (yes / no / unsure), `summary` (2 sentences), `steps` (3–5 short steps), `see_expert_when`, `safety_note`. Tell Gemini to use only the given facts and simple words, and to answer in the requested language (English or Bangla).
- [ ] Timeout of 20 seconds and one retry. Cache the answer by `check_id` so a page refresh doesn't spend quota.
- [ ] **Fallback:** if Gemini fails, times out or the daily quota is used up, build the same JSON from `diseases.json` with `source: "fallback"`.

#### Block C · Endpoints, log and tests (≈ 1.5 h)

- [ ] `POST /api/advice`, `GET /api/diseases`, `GET /api/diseases/{id}`.
- [ ] `app/db.py`: SQLite table `checks` (id, time, device_id, problem, level, label, vote_share, decision, gemini_agrees, advice_source, timing). Do **not** store photos (privacy).
- [ ] Tests: advice returns valid JSON; with the key removed it returns the fallback; an unknown `check_id` gives a clear 404.
- [ ] Put the key only in `backend/.env`. Run `git status` and make sure `.env` is not listed.

**Done when**

- [ ] `/api/advice` returns Gemini's advice in about 10 seconds or less, and fallback advice when the key is removed.
- [ ] `/api/diseases` returns all 8 diseases with checked facts and sources.
- [ ] Every check is written to the SQLite log; no photos are stored.

**If you get stuck**

If Gemini returns text that is not valid JSON, use the SDK's structured-output option (a response schema) instead of asking for JSON in words, and still wrap the parse in a try/except that falls back.

## Day 5 — Saturday 21 November: Front end: the full check flow

**Goal:** on the laptop, a user can upload a photo, watch the steps, see the result with similar pictures, and read the advice.

#### Block A · The Check page (≈ 2 h)

- [ ] Upload button (file picker), “Use camera” button (`<input type="file" accept="image/*" capture="environment">`, which opens the back camera on phones) and drag-and-drop on laptops.
- [ ] Show a preview of the chosen photo with “Check this leaf” and “Choose another” buttons.
- [ ] Only shrink the photo in the browser if it is larger than 2048 pixels or 5 MB (shrinking adds compression, which could change the photo check). Test that the photo check gives the same answer for 5 test images with and without this step.
- [ ] Disable the button while a check runs so it can't be sent twice.

#### Block B · Progress and the Result page (≈ 2.5 h)

- [ ] Progress steps tied to real calls: “Photo check” and “Compare” while `/api/check` runs, “Get advice” while `/api/advice` runs.
- [ ] Result card: disease name and crop, the confidence word (Very likely / Likely / Not sure), and the runner-up when it is close.
- [ ] Photo warning banner when the photo check finds a problem (for example “Your photo is blurry. Hold the phone steady and retake if you can.”). Use one simple “blurry” message for both blur types.
- [ ] “Similar pictures from our library”: the 5 thumbnails with their disease names.
- [ ] Advice box that fills in when `/api/advice` returns; if Gemini disagrees, show “Our second check is not sure about this answer. Retake the photo or ask an expert.”
- [ ] Buttons: Retake, Learn about this disease, See history.

#### Block C · Special results and errors (≈ 1.5 h)

- [ ] Screens for: healthy leaf, not in our list, retake needed, not sure. Each says what happened and what to do next.
- [ ] Error messages: no internet, server waking up (“SafeCrop is starting, try again in a minute”), wrong file, file too big, server error.
- [ ] Save every finished check to History in the browser (`src/lib/history.js`): id, date, small thumbnail, disease, confidence word, decision, advice. Keep at most 50 checks.

**Done when**

- [ ] Upload → steps → result → advice works for 8 sample photos on the laptop.
- [ ] You can trigger every special screen and every error message on purpose (for example stop the back end to see “offline”).
- [ ] Each check appears in the browser's saved history.

**If you get stuck**

To trigger the special screens without hunting for photos, add a hidden test option in development only (for example `?force=healthy`) that the back end ignores in production.

## Day 6 — Sunday 22 November: Real photos, the Week 10 update, and the disease pages

**Goal:** the first fair test of the app on real phone photos, Week 10 slides ready, and the Diseases pages filled with real facts.

**Week 10 update today**

The supervisor wants tables and numbers. Lead with the real-photo table and the time per check, not with descriptions.

#### Block A · Real-photo test (do this first) (≈ 2 h)

- [ ] Gather 20–30 real phone photos with a known disease (from the field trip or new ones), including a few healthy leaves and a few bad photos. Write the true label of each in a sheet **before** running them.
- [ ] Run each through the local app. Record: photo, true label, app answer, decision, photo-check problem and level, Gemini agrees?, time.
- [ ] Count: right / wrong / not sure, and how often the photo check warned. Do **not** change any threshold after seeing these results (that would make the test unfair); write ideas down for later.
- [ ] Save the table as `docs/TEST_RESULTS.md` (real-photo section).

#### Block B · Week 10 slides (supervisor update today) (≈ 1.5 h)

- [ ] Slide: how the app works (the “How the finished app works” diagram) and the tech stack table.
- [ ] Slide: the API table and the decision table.
- [ ] Slide: numbers — time per check, the two Day 2 fold-0 checks (with / without healthy pictures, resample), real-photo results table.
- [ ] Slide: screenshots of the Check, Result and special screens.
- [ ] Slide: plan for 23–27 Nov (Days 7–11 of this routine).

#### Block C · Diseases pages (≈ 1.5 h)

- [ ] Diseases page: cards from `/api/diseases` (photo, crop, name), grouped by crop.
- [ ] Detail page: signs to look for, what to do now, prevention, when to call an expert, sources (as links), and 4 example pictures from the database.
- [ ] Link from the Result page (“Learn about this disease”) and from the home page cards.

**Done when**

- [ ] Real-photo results table written, with the true labels recorded before the test.
- [ ] Week 10 slides are in the deck and presented.
- [ ] Diseases list and all 8 detail pages show real facts and sources.

**If you get stuck**

If you don't have labelled real photos yet, take 3–4 photos each of whatever leaves you can find (healthy leaves count) and ask your teammate for field-trip photos; even 15 photos give a useful first table.

## Day 7 — Monday 23 November: History, Profile and a home page with real data

**Goal:** every screen uses real data; the sample data file is deleted.

#### Block A · History page (≈ 2 h)

- [ ] List of past checks from browser storage: date, thumbnail, disease, confidence word, newest first.
- [ ] Tap a check to open its full result again (from storage, no new server call).
- [ ] Delete one check; “Clear all” with a confirmation inside the page (not a browser pop-up).
- [ ] Empty state: “No checks yet. Check your first leaf.” with a button to `/check`.

#### Block B · Profile page (≈ 1.5 h)

- [ ] Fields: name, district, main crops, language (English / Bangla). Saved in browser storage; a Save button with a “Saved” message.
- [ ] Create a device id once (`crypto.randomUUID()`), keep it in storage, send it as `X-Device-Id` with every check (for the server log only).
- [ ] A short “About SafeCrop” section: what it can and cannot do, and the safety note.

#### Block C · Home page with real data (≈ 2 h)

- [ ] Greeting uses the profile name (“Good evening, Nabil”), with the right greeting for the time of day.
- [ ] “Recent checks” row from History (hidden when empty). Disease cards come from `/api/diseases` and open the detail pages.
- [ ] Delete `src/data/sample.js` and fix anything that still used it.
- [ ] Nice to have, only if time is left: Bangla switch — one strings file for English and Bangla, Bangla disease names, advice requested with `lang: "bn"`.

**Done when**

- [ ] History opens, deletes and clears checks; Profile saves and reloads after a page refresh.
- [ ] The home page shows real recent checks and real disease cards.
- [ ] `sample.js` is gone and nothing breaks.

**If you get stuck**

Browser storage holds about 5 MB. Keep the history thumbnail small (about 160 pixels wide, JPEG) or 50 checks will not fit.

## Day 8 — Tuesday 24 November: Put SafeCrop online

**Goal:** one public link that works on a phone over mobile data, with the back end on a free Hugging Face Space and the front end on Vercel.

#### Block A · Back end on a Hugging Face Space (≈ 2.5 h)

- [ ] Write `backend/Dockerfile`: `python:3.11-slim`, install the CPU-only PyTorch wheel (much smaller), install requirements, copy the app, run Uvicorn on port **7860**.
- [ ] At start-up, download the model files from your Hugging Face model repo with `huggingface_hub` (using the `HF_TOKEN` secret) and cache them.
- [ ] Create a new Space: SDK **Docker**, hardware **CPU basic (free)**. Add secrets: `GEMINI_API_KEY`, `HF_TOKEN`, `ALLOWED_ORIGINS`.
- [ ] Push the back end to the Space. Watch the build log until it says it is running. Open `https://<your-space>.hf.space/api/health` and `/docs`; run one check from `/docs`.
- [ ] Measure: start-up time after sleeping, and time per check on the Space (write both down).

#### Block B · Front end on Vercel (≈ 1.5 h)

- [ ] In Vercel: import the GitHub repo, set the root directory to `frontend`, build command `npm run build`, output folder `dist`.
- [ ] Add the environment variable `VITE_API_URL=https://<your-space>.hf.space` and redeploy.
- [ ] Add `frontend/vercel.json` that sends every path to `index.html`, so refreshing `/history` doesn't give a 404.
- [ ] Put the Vercel address in the Space's `ALLOWED_ORIGINS` secret and restart the Space.

#### Block C · Phone test (≈ 1.5 h)

- [ ] Open the Vercel link on an Android phone in Chrome, on mobile data and on Wi-Fi. Take a photo with the camera button; upload one from the gallery.
- [ ] If anyone has an iPhone, test Safari too (HEIC photos, camera button).
- [ ] Check: the layout fits, buttons are easy to tap, the result and advice appear, History keeps the check after closing the browser.
- [ ] Write every problem you find in the bug list for Day 9.

**Done when**

- [ ] The public Vercel link works end to end on a phone over mobile data.
- [ ] Start-up time and time per check on the Space are written down.
- [ ] No secret appears in the GitHub repo or in the front-end code (search the built files for the key).

**If you get stuck**

If the Space build runs out of memory or space, make sure the CPU-only torch wheel is used and that model files are downloaded at start-up, not copied into the image. If the Space still fails, a backup for the demo is to run the back end on your laptop and share it with a free Cloudflare quick tunnel (`cloudflared tunnel --url http://localhost:8000`), which needs no account or card.

## Day 9 — Wednesday 25 November: Test everything and fix bugs

**Goal:** every test in the plan below passes on the public link, and every bug from Day 8 is fixed.

#### Block A · Run the test plan (≈ 2.5 h)

- [ ] Run every row of the test plan (next page) on the public link: phone and laptop. Mark pass or fail and note what happened.
- [ ] Run the back-end tests (`pytest`) once more against the local server.

#### Block B · Fix bugs (≈ 2 h)

- [ ] Fix the failed tests one at a time, most serious first (crashes and wrong answers before looks).
- [ ] After each fix, run that test again and the tests next to it (a fix can break something else).
- [ ] Push and let Vercel and the Space redeploy; recheck on the phone.

#### Block C · Speed and limits (≈ 1 h)

- [ ] If a check takes more than about 8 seconds on the Space, try: fewer CPU threads fighting (set threads = 2), make sure the photo is resized to 224 before CLIP, and show the result before the advice (already the design).
- [ ] Check what happens with 3 checks at the same time (open 3 tabs): nothing should crash; slower is fine.
- [ ] Count Gemini calls in the log; make sure caching stops repeat calls.

**Done when**

- [ ] Every must-have test in the plan passes on the public link.
- [ ] The bug list from Day 8 is empty or only has nice-to-have items left.
- [ ] `docs/TEST_RESULTS.md` has the full test table.

## Day 10 — Thursday 26 November: Polish, safety and documents

**Goal:** the app looks finished, is safe to show to farmers, and a teammate can run it from the README alone.

#### Block A · Look and feel (≈ 2 h)

- [ ] Loading placeholders instead of empty boxes; visible keyboard focus; text at least 16 px on phones; buttons at least 44 px tall.
- [ ] Check every page at 390, 820, 1366 and 1920 pixels wide. Nothing should spill sideways.
- [ ] Page titles and the browser tab icon; a friendly “page not found” page.
- [ ] Run Lighthouse in Chrome DevTools on the home and result pages; fix anything below 90 in Accessibility.

#### Block B · Safety, privacy and security (≈ 1.5 h)

- [ ] The safety note on every result: “SafeCrop gives a best guess, not a final diagnosis. Ask your local agriculture officer before using any chemical.”
- [ ] Privacy line on the Check page: photos are checked and not stored.
- [ ] Security check: search the whole repo history for the key (`git log -p | grep -i AIza`); upload size limit works; CORS allows only your Vercel address and localhost.
- [ ] If the key was ever committed, make a new key in AI Studio and delete the old one.

#### Block C · Documents (≈ 2 h)

- [ ] `README.md`: what SafeCrop does, a screenshot, how to run it locally (back end and front end), how to deploy, the environment variables.
- [ ] `docs/API.md` (or a link to `/docs`), `docs/MODEL_CARD.md`, and `docs/DATA_CARD.md`: where each disease's photos come from, how many, the licences, the noise recipe, and the known limits (one source per disease, synthetic noise).
- [ ] Ask your teammate to follow the README on their own laptop. Fix every step they get stuck on.

**Done when**

- [ ] Every page looks right on phone and laptop sizes; Lighthouse Accessibility ≥ 90.
- [ ] Safety and privacy notes are on screen; no secret in the repo history.
- [ ] Your teammate ran the app from the README without your help.

## Day 11 — Friday 27 November: Freeze, demo video and backups

**Goal:** version 1.0 is online, a demo video is recorded for the Week 11 update (29 Nov), and everything is backed up.

#### Block A · Freeze (≈ 1.5 h)

- [ ] Only fix bugs that break a must-have. No new features today.
- [ ] Final deploy of both parts. Tag the release in git: `git tag v1.0` and push the tag.
- [ ] Open the Space and the Vercel link 10 minutes before any demo to wake the Space.

#### Block B · Demo script and video (≈ 2.5 h)

- [ ] Write a 2–3 minute demo script: open the link on a phone → home → take a photo of a sick leaf → photo check warning → result with similar pictures → advice → History → disease page → (Bangla, if done).
- [ ] Practise it twice. Then record it: screen recording of the phone plus a short laptop part showing `/docs`.
- [ ] Keep the video as a backup in case the live demo fails (bad network, Space asleep).

#### Block C · Numbers, backups and notes (≈ 1.5 h)

- [ ] Numbers for the Week 11 slides: real-photo results, time per check (laptop and Space), start-up time, Gemini agreement rate, fallback count, tests passed.
- [ ] Backups: model files on Hugging Face and Drive; repo pushed; `.env` saved safely offline (never in Drive folders you share).
- [ ] Write “known limits” for the report: synthetic noise in training, one photo source per disease, real-photo test size, Gemini not tested as a classifier (E5), free hosting sleeps.
- [ ] Write the next steps: E5 (Gemini + fine-tuned neighbours), more real photos, the “Was this right?” button.

**Done when**

- [ ] `v1.0` is tagged and the live link works on a phone.
- [ ] The demo video is recorded and saved in two places.
- [ ] Week 11 numbers and the known-limits list are written.

## Test plan (Day 9; reuse for the final check on Day 11)

| \#  | Test                                                                 | Expected result                                          | Pass? |
|-----|----------------------------------------------------------------------|----------------------------------------------------------|-------|
| 1   | Clean photo of each of the 8 diseases (laptop upload)                | Right disease, “Very likely”, 5 similar pictures, advice |       |
| 2   | L3 photo of each noise type (5 photos)                               | Answer + the right photo warning                         |       |
| 3   | Healthy leaf                                                         | “Looks healthy” screen                                   |       |
| 4   | Look-alike disease not in our list (for example potato early blight) | “May be a disease SafeCrop doesn't know yet”             |       |
| 5   | Not a leaf (desk, face, wall)                                        | “We can't read this photo” + retake                      |       |
| 6   | Very dark photo; very blurry photo                                   | Warning; retake suggested when too unclear               |       |
| 7   | Phone camera button (Android Chrome)                                 | Back camera opens; check works                           |       |
| 8   | iPhone HEIC photo (if anyone has an iPhone)                          | Accepted and checked                                     |       |
| 9   | Huge photo (over 10 MB) and a PDF                                    | Clear “too big” / “not a photo” message                  |       |
| 10  | Turn off the internet during a check                                 | “No internet” message, no crash                          |       |
| 11  | Space asleep (first visit after a long break)                        | “SafeCrop is starting” message, then it works            |       |
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
| The Space build fails or runs out of memory | Build log stops with an error           | CPU-only torch; download models at start-up; if still stuck, run the back end on your laptop with a Cloudflare quick tunnel for the demo |
| The Space is asleep during the demo         | First request takes a minute            | Open the link 10 minutes before; show the “starting” message; keep the demo video ready                                                  |
| Gemini is slow, out of quota or down        | Advice takes \> 20 s or errors          | Fallback advice from `diseases.json` (built on Day 4); cache answers                                                                     |
| Checks are too slow on the free CPU         | More than about 8 s per check           | 2 threads; resize to 224 early; result shown before advice                                                                               |
| Real photos give many wrong answers         | Day 6 table below about 70%             | Report it honestly (it is a real finding); the “not sure” screen protects farmers; plan more real photos for Week 11                     |
| scikit-learn version mismatch               | Error when loading `photo_check.joblib` | Pin the exact version used in Colab in `requirements.txt`                                                                                |
| Model files too big for GitHub              | Push rejected                           | Keep them only in the Hugging Face model repo (and Drive); `models/` is in `.gitignore`                                                  |
| Camera button doesn't open the camera       | Gallery opens instead                   | Fine: upload still works; test `capture="environment"` on another phone                                                                  |
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
    npm run dev -- --host     (open on your phone on the same Wi-Fi)
    npm run build
    npm run preview

`frontend/.env.local`: `VITE_API_URL=http://localhost:8000`

### Git (end of every block)

    git add -A
    git status                      (check .env and models/ are NOT listed)
    git commit -m "Day 5: result page with similar pictures"
    git push

### Deploy

    Back end:  push backend/ to the Hugging Face Space repo (it rebuilds by itself)
    Front end: push to GitHub (Vercel rebuilds by itself)
    Release:   git tag v1.0 && git push --tags

**Good habits for the whole 11 days**

- Never paste the Gemini key or the Hugging Face token into code, chat screenshots or slides.
- Test on the phone early (from Day 5 with `npm run dev -- --host`), not only on Day 8.
- One change at a time: change, test, commit. If something breaks, `git diff` shows what changed.
- Keep a running “numbers” note (time per check, real-photo results, fold-0 checks) for the Week 10 and Week 11 slides.

## Master checklist for 27 November

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

### Online

- [ ] Back end on a free Hugging Face Space
- [ ] Front end on Vercel; page refresh works on every route
- [ ] CORS limited to your addresses; secrets only in Space settings
- [ ] Works on a phone over mobile data

### Front end

- [ ] Every menu item opens a working page
- [ ] Upload, camera and drag-and-drop
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

