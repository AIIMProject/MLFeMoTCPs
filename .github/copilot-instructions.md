# Copilot Instructions

## Project Overview

This repository implements a machine-learning pipeline for predicting properties (primarily formation energy `EF`) of intermetallic alloy structures from DFT data.
The primary focus is the **Fe-Mo** binary system (ignore the `Cr-Co-W/` directory). The project underpins a manuscript submitted to **npj Computational Materials** (post-acceptance revision stage, 2026).

### Research Context

The paper demonstrates that encoding **domain knowledge** at three levels into ML descriptors enables data-efficient prediction of complex TCP phase stability:
1. **Chemical**: Volume scaling via Vegard's law (linear interpolation of elemental volumes)
2. **Crystallographic**: Coordination-resolved averaging (**CNavg**) — features averaged over atoms sharing the same coordination number (Wyckoff-site-aware), rather than plain unit-cell averaging
3. **Local bonding**: Chemistry-aware descriptors (BOP moments, ACE, SOAP)

**TCP phases studied**:
- *Training* (simple, 2–5 Wyckoff sites): A15, C15, C14, C36, σ, χ, μ
- *Prediction* (complex, 11–14 Wyckoff sites): R, M, P, δ

**Key results**: RMSE improves from ~150 meV/atom (baseline) → **20–25 meV/atom** (KRR + ACE/BOP/SOAP with CNavg). R-phase predicted stable near 1:1 composition, validated by XRD + Rietveld refinement at 1700 K.

The workflow spans **Fe-Mo**, using multiple descriptor families (BOP moments, ACE, SOAP, atomic/Magpie) and multiple ML regressors (Random Forest, MLP, SVR, Kernel Ridge Regression).

## Environment

Conda environment name: `datasets_ml` (Python 3.10).

```bash
conda activate datasets_ml
```

No automated test runner is configured. Ad-hoc test scripts exist in `Scripts/Test*.py` and can be run directly:

```bash
python Scripts/TestSoapFeatures.py
python Scripts/TestFeatureConcatenation.py
```

The `Tools/` package (`datasetsml-tools`) is installed in editable mode:

```bash
pip install -e Tools/
```

## Notebook Workflow (Sequential)

The numbered notebooks form the main pipeline:

| Prefix | Purpose |
|--------|---------|
| `00_` | Parse DFT output → `FullyCuratedParsedBriefSummary.pkl` (called **BS**) |
| `01_` | Curate dataset using E-V curves (Birch-Murnaghan fits) |
| `02_` | Characterize dataset statistics and coverage |
| `03_` | Prepare/split dataset and `AtomsObjects` pickles |
| `04_` | Compute ACE and Library descriptors |
| `05_` | Compute BOP (Bond Order Potential) features via BOPfox → `Fe-Mo/Descriptors/CNAV_parallel_FeMo_*_WUBIND_16.csv` |
| `07_` | ML model training & hyperparameter search (one notebook per algorithm) |
| `08_` | Analyse and compare fitted models |
| `09_`–`11_` | Prepare features for new structures, validate predictions |

## Architecture

### Data Layout (per binary system, e.g. `Fe-Mo/`)

```
Fe-Mo/
  FullyCuratedParsedBriefSummary.pkl   # BS: curated DFT results, indexed by compound+mag
  Atomsobjects/                        # ASE Atoms objects as pickles
  Descriptors/                         # All computed feature files (CSV or pkl)
  results/                             # Trained model options (JSON) and outputs (pkl)
  graphs/                              # Generated figures
  data/                                # Raw DFT output files
```

### Key Classes and Utilities (`Tools/DatasetTools/`)

- **`Dataset`** (`DatasetOperator.py`) — central data accessor; loads BS, all feature groups, aligns indices, adds `random` baseline feature.  
  ```python
  DS = Dataset('Fe-Mo', target_name='EF_fmbcc')
  DS.BS          # pandas DataFrame with DFT values
  DS.Features    # dict[str, DataFrame] of feature groups
  DS.target      # pandas Series, the regression target
  ```
- **`load_fully_curated_briefsummary(dataset)`** — loads `{dataset}/FullyCuratedParsedBriefSummary.pkl`.
- **`load_features(dataset)`** — returns `dict[str, DataFrame]` of all descriptor groups from `{dataset}/Descriptors/`.
- **`CaseNamer`** (`Tools.py`) — generates canonical file-name strings for model outputs based on parameters (CASE, MODEL, CUTOFF, EMODE, CRITERION, TARGET).
- **`ModelOptions`** (`ModelSelection.py`) — saves/loads hyperparameter options as JSON in `{dataset}/results/`.
- **`need_to_update(afile)`** — recomputes a cached file only if the source script is newer than the cached file (used throughout notebooks and scripts).
- **`EVCurvesTools`** — Birch-Murnaghan EOS fitting using `ase.eos`; `eV_per_angstrom3_to_GPA = 160.21`.

### Feature Groups and Naming

Feature files live in `{dataset}/Descriptors/` and are loaded by key:

| Key | File pattern |
|-----|-------------|
| `atomic` | `matminer_atomic_features.pkl` |
| `dataset` | `DatasetFeatures.pkl` (contains `Mag`, `Structure` columns) |
| `SOAP_canonicalW_small` / `SOAP_specific_small` | SOAP CSV files |
| `Pyscal` | `CNAVPyscal.pkl` |
| `ACE`, `NOZERO-ACE`, `Canonical ACE`, … | `{dataset}-*-ACE-CNAV.csv` |
| `Canonical BOP`, `0.7dProjections 0.5OS BOP`, … | `CNAV_parallel_{dataset}_…_WUBIND_16.csv` |

CNAV = *Common Neighbor Analysis Vectors*. "No CNAV" variants strip these columns.

### Index Convention

Every DataFrame (BS, features, targets) shares the same **compound index** in the format:
- `{StructureName}_{MagConfig}` — e.g., `BccFe_FM`, `FeMo_NM`, `A15_FeMo_FM`
- Magnetic configs: `FM` (ferromagnetic), `NM` (non-magnetic)
- `DS.allindex` is the intersection of all feature indices; all features are `.loc[allindex]`-filtered.

### System Naming Duality

- Hyphenated: `'Fe-Mo'` — used for dataset path (`Fe-Mo/`), loading, and display.
- Concatenated: `'FeMo'` — used within filenames and some variable names.

Conversions: `system = dataset.replace('-', '')`, `components = dataset.split('-')`.

### BOP Parameters (`.bx` files)

Two distinct types of `.bx` files exist:
- **`models/*.bx`** — ASCII text files with BOPfox model parameters (bond integrals, repulsive terms). Human-readable.
- **`bopfox_keys.bx`** (and similar index files) — Pickled Python objects listing valid BOPfox parameter key names. Do not open as text.

**BOP model configurations** (defined in `05_ComputeBOPFeatures.ipynb` / `GetBopFeatures.py`):

| Model key | Description |
|-----------|-------------|
| `canonical` | Replace Fe→W, Mo→W; use W canonical model |
| `0.7projections_0.5os` | Bond integral scale 0.7, onsite levels scale 0.5, d-orbitals |
| `0.7projections_0.5os_0scf` | Same + `scfsteps=0` |
| `0.7projections_0.5os_10scf_jii8.0` | `scfsteps=10`, onsite_energy 8.0 |
| `0.7projections_0.5os_100scf_jii8.0` | `scfsteps=100`, onsite_energy 8.0 |

**BOP computation flow** (`05_ComputeBOPFeatures.ipynb`):
1. Load ASE `Atoms` objects via `load_atoms_objects(dataset, case, scaling)`
2. Generate `.bx` model file via `create_modelfile(...)` → `models/{dataset}-{components}_{model}.bx`
3. Run BOPfox via `BopfoxFeatures(...).featurize_dataframe(...)` with `globalmoments=16`, `cutoff='table'`
4. Cache raw output → `Fe-Mo/Descriptors/parallel_Fe-Mo_{case}_{model}_table_WUBIND_16.pkl`
5. Post-process: array expansion → **CN-averaging** (`gf.cn_average`) → shape factors → variance filtering
6. Save averaged features → `Fe-Mo/Descriptors/CNAV_parallel_Fe-Mo_{case}_{model}_table_WUBIND_16.csv`
7. Also save pre-selected (corr > 0.2) → `preselected_cnav_{model}_BOPds.pkl` and low-order → `smallorder_cnav_{model}_BOP.pkl`

**CN-averaging** groups atoms by coordination number (CN12–CN16); each output column has suffix `_0` (all atoms), `_CN12`, `_CN13`, etc. Normalisation is by `natoms` or NCP (number of coordination polyhedra vertices).

Caching uses simple file-existence checks (`os.path.exists`) with a `remake = False` flag to force recomputation.

### Key Notebooks

- **`07_MachineLearn-ModelSelection.ipynb`** — the central ML notebook: collects results from forward recursive feature selection runs and builds the final **ensemble models** used for prediction. This is the primary model-building notebook.
- **`05_ComputeBOPFeatures.ipynb`** — runs BOPfox on all crystal structures to compute BOP moment descriptors.
- Other `07_MachineLearn-*.ipynb` files (e.g., `-ACE-incomplete`, `-NonMag`, `-nmhcp`, `_yesterday`) are **legacy/experimental** variants; ignore them.

### ML Pipeline Pattern

The primary model is **Kernel Ridge Regression** (`ModelName = 'Kernel Ridge'`), target `EF_nmhcp`, on the Fe-Mo dataset with bcc/fcc/hcp phases excluded:
```python
DS = Dataset('Fe-Mo', target_name='EF_nmhcp',
             remove_phases_query='Phase != "bcc" and Phase != "fcc" and Phase !="hcp"')
```

Models are built using `sklearn.pipeline.Pipeline` with a scaler + regressor. Cross-validation uses custom stratified folds from `DS.get_folds()`. Results are saved as:
- `{dataset}/results/{ModelName}_options.json` — hyperparameters
- `{dataset}/results/concatenation_results_*.pkl` — fitted model outputs (learning curves from forward feature selection)

**Ensemble building** (`07_MachineLearn-ModelSelection.ipynb`):
1. Load saved feature-selection learning curves from `concatenation_results_{target_case}_{suffix}.pkl`
2. For each `(ModelName, FeatureName)` combination, create one `Pipeline` per learning-curve iteration, each with a `FunctionTransformer` that filters features using `filter_features(learning_curve, remove_structure=True)` prepended to the pipeline
3. Wrap all pipelines in a `VotingRegressor` → `voting_regressor[(ModelName, FeatureName)]`
4. Fit on training split; score with `score_fitted_model()`
5. Save with `joblib.dump()`:
   - `Fe-Mo/results/voting_regressor_KernelRidge.pkl`
   - `Fe-Mo/results/regressors_bag_KernelRidge.pkl`
   - `Fe-Mo/results/Fe-Mo_Kernel Ridge_OptimalScores_EF_nmhcp.pkl`
   - `Fe-Mo/results/KernelRidge_inportances.pkl`

Key helper functions (from `MLConveniences`): `filter_features`, `get_optimal_features`, `score_fitted_model`, `get_importances`, `get_bag_of_predictions`.

### External Dependencies (`dependencies/`)

Local source installs for domain-specific packages:
- `bopfoxfeaturizer` — BOPfox-based moment feature computation
- `PyCEF` / `python-ace` — ACE descriptor computation  
- `bopfox` / `bopdftprojections` — BOPfox simulation interface

### Matplotlib Defaults

Set globally in `Commoms.py`:
```python
plt.rc('text', usetex=True)
plt.rc('figure', figsize=(7, 5))
plt.rc('font', size=20)
```
LaTeX rendering is enabled by default. Feature label formatting (`get_str_formatted()`) returns LaTeX strings like `$\mu_{0}$`.

