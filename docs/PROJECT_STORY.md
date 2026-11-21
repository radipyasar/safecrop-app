# SafeCrop — the project story so far (up to 17 Nov 2026)

## The question

Can AI recognise crop diseases from **noisy phone photos** (blur, grain, darkness, compression) the way
farmers actually take them? And does it work as well for **info-scarce** diseases (little written about
them online) as for **info-rich** ones?

## The 8 diseases (4 crops from abroad, 4 local to Bangladesh)

| Group | Disease | Crop | Photo source (licence) |
| --- | --- | --- | --- |
| A, info-rich | Potato late blight | Potato | PlantVillage (CC BY-SA 3.0) |
| A, info-rich | Apple scab | Apple | AppleLeaf9 (CC BY 4.0) |
| A, info-rich | Rice stem borer (insect pest, not a disease) | Rice | Mendeley hnfjs42d5g (CC BY 4.0) |
| A, info-rich | Black gram yellow mosaic (added Nov 2026) | Black gram | Mendeley z55yrbmn2d IDBGL (CC BY 4.0) |
| B, info-scarce | Pear leaf spot | Pear | DiaMOS Plant (CC BY 4.0) |
| B, info-scarce | Grape leaf blight | Grape | PlantVillage (CC BY-SA 3.0) |
| B, info-scarce | Jute mosaic | Jute | Harvard Dataverse doi:10.7910/DVN/FJ1DM1 (CC0) |
| B, info-scarce | Jute dieback | Jute | Harvard Dataverse doi:10.7910/DVN/FJ1DM1 (CC0) |

Test set: 30 photos per disease. Each photo exists at **L0** (clean) and three noise levels **L1, L2, L3**
(L3 = severe), with one of 5 noise types: sensor noise (grain), hand-shake blur, out of focus, low light,
compression. 7 diseases → 840 images; black gram adds 120 → 960. Extra: 240 PlantVillage pictures of
4 look-alike diseases and 3 healthy leaves.

## Timeline

| When | What happened | Key number |
| --- | --- | --- |
| Oct | Chose the diseases and groups; field trip 20–22 Oct to collect real photos | — |
| Step 2 | Compared CLIP zero-shot, the CLIP "database" (5 most similar clean photos vote), plain Gemini 3.5 Flash-Lite | L3: database 40.0%, plain Gemini 12.9%, zero-shot 3.8% |
| Step 2b | Gemini + 5 reference photos from the database + descriptions | L3 47.1% (best before fine-tuning) |
| Week 8 | Fairness tests: same 7 choices → plain Gemini 41% ≈ database 40% at L3; healthy photos in the database pulled 73% of L3 photos to "healthy" (40% → 15%) | — |
| Week 8 | Fixing L3 photos by editing them (brighten, zoom, CLAHE…) mostly hurt; only "resample" helped compressed photos (57% → 79%) | — |
| Week 8 | Photo check (16 measurements + random forest): problem right 97.7%, level right 92.0% | — |
| 9 Nov | Noisy album (supervisor's idea: compare noisy photos with noisy pictures). Idea 2 = one album per noise type and level, picked by the photo check | Filled album L3: 15.2% → 85.7%; our 7: 40.0% → 93.8% |
| 8–11 Nov | Fine-tuning kit and experiments E0–E4 (repo `NabilRafi/SafeCrop`) | E4 L3 97.1% |
| 11 Nov | Recipe B: same photos, noise made a different way, same strength — the robustness test | E4 L3 85.2% (best) |
| 15 Nov | Week 9 update; React home page built (sample data, no back end) | — |
| 17–30 Nov | Build the full web app (this repo) — see `docs/ROUTINE.md` | — |

## The experiments E0–E4 (all CLIP ViT-L/14, 5 folds by photo)

| ID | What it is | Test images L0/L1/L2/L3 (All) | Recipe B L3 (All) |
| --- | --- | --- | --- |
| E0 | Frozen CLIP database (= Step 2, recomputed; 0 of 840 answers changed) | 100 / 93.3 / 71.9 / 40.0 (76.3) | 30.5 (67.9) |
| — | Gemini + references (Step 2b) | 100 / 92.9 / 75.2 / 47.1 (78.8) | not run |
| E1 | Frozen CLIP + 3,150 noisy copies in the database | 100 / 100 / 99.0 / 95.2 (98.6) | 67.1 (88.8) |
| E2 | RBF SVM on frozen features, trained on clean + noisy copies | 100 / 99.5 / 99.0 / 97.6 (99.0) | 78.1 (93.5) |
| E3 database | Fine-tuned CLIP (last 4 blocks + projection), database vote | 100 / 100 / 99.5 / 93.8 (98.3) | 73.8 (91.9) |
| E3 head | Fine-tuned CLIP, its own classifier | 100 / 100 / 99.5 / 95.2 (98.7) | 79.5 (94.2) |
| **E4** | **E3 + fine-tuned noisy copies in the database** | 100 / 100 / 99.5 / **97.1** (99.2) | **85.2 (95.4)** |

- E3/E4 settings (only 1 setting tried): 15 epochs, 16 photos per step (1 clean + 1 noisy view), AdamW lr 1e-5
  (head 1e-3), weight decay 0.05, cosine schedule, loss = cross-entropy + 1.0 × (1 − cos(noisy, clean)).
  Free Colab T4: E3 ~95 s per fold, E4 ~160 s (with black gram ~122 / ~278 s).
- On the test images all of E1–E4 beat frozen CLIP and Gemini + references at L3 (p < 0.001) but not each other.
- **Recipe B separates them:** E4 beats the SVM 28 / 13 (p = 0.028), E3 head 19 / 7 (p = 0.029), E1 44 / 6.
  E1 dropped most (−28.6 points): it had partly learned the test noise itself.
- On recipe B the info-rich vs info-scarce gap returns: E4 L3 group A 95.3% vs group B 78.4% (Fisher p = 0.0006);
  weakest is jute mosaic (53.3%).
- Black gram at L3: E4 90.0% on test images, 76.7% on recipe B. Adding it didn't change the old 840 answers.
- Images with no correct disease among the 5 neighbours at L3: frozen 81, E1 1, E3 9, E4 3 (of 210).

**Decision for the app: use E4** (fine-tuned CLIP + noisy copies in the database) — the most robust method.

## Decisions and lessons that shape the app

- A clearer photo beats any automatic fix, so the app warns and offers a retake instead of editing photos
  (except resample for blocky photos, if it still helps E4 — checked on Day 2).
- Healthy / look-alike pictures must be in the database (with noisy copies) so the app can say "healthy" or
  "not in our list" — but they can lower accuracy a little; measure it on fold 0 (Day 2).
- Gemini is good at explaining, not proven as the classifier with fine-tuned neighbours (E5 not run yet).
- Everything is free and needs no card.

## Known limits (say these in reports)

- Noise is computer-made, one problem per photo; real phone photos are not tested yet.
- Each disease comes from one photo source, so CLIP can partly match photo style.
- Only default fine-tuning settings were tried; black gram rests on 30 photos.
- 210 images per level → about ±7 points of chance variation; use McNemar counts, not just accuracy gaps.

## Deadlines

- Week 10 update: Sun 22 Nov 2026 (supervisor wants tables and numbers; shows work up to Day 3).
- Week 11 update: Mon 30 Nov 2026 (working app + demo video).
- Week 12: Sun 6 Dec 2026 — final presentation, live demo, 8-page report.

## Links

- Research repo (code, data, all results): https://github.com/NabilRafi/SafeCrop
- Colab notebooks folder: https://drive.google.com/drive/folders/1AaxAU0TmKNfnX91Npf2VMP0BXc1YowJ6
- Dataset folder: https://drive.google.com/drive/folders/1q3rB5OeE9UBq9kQnvbbMCx996hbczyhh
- Fine-tuning runner zips: https://drive.google.com/drive/folders/1EB43yD0e2c-kHmsbk46l89na6bvFMeMB
- Full result tables: `docs/results/finetune-results.md`, `docs/results/noisy-album-idea2.md`
