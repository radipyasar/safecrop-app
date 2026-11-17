# SafeCrop – noisy matched albums (Idea 2), 9 Nov 2026

**Why:** in the filled CLIP album (our 7 diseases + 4 PlantVillage look-alikes + 3 healthy leaves) 73% of L3 photos were called a healthy leaf and L3 accuracy fell 40.0% → 15.2%. Supervisor's advice: put noisy images in the album so noisy photos are compared with noisy photos.

**Ideas offered:** (1) one mixed album with clean + noisy copies; (2) matched albums: one album per noise type and level, the photo check picks which; (3) noisy class averages. Idea 2 was chosen.

**Notebook:** `SafeCrop_noisy_album_idea2.ipynb` (Colab, T4 GPU; no Gemini requests).
- Album: every photo clean + 1 noisy copy per noise type and level (5 × 3 = 15), seed family 2026 (test images use 299); 210 of ours + 210 PlantVillage = 420 photos, 6,720 pictures. Leave-one-photo-out; same CLIP ViT-L/14 and k = 5 weighted vote as Step 2.
- Routing: the photo check (16 measurements + random forests, out-of-fold by photo: problem 97.7%, level 92.1%; right album at L3 90.5%).

## Results (all 840 images)

| Album | Row | L0 | L1 | L2 | L3 | All | L3 A | L3 B | L3 called healthy | L3 no correct neighbour |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Filled | Clean only (before) | 99.5 | 86.7 | 46.2 | 15.2 | 61.9 | 27.1 | 7.2 | 72.9% | 151 |
| Filled | Mixed clean + noisy (Idea 1) | 99.5 | 98.6 | 95.2 | 88.1 | 95.4 | 84.7 | 90.4 | 3.8% | 5 |
| Filled | Matched, true noise (best case) | 99.5 | 98.1 | 94.8 | 87.6 | 95.0 | 83.5 | 90.4 | 4.3% | 4 |
| Filled | **Matched, photo check (realistic)** | 99.5 | 96.7 | 92.4 | **85.7** | 93.6 | 81.2 | 88.8 | 4.8% | 6 |
| Filled | Matched, photo-check level only | 99.5 | 96.7 | 92.4 | 86.7 | 93.8 | 82.4 | 89.6 | 4.8% | 5 |
| Our 7 | Clean only (Step 2) | 100 | 93.3 | 71.9 | 40.0 | 76.3 | 48.2 | 34.4 | – | 81 |
| Our 7 | Mixed (Idea 1) | 100 | 100 | 99.0 | 95.2 | 98.6 | 95.3 | 95.2 | – | 1 |
| Our 7 | **Matched, photo check** | 100 | 99.5 | 97.1 | **93.8** | 97.6 | 94.1 | 93.6 | – | 2 |

- McNemar vs before, L3: filled realistic 151 fixed / 3 broken; our 7 realistic 117 / 4 (both p < 0.001).
- The noisy copies do the work, not the matching: Idea 1 (mixed) is as good or slightly better (88.1 vs 85.7); the photo check costs ~2 points; when it picks the wrong album the answer is still right 15 of 20 times at L3.
- Filled album L3 by noise type (Idea 2): sensor 76.2, shake 85.7, focus 85.7, low light 88.1, compression 92.9.
- Filled album L3 by disease: apple scab 96.7, jute mosaic 100, jute dieback 90, pear 88.6, rice 86.7, grape leaf blight 76.7, potato late blight 56.0 (mistakes mostly potato healthy / early blight, grape healthy: same PlantVillage source).

**Caveats:** one dataset per disease, so matching can partly use dataset style; the album's copies use the same noise recipe as the test images (best case).
