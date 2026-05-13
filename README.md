# Phycocyanin Hybrid Model

This repository contains research scripts and supporting spreadsheets for the phycocyanin retrieval workflow built around Sentinel-3 OLCI data.

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

### `hybrid_model`

Purpose: Apply the full hybrid phycocyanin model to an atmospherically corrected OLCI image.

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
