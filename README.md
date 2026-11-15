# Project Demeter: cropland versus other vegetation near Massafra (Puglia, Italy)

Space Academy 2026 · Hyperspectral course · Final graduation project · Theme: precision agriculture
Team: Mariolino Daniel III Julabar · AlReem AlRowahi

**Problem.** NDVI > 0.5 flags 131 km² of "vegetation" near Massafra, but only 16 % of it is cropland, and it still misses 53 % of the cropland (forest, scrub and grass are green too). An analyst planning field inspections needs cropland. **Question:** can the full Tanager spectrum separate cropland from other land cover, and does it beat what a multispectral sensor could do?

**Data.** Tanager scene `20250430_101724_87_4001` (30 April 2025, 426 bands, 30 m, EPSG:32633), central 512 × 512 crop (236 km²); 352 bands and 98.0 % of pixels valid after quality control. Reference labels: ESA WorldCover 2021 v200 (CC-BY 4.0), only where all nine 10 m cells in a 30 m pixel agree, merged to five classes. The raw HDF5 scene is not included; the notebook downloads it.

**Method.** Whole 40 × 40-pixel blocks go to train (50 %), validation (20 %) or test (30 %). Three feature sets see the same pixels: four narrow-band indices, ten simulated Sentinel-2 bands, the full 352-band spectrum. For each set the best of four pre-specified classifiers is chosen on validation; the test blocks are scored once with 95 % block-bootstrap confidence intervals.

**Key results** (48,550 test pixels in 51 blocks)

| Feature set | Macro-F1 [95 % CI] | Cropland F1 |
|---|---|---|
| Four indices | 0.700 [0.644, 0.733] | 0.478 |
| Sentinel-2-like (simulated) | 0.771 [0.732, 0.792] | 0.605 |
| **Full spectrum** | **0.823 [0.793, 0.840]** | **0.698** |

Full spectrum minus Sentinel-2-like: macro-F1 +0.052 (CI 0.039 to 0.071), same ordering in 5 of 5 random splits. The map points at 51 km² of cropland (precision 71 %, recall 69 %) instead of 131 km²: 61 % less land to inspect. The macro-F1 ≥ 0.80 target is met on the point estimate; its CI lower bound is 0.79.

**Limitations.** Accuracy is agreement with WorldCover 2021 (four years older than the scene), not field truth. One date, one scene. Sentinel-2-like bands are simulated. The beta cloud mask gives false positives over bright built-up surfaces. No crop type, health or yield claim.

**How to run.** `pip install -r requirements.txt`, open `project.ipynb`, *Restart & Run All* (6-13 minutes; the first run downloads about 1.1 GB into `data/`, or into the folder in `DEMETER_DATA_DIR`).

| Path | Content |
|---|---|
| `project.ipynb` | executed notebook; the scoping canvas is its first section |
| `src/demeter.py` | helper functions |
| `outputs/` | 5 Cloud-Optimised GeoTIFFs, `Project_Demeter_metadata.json`, `demeter_report.html`, `inspection_priority_cells.csv`, `figures/`, `manifest.json` |
| `validation/` | validation tables (CSV), confusion matrices, reference samples and splits |
| `presentation.pdf`, `presentation.pptx` | final slides (PDF) and the editable slides with speaker notes |

**Team contributions.** No team lead; both members contributed equally (50 % each), reviewed the whole notebook and can explain every part. Mariolino Daniel III Julabar: data, preprocessing, uncertainty and product layers. AlReem AlRowahi: method, validation and impact. An AI coding assistant (Claude) helped write code and text, as the course allows.

**Credits.** Tanager STAC Data, available at www.planet.com/data/stac © 2025 Planet Labs PBC (CC-BY-4.0). ESA WorldCover 10 m 2021 v200, Zanaga et al. (2022), https://doi.org/10.5281/zenodo.7254221, © ESA WorldCover project / Contains modified Copernicus Sentinel data (2021) processed by the ESA WorldCover consortium (CC-BY 4.0).
