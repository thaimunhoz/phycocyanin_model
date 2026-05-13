# phycocyanin_model

This repository contains research scripts and supporting spreadsheets for a phycocyanin retrieval workflow built around Sentinel-3 OLCI data. The code is organized by processing stage rather than as a packaged Python module.

The project currently looks like a working research codebase: most scripts are meant to be run manually, many input and output locations are hard-coded, and several scripts depend on local Excel or raster files that are not fully portable yet.

## Folder overview

### `atmospheric_correction`

Purpose: prepare OLCI reflectance for downstream modeling.

Files:

- `Py6_OLCI_mapaquali.py`: runs the Py6S radiative transfer model band by band using OLCI spectral response functions and scene geometry extracted from Sentinel-3 `.nc` metadata files.
- `RTE_OLCI_mapaquali.py`: applies the atmospheric correction equation to TOA reflectance rasters and writes a corrected multi-band GeoTIFF.
- `olci_bands.xlsx`: band metadata used by the correction workflow.
- `6S_parameters_OLCI_03102021.json`: saved Py6S outputs used later by the radiative transfer equation.
- `S3A_FRS_1nm.xlsx`: interpolated spectral response function data used by the 6S step.

Typical use:

1. Configure the paths inside `Py6_OLCI_mapaquali.py` so they point to your Sentinel-3 tie geometry files and local SRF tables.
2. Run `Py6_OLCI_mapaquali.py` to generate the 6S parameter JSON.
3. Configure the paths inside `RTE_OLCI_mapaquali.py` for the TOA reflectance bands and the JSON created above.
4. Run `RTE_OLCI_mapaquali.py` to create the atmospherically corrected `Rrs` raster stack.

Notes:

- These scripts rely on `Py6S`, `xarray`, `pandas`, `numpy`, and `GDAL`.
- The output of this folder feeds the `hybrid_model` folder.

### `OLCI_bands_simulation`

Purpose: simulate OLCI bands from higher-resolution or field spectra and visualize spectral resampling results.

Files:

- `leitura_FRS.py`: reads OLCI spectral response sheets and interpolates them to 1 nm spacing.
- `OLCI_band_simulation.py`: applies normalized spectral response functions to in situ spectra to simulate OLCI band reflectance values.
- `plot.py`: compares original spectra with resampled PRISMA and OLCI spectra using plots.
- `S3A_OLCI_SRF.xlsx`, `S3B_OLCI_SRF.xlsx`: original spectral response definitions.
- `S3A_FRS_1nm.xlsx`, `S3B_FRS_1nm.xlsx`: interpolated 1 nm spectral response tables.
- `S3A_FRS_1nm_clip.xlsx`, `S3B_FRS_1nm_clip.xlsx`: clipped response tables used in simulation.

Typical use:

1. Run `leitura_FRS.py` if you need to regenerate the 1 nm spectral response tables from the original SRF spreadsheets.
2. Update the path to the field spectra workbook in `OLCI_band_simulation.py`.
3. Run `OLCI_band_simulation.py` to generate simulated OLCI-band reflectance outputs.
4. Use `plot.py` to compare original and resampled spectra visually.

Notes:

- This folder is mostly for preprocessing and spectral analysis rather than final map production.
- The generated simulation tables appear to support later training and algorithm development.

### `Training`

Purpose: build and evaluate the Random Forest classifier used by the hybrid phycocyanin workflow.

Files:

- `features_selection.py`: exploratory feature ranking using Fisher score, PPS score, pairplots, and correlation analysis.
- `RF_feature_choice.py`: tests different Pearson-correlation thresholds to remove collinear features and evaluates classification performance.
- `RF_hyperparameters.py`: searches for good Random Forest hyperparameters using randomized search and grid search.
- `RF_MonteCarlo.py`: performs repeated train/test splits to choose a representative split and exports training and testing tables.
- `RF_training.py`: trains the final Random Forest classifier and plots a confusion matrix plus summary metrics.
- `features_initial.xlsx`, `features_selected.xlsx`: feature tables used in feature-selection and model-building steps.
- `RF_Train.xlsx`, `RF_Test.xlsx`: curated train/test tables for the final classifier.
- `Spectral_features.xlsx`, `S3_Simulated_Bands.xlsx`: supporting training inputs.

Typical use:

1. Start with `features_selection.py` to inspect which spectral metrics are most informative.
2. Run `RF_feature_choice.py` to narrow the feature set and evaluate correlation-based feature pruning.
3. Run `RF_hyperparameters.py` to identify promising Random Forest settings.
4. Run `RF_MonteCarlo.py` to choose a stable training/testing split.
5. Run `RF_training.py` to train and evaluate the final classifier.

Notes:

- These scripts rely on `scikit-learn`, `pandas`, `numpy`, `matplotlib`, `seaborn`, `ppscore`, and `skfeature`.
- The output training tables are consumed by the `hybrid_model` folder.

### `hybrid_model`

Purpose: apply the full hybrid phycocyanin model to an atmospherically corrected OLCI image.

Files:

- `hybrid_model_mapaquali.py`: loads the corrected OLCI raster, computes spectral indices, classifies pixels with a Random Forest model, then applies a class-specific bio-optical algorithm to estimate phycocyanin concentration.
- `RF_Train.xlsx`: training table for the classifier.
- `Train_oga.xlsx`: training data for the low-concentration linear model.
- `Train_liu.xlsx`: training data for the high-concentration linear model.

What the script does:

1. Reads selected OLCI bands from the corrected raster.
2. Computes spectral indices such as `SIM05`, `SY00`, `BE16`, `NI5`, `LH5`, and `LH4`.
3. Uses a Random Forest classifier to assign each valid pixel to a concentration class.
4. Applies one linear bio-optical model for low-phycocyanin pixels and another for high-phycocyanin pixels.
5. Writes output rasters for the classification and concentration maps.

Important note:

- `hybrid_model_mapaquali.py` appears incomplete near the final output section. One `CreateGeoTiff(...)` call for the concentration raster is cut off in the current file, so this script likely needs a quick repair before it can run end-to-end.

## Recommended workflow

If you want to run the full pipeline from raw OLCI inputs to phycocyanin maps, the intended order appears to be:

1. Use `OLCI_bands_simulation` to prepare or inspect spectral response functions and simulated band datasets.
2. Use `Training` to select features, tune the classifier, and produce the final Random Forest training tables.
3. Use `atmospheric_correction` to generate 6S parameters and convert TOA reflectance to atmospherically corrected `Rrs`.
4. Use `hybrid_model` to classify pixels and estimate phycocyanin concentration.

## How to run the scripts

These scripts are plain Python files, so the usual pattern is:

```powershell
python .\Training\RF_training.py
python .\atmospheric_correction\Py6_OLCI_mapaquali.py
python .\hybrid_model\hybrid_model_mapaquali.py
```

Before running anything, update the hard-coded file paths inside each script. Most of them still point to the original author’s `G:\...` directories.

## Suggested environment

At minimum, expect to need packages in this range:

- `numpy`
- `pandas`
- `matplotlib`
- `scipy`
- `scikit-learn`
- `seaborn`
- `xarray`
- `Py6S`
- `gdal`
- `ppscore`
- `skfeature-chappers`
- `openpyxl`

A simple setup could be:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install numpy pandas matplotlib scipy scikit-learn seaborn xarray Py6S ppscore openpyxl
```

For `GDAL` and `skfeature`, installation can be more system-specific on Windows, so you may want to install them through Conda if `pip` gives trouble.

## Practical cleanup ideas

If you plan to keep developing this repository, the highest-value improvements would be:

1. Replace hard-coded paths with relative paths or a small config file.
2. Add a `requirements.txt` or `environment.yml`.
3. Separate reusable functions from one-off notebook-style scripts.
4. Repair and test `hybrid_model_mapaquali.py`.
5. Add small sample inputs so the workflow can be reproduced more easily.

## Current limitations

- The code is not yet packaged as a reusable library.
- Some scripts write `.csv` outputs while the repository currently stores `.xlsx` versions of related files.
- Several files use Portuguese variable names and comments, which is fine internally but may slow down onboarding for new collaborators.
- Reproducibility depends on external local datasets that are not fully included in the repository.
