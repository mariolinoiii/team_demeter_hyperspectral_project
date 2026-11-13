# Project Demeter
Hyperspectral Vegetation Mapping of Puglia, Italia — Space Academy 2026.

## Team contributions
| Member | Contribution |
|---|---|
| Mariolino Daniel III Julabar | Project lead and primary developer |
| AlReem AlRowahi | Project design, testing and analysis support |

## Scope and results
One Tanager crop; NDVI candidates and unlabelled spectral clusters. WorldCover 2021 v200 supplies coarse agreement, not ground-truth accuracy. No manual labels are planned. Run: 20261113T103007_431873Z. See the HTML report and validation CSVs.

## Run
Open Project_Demeter.ipynb, install dependencies and use Restart & Run All. The helper is embedded. First execution downloads the HDF5 if absent. Keep raw HDF5 and demeter_cache out of submission. CONFIG refresh_cache=True forces recomputation; restore False for reuse. Stage-specific refresh flags and country-scale requirements are documented in the notebook. requirements_used.txt records this run's versions.

## Delivery
COGs, metadata, crop geometry, validation CSVs/figures, report and ZIP. Review submission_checks.json. Presentation and submission timing remain separate tasks.

## Credits
Tanager STAC Data, available at www.planet.com/data/stac © 2025 Planet Labs PBC, CC BY 4.0.
ESA WorldCover 2021 v200, European Space Agency, CC BY 4.0; Microsoft Planetary Computer.
Supplied Space Academy 2026 helper and templates; retain their notices.
