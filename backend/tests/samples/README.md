# Sample photos for the back-end tests

16 test images from the SafeCrop test set (`NabilRafi/SafeCrop`, `data/images`): for each of the 8 diseases one
photo, clean (L0) and at the worst noise level (L3). 224 x 224 PNG, made from the original photos by the research
repo's noise code.

How they were picked (a fixed rule, not by looking at answers): diseases in alphabetical order, each takes the first
photo whose L3 noise type is next in the cycle grain (`gaussian_noise`) → `low_light` → `motion_blur` →
`defocus_blur` → `jpeg_compression`, so all 5 noise types appear.

**These photos are not a fair accuracy test.** The app model was trained on all of them. The tests only check that
the code works (right disease, right photo-check problem). Accuracy claims come from the 5-fold results.

| Files | Disease | L3 noise | Source | Licence | Original file |
| --- | --- | --- | --- | --- | --- |
| `apple_scab_001_clean_L0.png`, `apple_scab_001_gaussian_noise_L3.png` | Apple scab | gaussian_noise | AppleLeaf9 | CC BY 4.0 | Scab (117).jpg |
| `black_gram_yellow_mosaic_002_clean_L0.png`, `black_gram_yellow_mosaic_002_low_light_L3.png` | Black gram yellow mosaic | low_light | Mendeley Data z55yrbmn2d (IDBGL) | CC BY 4.0 | IDBGL dataset |
| `grape_leaf_blight_001_clean_L0.png`, `grape_leaf_blight_001_motion_blur_L3.png` | Grape leaf blight | motion_blur | PlantVillage | CC BY-SA 3.0 | 0001aa74-bbd7-433b-a900-1dccab39d521___FAM_L.Blight 4508.JPG |
| `jute_dieback_004_clean_L0.png`, `jute_dieback_004_defocus_blur_L3.png` | Jute dieback | defocus_blur | Harvard Dataverse doi:10.7910/DVN/FJ1DM1 | CC0 | Dieback-004.jpg |
| `jute_mosaic_007_clean_L0.png`, `jute_mosaic_007_jpeg_compression_L3.png` | Jute mosaic | jpeg_compression | Harvard Dataverse doi:10.7910/DVN/FJ1DM1 | CC0 | Mosaic-007.jpg |
| `pear_leaf_spot_006_clean_L0.png`, `pear_leaf_spot_006_gaussian_noise_L3.png` | Pear leaf spot | gaussian_noise | DiaMOS Plant | CC BY 4.0 | pear_leaf_spot_06.jpg |
| `potato_late_blight_007_clean_L0.png`, `potato_late_blight_007_low_light_L3.png` | Potato late blight | low_light | PlantVillage | CC BY-SA 3.0 | potato_late_blight_07.jpg |
| `rice_stem_borer_001_clean_L0.png`, `rice_stem_borer_001_motion_blur_L3.png` | Rice stem borer | motion_blur | Mendeley Data hnfjs42d5g | CC BY 4.0 | Dead_heart (18).jpg |

The PlantVillage images (CC BY-SA 3.0) are changed (cropped, resized, noise added) and shared under the same licence.
