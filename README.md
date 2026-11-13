# Project Demeter (Draft, revise info and revert changes from template)

**Hyperspectral Vegetation Mapping of Puglia, Italia**  
Space Academy 2026 · Hyperspectral course · Final graduation project

Team: Mariolino Daniel III Julabar · AlReem AlRowahi  
Theme: Agriculture  
Version: 13 November 2026

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mariolinoiii/team_demeter_hyperspectral_project/blob/main/Project_Demeter.ipynb)

## Problem

Project Demeter explores vegetation distribution and spectral variability near Massafra, Puglia, Italia, to help agricultural and environmental analysts prioritise locations for inspection.

The single-date Tanager hyperspectral workflow produces vegetation-index maps, an NDVI vegetation-candidate mask and exploratory spectral clusters. ESA WorldCover 2021 v200 provides a coarse external land-cover reference for quantitative agreement checks.

The project does not deliver validated land-cover classification, confirm cropland, identify crop species, or diagnose crop health, disease, yield or productivity.

## Team contributions

| Team member | Contribution |
|---|---|
| Mariolino Daniel III Julabar | Project lead and primary developer |
| AlReem AlRowahi | Project design, testing and analysis support |

## Data

| Dataset | Scene ID / product | Date | Role |
|---|---|---|---|
| Tanager | `20250430_101724_87_4001`, ortho surface-reflectance HDF5 | 30 April 2025, 10:17:24.870 UTC | Primary analysis |
| ESA WorldCover | 2021 v200; tile `ESA_WorldCover_10m_2021_v200_N39E015` | 2021 | Coarse external agreement reference |
| Ancillary source information | Catalogue footprint, source CRS/transform and no-data/cloud/cirrus masks | Source-associated | Geographic review, QA and export |

Image source: [Tanager STAC Data — Planet Labs](https://www.planet.com/data/stac/browser/tanager-core-imagery/agriculture/20250430_101724_87_4001/20250430_101724_87_4001.json).

WorldCover is retrieved automatically through the Microsoft Planetary Computer STAC API. No manual WorldCover download or manually labelled CSV is required.

No independent external Sentinel-2 or EnMAP scene is used. The optional Sentinel-2-like bandpass comparison is calculated from the same Tanager spectra and is not independent validation.

### Study area and final crop

| Item | Value |
|---|---|
| Location | Coastal–agricultural area near Massafra, Puglia, Italia |
| Analysis crop | Central 512 × 512 pixels |
| Pixel size | 30 × 30 m |
| CRS | EPSG:32633 |
| Row window | `[127, 639)` |
| Column window | `[182, 694)` |
| Pixel indexing | Zero-based; start inclusive, stop exclusive |
| Projected bounds (W, S, E, N), metres | 674520, 4486140, 689880, 4501500 |
| Geographic bounds (W, S, E, N), degrees | 17.059788602, 40.504259480, 17.245570198, 40.645918944 |
| Projected crop area | 235.9296 km² |
| Valid analysed area | 231.2397 km² |

The AOI is a georeferenced rectangular image crop, not an administrative boundary. An administrative-boundary comparison has not been performed.

The report includes full-scene true colour with the crop outlined, crop true colour, and crop geometry. The locally stretched RGB image may differ in appearance from the Planet website thumbnail.

## Method

```text
Scene and QA review
  → Crop and spectral-band screening
  → NDVI / NDRE / NDMI and PCA
  → Fixed NDVI vegetation baseline and k-means clustering
  → Cluster-prototype spectral exploration
  → Coarse agreement with ESA WorldCover
  → Sensitivity analysis, COGs, metadata, HTML report and ZIP
```

### Preprocessing

- Opens the Tanager ortho surface-reflectance HDF5 scene.
- Applies supplied good-band flags.
- Excludes atmospheric water-vapour regions, wavelengths below 400 nm and wavelengths above 2450 nm.
- Applies no-data, cloud and cirrus screening.
- Retains complete valid spectra within the crop.
- Does not impose spectral smoothing, continuum removal or spectral normalisation.

### Features and exploratory analysis

| Feature / method | Inputs | Purpose |
|---|---|---|
| NDVI | Bands nearest 860 and 665 nm | Vegetation-greenness baseline |
| NDRE | Bands nearest 790 and 720 nm | Red-edge spectral contrast |
| NDMI | Bands nearest 860 and 1650 nm | NIR–SWIR moisture-related contrast |
| PCA | Retained full spectra; 10 components | Dimensionality reduction |
| K-means | PCA-reduced spectra; five clusters | Exploratory spectral grouping |
| SAM / SID | Spectra and unlabelled cluster prototypes | Spectral-similarity exploration |
| Normalised NNLS | Sampled spectra and cluster prototypes | Exploratory reconstruction and mixture diagnostics |

The vegetation baseline uses a fixed threshold of NDVI > 0.5.

Clusters have no verified semantic identity. They must not be presented as confirmed vegetation, soil, water, crop or other land-cover classes.

The current workflow does not use supervised classifiers or manual-label training.

## Validation approach: coarse WorldCover agreement

Due to limited time and the absence of manually interpreted labels, ESA WorldCover 2021 v200 is used as a coarse external reference.

The notebook compares the fixed NDVI vegetation mask with:

1. WorldCover vegetation classes: `10, 20, 30, 40, 90, 95, 100`.
2. WorldCover cropland: class `40`.

WorldCover is mode-aggregated from its native 10 m grid to the georeferenced 30 m Tanager crop. All core-valid pixels with finite NDVI and non-zero WorldCover coverage are evaluated, including mixed pixels.

The assessment reports:

- Overall agreement: OA with respect to WorldCover.
- Per-class precision/UA and recall/PA.
- Per-class F1 and IoU.
- Macro-F1.
- Confusion matrices.
- Comparison with a constant all-vegetation baseline.
- Conditional 95% spatial-block bootstrap intervals.

WorldCover is not used for training or threshold tuning. There is no independent manually labelled train/test split.

The reported run uses 169 spatial blocks of 40 × 40 pixels and 500 bootstrap replicates. Blocks describe spatial variability; they do not create independent ground truth. The block size is provisional.

### Interpretation limits

These statistics quantify agreement with WorldCover, not true map accuracy.

- Temporal mismatch: annual 2021 WorldCover versus Tanager on 30 April 2025. Land-cover change and seasonality may cause disagreement.
- Resolution mismatch: 10 m classes are aggregated to 30 m pixels; mixed pixels affect assignments.
- Different definitions: NDVI measures single-date greenness, while WorldCover describes broad land cover. Cropland can be bare or fallow, and vegetation need not be cropland.
- Reference uncertainty: WorldCover is a classified product with its own errors.
- Cluster interpretation: spectral clusters have no one-to-one mapping to WorldCover classes.

Bootstrap intervals are conditional on the scene, fixed threshold and reference. They exclude WorldCover classification error and do not establish true-accuracy or map-area confidence intervals.

## Key results

Results below are from the supplied executed report:

- Run ID: `20261113T101551_705207Z`
- Report generated: 13 November 2026, 10:17:26 UTC

Later notebook edits do not themselves recalculate these values. A fresh execution produces a new run ID and report.

### Scene and analysis results

| Item | Result |
|---|---:|
| Vegetation-candidate pixels | 145,771 |
| Valid analysed pixels | 256,933 |
| Valid-pixel fraction | 98.01% |
| Candidate area | 13,119.39 ha |
| NDVI threshold | 0.5 |
| PCA components | 10 |
| Spectral clusters | 5 |

Candidate area is threshold dependent and is not error-adjusted.

### Agreement with WorldCover

| Reference comparison | Prediction | Overall agreement | Macro-F1 | Positive-class F1 | Positive-class IoU |
|---|---|---:|---:|---:|---:|
| Vegetation | Fixed NDVI threshold | 0.696676 | 0.627832 | 0.787899 | 0.650027 |
| Vegetation | All-vegetation baseline | 0.862742 | 0.463157 | 0.926314 | 0.862742 |
| Cropland | Fixed NDVI threshold | 0.430315 | 0.402619 | 0.273993 | 0.158744 |
| Cropland | All-vegetation baseline | 0.217333 | 0.178532 | 0.357064 | 0.217333 |

For NDVI vegetation versus WorldCover vegetation:

- Precision with respect to WorldCover: 0.993010.
- Recall with respect to WorldCover: 0.653016.
- Conditional 95% positive-F1 block interval: 0.765342–0.809086.

### Descriptive benchmark

The notebook reports a project-specific descriptive benchmark:

> Vegetation agreement F1 ≥ 0.80 and higher than the all-vegetation baseline’s positive F1.

This benchmark was not met.

It was introduced during project development, not mandated as a course pass/fail threshold or established as a pre-registered success criterion. It is not an operational accuracy requirement.

The constant baseline benefits from vegetation dominating the WorldCover reference. NDVI has lower vegetation-only F1 but higher macro-F1, indicating more balanced discrimination across the two reference classes.

The conclusion is therefore partial reference correspondence—not a general accuracy advantage or a failed software workflow.

## Outputs

Outputs are written under:

```text
demeter_outputs/<run_id>/
```

The notebook packages that run’s outputs into `Project_Demeter_results.zip`.

### Geospatial layers and metadata

- `core_analysis/Project_Demeter_NDVI_COG.tif`: continuous NDVI index.
- `core_analysis/Project_Demeter_baseline_COG.tif`: binary NDVI vegetation-candidate mask.
- `core_analysis/Project_Demeter_result_COG.tif`: unlabelled spectral-cluster map.
- `core_analysis/Project_Demeter_metadata.json`: configuration, provenance, versions and processing information.
- `crop_geometry.json`: crop window, transform, bounds and areas.
- `cropped_AOI.geojson`: geographic footprint of the analysis crop.
- `validation/worldcover_2021_aligned.tif`: aligned WorldCover reference labels.

### Agreement tables and figures

```text
validation/
├── worldcover_agreement_metrics.csv
├── worldcover_per_class_agreement.csv
├── worldcover_conditional_block_intervals.csv
├── worldcover_spatial_block_agreement.csv
├── vegetation_NDVI_fixed_threshold_agreement_confusion.csv
├── vegetation_All_vegetation_baseline_agreement_confusion.csv
├── cropland_NDVI_fixed_threshold_agreement_confusion.csv
├── cropland_All_vegetation_baseline_agreement_confusion.csv
├── validation_design_status.json
├── worldcover_2021_aligned.tif
├── worldcover_scene_comparison.png
├── worldcover_confusion_matrices.png
├── worldcover_agreement_map.png
└── worldcover_baseline_uncertainty.png
```

Threshold-sensitivity CSV and PNG files are saved under `core_analysis/`.

### Report and reproducibility records

- `Project_Demeter_Report.html`: standalone report with embedded figures, crop geometry, results, agreement tables, limitations, provenance and inventory.
- `README.md`: generated run documentation and team contributions.
- `requirements_used.txt`: installed dependency versions recorded for the run.
- `cache_events.json`: cached/computed stage log.
- `scalability_notes.json`: requirements and limitations for larger-scale processing.
- `submission_checks.json`: technical checks and unresolved review items.
- `manifest.json`: output sizes and SHA-256 checksums.

## How to run

### Google Colab

1. Open `Project_Demeter.ipynb` using the Colab badge above.
2. Run the setup cell to install dependencies and load the embedded course helper.
3. Review the configuration cell.
4. Use Restart & Run All and execute the notebook from top to bottom.
5. Allow the source HDF5 download if the scene is not already available locally.
6. Open the generated HTML report and inspect the validation tables, figures and technical checks.
7. Save the executed notebook with outputs and retain the results ZIP.

The source HDF5 is approximately 1 GB. Do not add it to the repository or submission.

### Local Jupyter environment

Install the dependencies:

```bash
pip install requests h5py numpy matplotlib pandas scipy scikit-learn joblib \
  rasterio rioxarray xarray geopandas shapely pyproj pystac-client \
  planetary-computer ipython ipykernel notebook
```

Then open `Project_Demeter.ipynb`, review `CONFIG`, and run from a fresh kernel.

The course helper is embedded in the notebook; a separate manual copy of `hsi_utils.py` is not required for this version.

The reported execution used Python 3.13.18. Other environments require compatibility testing. Use `requirements_used.txt` to inspect the versions recorded by a completed run; it is not a guarantee of cross-platform compatibility.

Internet access is required for initial package installation, scene download, catalogue access and WorldCover retrieval.

## Caching and refresh controls

The final notebook includes local caches for expensive spectral processing, aligned WorldCover labels and block-bootstrap assessment.

Configuration controls include:

```python
CONFIG["cache_enabled"] = True
CONFIG["refresh_cache"] = False

CONFIG["refresh_spectral_cache"] = False
CONFIG["refresh_worldcover_cache"] = False
CONFIG["refresh_agreement_cache"] = False
```

- Set `refresh_cache=True` to force recomputation of all cached stages.
- Use a stage-specific flag to refresh one processing group.
- Return refresh flags to `False` to reuse caches.
- Set `catalog_refresh=True` to rebuild the catalogue index.
- Source, configuration and code changes are included in cache invalidation.

Cache files belong in the local `demeter_cache` directory, not in the submitted results package. Never load pickle caches from an untrusted source.

Caching does not make the entire notebook an offline application; some operations may still require internet access.

## Technical checks and reproducibility status

The latest supplied report records 28 passing technical checks, including:

- Output shape and valid-pixel checks.
- Binary baseline and finite-NDVI range checks.
- COG existence and layout.
- CRS, transform and band descriptions.
- Raster-array round-trip consistency.
- WorldCover coverage and agreement-table presence.
- No raw HDF5 in the output package.

These checks do not certify:

- Successful clean-kernel execution of every later notebook edit.
- Human review of figure readability or geographic alignment.
- Independent ground-truth validation.
- Presentation completeness or on-time submission.

Run the final notebook in a fresh kernel, inspect the generated checks, and save the executed file before submission.

## Scalability

Monthly country-scale processing would require:

- Verification of acquisition availability, coverage and data-access constraints.
- Automated STAC discovery and versioned scene manifests.
- Consistent QA and spectral preprocessing.
- Windowed/tiled processing and batch orchestration.
- Retries, failure monitoring and resource budgeting.
- Central COG storage, metadata and result cataloguing.
- Harmonised feature/model policies across scenes and dates.
- Assessment of geographic and temporal transfer.

The current implementation demonstrates one crop, not complete monthly country-wide coverage.

Scene-specific k-means cluster IDs are not consistent semantic classes across scenes. WorldCover is an annual reference, not contemporaneous monthly ground truth.

## Limitations

- One acquisition date; no temporal-change assessment.
- Residual cloud, cirrus, shadow, glint and mixed pixels may affect results.
- Vegetation-candidate area depends on the NDVI threshold.
- Spectral clusters and prototypes have no verified material identity.
- Normalised NNLS is an exploratory reconstruction, not exact fully constrained unmixing.
- WorldCover agreement is limited by reference errors, date/resolution mismatch and class definitions.
- Conditional block intervals exclude reference error and do not estimate true map accuracy or error-adjusted area uncertainty.
- No crop-health, disease, yield or species diagnosis is supported.
- Stronger independent validation is required before operational accuracy claims.

## Data attribution and methods

- Tanager STAC Data, available at [www.planet.com/data/stac](https://www.planet.com/data/stac) © 2025 Planet Labs PBC, CC-BY-4.0.
- ESA WorldCover 2021 v200, European Space Agency, CC-BY-4.0; accessed through Microsoft Planetary Computer.
- Rouse et al. (1974), NASA SP-351, pp. 309–317: NDVI background.
- USGS, Normalized Difference Moisture Index: NIR–SWIR index interpretation.
- Supplied Space Academy 2026 course notebooks, project templates and `hsi_utils.py`: preprocessing, spectral analysis, scene selection, validation and product delivery. Retain the supplied authorship and licence notices.

The named index wavelengths describe this notebook’s implementation. No calibrated physiological retrieval or demonstrated hyperspectral accuracy advantage is claimed.

## AI-Assisted Development

AI tools, including ChatGPT, Gemini, gIQ AI Assistant and Perplexity, were used to assist with:

- Code generation and refactoring.
- Debugging, caching and reproducibility checks.
- Documentation, report layout and usage instructions.

AI assistance does not replace scientific validation or execution testing. Architectural decisions, final code, verification and interpretation remain the responsibility of Team Demeter.
