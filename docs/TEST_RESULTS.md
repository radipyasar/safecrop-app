# SafeCrop web app — test results

Two parts: the **test plan** (does every feature work, Day 9) and the **real-photo test** (does the model work on real
phone photos, Day 6 Block A). The app runs on the laptop (no hosting since 26 Nov), so every test is on the laptop app.

Accuracy claims for the report come from the 5-fold results in `NabilRafi/SafeCrop`, not from this page: the sample
photos below are from the training data, so they only show that each feature works.

## Test plan (Day 9) — 26 Nov 2026: 20 / 20 passed

How it was run: back end (`uvicorn`, port 8000) and front end (`npm run dev`, port 5173) on the laptop (i5-13420H),
Chrome driven headless by a small script (uploads, clicks, screenshots; the script is not in the repo). Real Gemini
key, except row 12.

| # | Test | Expected | Result | Pass? |
|---|------|----------|--------|-------|
| 1 | Clean photo of each of the 8 diseases | Right disease, "Very likely", 5 similar pictures, advice | 8/8 right disease, all "Very likely" (vote 100%), 5 pictures each, Gemini advice for all 8 (Gemini agreed on 8/8) | ✅ |
| 2 | L3 photo of each noise type (8 photos: grain ×2, low light ×2, shake blur ×2, out of focus, blocky) | Answer + the right photo warning | 8/8 right noise type and level L3, warning shown on all 8; disease still right on 8/8 | ✅ |
| 3 | Healthy leaf (healthy apple, PlantVillage) | "Looks healthy" screen | "Healthy apple leaf · Looks healthy" | ✅ |
| 4 | Look-alike not in our list (potato early blight) | "May be a disease SafeCrop doesn't know yet" | "Not in our list" screen | ✅ |
| 5 | Not a leaf (a made-up desk picture) | "We can't read this photo" + retake | "We can't read this photo" (`not_a_leaf`), retake button, no advice call | ✅ |
| 6 | Very dark photo; very blurry photo | Warning; retake suggested when too unclear | Dark: "Your photo is too dark. Move to brighter light…"; blurry: blur warning. Both still named the disease (vote was strong), so the "too unclear" retake screen was not needed | ✅ |
| 7 | Drag a photo onto the Check page and onto the home card | Preview shows; check works | Both: preview + file name, check works (home card opens the Check page with the photo) | ✅ |
| 8 | HEIC photo uploaded on the laptop | Accepted and checked | HEIC made from a grape sample: Chrome shows "can't show a preview", the check still works → Grape leaf blight, Very likely | ✅ |
| 9 | Huge photo (over 10 MB) and a PDF | Clear message | 17.7 MB PNG (4032 × 3024) shrunk in the browser and checked (by design, see PROGRESS); sent straight to the server it gets 413 "The photo is too big. The limit is 10 MB."; PDF → "Not a photo" | ✅ |
| 10 | Internet off during a check | "No internet", no crash | "No internet" message; back online, the same photo checks fine | ✅ |
| 11 | Check right after starting the back end (model still loading) | "SafeCrop is starting", then it works | "SafeCrop is starting" (503); the same photo worked once the model was loaded | ✅ |
| 12 | Gemini key broken | Fallback advice; result still shown | Fallback advice from `diseases.json` (`client_error`) in 0.3–0.6 s, marked "From SafeCrop's checked facts"; result shown | ✅ |
| 13 | Refresh on `/result/…`, `/history`, `/diseases/…`, `/diseases`, `/profile`, unknown address | Page loads (no 404) | All load; unknown address → "Page not found" page | ✅ |
| 14 | History: open, delete one, clear all, reload | Works, stays right after reload | Open → saved result (no server call); delete 5 → 4; clear all with in-page "Yes, delete all" → 0; reload → "No checks yet. Check your first leaf." | ✅ |
| 15 | Profile: save name and language, reload | Name in greeting; settings kept | "Saved"; home says "Good evening, Nabil"; Bangla still chosen after reload | ✅ |
| 16 | 3 checks at the same time | All finish; nothing crashes | All 3 right (HTTP 200) in 2.2 s together (2.08 / 2.10 / 2.20 s each, vs 0.8 s alone) | ✅ |
| 17 | Page widths 390 / 820 / 1366 / 1920 px | No sideways scrolling | 8 pages × 4 widths: no sideways scrolling anywhere | ✅ |
| 18 | Keyboard only (Tab) | Every button reachable, focus visible | Home 24, Check 23, History 23, Profile 25 Tab stops; focus outline visible on every one | ✅ |
| 19 | Search the built front end and the repo for keys | Not found | 0 keys in the whole git history, 0 in tracked files, 0 in the built front end; `backend/.env` is git-ignored | ✅ |
| 20 | Back-end `pytest` | All pass | 140 / 140 (128 s, model loaded once, Gemini faked) | ✅ |

Also checked on 26 Nov: CORS answers only `http://localhost:5173` (another site gets no permission header); the same
advice asked twice comes from the cache (second answer 0 ms, `cached: true`, no second Gemini call); no browser console
errors or warnings in any run.

**Not run:** Lighthouse (Chrome DevTools → Lighthouse → Accessibility) on the home and result pages — Nabil, 2 minutes.

Bugs found: none in the app. Polish done on 26 Nov: a tab title for every page ("Potato late blight · SafeCrop"),
"Use camera" shown only on touch screens (on a laptop it opened the same file picker as "Upload a photo"), the Result
page's buttons one per row on wide screens ("Learn about this disease" no longer breaks in two).

## Real-photo test (Day 6 Block A) — not run yet

The only fair new test of the app model. Rules: the true label of every photo is written **before** running it; the
cut-offs in `backend/models/thresholds.json` are **not** changed after seeing the results; `backend/safecrop.db` is
deleted first so the log counts only these photos. **Since 26 Nov** (Gemini can override CLIP): keep
`LEARN_FROM_GEMINI=false` in `backend/.env`, and run `python scripts/undo_added.py --list` first: it must say 0 rows
(else `--all`), so no photo is matched against a fingerprint saved from an earlier photo.

Each row has three answers, so we can count which one was right more often. CLIP's answer = the picture comparison
(`label` in the log), Gemini's answer = its own label and words (`gemini_label`, `gemini_name`, `gemini_sure`), final =
what the farmer saw (`final_label`). "Right?" uses the true label; a photo of something not in our 8 counts as right when
the answer is "not in our list" / "not sure" (not one of our 8 by mistake).

| # | Photo | True label (written before) | CLIP's answer (decision, vote) | CLIP right? | Gemini's answer (label, words, how sure) | Gemini agrees? | Gemini right? | Final answer (source) | Final right? | Photo check (problem, level) | Time (s) |
|---|-------|-----------------------------|--------------------------------|-------------|-------------------------------------------|----------------|---------------|-----------------------|--------------|------------------------------|----------|
| | | | | | | | | | | | |

Summary (fill in), of __ photos:

| | Right | Wrong | Not sure |
|---|---|---|---|
| CLIP alone | | | |
| Gemini alone | | | |
| Final (CLIP + Gemini rule) | | | |

Also count: Gemini said "no" on __ photos; of these CLIP was wrong on __ (Gemini caught it) and right on __ (Gemini
overrode a right answer). Photo check warned on __. Compare CLIP vs final on the same photos with McNemar counts
(CLIP right & final wrong vs CLIP wrong & final right), not just the two percentages.

The 26 Nov evening checks (before this change, not labelled in advance) are an informal first look, not this test:
CLIP said "Very likely" (vote 100%) on 5 photos: rice stem borer ×2, black gram yellow mosaic ×3 (log rows
16:23–16:45). Nabil says the photos shown were neither. Gemini said "no" on 4 of the 5 (it agreed on the 16:42 one).
The "dry grass head" photo passed the "not a leaf" cut by 0.0006 (best similarity 0.7606 vs 0.7602).
