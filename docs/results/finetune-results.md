# SafeCrop – CLIP fine-tuning results (E0–E4, black gram, recipe B), 11 Nov 2026

**Source:** GitHub repo https://github.com/NabilRafi/SafeCrop (public), one commit `d22d192` (11 Nov 2026, 22:25 Dhaka time):
the fine-tuning kit with its code, `CLAUDE.md`, docs, the 840 test images, the 240 PlantVillage extras, the 120 black gram
images and every run. All tables below are copied from the repo's result files (`results/compare_*.md`,
`results/robustness_20261111_8diseases.md`, `results/runs.csv`, the run summaries). The headline numbers were recounted
from the per-image prediction files on 11 Nov and all matched.

**How to read the numbers.** % correct. L0 = clean, L1 mild, L2 medium, L3 severe noise. "Test recipe" = the noise
used to make the 840 test images. "Recipe B" = the same photos with the noise made a different way (a robustness
test). "Only new right / only baseline right" = images one method gets right and the other gets wrong; p = McNemar
exact test (p < 0.05 = a real difference, not luck). Group A = info-rich diseases, group B = info-scarce.

## In short

- **On the usual test images every method that saw noisy copies is near the top.** At L3: E2 SVM 97.6, E4 97.1,
  E1 95.2, E3 head 95.2, E3 database 93.8, against 40.0 for the frozen CLIP database and 47.1 for Gemini + references
  (all p < 0.001). Among themselves they can't be told apart: E4 vs E1 6 / 2 (p = 0.29), E4 vs SVM 2 / 3 (p = 1.0).
  Only about 10 L3 images are still wrong, so this test set has run out of room.
- **Recipe B separates them.** At L3 (old 7 diseases): E4 85.2 > E3 head 79.5 ≈ SVM 78.1 > E3 database 73.8 > E1 67.1
  > frozen 30.5. E4 beats the SVM 28 / 13 (p = 0.028) and E1 44 / 6 (p < 0.001). So **fine-tuning + noisy copies (E4)
  is the most robust**; noisy copies alone (E1) had partly learned the test recipe itself (the biggest drop, −28.6).
- **Black gram (8th disease) did not change the old 840 results** (every method within 3 images, all p ≥ 0.25).
  Black gram at L3 (30 images): SVM 96.7, E3 head 93.3, E1 90.0, E4 90.0, E3 database 80.0, frozen 6.7.
- **On recipe B the info-rich vs info-scarce gap comes back:** E4 at L3, group A 95.3% (81/85) vs group B 78.4%
  (98/125), Fisher p = 0.0006; mostly jute mosaic (53%).
- **Only one setting was tried** (the defaults). Not done yet: E5 (Gemini + fine-tuned neighbours), E6 (healthy /
  look-alike negatives, more photos per disease), real phone photos.

## Headline table

| Method | What it is | Test recipe L3 | Test recipe all | Recipe B L3 | Recipe B all | Black gram L3, test → B |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Frozen CLIP database (E0 = Step 2) | 5 most similar clean photos vote; no training | 40.0 | 76.3 | 30.5 | 67.9 | 6.7 → 0.0 |
| Gemini + references (Step 2b) | Gemini sees the database's 5 photos + descriptions | 47.1 | 78.8 | not run | not run | not run |
| E1 frozen + noisy copies | database also holds 3,150 noisy copies of the other photos | 95.2 | 98.6 | 67.1 | 88.8 | 90.0 → 20.0 |
| E2 SVM + noisy copies | RBF SVM on frozen CLIP features, trained on clean + noisy copies | 97.6 | 99.0 | 78.1 | 93.5 | 96.7 → 70.0 |
| E3 fine-tuned, database | fine-tuned CLIP; database vote over clean photos | 93.8 | 98.3 | 73.8 | 91.9 | 80.0 → 63.3 |
| E3 fine-tuned, head | fine-tuned CLIP; its own classifier | 95.2 | 98.7 | 79.5 | 94.2 | 93.3 → 73.3 |
| E4 fine-tuned + noisy copies | fine-tuned CLIP; database with fine-tuned noisy copies | **97.1** | **99.2** | **85.2** | **95.4** | 90.0 → 76.7 |

Test-recipe columns: the 7-choice runs on the 840 images. Recipe B columns: the 8-choice runs, scored on the old 7
diseases' 840 recipe-B images (the same 8-choice runs on the test recipe gave L3: frozen 40.0, E1 95.7, SVM 97.1,
E3 database 92.4, E3 head 94.3, E4 96.7; the test → recipe B drops below use these). Black gram: its 30 L3 images.

## What was run

| ID | Method | Details |
| --- | --- | --- |
| E0 | Frozen ViT-L/14 recomputed from the images | Exactly the Step 2 numbers (0 of 840 answers changed). Nabil's laptop, CPU, ~50 min. |
| E1 | Frozen CLIP + noisy copies in the database | 210 clean photos + 3,150 noisy copies (5 types × L1–L3, seed 2026), leave-one-photo-out, k = 5. Same design as the noisy album's Idea 1 (same L3 result, 95.2). Share of the 5 neighbours that are copies: L0 4%, L3 100%. |
| E2 | RBF SVM on frozen features, clean + noisy copies | 5 folds by photo; C chosen inside the training photos (7 diseases: 100 / 10 / 1 / 10 / 100 per fold; 8 diseases: 10 in every fold). |
| E3 | Fine-tuned CLIP | Last 4 of 24 blocks + final norm + projection trained; 15 epochs; 16 photos per step (1 clean + 1 noisy view, L1–L3, flips / quarter turns); AdamW lr 1e-5 (head 1e-3), weight decay 0.05, 1 warm-up epoch, cosine schedule; loss = cross-entropy + 1.0 × (1 − cos(noisy, own clean)). Two predictors: "database" (Step 2 vote with fine-tuned embeddings of clean photos) and "head" (cosine classifier, scale 30). |
| E4 | E3 + fine-tuned noisy copies in the database | `--set finetune.db_noisy_copies=true` |
| Sanity | E3 with 0 epochs, fold 0 | Gives exactly the frozen database's answers (0 fixed / 0 broken on 168 images). |
| E7 | Recipe B robustness test | Nothing retrained: every method learned only from the test recipe, then was scored on recipe B. |

- **Settings tried: 1 (the defaults).** Fold 0 first (168 images), then all 5 folds once.
- **Time on a free Colab T4:** E3 ~95 s per fold, E4 ~160 s per fold (7 diseases); with black gram E3 ~122 s, E4 ~278 s
  per fold (one training per fold scored both test sets).
- 5 folds by photo (42 photos per fold; black gram has its own folds, 6 photos each, every noise type in every fold), so
  every image is scored by a model that never saw its photo.

## 1. Test recipe, 7 diseases (840 images): the comparable numbers

### Accuracy by noise level (% correct)

| Predictor | L0 | L1 | L2 | L3 | All | n |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E1 frozen + noisy copies (database) | 100.0 | 100.0 | 99.0 | 95.2 | 98.6 | 840 |
| E2 SVM, frozen + noisy copies | 100.0 | 99.5 | 99.0 | 97.6 | 99.0 | 840 |
| E3 fine-tuned (database) | 100.0 | 100.0 | 99.5 | 93.8 | 98.3 | 840 |
| E3 fine-tuned (head) | 100.0 | 100.0 | 99.5 | 95.2 | 98.7 | 840 |
| E4 fine-tuned + noisy copies (database) | 100.0 | 100.0 | 99.5 | 97.1 | 99.2 | 840 |
| CLIP database, frozen (Step 2) | 100.0 | 93.3 | 71.9 | 40.0 | 76.3 | 840 |
| Gemini + references + descriptions (Step 2b) | 100.0 | 92.9 | 75.2 | 47.1 | 78.8 | 840 |
| Gemini plain, 33 options (Step 2) | 66.7 | 48.6 | 26.2 | 12.9 | 38.6 | 840 |
| CLIP zero-shot, 33 options (Step 2) | 25.7 | 15.2 | 8.6 | 3.8 | 13.3 | 840 |

### Info-rich (A) vs info-scarce (B) (% correct)

| Predictor | A all | A L3 | B all | B L3 |
| --- | ---: | ---: | ---: | ---: |
| E1 frozen + noisy copies (database) | 98.8 | 95.3 | 98.4 | 95.2 |
| E2 SVM, frozen + noisy copies | 99.4 | 97.6 | 98.8 | 97.6 |
| E3 fine-tuned (database) | 98.8 | 95.3 | 98.0 | 92.8 |
| E3 fine-tuned (head) | 98.8 | 95.3 | 98.6 | 95.2 |
| E4 fine-tuned + noisy copies (database) | 99.4 | 97.6 | 99.0 | 96.8 |
| CLIP database, frozen (Step 2) | 81.2 | 48.2 | 73.0 | 34.4 |
| Gemini + references + descriptions (Step 2b) | 80.6 | 48.2 | 77.6 | 46.4 |
| Gemini plain, 33 options (Step 2) | 54.7 | 29.4 | 27.6 | 1.6 |
| CLIP zero-shot, 33 options (Step 2) | 9.1 | 3.5 | 16.2 | 4.0 |

### By noise type, L3 (% correct)

| Predictor | Sensor noise | Hand-shake blur | Out of focus | Low light | Compression |
| --- | ---: | ---: | ---: | ---: | ---: |
| E1 frozen + noisy copies (database) | 85.7 | 100.0 | 95.2 | 100.0 | 95.2 |
| E2 SVM, frozen + noisy copies | 92.9 | 100.0 | 100.0 | 100.0 | 95.2 |
| E3 fine-tuned (database) | 88.1 | 97.6 | 90.5 | 97.6 | 95.2 |
| E3 fine-tuned (head) | 92.9 | 100.0 | 90.5 | 97.6 | 95.2 |
| E4 fine-tuned + noisy copies (database) | 92.9 | 100.0 | 97.6 | 97.6 | 97.6 |
| CLIP database, frozen (Step 2) | 26.2 | 33.3 | 28.6 | 54.8 | 57.1 |
| Gemini + references + descriptions (Step 2b) | 31.0 | 52.4 | 38.1 | 52.4 | 61.9 |
| Gemini plain, 33 options (Step 2) | 9.5 | 14.3 | 14.3 | 4.8 | 21.4 |
| CLIP zero-shot, 33 options (Step 2) | 4.8 | 0.0 | 0.0 | 11.9 | 2.4 |

### By noise type, L1-L3 (% correct)

| Predictor | Sensor noise | Hand-shake blur | Out of focus | Low light | Compression |
| --- | ---: | ---: | ---: | ---: | ---: |
| E1 frozen + noisy copies (database) | 95.2 | 100.0 | 97.6 | 99.2 | 98.4 |
| E2 SVM, frozen + noisy copies | 97.6 | 100.0 | 97.6 | 100.0 | 98.4 |
| E3 fine-tuned (database) | 96.0 | 99.2 | 96.0 | 99.2 | 98.4 |
| E3 fine-tuned (head) | 97.6 | 100.0 | 96.0 | 99.2 | 98.4 |
| E4 fine-tuned + noisy copies (database) | 97.6 | 100.0 | 98.4 | 99.2 | 99.2 |
| CLIP database, frozen (Step 2) | 61.1 | 70.6 | 61.9 | 70.6 | 77.8 |
| Gemini + references + descriptions (Step 2b) | 61.1 | 78.6 | 65.9 | 69.0 | 84.1 |
| Gemini plain, 33 options (Step 2) | 25.4 | 34.9 | 26.2 | 19.0 | 40.5 |
| CLIP zero-shot, 33 options (Step 2) | 5.6 | 9.5 | 7.1 | 16.7 | 7.1 |

### Against the frozen database (Step 2) and Gemini + references (Step 2b), 7-choice runs

| Method | vs frozen, all (only new right / only old right) | vs frozen, L3 | vs Gemini + refs, all | vs Gemini + refs, L3 |
| --- | ---: | ---: | ---: | ---: |
| E1 frozen + noisy copies | 192 / 5 | 120 / 4 | 172 / 6 | 106 / 5 |
| E2 SVM + noisy copies | 194 / 3 | 123 / 2 | 173 / 3 | 108 / 2 |
| E3 fine-tuned, database | 186 / 1 | 114 / 1 | 165 / 1 | 99 / 1 |
| E3 fine-tuned, head | 189 / 1 | 117 / 1 | 168 / 1 | 102 / 1 |
| E4 fine-tuned + noisy copies | 193 / 1 | 121 / 1 | 172 / 1 | 106 / 1 |

All p < 0.001.

### Fine-tuned vs E1 (frozen + noisy copies)

#### Head to head (McNemar exact test)

| New | Baseline | Levels | Images | Only new right | Only baseline right | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E3 fine-tuned (database) | E1 frozen + noisy copies (database) | All | 840 | 6 | 8 | 0.791 |
| E3 fine-tuned (database) | E1 frozen + noisy copies (database) | L3 | 210 | 5 | 8 | 0.581 |
| E3 fine-tuned (head) | E1 frozen + noisy copies (database) | All | 840 | 7 | 6 | 1.000 |
| E3 fine-tuned (head) | E1 frozen + noisy copies (database) | L3 | 210 | 6 | 6 | 1.000 |
| E4 fine-tuned + noisy copies (database) | E1 frozen + noisy copies (database) | All | 840 | 7 | 2 | 0.180 |
| E4 fine-tuned + noisy copies (database) | E1 frozen + noisy copies (database) | L3 | 210 | 6 | 2 | 0.289 |

### Fine-tuned vs E2 (SVM)

#### Head to head (McNemar exact test)

| New | Baseline | Levels | Images | Only new right | Only baseline right | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E3 fine-tuned (database) | E2 SVM, frozen + noisy copies | All | 840 | 4 | 10 | 0.180 |
| E3 fine-tuned (database) | E2 SVM, frozen + noisy copies | L3 | 210 | 2 | 10 | 0.039 |
| E3 fine-tuned (head) | E2 SVM, frozen + noisy copies | All | 840 | 4 | 7 | 0.549 |
| E3 fine-tuned (head) | E2 SVM, frozen + noisy copies | L3 | 210 | 2 | 7 | 0.180 |
| E4 fine-tuned + noisy copies (database) | E2 SVM, frozen + noisy copies | All | 840 | 4 | 3 | 1.000 |
| E4 fine-tuned + noisy copies (database) | E2 SVM, frozen + noisy copies | L3 | 210 | 2 | 3 | 1.000 |

### E2 (SVM) vs E1

#### Head to head (McNemar exact test)

| New | Baseline | Levels | Images | Only new right | Only baseline right | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E2 SVM, frozen + noisy copies | E1 frozen + noisy copies (database) | All | 840 | 7 | 3 | 0.344 |
| E2 SVM, frozen + noisy copies | E1 frozen + noisy copies (database) | L3 | 210 | 6 | 1 | 0.125 |

### Images with no correct disease among their 5 database neighbours

| Method | L3 (of 210) | All levels (of 840) | Mean correct of 5 at L3 |
| --- | ---: | ---: | ---: |
| Frozen database (E0) | 81 | 122 | 2.0 |
| E1 frozen + noisy copies | 1 | 1 | 4.4 |
| E3 fine-tuned, database | 9 | 10 | 4.6 |
| E4 fine-tuned + noisy copies | 3 | 3 | 4.7 |

The fine-tuned `neighbours.csv` files (Step 2b format) are ready for E5 (Gemini + fine-tuned neighbours).

### L3 images still wrong

| Predictor | Image | True | Predicted | Noise |
| --- | --- | --- | --- | --- |
| E1 frozen + noisy copies (database) | L3/grape_leaf_blight/grape_leaf_blight_003_gaussian_noise_L3.png | grape_leaf_blight | potato_late_blight | gaussian_noise |
| E1 frozen + noisy copies (database) | L3/jute_dieback/jute_dieback_026_jpeg_compression_L3.png | jute_dieback | apple_scab | jpeg_compression |
| E1 frozen + noisy copies (database) | L3/jute_dieback/jute_dieback_030_gaussian_noise_L3.png | jute_dieback | apple_scab | gaussian_noise |
| E1 frozen + noisy copies (database) | L3/pear_leaf_spot/pear_leaf_spot_009_defocus_blur_L3.png | pear_leaf_spot | apple_scab | defocus_blur |
| E1 frozen + noisy copies (database) | L3/pear_leaf_spot/pear_leaf_spot_014_defocus_blur_L3.png | pear_leaf_spot | jute_dieback | defocus_blur |
| E1 frozen + noisy copies (database) | L3/pear_leaf_spot/pear_leaf_spot_022_gaussian_noise_L3.png | pear_leaf_spot | jute_dieback | gaussian_noise |
| E1 frozen + noisy copies (database) | L3/rice_stem_borer/rice_stem_borer_011_gaussian_noise_L3.png | rice_stem_borer | jute_dieback | gaussian_noise |
| E1 frozen + noisy copies (database) | L3/rice_stem_borer/rice_stem_borer_012_gaussian_noise_L3.png | rice_stem_borer | jute_dieback | gaussian_noise |
| E1 frozen + noisy copies (database) | L3/rice_stem_borer/rice_stem_borer_027_gaussian_noise_L3.png | rice_stem_borer | apple_scab | gaussian_noise |
| E1 frozen + noisy copies (database) | L3/rice_stem_borer/rice_stem_borer_028_jpeg_compression_L3.png | rice_stem_borer | jute_dieback | jpeg_compression |
| E2 SVM, frozen + noisy copies | L3/jute_dieback/jute_dieback_026_jpeg_compression_L3.png | jute_dieback | jute_mosaic | jpeg_compression |
| E2 SVM, frozen + noisy copies | L3/jute_dieback/jute_dieback_030_gaussian_noise_L3.png | jute_dieback | apple_scab | gaussian_noise |
| E2 SVM, frozen + noisy copies | L3/rice_stem_borer/rice_stem_borer_027_gaussian_noise_L3.png | rice_stem_borer | apple_scab | gaussian_noise |
| E2 SVM, frozen + noisy copies | L3/rice_stem_borer/rice_stem_borer_028_jpeg_compression_L3.png | rice_stem_borer | jute_dieback | jpeg_compression |
| E2 SVM, frozen + noisy copies | L3/jute_dieback/jute_dieback_005_gaussian_noise_L3.png | jute_dieback | rice_stem_borer | gaussian_noise |
| E3 fine-tuned (database) | L3/apple_scab/apple_scab_012_defocus_blur_L3.png | apple_scab | jute_dieback | defocus_blur |
| E3 fine-tuned (database) | L3/grape_leaf_blight/grape_leaf_blight_028_motion_blur_L3.png | grape_leaf_blight | potato_late_blight | motion_blur |
| E3 fine-tuned (database) | L3/jute_dieback/jute_dieback_026_jpeg_compression_L3.png | jute_dieback | jute_mosaic | jpeg_compression |
| E3 fine-tuned (database) | L3/pear_leaf_spot/pear_leaf_spot_021_defocus_blur_L3.png | pear_leaf_spot | jute_mosaic | defocus_blur |
| E3 fine-tuned (database) | L3/pear_leaf_spot/pear_leaf_spot_027_gaussian_noise_L3.png | pear_leaf_spot | jute_mosaic | gaussian_noise |
| E3 fine-tuned (database) | L3/apple_scab/apple_scab_014_low_light_L3.png | apple_scab | pear_leaf_spot | low_light |
| E3 fine-tuned (database) | L3/apple_scab/apple_scab_030_gaussian_noise_L3.png | apple_scab | jute_dieback | gaussian_noise |
| E3 fine-tuned (database) | L3/jute_dieback/jute_dieback_008_defocus_blur_L3.png | jute_dieback | rice_stem_borer | defocus_blur |
| E3 fine-tuned (database) | L3/jute_dieback/jute_dieback_030_gaussian_noise_L3.png | jute_dieback | apple_scab | gaussian_noise |
| E3 fine-tuned (database) | L3/jute_dieback/jute_dieback_015_gaussian_noise_L3.png | jute_dieback | rice_stem_borer | gaussian_noise |
| E3 fine-tuned (database) | L3/rice_stem_borer/rice_stem_borer_028_jpeg_compression_L3.png | rice_stem_borer | jute_dieback | jpeg_compression |
| E3 fine-tuned (database) | L3/pear_leaf_spot/pear_leaf_spot_014_defocus_blur_L3.png | pear_leaf_spot | jute_dieback | defocus_blur |
| E3 fine-tuned (database) | L3/pear_leaf_spot/pear_leaf_spot_022_gaussian_noise_L3.png | pear_leaf_spot | jute_mosaic | gaussian_noise |
| E3 fine-tuned (head) | L3/apple_scab/apple_scab_012_defocus_blur_L3.png | apple_scab | jute_dieback | defocus_blur |
| E3 fine-tuned (head) | L3/jute_dieback/jute_dieback_026_jpeg_compression_L3.png | jute_dieback | jute_mosaic | jpeg_compression |
| E3 fine-tuned (head) | L3/apple_scab/apple_scab_014_low_light_L3.png | apple_scab | pear_leaf_spot | low_light |
| E3 fine-tuned (head) | L3/apple_scab/apple_scab_030_gaussian_noise_L3.png | apple_scab | jute_dieback | gaussian_noise |
| E3 fine-tuned (head) | L3/jute_dieback/jute_dieback_008_defocus_blur_L3.png | jute_dieback | rice_stem_borer | defocus_blur |
| E3 fine-tuned (head) | L3/jute_dieback/jute_dieback_030_gaussian_noise_L3.png | jute_dieback | rice_stem_borer | gaussian_noise |
| E3 fine-tuned (head) | L3/pear_leaf_spot/pear_leaf_spot_009_defocus_blur_L3.png | pear_leaf_spot | apple_scab | defocus_blur |
| E3 fine-tuned (head) | L3/jute_dieback/jute_dieback_015_gaussian_noise_L3.png | jute_dieback | rice_stem_borer | gaussian_noise |
| E3 fine-tuned (head) | L3/pear_leaf_spot/pear_leaf_spot_030_defocus_blur_L3.png | pear_leaf_spot | jute_dieback | defocus_blur |
| E3 fine-tuned (head) | L3/rice_stem_borer/rice_stem_borer_028_jpeg_compression_L3.png | rice_stem_borer | jute_dieback | jpeg_compression |
| E4 fine-tuned + noisy copies (database) | L3/jute_dieback/jute_dieback_026_jpeg_compression_L3.png | jute_dieback | jute_mosaic | jpeg_compression |
| E4 fine-tuned + noisy copies (database) | L3/apple_scab/apple_scab_014_low_light_L3.png | apple_scab | pear_leaf_spot | low_light |
| E4 fine-tuned + noisy copies (database) | L3/jute_dieback/jute_dieback_030_gaussian_noise_L3.png | jute_dieback | apple_scab | gaussian_noise |
| E4 fine-tuned + noisy copies (database) | L3/pear_leaf_spot/pear_leaf_spot_009_defocus_blur_L3.png | pear_leaf_spot | apple_scab | defocus_blur |
| E4 fine-tuned + noisy copies (database) | L3/rice_stem_borer/rice_stem_borer_027_gaussian_noise_L3.png | rice_stem_borer | jute_dieback | gaussian_noise |
| E4 fine-tuned + noisy copies (database) | L3/pear_leaf_spot/pear_leaf_spot_019_gaussian_noise_L3.png | pear_leaf_spot | jute_dieback | gaussian_noise |

`jute_dieback_026` (compression, L3) is wrong for every method.

## 2. Fold 0 only (the settings check before running all folds)

Images compared: 168 of 840 (folds [0]; all predictors scored them without seeing their photo).
E1 and E2 were run on all 840 images; here they are cut to the same fold-0 images.

### Accuracy by noise level (% correct)

| Predictor | L0 | L1 | L2 | L3 | All | n |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E1 frozen + noisy copies (database) | 100.0 | 100.0 | 100.0 | 95.2 | 98.8 | 168 |
| E2 SVM, frozen + noisy copies | 100.0 | 97.6 | 97.6 | 97.6 | 98.2 | 168 |
| E3 fine-tuned (database) | 100.0 | 100.0 | 100.0 | 88.1 | 97.0 | 168 |
| E3 fine-tuned (head) | 100.0 | 100.0 | 100.0 | 95.2 | 98.8 | 168 |
| E4 fine-tuned + noisy copies (database) | 100.0 | 100.0 | 100.0 | 97.6 | 99.4 | 168 |
| CLIP database, frozen (Step 2) | 100.0 | 92.9 | 76.2 | 35.7 | 76.2 | 168 |
| Gemini + references + descriptions (Step 2b) | 100.0 | 92.9 | 81.0 | 40.5 | 78.6 | 168 |
| Gemini plain, 33 options (Step 2) | 64.3 | 42.9 | 16.7 | 9.5 | 33.3 | 168 |
| CLIP zero-shot, 33 options (Step 2) | 31.0 | 16.7 | 7.1 | 7.1 | 15.5 | 168 |

### Fine-tuned vs E1 (frozen + noisy copies)

#### Head to head (McNemar exact test)

| New | Baseline | Levels | Images | Only new right | Only baseline right | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E3 fine-tuned (database) | E1 frozen + noisy copies (database) | All | 168 | 1 | 4 | 0.375 |
| E3 fine-tuned (database) | E1 frozen + noisy copies (database) | L3 | 42 | 1 | 4 | 0.375 |
| E3 fine-tuned (head) | E1 frozen + noisy copies (database) | All | 168 | 1 | 1 | 1.000 |
| E3 fine-tuned (head) | E1 frozen + noisy copies (database) | L3 | 42 | 1 | 1 | 1.000 |
| E4 fine-tuned + noisy copies (database) | E1 frozen + noisy copies (database) | All | 168 | 1 | 0 | 1.000 |
| E4 fine-tuned + noisy copies (database) | E1 frozen + noisy copies (database) | L3 | 42 | 1 | 0 | 1.000 |

### Fine-tuned vs E2 (SVM)

#### Head to head (McNemar exact test)

| New | Baseline | Levels | Images | Only new right | Only baseline right | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E3 fine-tuned (database) | E2 SVM, frozen + noisy copies | All | 168 | 2 | 4 | 0.688 |
| E3 fine-tuned (database) | E2 SVM, frozen + noisy copies | L3 | 42 | 0 | 4 | 0.125 |
| E3 fine-tuned (head) | E2 SVM, frozen + noisy copies | All | 168 | 2 | 1 | 1.000 |
| E3 fine-tuned (head) | E2 SVM, frozen + noisy copies | L3 | 42 | 0 | 1 | 1.000 |
| E4 fine-tuned + noisy copies (database) | E2 SVM, frozen + noisy copies | All | 168 | 2 | 0 | 0.500 |
| E4 fine-tuned + noisy copies (database) | E2 SVM, frozen + noisy copies | L3 | 42 | 0 | 0 | 1.000 |

### E2 (SVM) vs E1

#### Head to head (McNemar exact test)

| New | Baseline | Levels | Images | Only new right | Only baseline right | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E2 SVM, frozen + noisy copies | E1 frozen + noisy copies (database) | All | 168 | 1 | 2 | 1.000 |
| E2 SVM, frozen + noisy copies | E1 frozen + noisy copies (database) | L3 | 42 | 1 | 0 | 1.000 |

## 3. Black gram yellow mosaic as an 8th disease (960 images)

Black gram: 30 photos (group A, Local, index 0.65), 6 per noise type, its own folds; added as an extension
(`data/images_black_gram/`, `data/manifest_black_gram.csv`; recipe check 88/90 noisy images identical, 90/90 within
1 grey level). Score with `--set black_gram=true`. The 840 old files, `data/manifest.csv` and their folds are unchanged.

### Old 840 images, 8 choices (comparable images; the methods could also answer black gram)

#### Accuracy by noise level (% correct)

| Predictor | L0 | L1 | L2 | L3 | All | n |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E0 frozen database [8 diseases] | 100.0 | 93.3 | 71.9 | 40.0 | 76.3 | 840 |
| E0 CLIP zero-shot (33 options) [8 diseases] | 25.7 | 15.2 | 8.6 | 3.8 | 13.3 | 840 |
| E1 frozen + noisy copies [8 diseases] | 100.0 | 100.0 | 98.6 | 95.7 | 98.6 | 840 |
| E2 SVM + noisy copies [8 diseases] | 99.5 | 99.5 | 98.6 | 97.1 | 98.7 | 840 |
| E3 fine-tuned, database [8 diseases] | 100.0 | 100.0 | 99.5 | 92.4 | 98.0 | 840 |
| E3 fine-tuned, head [8 diseases] | 100.0 | 100.0 | 99.5 | 94.3 | 98.5 | 840 |
| E4 fine-tuned + noisy copies [8 diseases] | 100.0 | 100.0 | 99.0 | 96.7 | 98.9 | 840 |
| CLIP database, frozen (Step 2) | 100.0 | 93.3 | 71.9 | 40.0 | 76.3 | 840 |
| Gemini + references + descriptions (Step 2b) | 100.0 | 92.9 | 75.2 | 47.1 | 78.8 | 840 |

#### Info-rich (A) vs info-scarce (B) (% correct)

| Predictor | A all | A L3 | B all | B L3 |
| --- | ---: | ---: | ---: | ---: |
| E0 frozen database [8 diseases] | 81.2 | 48.2 | 73.0 | 34.4 |
| E0 CLIP zero-shot (33 options) [8 diseases] | 9.1 | 3.5 | 16.2 | 4.0 |
| E1 frozen + noisy copies [8 diseases] | 98.8 | 95.3 | 98.4 | 96.0 |
| E2 SVM + noisy copies [8 diseases] | 99.4 | 97.6 | 98.2 | 96.8 |
| E3 fine-tuned, database [8 diseases] | 98.5 | 94.1 | 97.6 | 91.2 |
| E3 fine-tuned, head [8 diseases] | 97.9 | 91.8 | 98.8 | 96.0 |
| E4 fine-tuned + noisy copies [8 diseases] | 98.8 | 96.5 | 99.0 | 96.8 |
| CLIP database, frozen (Step 2) | 81.2 | 48.2 | 73.0 | 34.4 |
| Gemini + references + descriptions (Step 2b) | 80.6 | 48.2 | 77.6 | 46.4 |

(The 8-choice noise-type and Step 2 / 2b McNemar tables differ from the 7-choice ones by at most 3 images per method; full tables in `results/compare_20261111_8diseases.md`.)

### Black gram yellow mosaic only (30 photos, 120 images)

#### Accuracy by noise level (% correct)

| Predictor | L0 | L1 | L2 | L3 | All | n |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E0 frozen database | 100.0 | 66.7 | 20.0 | 6.7 | 48.3 | 120 |
| E0 CLIP zero-shot (33 options) | 0.0 | 3.3 | 6.7 | 10.0 | 5.0 | 120 |
| E1 frozen + noisy copies | 100.0 | 96.7 | 86.7 | 90.0 | 93.3 | 120 |
| E2 SVM + noisy copies | 100.0 | 100.0 | 100.0 | 96.7 | 99.2 | 120 |
| E3 fine-tuned, database | 100.0 | 96.7 | 93.3 | 80.0 | 92.5 | 120 |
| E3 fine-tuned, head | 100.0 | 96.7 | 96.7 | 93.3 | 96.7 | 120 |
| E4 fine-tuned + noisy copies | 100.0 | 96.7 | 96.7 | 90.0 | 95.8 | 120 |

#### By noise type, L3 (% correct)

| Predictor | Sensor noise | Hand-shake blur | Out of focus | Low light | Compression |
| --- | ---: | ---: | ---: | ---: | ---: |
| E0 frozen database | 0.0 | 0.0 | 0.0 | 0.0 | 33.3 |
| E0 CLIP zero-shot (33 options) | 16.7 | 0.0 | 0.0 | 0.0 | 33.3 |
| E1 frozen + noisy copies | 50.0 | 100.0 | 100.0 | 100.0 | 100.0 |
| E2 SVM + noisy copies | 100.0 | 100.0 | 100.0 | 83.3 | 100.0 |
| E3 fine-tuned, database | 16.7 | 100.0 | 83.3 | 100.0 | 100.0 |
| E3 fine-tuned, head | 66.7 | 100.0 | 100.0 | 100.0 | 100.0 |
| E4 fine-tuned + noisy copies | 50.0 | 100.0 | 100.0 | 100.0 | 100.0 |

#### By noise type, L1-L3 (% correct)

| Predictor | Sensor noise | Hand-shake blur | Out of focus | Low light | Compression |
| --- | ---: | ---: | ---: | ---: | ---: |
| E0 frozen database | 27.8 | 22.2 | 27.8 | 0.0 | 77.8 |
| E0 CLIP zero-shot (33 options) | 16.7 | 0.0 | 5.6 | 0.0 | 11.1 |
| E1 frozen + noisy copies | 72.2 | 94.4 | 94.4 | 94.4 | 100.0 |
| E2 SVM + noisy copies | 100.0 | 100.0 | 100.0 | 94.4 | 100.0 |
| E3 fine-tuned, database | 55.6 | 100.0 | 94.4 | 100.0 | 100.0 |
| E3 fine-tuned, head | 77.8 | 100.0 | 100.0 | 100.0 | 100.0 |
| E4 fine-tuned + noisy copies | 72.2 | 100.0 | 100.0 | 100.0 | 100.0 |

### Did adding black gram as an 8th choice change the old 840 images? (McNemar, same images)

| Method | Levels | 7 diseases % | 8 diseases % | Change | Only 8 right | Only 7 right | p | Old images called black gram |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E0 frozen database | L3 | 40.0 | 40.0 | 0.0 | 0 | 0 | 1.000 |  |
| E0 frozen database | All | 76.3 | 76.3 | 0.0 | 0 | 0 | 1.000 | 0 |
| E0 CLIP zero-shot (33 options) | L3 | 3.8 | 3.8 | 0.0 | 0 | 0 | 1.000 |  |
| E0 CLIP zero-shot (33 options) | All | 13.3 | 13.3 | 0.0 | 0 | 0 | 1.000 | 14 |
| E1 frozen + noisy copies | L3 | 95.2 | 95.7 | 0.5 | 1 | 0 | 1.000 |  |
| E1 frozen + noisy copies | All | 98.6 | 98.6 | 0.0 | 1 | 1 | 1.000 | 4 |
| E2 SVM + noisy copies | L3 | 97.6 | 97.1 | -0.5 | 0 | 1 | 1.000 |  |
| E2 SVM + noisy copies | All | 99.0 | 98.7 | -0.3 | 0 | 3 | 0.250 | 4 |
| E3 fine-tuned, database | L3 | 93.8 | 92.4 | -1.4 | 0 | 3 | 0.250 |  |
| E3 fine-tuned, database | All | 98.3 | 98.0 | -0.3 | 0 | 3 | 0.250 | 0 |
| E3 fine-tuned, head | L3 | 95.2 | 94.3 | -0.9 | 1 | 3 | 0.625 |  |
| E3 fine-tuned, head | All | 98.7 | 98.5 | -0.2 | 1 | 3 | 0.625 | 2 |
| E4 fine-tuned + noisy copies | L3 | 97.1 | 96.7 | -0.4 | 0 | 1 | 1.000 |  |
| E4 fine-tuned + noisy copies | All | 99.2 | 98.9 | -0.3 | 0 | 2 | 0.500 | 0 |

### Mistakes involving black gram (all levels)

| Method | Black gram wrong (of 120) | Black gram called (top 3) | Old images called black gram (by true disease) |
| --- | ---: | ---: | ---: |
| E0 frozen database | 62 | jute_mosaic 26; rice_stem_borer 23; apple_scab 8 | - |
| E0 CLIP zero-shot (33 options) | 114 | apple_alternaria_leaf_spot 64; pear_leaf_spot 12; jute_healthy 10 | jute_dieback 5; jute_mosaic 5; pear_leaf_spot 3 |
| E1 frozen + noisy copies | 8 | jute_mosaic 3; jute_dieback 2; pear_leaf_spot 2 | jute_mosaic 2; jute_dieback 1; pear_leaf_spot 1 |
| E2 SVM + noisy copies | 1 | jute_dieback 1 | jute_dieback 2; rice_stem_borer 1; pear_leaf_spot 1 |
| E3 fine-tuned, database | 9 | jute_mosaic 6; grape_leaf_blight 1; apple_scab 1 | - |
| E3 fine-tuned, head | 4 | jute_mosaic 4 | apple_scab 1; jute_dieback 1 |
| E4 fine-tuned + noisy copies | 5 | jute_mosaic 3; pear_leaf_spot 1; jute_dieback 1 | - |

## 4. Recipe B: the robustness test (E7)

Why: on the test recipe E1, E2 and E4 are 1–2 images apart at L3, and every method learned the test recipe's own noise.
Recipe B keeps the 240 photos (with black gram), noise types, levels and folds, and makes the noise a different way
(`src/safecrop/noise_b.py`):

| Noise | Test recipe | Recipe B | B strength L1 / L2 / L3 |
| --- | --- | --- | --- |
| Sensor noise | even Gaussian grain per pixel and colour | grain that grows with brightness, clumped, + colour blotches | 241 / 52 / 11 photons |
| Hand-shake blur | straight line, -45..45 degrees | curved shake path, any direction | 13 / 30 / 50 px path |
| Out of focus | sharp-edged disk | Gaussian blur + colour fringes | sigma 1.7 / 3.7 / 6.6 px |
| Low light | darker, grainy, faded | auto-brightened very noisy dark photo, smoothed, warm cast | 8.3% / 3.7% / 1.8% light |
| Compression | JPEG 25 / 15 / 7 | shrink, WebP, enlarge | 78% size q43 / 68% q27 / 53% q9 |

Strength matched per noise type and level to the test images (same 42 photos each; no model, no labels) by levelled
colour MS-SSIM (structural similarity at 5 scales, per colour channel, after matching each channel's brightness and
contrast). Every level within 0.001 (calibration seeds 5005; image seeds 4242). Three simpler matching rules were tried
and dropped **before** anything was scored on recipe B (plain grey SSIM made B's low light far harsher; levelled grey
SSIM barely sees colour grain; single-scale levelled colour SSIM made B's blotchy noise harsher). B's sensor noise at
L3 still looks a little rougher than the test images'. Colab rebuilt recipe B with 633 of 720 noisy images
bit-identical to the local set (the scores use Colab's images). `data/images_recipe_b/` is not in git: rebuild with
`python scripts/make_recipe_b.py`.

Average levelled colour MS-SSIM to the clean photo (1 = undamaged):

| Noise | Level | SSIM test images | SSIM recipe B |
| --- | --- | --- | --- |
| Out of focus | L1 | 0.938 | 0.937 |
| Out of focus | L2 | 0.819 | 0.818 |
| Out of focus | L3 | 0.679 | 0.679 |
| Sensor noise | L1 | 0.893 | 0.894 |
| Sensor noise | L2 | 0.735 | 0.738 |
| Sensor noise | L3 | 0.517 | 0.52 |
| Compression | L1 | 0.949 | 0.95 |
| Compression | L2 | 0.923 | 0.923 |
| Compression | L3 | 0.855 | 0.855 |
| Low light | L1 | 0.879 | 0.881 |
| Low light | L2 | 0.813 | 0.817 |
| Low light | L3 | 0.732 | 0.738 |
| Hand-shake blur | L1 | 0.885 | 0.885 |
| Hand-shake blur | L2 | 0.698 | 0.71 |
| Hand-shake blur | L3 | 0.566 | 0.572 |

Images compared: 960 of 960 per test set (only images that every file scored).
Recipe B: same photos, noise types, levels and folds; each level matched to the test images' damage (levelled colour MS-SSIM). Every method learned or built its references from the TEST recipe's noise only.

### Accuracy drop from the test recipe to recipe B (paired McNemar: same photo, same level)

| Method | Levels | Test recipe % | Recipe B % | Change | Images | Only B right | Only test right | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E0 frozen database (7 diseases) | L3 | 40.0 | 30.5 | -9.5 | 210 | 8 | 28 | 0.001 |
| E0 frozen database (7 diseases) | All | 76.3 | 67.9 | -8.4 | 840 | 22 | 93 | <0.001 |
| E0 frozen database (black gram) | L3 | 6.7 | 0.0 | -6.7 | 30 | 0 | 2 | 0.500 |
| E0 frozen database (black gram) | All | 48.3 | 42.5 | -5.8 | 120 | 1 | 8 | 0.039 |
| E0 CLIP zero-shot (7 diseases) | L3 | 3.8 | 1.4 | -2.4 | 210 | 2 | 7 | 0.180 |
| E0 CLIP zero-shot (7 diseases) | All | 13.3 | 13.0 | -0.3 | 840 | 35 | 38 | 0.815 |
| E0 CLIP zero-shot (black gram) | L3 | 10.0 | 13.3 | 3.3 | 30 | 4 | 3 | 1.000 |
| E0 CLIP zero-shot (black gram) | All | 5.0 | 7.5 | 2.5 | 120 | 6 | 3 | 0.508 |
| E1 frozen + noisy copies (7 diseases) | L3 | 95.7 | 67.1 | -28.6 | 210 | 5 | 65 | <0.001 |
| E1 frozen + noisy copies (7 diseases) | All | 98.6 | 88.8 | -9.8 | 840 | 7 | 89 | <0.001 |
| E1 frozen + noisy copies (black gram) | L3 | 90.0 | 20.0 | -70.0 | 30 | 0 | 21 | <0.001 |
| E1 frozen + noisy copies (black gram) | All | 93.3 | 73.3 | -20.0 | 120 | 2 | 26 | <0.001 |
| E2 SVM + noisy copies (7 diseases) | L3 | 97.1 | 78.1 | -19.0 | 210 | 4 | 44 | <0.001 |
| E2 SVM + noisy copies (7 diseases) | All | 98.7 | 93.5 | -5.2 | 840 | 6 | 50 | <0.001 |
| E2 SVM + noisy copies (black gram) | L3 | 96.7 | 70.0 | -26.7 | 30 | 1 | 9 | 0.021 |
| E2 SVM + noisy copies (black gram) | All | 99.2 | 89.2 | -10.0 | 120 | 1 | 13 | 0.002 |
| E3 fine-tuned, database (7 diseases) | L3 | 92.4 | 73.8 | -18.6 | 210 | 7 | 46 | <0.001 |
| E3 fine-tuned, database (7 diseases) | All | 98.0 | 91.9 | -6.1 | 840 | 7 | 58 | <0.001 |
| E3 fine-tuned, database (black gram) | L3 | 80.0 | 63.3 | -16.7 | 30 | 1 | 6 | 0.125 |
| E3 fine-tuned, database (black gram) | All | 92.5 | 88.3 | -4.2 | 120 | 2 | 7 | 0.180 |
| E3 fine-tuned, head (7 diseases) | L3 | 94.3 | 79.5 | -14.8 | 210 | 5 | 36 | <0.001 |
| E3 fine-tuned, head (7 diseases) | All | 98.5 | 94.2 | -4.3 | 840 | 5 | 41 | <0.001 |
| E3 fine-tuned, head (black gram) | L3 | 93.3 | 73.3 | -20.0 | 30 | 1 | 7 | 0.070 |
| E3 fine-tuned, head (black gram) | All | 96.7 | 91.7 | -5.0 | 120 | 1 | 7 | 0.070 |
| E4 fine-tuned + noisy copies (7 diseases) | L3 | 96.7 | 85.2 | -11.5 | 210 | 5 | 29 | <0.001 |
| E4 fine-tuned + noisy copies (7 diseases) | All | 98.9 | 95.4 | -3.5 | 840 | 6 | 36 | <0.001 |
| E4 fine-tuned + noisy copies (black gram) | L3 | 90.0 | 76.7 | -13.3 | 30 | 2 | 6 | 0.289 |
| E4 fine-tuned + noisy copies (black gram) | All | 95.8 | 92.5 | -3.3 | 120 | 2 | 6 | 0.289 |

### Recipe B (7 diseases): the usual tables

#### Accuracy by noise level (% correct)

| Predictor | L0 | L1 | L2 | L3 | All | n |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E0 frozen database [recipe B] | 100.0 | 85.2 | 55.7 | 30.5 | 67.9 | 840 |
| E0 CLIP zero-shot [recipe B] | 25.7 | 14.3 | 10.5 | 1.4 | 13.0 | 840 |
| E1 frozen + noisy copies [recipe B] | 100.0 | 96.7 | 91.4 | 67.1 | 88.8 | 840 |
| E2 SVM + noisy copies [recipe B] | 99.5 | 99.0 | 97.1 | 78.1 | 93.5 | 840 |
| E3 fine-tuned, database [recipe B] | 100.0 | 99.0 | 94.8 | 73.8 | 91.9 | 840 |
| E3 fine-tuned, head [recipe B] | 100.0 | 99.5 | 97.6 | 79.5 | 94.2 | 840 |
| E4 fine-tuned + noisy copies [recipe B] | 100.0 | 99.0 | 97.1 | 85.2 | 95.4 | 840 |

#### Info-rich (A) vs info-scarce (B) (% correct)

| Predictor | A all | A L3 | B all | B L3 |
| --- | ---: | ---: | ---: | ---: |
| E0 frozen database [recipe B] | 74.1 | 41.2 | 63.6 | 23.2 |
| E0 CLIP zero-shot [recipe B] | 6.2 | 1.2 | 17.6 | 1.6 |
| E1 frozen + noisy copies [recipe B] | 90.3 | 75.3 | 87.8 | 61.6 |
| E2 SVM + noisy copies [recipe B] | 96.2 | 88.2 | 91.6 | 71.2 |
| E3 fine-tuned, database [recipe B] | 96.8 | 90.6 | 88.6 | 62.4 |
| E3 fine-tuned, head [recipe B] | 97.1 | 90.6 | 92.2 | 72.0 |
| E4 fine-tuned + noisy copies [recipe B] | 98.2 | 95.3 | 93.4 | 78.4 |

#### By noise type, L3 (% correct)

| Predictor | Sensor noise | Hand-shake blur | Out of focus | Low light | Compression |
| --- | ---: | ---: | ---: | ---: | ---: |
| E0 frozen database [recipe B] | 14.3 | 28.6 | 21.4 | 28.6 | 59.5 |
| E0 CLIP zero-shot [recipe B] | 0.0 | 0.0 | 0.0 | 4.8 | 2.4 |
| E1 frozen + noisy copies [recipe B] | 54.8 | 76.2 | 64.3 | 69.0 | 71.4 |
| E2 SVM + noisy copies [recipe B] | 54.8 | 90.5 | 83.3 | 78.6 | 83.3 |
| E3 fine-tuned, database [recipe B] | 38.1 | 81.0 | 81.0 | 71.4 | 97.6 |
| E3 fine-tuned, head [recipe B] | 42.9 | 85.7 | 88.1 | 83.3 | 97.6 |
| E4 fine-tuned + noisy copies [recipe B] | 64.3 | 92.9 | 85.7 | 85.7 | 97.6 |

#### By noise type, L1-L3 (% correct)

| Predictor | Sensor noise | Hand-shake blur | Out of focus | Low light | Compression |
| --- | ---: | ---: | ---: | ---: | ---: |
| E0 frozen database [recipe B] | 50.8 | 53.2 | 50.8 | 50.0 | 81.0 |
| E0 CLIP zero-shot [recipe B] | 7.9 | 4.8 | 7.9 | 7.1 | 15.9 |
| E1 frozen + noisy copies [recipe B] | 81.7 | 91.3 | 81.7 | 83.3 | 87.3 |
| E2 SVM + noisy copies [recipe B] | 84.1 | 96.0 | 92.9 | 90.5 | 93.7 |
| E3 fine-tuned, database [recipe B] | 77.8 | 91.3 | 92.1 | 85.7 | 99.2 |
| E3 fine-tuned, head [recipe B] | 80.2 | 94.4 | 95.2 | 92.1 | 99.2 |
| E4 fine-tuned + noisy copies [recipe B] | 87.3 | 96.0 | 94.4 | 92.1 | 99.2 |

### The info-richness gap on recipe B (E4, L3, old 7 diseases)

- Group A 95.3% (81 of 85) vs group B 78.4% (98 of 125): Fisher p = 0.0006 (SVM p = 0.004; frozen p = 0.006;
  E1 p = 0.051). On the test recipe it was gone (p = 1.0).
- E4 on recipe B at L3 by disease: potato 96.0, rice stem borer 96.7, apple scab 93.3, jute dieback 93.3, grape 86.7,
  pear leaf spot 80.0, **jute mosaic 53.3** (its misses: apple scab 6, black gram 6, pear 2; mostly sensor noise and low
  light, recipe B's blotchy-colour types).
- Caveats: one photo source per disease (A vs B is mixed up with disease and source), small numbers per disease.

### Recipe B (black gram): the usual tables

#### Accuracy by noise level (% correct)

| Predictor | L0 | L1 | L2 | L3 | All | n |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E0 frozen database [recipe B] | 100.0 | 46.7 | 23.3 | 0.0 | 42.5 | 120 |
| E0 CLIP zero-shot [recipe B] | 0.0 | 3.3 | 13.3 | 13.3 | 7.5 | 120 |
| E1 frozen + noisy copies [recipe B] | 100.0 | 93.3 | 80.0 | 20.0 | 73.3 | 120 |
| E2 SVM + noisy copies [recipe B] | 100.0 | 93.3 | 93.3 | 70.0 | 89.2 | 120 |
| E3 fine-tuned, database [recipe B] | 100.0 | 96.7 | 93.3 | 63.3 | 88.3 | 120 |
| E3 fine-tuned, head [recipe B] | 100.0 | 96.7 | 96.7 | 73.3 | 91.7 | 120 |
| E4 fine-tuned + noisy copies [recipe B] | 100.0 | 96.7 | 96.7 | 76.7 | 92.5 | 120 |

#### By noise type, L3 (% correct)

| Predictor | Sensor noise | Hand-shake blur | Out of focus | Low light | Compression |
| --- | ---: | ---: | ---: | ---: | ---: |
| E0 frozen database [recipe B] | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| E0 CLIP zero-shot [recipe B] | 16.7 | 0.0 | 16.7 | 33.3 | 0.0 |
| E1 frozen + noisy copies [recipe B] | 0.0 | 33.3 | 16.7 | 16.7 | 33.3 |
| E2 SVM + noisy copies [recipe B] | 50.0 | 66.7 | 50.0 | 83.3 | 100.0 |
| E3 fine-tuned, database [recipe B] | 33.3 | 100.0 | 33.3 | 66.7 | 83.3 |
| E3 fine-tuned, head [recipe B] | 33.3 | 100.0 | 66.7 | 83.3 | 83.3 |
| E4 fine-tuned + noisy copies [recipe B] | 66.7 | 100.0 | 66.7 | 50.0 | 100.0 |

#### By noise type, L1-L3 (% correct)

| Predictor | Sensor noise | Hand-shake blur | Out of focus | Low light | Compression |
| --- | ---: | ---: | ---: | ---: | ---: |
| E0 frozen database [recipe B] | 11.1 | 22.2 | 16.7 | 0.0 | 66.7 |
| E0 CLIP zero-shot [recipe B] | 16.7 | 0.0 | 22.2 | 11.1 | 0.0 |
| E1 frozen + noisy copies [recipe B] | 55.6 | 72.2 | 55.6 | 61.1 | 77.8 |
| E2 SVM + noisy copies [recipe B] | 83.3 | 88.9 | 77.8 | 77.8 | 100.0 |
| E3 fine-tuned, database [recipe B] | 61.1 | 100.0 | 77.8 | 88.9 | 94.4 |
| E3 fine-tuned, head [recipe B] | 66.7 | 100.0 | 88.9 | 94.4 | 94.4 |
| E4 fine-tuned + noisy copies [recipe B] | 77.8 | 100.0 | 88.9 | 83.3 | 100.0 |

### Methods against each other on recipe B (7 diseases) (McNemar)

| Method A | Method B | Levels | Images | Only A right | Only B right | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E1 frozen + noisy copies | E2 SVM + noisy copies | L3 | 210 | 11 | 34 | <0.001 |
| E1 frozen + noisy copies | E2 SVM + noisy copies | All | 840 | 18 | 57 | <0.001 |
| E1 frozen + noisy copies | E3 fine-tuned, database | L3 | 210 | 20 | 34 | 0.076 |
| E1 frozen + noisy copies | E3 fine-tuned, database | All | 840 | 27 | 53 | 0.005 |
| E1 frozen + noisy copies | E3 fine-tuned, head | L3 | 210 | 16 | 42 | <0.001 |
| E1 frozen + noisy copies | E3 fine-tuned, head | All | 840 | 18 | 63 | <0.001 |
| E1 frozen + noisy copies | E4 fine-tuned + noisy copies | L3 | 210 | 6 | 44 | <0.001 |
| E1 frozen + noisy copies | E4 fine-tuned + noisy copies | All | 840 | 9 | 64 | <0.001 |
| E2 SVM + noisy copies | E3 fine-tuned, database | L3 | 210 | 27 | 18 | 0.233 |
| E2 SVM + noisy copies | E3 fine-tuned, database | All | 840 | 39 | 26 | 0.136 |
| E2 SVM + noisy copies | E3 fine-tuned, head | L3 | 210 | 18 | 21 | 0.749 |
| E2 SVM + noisy copies | E3 fine-tuned, head | All | 840 | 23 | 29 | 0.488 |
| E2 SVM + noisy copies | E4 fine-tuned + noisy copies | L3 | 210 | 13 | 28 | 0.028 |
| E2 SVM + noisy copies | E4 fine-tuned + noisy copies | All | 840 | 20 | 36 | 0.044 |
| E3 fine-tuned, database | E3 fine-tuned, head | L3 | 210 | 2 | 14 | 0.004 |
| E3 fine-tuned, database | E3 fine-tuned, head | All | 840 | 2 | 21 | <0.001 |
| E3 fine-tuned, database | E4 fine-tuned + noisy copies | L3 | 210 | 0 | 24 | <0.001 |
| E3 fine-tuned, database | E4 fine-tuned + noisy copies | All | 840 | 0 | 29 | <0.001 |
| E3 fine-tuned, head | E4 fine-tuned + noisy copies | L3 | 210 | 7 | 19 | 0.029 |
| E3 fine-tuned, head | E4 fine-tuned + noisy copies | All | 840 | 9 | 19 | 0.087 |

### Methods against each other on recipe B (black gram) (McNemar)

| Method A | Method B | Levels | Images | Only A right | Only B right | p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E1 frozen + noisy copies | E2 SVM + noisy copies | L3 | 30 | 0 | 15 | <0.001 |
| E1 frozen + noisy copies | E2 SVM + noisy copies | All | 120 | 2 | 21 | <0.001 |
| E1 frozen + noisy copies | E3 fine-tuned, database | L3 | 30 | 1 | 14 | <0.001 |
| E1 frozen + noisy copies | E3 fine-tuned, database | All | 120 | 2 | 20 | <0.001 |
| E1 frozen + noisy copies | E3 fine-tuned, head | L3 | 30 | 0 | 16 | <0.001 |
| E1 frozen + noisy copies | E3 fine-tuned, head | All | 120 | 0 | 22 | <0.001 |
| E1 frozen + noisy copies | E4 fine-tuned + noisy copies | L3 | 30 | 0 | 17 | <0.001 |
| E1 frozen + noisy copies | E4 fine-tuned + noisy copies | All | 120 | 0 | 23 | <0.001 |
| E2 SVM + noisy copies | E3 fine-tuned, database | L3 | 30 | 6 | 4 | 0.754 |
| E2 SVM + noisy copies | E3 fine-tuned, database | All | 120 | 9 | 8 | 1.000 |
| E2 SVM + noisy copies | E3 fine-tuned, head | L3 | 30 | 3 | 4 | 1.000 |
| E2 SVM + noisy copies | E3 fine-tuned, head | All | 120 | 5 | 8 | 0.581 |
| E2 SVM + noisy copies | E4 fine-tuned + noisy copies | L3 | 30 | 4 | 6 | 0.754 |
| E2 SVM + noisy copies | E4 fine-tuned + noisy copies | All | 120 | 6 | 10 | 0.454 |
| E3 fine-tuned, database | E3 fine-tuned, head | L3 | 30 | 0 | 3 | 0.250 |
| E3 fine-tuned, database | E3 fine-tuned, head | All | 120 | 0 | 4 | 0.125 |
| E3 fine-tuned, database | E4 fine-tuned + noisy copies | L3 | 30 | 1 | 5 | 0.219 |
| E3 fine-tuned, database | E4 fine-tuned + noisy copies | All | 120 | 1 | 6 | 0.125 |
| E3 fine-tuned, head | E4 fine-tuned + noisy copies | L3 | 30 | 2 | 3 | 1.000 |
| E3 fine-tuned, head | E4 fine-tuned + noisy copies | All | 120 | 2 | 3 | 1.000 |

(Rows against the frozen database and CLIP zero-shot are left out here: E1-E4 beat both of them, p < 0.05, except E1 vs zero-shot on black gram L3, 4 / 2, p = 0.69. Full tables: `results/robustness_20261111_8diseases.md`.)

## 5. Every run (`results/runs.csv`, 42 lines)

| Time | Run folder | Method | n | L0 | L1 | L2 | L3 | All | A | B | L3 vs frozen (new / old, p) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2026-11-11 17:44:40 | 20261111-174417_clip-vit-large-patch14_e0 | CLIP database, frozen clip-vit-large-patch14 (recomputed) | 840 | 100.0 | 93.3 | 71.9 | 40.0 | 76.3 | 81.2 | 73.0 | 0 / 0, p = 1.000 |
| 2026-11-11 17:44:40 | 20261111-174417_clip-vit-large-patch14_e0 | CLIP zero-shot, frozen clip-vit-large-patch14 (recomputed) | 840 | 25.7 | 15.2 | 8.6 | 3.8 | 13.3 | 9.1 | 16.2 | 7 / 83, p < 0.001 |
| 2026-11-11 12:09:39 | 20261111-120939_clip-vit-large-patch14_e1 | CLIP database + noisy copies (levels [1, 2, 3], x1) | 840 | 100.0 | 100.0 | 99.0 | 95.2 | 98.6 | 98.8 | 98.4 | 120 / 4, p < 0.001 |
| 2026-11-11 13:13:37 | 20261111-131304_clip-vit-large-patch14_sanity_f0 | Fine-tuned CLIP database (k4 e0 cons1.0) | 168 | 100.0 | 92.9 | 76.2 | 35.7 | 76.2 | 82.4 | 72.0 | 0 / 0, p = 1.000 |
| 2026-11-11 13:13:37 | 20261111-131304_clip-vit-large-patch14_sanity_f0 | Fine-tuned CLIP head (k4 e0 cons1.0) | 168 | 97.6 | 92.9 | 59.5 | 33.3 | 70.8 | 79.4 | 65.0 | 1 / 2, p = 1.000 |
| 2026-11-11 13:16:42 | 20261111-131642_clip-vit-large-patch14_svm | SVM on frozen CLIP (clean + noisy copies) | 840 | 100.0 | 99.5 | 99.0 | 97.6 | 99.0 | 99.4 | 98.8 | 123 / 2, p < 0.001 |
| 2026-11-11 13:18:29 | 20261111-131650_clip-vit-large-patch14_e3_f0 | Fine-tuned CLIP database (k4 e15 cons1.0) | 168 | 100.0 | 100.0 | 100.0 | 88.1 | 97.0 | 98.5 | 96.0 | 22 / 0, p < 0.001 |
| 2026-11-11 13:18:29 | 20261111-131650_clip-vit-large-patch14_e3_f0 | Fine-tuned CLIP head (k4 e15 cons1.0) | 168 | 100.0 | 100.0 | 100.0 | 95.2 | 98.8 | 98.5 | 99.0 | 25 / 0, p < 0.001 |
| 2026-11-11 13:21:24 | 20261111-131836_clip-vit-large-patch14_e4_f0 | Fine-tuned CLIP database (k4 e15 cons1.0) + noisy copies | 168 | 100.0 | 100.0 | 100.0 | 97.6 | 99.4 | 100.0 | 99.0 | 26 / 0, p < 0.001 |
| 2026-11-11 13:21:24 | 20261111-131836_clip-vit-large-patch14_e4_f0 | Fine-tuned CLIP head (k4 e15 cons1.0) | 168 | 100.0 | 100.0 | 100.0 | 95.2 | 98.8 | 98.5 | 99.0 | 25 / 0, p < 0.001 |
| 2026-11-11 13:44:14 | 20261111-133622_clip-vit-large-patch14_e3_all | Fine-tuned CLIP database (k4 e15 cons1.0) | 840 | 100.0 | 100.0 | 99.5 | 93.8 | 98.3 | 98.8 | 98.0 | 114 / 1, p < 0.001 |
| 2026-11-11 13:44:14 | 20261111-133622_clip-vit-large-patch14_e3_all | Fine-tuned CLIP head (k4 e15 cons1.0) | 840 | 100.0 | 100.0 | 99.5 | 95.2 | 98.7 | 98.8 | 98.6 | 117 / 1, p < 0.001 |
| 2026-11-11 13:57:47 | 20261111-134420_clip-vit-large-patch14_e4_all | Fine-tuned CLIP database (k4 e15 cons1.0) + noisy copies | 840 | 100.0 | 100.0 | 99.5 | 97.1 | 99.2 | 99.4 | 99.0 | 121 / 1, p < 0.001 |
| 2026-11-11 13:57:47 | 20261111-134420_clip-vit-large-patch14_e4_all | Fine-tuned CLIP head (k4 e15 cons1.0) | 840 | 100.0 | 100.0 | 99.5 | 95.2 | 98.7 | 98.8 | 98.6 | 117 / 1, p < 0.001 |
| 2026-11-11 15:22:03 | 20261111-152201_clip-vit-large-patch14_e0_8d | CLIP database, frozen clip-vit-large-patch14 (recomputed) [8 diseases] (original 7 diseases) | 840 | 100.0 | 93.3 | 71.9 | 40.0 | 76.3 | 81.2 | 73.0 | 0 / 0, p = 1.000 |
| 2026-11-11 15:22:03 | 20261111-152201_clip-vit-large-patch14_e0_8d | CLIP database, frozen clip-vit-large-patch14 (recomputed) [8 diseases] (black gram only) | 120 | 100.0 | 66.7 | 20.0 | 6.7 | 48.3 | 48.3 |  |  |
| 2026-11-11 15:22:03 | 20261111-152201_clip-vit-large-patch14_e0_8d | CLIP zero-shot, frozen clip-vit-large-patch14 (recomputed) [8 diseases] (original 7 diseases) | 840 | 25.7 | 15.2 | 8.6 | 3.8 | 13.3 | 9.1 | 16.2 | 7 / 83, p < 0.001 |
| 2026-11-11 15:22:03 | 20261111-152201_clip-vit-large-patch14_e0_8d | CLIP zero-shot, frozen clip-vit-large-patch14 (recomputed) [8 diseases] (black gram only) | 120 | 0.0 | 3.3 | 6.7 | 10.0 | 5.0 | 5.0 |  |  |
| 2026-11-11 15:22:30 | 20261111-152229_clip-vit-large-patch14_e0_8d_rb | CLIP database, frozen clip-vit-large-patch14 (recomputed) [recipe B, 8 diseases] (original 7 diseases) | 840 | 100.0 | 85.2 | 55.7 | 30.5 | 67.9 | 74.1 | 63.6 |  |
| 2026-11-11 15:22:30 | 20261111-152229_clip-vit-large-patch14_e0_8d_rb | CLIP zero-shot, frozen clip-vit-large-patch14 (recomputed) [recipe B, 8 diseases] (original 7 diseases) | 840 | 25.7 | 14.3 | 10.5 | 1.4 | 13.0 | 6.2 | 17.6 |  |
| 2026-11-11 15:23:56 | 20261111-152356_clip-vit-large-patch14_e1_8d | CLIP database + noisy copies (levels [1, 2, 3], x1) [8 diseases] (original 7 diseases) | 840 | 100.0 | 100.0 | 98.6 | 95.7 | 98.6 | 98.8 | 98.4 | 121 / 4, p < 0.001 |
| 2026-11-11 15:24:08 | 20261111-152408_clip-vit-large-patch14_e1_8d_rb | CLIP database + noisy copies (levels [1, 2, 3], x1) [recipe B, 8 diseases] (original 7 diseases) | 840 | 100.0 | 96.7 | 91.4 | 67.1 | 88.8 | 90.3 | 87.8 |  |
| 2026-11-11 15:26:44 | 20261111-152643_clip-vit-large-patch14_svm_8d | SVM on frozen CLIP (clean + noisy copies) [8 diseases] (original 7 diseases) | 840 | 99.5 | 99.5 | 98.6 | 97.1 | 98.7 | 99.4 | 98.2 | 122 / 2, p < 0.001 |
| 2026-11-11 15:26:44 | 20261111-152643_clip-vit-large-patch14_svm_8d | SVM on frozen CLIP (clean + noisy copies) [8 diseases] (black gram only) | 120 | 100.0 | 100.0 | 100.0 | 96.7 | 99.2 | 99.2 |  |  |
| 2026-11-11 15:29:18 | 20261111-152918_clip-vit-large-patch14_svm_8d_rb | SVM on frozen CLIP (clean + noisy copies) [recipe B, 8 diseases] (original 7 diseases) | 840 | 99.5 | 99.0 | 97.1 | 78.1 | 93.5 | 96.2 | 91.6 |  |
| 2026-11-11 15:29:18 | 20261111-152918_clip-vit-large-patch14_svm_8d_rb | SVM on frozen CLIP (clean + noisy copies) [recipe B, 8 diseases] (black gram only) | 120 | 100.0 | 93.3 | 93.3 | 70.0 | 89.2 | 89.2 |  |  |
| 2026-11-11 15:39:37 | 20261111-152925_clip-vit-large-patch14_e3_8d | Fine-tuned CLIP database (k4 e15 cons1.0) [8 diseases] (original 7 diseases) | 840 | 100.0 | 100.0 | 99.5 | 92.4 | 98.0 | 98.5 | 97.6 | 111 / 1, p < 0.001 |
| 2026-11-11 15:39:37 | 20261111-152925_clip-vit-large-patch14_e3_8d | Fine-tuned CLIP database (k4 e15 cons1.0) [8 diseases] (black gram only) | 120 | 100.0 | 96.7 | 93.3 | 80.0 | 92.5 | 92.5 |  |  |
| 2026-11-11 15:39:37 | 20261111-152925_clip-vit-large-patch14_e3_8d | Fine-tuned CLIP head (k4 e15 cons1.0) [8 diseases] (original 7 diseases) | 840 | 100.0 | 100.0 | 99.5 | 94.3 | 98.5 | 97.9 | 98.8 | 115 / 1, p < 0.001 |
| 2026-11-11 15:39:37 | 20261111-152925_clip-vit-large-patch14_e3_8d | Fine-tuned CLIP head (k4 e15 cons1.0) [8 diseases] (black gram only) | 120 | 100.0 | 96.7 | 96.7 | 93.3 | 96.7 | 96.7 |  |  |
| 2026-11-11 15:39:38 | 20261111-153937_clip-vit-large-patch14_e3_8d_rb | Fine-tuned CLIP database (k4 e15 cons1.0) [recipe B, 8 diseases] (original 7 diseases) | 840 | 100.0 | 99.0 | 94.8 | 73.8 | 91.9 | 96.8 | 88.6 |  |
| 2026-11-11 15:39:38 | 20261111-153937_clip-vit-large-patch14_e3_8d_rb | Fine-tuned CLIP database (k4 e15 cons1.0) [recipe B, 8 diseases] (black gram only) | 120 | 100.0 | 96.7 | 93.3 | 63.3 | 88.3 | 88.3 |  |  |
| 2026-11-11 15:39:38 | 20261111-153937_clip-vit-large-patch14_e3_8d_rb | Fine-tuned CLIP head (k4 e15 cons1.0) [recipe B, 8 diseases] (original 7 diseases) | 840 | 100.0 | 99.5 | 97.6 | 79.5 | 94.2 | 97.1 | 92.2 |  |
| 2026-11-11 15:39:38 | 20261111-153937_clip-vit-large-patch14_e3_8d_rb | Fine-tuned CLIP head (k4 e15 cons1.0) [recipe B, 8 diseases] (black gram only) | 120 | 100.0 | 96.7 | 96.7 | 73.3 | 91.7 | 91.7 |  |  |
| 2026-11-11 16:02:58 | 20261111-153945_clip-vit-large-patch14_e4_8d | Fine-tuned CLIP database (k4 e15 cons1.0) + noisy copies [8 diseases] (original 7 diseases) | 840 | 100.0 | 100.0 | 99.0 | 96.7 | 98.9 | 98.8 | 99.0 | 120 / 1, p < 0.001 |
| 2026-11-11 16:02:58 | 20261111-153945_clip-vit-large-patch14_e4_8d | Fine-tuned CLIP database (k4 e15 cons1.0) + noisy copies [8 diseases] (black gram only) | 120 | 100.0 | 96.7 | 96.7 | 90.0 | 95.8 | 95.8 |  |  |
| 2026-11-11 16:02:58 | 20261111-153945_clip-vit-large-patch14_e4_8d | Fine-tuned CLIP head (k4 e15 cons1.0) [8 diseases] (original 7 diseases) | 840 | 100.0 | 100.0 | 99.5 | 94.3 | 98.5 | 97.9 | 98.8 | 115 / 1, p < 0.001 |
| 2026-11-11 16:02:58 | 20261111-153945_clip-vit-large-patch14_e4_8d | Fine-tuned CLIP head (k4 e15 cons1.0) [8 diseases] (black gram only) | 120 | 100.0 | 96.7 | 96.7 | 93.3 | 96.7 | 96.7 |  |  |
| 2026-11-11 16:02:59 | 20261111-160258_clip-vit-large-patch14_e4_8d_rb | Fine-tuned CLIP database (k4 e15 cons1.0) + noisy copies [recipe B, 8 diseases] (original 7 diseases) | 840 | 100.0 | 99.0 | 97.1 | 85.2 | 95.4 | 98.2 | 93.4 |  |
| 2026-11-11 16:02:59 | 20261111-160258_clip-vit-large-patch14_e4_8d_rb | Fine-tuned CLIP database (k4 e15 cons1.0) + noisy copies [recipe B, 8 diseases] (black gram only) | 120 | 100.0 | 96.7 | 96.7 | 76.7 | 92.5 | 92.5 |  |  |
| 2026-11-11 16:02:59 | 20261111-160258_clip-vit-large-patch14_e4_8d_rb | Fine-tuned CLIP head (k4 e15 cons1.0) [recipe B, 8 diseases] (original 7 diseases) | 840 | 100.0 | 99.5 | 97.6 | 79.5 | 94.2 | 97.1 | 92.2 |  |
| 2026-11-11 16:02:59 | 20261111-160258_clip-vit-large-patch14_e4_8d_rb | Fine-tuned CLIP head (k4 e15 cons1.0) [recipe B, 8 diseases] (black gram only) | 120 | 100.0 | 96.7 | 96.7 | 73.3 | 91.7 | 91.7 |  |  |

## 6. Caveats to say in reports

- Synthetic noise, one problem per photo; real phone photos are not tested yet.
- Each disease comes from one photo source, so CLIP can partly match photo style (apple scab with other-source
  references: 100% → 7% on clean photos). Potato and grape are PlantVillage lab photos.
- The noisy copies and fine-tuning used the test recipe's noise; recipe B is the first check against that, and it
  shows real drops for every method (−11.5 to −28.6 points at L3).
- 210 images per level: about ±7 points chance variation; use the McNemar counts, not just accuracy gaps.
- Only the default settings were tried; the black gram results rest on 30 photos.

## 7. Still to do (from the repo's plan)

- E5: Gemini + references using the fine-tuned `neighbours.csv` (L3 first; 210 requests fit one day's free quota),
  compared with Step 2b (47.1%).
- E6: healthy / look-alike negatives (never PlantVillage potato late blight or grape leaf blight); more photos per
  disease from the source datasets; a prompt-tuned text side; fine-tuned CLIP inside the retake loop and the app.
- More settings on fold 0 (consistency weight 0 / 1 / 3, unfreeze 2 / 4 / 8 blocks, epochs, noisy views, L3-only
  training), then all 5 folds once.
- Real phone / field photos (e.g. PlantDoc for potato and grape).
- Timeline: Week 9 slides Sunday 15 Nov 2026 (fine-tuned CLIP + SVM, four-way comparison); Week 10 (22 Nov) real field
  photos incl. black gram, data card, FastAPI back end around the retake loop; Week 11 (29 Nov) React front end, demo
  video; Week 12 (6 Dec) final presentation, live demo, 8-page report.

## 8. Where the per-image data is (in the repo)

| What | Path |
| --- | --- |
| Every run: settings, predictions, neighbours, tables | `results/<experiment>/<time>_clip-vit-large-patch14_<tag>/` (`config.yaml`, `predictions_*.csv`, `neighbours.csv`, `summary.md`, `metrics.json`, `timing.json`, `train_log.csv`) |
| Comparison tables | `results/compare_20261111_all840_E1-E4.md`, `results/compare_20261111_fold0_E1-E4.md`, `results/compare_20261111_E2svm_vs_E1_all840.md`, `results/compare_20261111_8diseases.md`, `results/robustness_20261111_8diseases.md` |
| Recipe B builds and calibrations | `results/robustness/*recipe_b_build/` (summary + preview.png), `*recipe_b_calibration/calibration.md` |
| Test images | `data/images/` (840), `data/images_black_gram/` (120), `data/extra_references/` (240 PlantVillage) |
| Manifests | `data/manifest.csv` (840), `data/manifest_black_gram.csv` (120), `data/manifest_recipe_b.csv` (960) |
| Earlier per-image predictions | `data/baselines/` (Step 2, Step 2b, fairness, L3 variants, photo check, loop v2) |
| Frozen features | `data/features/clip_vitl14_frozen.npz` |
| Project story and rules | `CLAUDE.md`, `docs/PROJECT_HISTORY.md`, `docs/FINETUNING_PLAN.md`, `docs/DATA.md` |
| Colab GPU runner | `notebooks/colab_gpu_runner.ipynb` (reads the code and image zips from Drive folder https://drive.google.com/drive/folders/1EB43yD0e2c-kHmsbk46l89na6bvFMeMB) |
