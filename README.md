# Project Demeter (Draft, revise info and revert changes from template)

Hyperspectral Vegetation Mapping of Puglia, Italia  
Space Academy 2026 · Hyperspectral course · Final graduation project  
Version: 13 November 2026

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mariolinoiii/team_demeter_hyperspectral_project/blob/main/Project_Demeter.ipynb)

## Problem

Project Demeter helps agricultural and environmental analysts prioritise vegetation inspection near Massafra, Puglia, Italia. It produces NDVI vegetation candidates and exploratory spectral clusters from one Tanager scene—not confirmed cropland, crop species, health, disease or yield.

## Data

- Tanager scene: `20250430_101724_87_4001`, ortho surface-reflectance HDF5; acquired 30 April 2025, 10:17:24.870 UTC.
- Analysis AOI: central 512 × 512-pixel crop, 30 m resolution, EPSG:32633; 235.9296 km².
- Crop bounds (W, S, E, N): 17.059788602, 40.504259480, 17.245570198, 40.645918944.
- External reference: ESA WorldCover 2021 v200, retrieved automatically through Microsoft Planetary Computer.
- No manual labels are planned. The AOI is an image crop, not an administratively restricted boundary.

## Method

```text
Scene QA → crop/band screening → NDVI/NDRE/NDMI and PCA
→ NDVI > 0.5 and five spectral clusters
→ WorldCover agreement → uncertainty, COGs and HTML report
```

The workflow screens no-data, cloud/cirrus and unreliable bands; calculates NDVI (860/665 nm), NDRE (790/720 nm) and NDMI (860/1650 nm); and applies 10-component PCA and k-means. SAM/SID and normalised NNLS provide additional cluster-prototype exploration. Clusters have no verified land-cover identities.

## Key results and limitations

Results from run `20261113T101551_705207Z`, reported 13 November 2026:

| Result | Value |
|---|---:|
| Valid analysed pixels | 256,933 — 98.01% of crop |
| NDVI vegetation-candidate pixels / area | 145,771 / 13,119.39 ha |
| Vegetation agreement with WorldCover: OA / F1 / IoU | 0.696676 / 0.787899 / 0.650027 |
| Conditional 95% vegetation-F1 block interval | 0.765342–0.809086 |
| NDVI / all-vegetation baseline macro-F1 | 0.627832 / 0.463157 |
| NDVI / all-vegetation baseline positive F1 | 0.787899 / 0.926314 |
| Cropland agreement F1 | 0.273993 |

The descriptive benchmark—vegetation F1 ≥ 0.80 and above the constant baseline—was not met. It is not a course pass/fail or operational accuracy threshold.

These are coarse WorldCover agreement statistics, not ground-truth accuracy. Limits include the 2021/2025 date mismatch, 10 m/30 m aggregation, reference errors, mixed pixels and different class definitions. Greenness is not cropland. Block intervals exclude reference errors and do not establish true-accuracy or map-area confidence intervals.

## Repository structure

```text
team_demeter_hyperspectral_project/
├── README.md
├── Project_Demeter.ipynb
├── Project_Demeter_Presentation.pdf
├── requirements.txt
├── outputs/
│   ├── core_analysis/       # Main COGs, metadata, analysis tables and figures
│   └── ...                  # Report, scene/crop figures and supporting outputs
└── validation/              # WorldCover agreement CSVs and comparison plots
```

The project uses descriptive notebook and presentation filenames in place of the template’s `project.ipynb` and `presentation.pdf`. Main result layers and metadata are grouped under `outputs/core_analysis/`.

Main products:
- `Project_Demeter_NDVI_COG.tif`: continuous NDVI.
- `Project_Demeter_baseline_COG.tif`: binary vegetation-candidate mask.
- `Project_Demeter_result_COG.tif`: unlabelled spectral clusters.
- `Project_Demeter_metadata.json`: provenance and processing information.
- `Project_Demeter_Report.html`: standalone report with embedded figures.
- Agreement metrics, per-class tables, confusion matrices and conditional intervals.

## How to run

1. Open `Project_Demeter.ipynb` using the Colab badge, or install `requirements.txt` in a local Jupyter environment.
2. Run the setup cell; it installs dependencies in Colab and loads the embedded course helper.
3. Review `CONFIG`, then use Restart & Run All.
4. Allow the approximately 1 GB Tanager download if absent. WorldCover is fetched automatically.
5. Inspect the generated report, figures and technical checks; save the executed notebook.

New runs write to `demeter_outputs/<run_id>/` and produce `Project_Demeter_results.zip`. The repository’s `outputs/` and `validation/` folders contain the selected submission artifacts.

Local caches are controlled by `cache_enabled` and refresh flags in `CONFIG`. Set `refresh_cache=True` to recompute cached stages; return it to `False` for reuse. Do not commit raw HDF5 files or local caches.

## Team contributions

| Member | Contribution |
|---|---|
| Mariolino Daniel III Julabar | Project lead and primary developer |
| AlReem AlRowahi | Project design, testing and analysis support |

## Credits and responsibility

Tanager STAC Data, available at [www.planet.com/data/stac](https://www.planet.com/data/stac) © 2025 Planet Labs PBC, CC-BY-4.0. ESA WorldCover 2021 v200, European Space Agency, CC-BY-4.0; Microsoft Planetary Computer. Methods and structure draw on the supplied Space Academy 2026 course materials; retain their authorship and licence notices.

## AI‑Assisted Development

The project made use of AI tools (e.g., ChatGPT, Gemini, gIQ AI Assistant, Perplexity) for:

- Code generation and refactoring  
- Debugging and performance improvements (e.g., tiled processing)  
- Drafting documentation and usage guidelines  

All architectural choices, final code, and interpretation remain the responsibility of **Team Demeter**.
