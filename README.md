# Project Demeter
## Hyperspectral Vegetation Mapping of Puglia, Italia

Space Academy 2026 · Hyperspectral Course · Agriculture Theme

**Team**
- Mariolino Daniel III Julabar — Aerospace Engineer · Project Lead & Primary Developer
- AlReem AlRowahi — Aerospace Engineer · Project Design, Testing & Analysis Support

## Problem

Project Demeter maps vegetation candidates and explores spectral variability near Massafra, Puglia, Italia, to identify locations for closer inspection and reference-data collection. Outputs describe relative greenness and spectral differences—not confirmed cropland, crop health, disease, species, or yield.

## Data

- **Source:** Planet Tanager orthorectified surface-reflectance imagery.
- **Scene:** `20250430_101724_87_4001`.
- **Acquisition:** 30 April 2025, 10:17:24.870 UTC, from catalogue metadata.
- **Spectral coverage:** 426 bands, approximately 376–2,499 nm before filtering.
- **Study crop:** Central 512 × 512 pixels; 30 m pixels; EPSG:32633; projected area 235.9296 km².
- **Quality:** Catalogue cloud cover is 2% for the scene, not specifically the crop. Administrative-boundary verification and spatial QA review remain outstanding.

Direct source:
https://storage.googleapis.com/open-cogs/planet-stac/tanager1-release2-core-imagery/ortho_sr_hdf5/20250430_101724_87_4001_ortho_sr_hdf5.h5

## Method

1. Read wavelength metadata, crop the scene, review QA, and screen bands and invalid spectra.
2. Calculate NDVI, NDRE, NDMI, and PCA.
3. Compare an NDVI > 0.5 vegetation-candidate baseline with five spectral clusters.
4. Explore SAM/SID similarity and normalised nonnegative least-squares mixtures.
5. Assess threshold sensitivity and approximate same-scene sensor-bandpass differences.
6. Export maps, tables, COGs, metadata, quality checks, and an HTML report.

Optional LDA, Random Forest, SVM, and spectral 1D-CNN require independent reference labels. These supervised stages were skipped in the reported run. No temporal change detection is performed.

## Key Results

| Item | Current result |
|---|---|
| Numerically valid crop pixels | 262,144; not proof of cloud-free coverage |
| Vegetation candidates at NDVI > 0.5 | 145,771 pixels; 55.61% of the crop |
| Projected candidate area | 131.1939 km²; not validated cropland area |
| Main output | Five unlabelled spectral clusters |
| Threshold sensitivity, 0.2 → 0.6 | 234,261 → 91,875 candidate pixels |
| Simulated S2-like minus narrow-band NDVI | Bias −0.01539; RMSE 0.01700; not external validation |
| Product checks | All 10 recorded smoke tests passed |
| Classification accuracy | Unavailable: no independent reference labels |

COG creation, CRS presence, and array-roundtrip checks passed. Geographic alignment still requires GIS review; technical checks do not establish classification accuracy.

## How to Run

1. Open `Project_Demeter.ipynb` in Google Colab.
2. Review the scene, crop, thresholds, and optional labels in **Section 2: Configuration**.
3. Select **Runtime → Run all**. Setup installs dependencies and obtains the course helpers; the source HDF5 downloads automatically.
4. Inspect QA, maps, warnings, skipped stages, and product checks.
5. Download the results ZIP from the final download cell.

Internet access and space for the approximately 1.1 GB source file plus outputs are required. Selected catalogue and georeferencing functions depend on the course `hsi_utils.py` helper.

For supervised analysis, supply an independent CSV with:

```text
row,col,label,split
```

Coordinates are zero-based within the crop. Use `train`, `val`, or `test`; every class must appear in each split, and spatial blocks must not overlap. Do not derive reference truth from the indices being evaluated.

The notebook also exports a reusable pipeline and JSON configuration. After environment setup, optional repeat processing uses:

```bash
python demeter_product.py --config demeter_config.json
```

This is a processing interface, not a deployed application. Products include figures, CSVs, COGs where export succeeds, an HTML report, metadata, quality flags, and a ZIP. The latest workflow still requires independent clean-runtime verification.

## Credits

Tanager imagery: © Planet Labs PBC, CC-BY-4.0 as specified in the course materials; verify selected asset terms.

Methods and structure adapt Space Academy course notebooks 11, 13, 14, 15, 16, 20, 21, 30, and 31, the project/scoping templates, and selected course helpers:
https://github.com/Tnecniv-Teikram/NSA-hyperspectral-course-2026

Retain course authorship/licence notices and record the helper version. See the notebook for scientific references. ESA WorldCover and independent Sentinel-2/EnMAP imagery are not used by default. Imagery licensing does not define the licence of this repository’s code.
