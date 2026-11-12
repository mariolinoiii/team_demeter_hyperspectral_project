# Project Demeter (Draft, revise info and revert changes from template)

**Hyperspectral Vegetation Mapping of Puglia, Italia**  
**Space Academy 2026 · Hyperspectral course · Final graduation project**

**Team:** Mariolino Daniel III Julabar · AlReem AlRowahi  
**Theme:** Agriculture  
**Version:** 12 November 2026

## Problem

Agricultural and environmental analysts need a way to prioritise locations for vegetation inspection and independent reference sampling near Massafra, Puglia, Italia.

Project Demeter addresses this need with a single-date Tanager hyperspectral workflow. It produces a vegetation-candidate map and exploratory spectral clusters to support decisions on where field inspection and reference-sample collection should be prioritised.

The project does **not** classify land cover, identify crop species, or diagnose crop health, disease, yield, or productivity.

## Data

| Dataset | Scene ID / product | Date | Role |
|---|---|---|---|
| Tanager | `20250430_101724_87_4001`, ortho surface-reflectance HDF5 | 30 April 2025, 10:17:24.870 UTC | Primary analysis |
| Reference labels | Independent labelled CSV, not supplied | Not available | Required for supervised training and independent validation |
| Ancillary data | Tanager catalogue footprint, source CRS and transform | Source-associated | Geographic checks and export |

### Study area

- **Location:** Massafra area, Puglia, Italia.
- **Analysis crop:** Central 512 × 512-pixel crop.
- **Spatial resolution:** 30 m.
- **Coordinate reference system:** EPSG:32633.
- **Projected crop area:** 235.9296 km².
- **Approximate crop bounding box (W, S, E, N):** 17.059789, 40.504259, 17.245570, 40.645919.
- **Important note:** The administrative boundary is not verified; the crop extent is derived from the Tanager scene grid.

The Tanager scene footprint was checked against the configured area of interest. Cloud and cirrus flags were inspected, but visual review of residual cloud, shadow, glare, and mixed pixels is still recommended.

## Method

The workflow uses a single-date hyperspectral analysis:

```text
Scene/QA
  → Crop and band screening
  → Spectral indices and PCA
  → NDVI baseline and k-means clustering
  → Conditional validation
  → Threshold sensitivity, COGs, report, and results package
```

### Preprocessing

- Opens the Tanager ortho surface-reflectance HDF5 scene.
- Removes unreliable spectral regions, including atmospheric water-vapour windows, wavelengths below 400 nm, and wavelengths above 2450 nm.
- Applies no-data, cloud, and cirrus masking.
- Extracts a central 512 × 512-pixel analysis crop.

### Spectral features

| Feature | Wavelengths | Purpose |
|---|---|---|
| NDVI | 860 nm / 665 nm | Baseline vegetation-greenness candidate map |
| NDRE | 790 nm / 720 nm | Red-edge spectral information |
| NDMI | 860 nm / 1650 nm | Vegetation and moisture-related spectral contrast |
| PCA | Full retained spectrum | Reduces spectral dimensionality for exploratory analysis |
| K-means | PCA-reduced spectra | Produces five unlabelled spectral clusters |

### Analysis

- The **baseline** identifies vegetation candidates using NDVI greater than 0.5.
- The **main exploratory method** applies PCA followed by k-means clustering to complete valid spectra.
- The clusters are unlabelled and must not be interpreted as vegetation, soil, water, crop, or land-cover classes.
- If an independent reference CSV is supplied, the notebook can train and evaluate a Random Forest classifier using spatially separated train, validation, and test blocks.
- Without reference labels, supervised accuracy is skipped; no accuracy metrics are invented.

## Key results

The following results are from the executed run on 12 November 2026.

| Item | Result |
|---|---|
| Vegetation-candidate pixels | 145,771 |
| Valid analysed pixels | 256,933 |
| Valid-pixel fraction | 98.01% |
| Baseline candidate area | 13,119.39 ha |
| NDVI threshold | 0.5 |
| PCA components | 10 |
| Spectral clusters | 5 |
| Supervised validation | Skipped: no independent reference labels |
| Run ID | `20261112T061915341103Z` |

The candidate area is a threshold-dependent estimate, not an error-adjusted area estimate. The NDVI threshold-sensitivity analysis shows how the candidate area changes with the threshold, but it does not validate the map or provide a confidence interval.

## Outputs

The notebook produces:

- `Project_Demeter_Report.html`: standalone HTML report with embedded figures, results, quality flags, provenance, and file inventory.
- `Project_Demeter_NDVI_COG.tif`: NDVI vegetation-candidate layer as a Cloud-Optimised GeoTIFF.
- `Project_Demeter_result_COG.tif`: exploratory spectral-cluster layer as a Cloud-Optimised GeoTIFF.
- `Project_Demeter_metadata.json`: provenance, configuration, software versions, attribution, and processing information.
- CSV files for threshold sensitivity, mean spectra, and validation status.
- PNG figures for the scene, QA masks, spectral features, clustering, and threshold sensitivity.
- `Project_Demeter_results.zip`: packaged results.

## How to run

### Option 1: Google Colab

1. Open `Project_Demeter.ipynb` in Google Colab.
2. Run the first code cell. It clones the course repository and installs the required packages.
3. Run the remaining cells in order.
4. The notebook will download the Tanager HDF5 scene if it is not already available locally. The file is approximately 1 GB.
5. Open `Project_Demeter_Report.html` from the output folder to view the full report.

### Option 2: Local Python environment

1. Install Python 3.10 or later.
2. Install the required packages:

```bash
pip install requests h5py numpy matplotlib pandas scipy scikit-learn joblib rasterio rioxarray xarray geopandas shapely
```

3. Place `hsi_utils.py` in the project folder or ensure the course repository is available.
4. Open and run `Project_Demeter.ipynb` from top to bottom.
5. Find the generated report and geospatial outputs in the `demeter_outputs` directory.

### Reference labels

To enable supervised validation, provide a CSV file with the following columns:

```csv
row,col,label,split
```

- `row` and `col` must be local crop pixel coordinates.
- `label` must contain the reference class label.
- `split` must contain `train`, `validation`, or `test`.
- Reference samples must be spatially separated so that the same 40 × 40-pixel block does not appear in more than one split.

Update `labels_csv` in the configuration cell before running the notebook.

## Validation status

No independent reference labels were supplied for the executed run. Therefore:

- No overall accuracy, F1 score, confusion matrix, or per-class accuracy is reported.
- No map-area confidence interval is reported.
- The vegetation-candidate map is exploratory and must not be treated as a validated land-cover classification.
- Future validation should use independently interpreted reference samples that are not derived from the NDVI map or spectral clusters.

## Limitations

- The analysis uses one acquisition date and cannot assess temporal change.
- Cloud, cirrus, shadow, sun glint, and mixed pixels can affect the spectral indices and clusters.
- Exploratory clusters have no verified material identity.
- The candidate area depends on the selected NDVI threshold.
- The workflow does not diagnose crop health, disease, yield, or species.
- Independent validation is required before operational decision-support use.

## Data attribution

- Tanager STAC Data, available at https://www.planet.com/data/stac © 2025 Planet Labs PBC, CC-BY-4.0.
- NDVI: Rouse et al. (1974), *NASA Special Publication*, 351, 309–317.
- NDRE: Gitelson and Merzlyak (1994), *Journal of Plant Physiology*, 143(3), 286–292; Barnes et al. (2000), *Remote Sensing of Environment*, 74(3), 584–593.
- NDMI: Gao (1996), *Remote Sensing of Environment*, 58(3), 257–266.

## AI‑Assisted Development

The project made use of AI tools (e.g., ChatGPT, Gemini, gIQ AI Assistant, Perplexity) for:

- Code generation and refactoring  
- Debugging and performance improvements (e.g., tiled processing)  
- Drafting documentation and usage guidelines  

All architectural choices, final code, and interpretation remain the responsibility of **Team Demeter**.
