# Zenodo Data Archive — Fe-Mo TCP Phase Dataset

This file documents the data files that are archived on Zenodo as supplementary material to:

> M. Seiser et al., *Machine-learning prediction of Fe-Mo TCP phase stability from BOP descriptors*, npj Computational Materials (2025).

DOI: **TODO — insert Zenodo DOI after upload**

---

## Data storage overview

| Location | Contents |
|----------|----------|
| **Git repository** (GitHub) | Notebooks, scripts, Tools package, curated DFT data, Atoms objects, derived descriptors (CSV), model hyperparameter JSONs, validation data |
| **Zenodo** (this archive) | Raw BOP descriptor pkl files — require BOPfox to recompute |
| **Sciebo** | Trained ML learning-curve results (`concatenation_results_*.pkl`) — expensive to recompute |
| **Rebuilt on demand** | Final ensemble regressors (`voting_regressor_*.pkl`) — run notebook 07 from `concatenation_results` |

---

## Files included in Zenodo archive

### 1. Raw BOP training descriptors (~27 MB)

Raw BOPfox moment descriptor tables for all training structures
(simple TCP: A15, C14, C15, C36, σ, χ, μ and reference bcc/fcc/hcp phases).
Direct output of `REQUIRE_RAW_DATA_05_ComputeBOPFeatures.ipynb`.

The CNAV-averaged variants (`CNAV_parallel_Fe-Mo_*.csv`) are derived from these and
are already in the git repository.

| File | Size | Description |
|------|------|-------------|
| `Fe-Mo/Descriptors/parallel_Fe-Mo_initial_0.7projections_0.5os_table_WUBIND_20.pkl` | 7.2 MB | BOP raw moments, initial geometry, 0.7d-projections/0.5os model, 20 moments |
| `Fe-Mo/Descriptors/parallel_Fe-Mo_initial_canonical_table_WUBIND_16.pkl` | 6.5 MB | BOP raw moments, initial geometry, canonical (W-like) model, 16 moments |
| `Fe-Mo/Descriptors/parallel_Fe-Mo_relaxed_0.7projections_0.5os_table_WUBIND_20.pkl` | 7.2 MB | BOP raw moments, relaxed geometry, 0.7d-projections/0.5os model, 20 moments |
| `Fe-Mo/Descriptors/parallel_Fe-Mo_relaxed_canonical_table_WUBIND_16.pkl` | 6.5 MB | BOP raw moments, relaxed geometry, canonical (W-like) model, 16 moments |

### 2. BOP prediction descriptors for complex TCP phases (~1.3 GB)

Pre-computed BOP moment descriptors for the complex TCP phases (R, M, P, δ),
used in `09_PrepareFeaturesPrediction.ipynb`. Require BOPfox to recompute;
a download fallback is built into notebook 09.

| File | Size | Description |
|------|------|-------------|
| `Fe-Mo/Descriptors/PREDICTION_Fe-Mo_R_0.7dprojections_0.5os_table_WUBIND_16.pkl` | 104 MB | BOP prediction descriptors, R phase |
| `Fe-Mo/Descriptors/PREDICTION_Fe-Mo_M_0.7dprojections_0.5os_table_WUBIND_16.pkl` | 102 MB | BOP prediction descriptors, M phase |
| `Fe-Mo/Descriptors/PREDICTION_Fe-Mo_P_0.7dprojections_0.5os_table_WUBIND_16.pkl` | 220 MB | BOP prediction descriptors, P phase |
| `Fe-Mo/Descriptors/PREDICTION_Fe-Mo_delta_0.7dprojections_0.5os_table_WUBIND_16.pkl` | 877 MB | BOP prediction descriptors, δ phase |

---

## Files in the git repository (not in Zenodo)

| File / Pattern | Description |
|----------------|-------------|
| `Fe-Mo/FullyCuratedParsedBriefSummary.pkl` | Curated DFT dataset (76 KB) |
| `Fe-Mo/Atomsobjects/Fe-Mo-POSCAR-initial-rescaled-AtomsObjects.pkl` | ASE Atoms objects, initial geometry (348 KB) |
| `Fe-Mo/Atomsobjects/Fe-Mo-POSCAR-relaxed-all-rescaled-AtomsObjects.pkl` | ASE Atoms objects, relaxed geometry (420 KB) |
| `Fe-Mo/Atomsobjects/SUBLATICETAGS_POSCAR-initial.pkl` | Sublattice tags, initial geometry (4 KB) |
| `Fe-Mo/Atomsobjects/SUBLATICETAGS_POSCAR-relaxed-all.pkl` | Sublattice tags, relaxed geometry (4 KB) |
| `Fe-Mo/validation_data/ValidationFullyCuratedParsedBriefSummary.pkl` | Curated DFT dataset for validation structures (8 KB) |
| `Fe-Mo/Descriptors/CNAV_parallel_Fe-Mo_*.csv` | CNAV-averaged BOP training descriptors (derived from Zenodo raw pkl) |
| `Fe-Mo/Descriptors/Fe-Mo-*ACE-CNAV.csv` | ACE training descriptors |
| `Fe-Mo/Descriptors/soap_features_*.csv` | SOAP training descriptors |
| `Fe-Mo/results/*_options.json` | Hyperparameter options per model |
| `Fe-Mo/results/PREDICTION__*.csv` | Prediction output tables |

---

## Files on Sciebo (trained ML results)

These pkl files store the full learning-curve outputs from forward recursive feature
selection (notebook 07). They are expensive to recompute (~hours of CPU time) but are
not needed for routine use — the final voting regressors can be rebuilt from them.

| File | Size | Description |
|------|------|-------------|
| `Fe-Mo/results/concatenation_results_EF_nmhcp_no_hcp_bcc_fcc_KernelRidge.pkl` | 3.3 MB | KRR learning curves |
| `Fe-Mo/results/concatenation_results_EF_nmhcp_no_hcp_bcc_fcc_MLP.pkl` | 8.4 MB | MLP learning curves |
| `Fe-Mo/results/concatenation_results_EF_nmhcp_no_hcp_bcc_fcc_RandomForest.pkl` | 3.1 MB | Random Forest learning curves |
| `Fe-Mo/results/concatenation_results_EF_nmhcp_FixedOS.pkl` | 2.4 MB | KRR learning curves (fixed onsite variant) |
| `Fe-Mo/results/concatenation_results_EF_nmhcp_FixedNames.pkl` | 1.2 MB | KRR learning curves (fixed names variant) |

Sciebo link: **TODO — insert Sciebo share link**

---

## Files rebuilt on demand

These files are **not stored anywhere** — they are generated by running notebook 07
(`07_MachineLearn-ModelSelection.ipynb`) from the `concatenation_results` above:

- `Fe-Mo/results/voting_regressor_KernelRidge.pkl` (~23 MB)
- `Fe-Mo/results/voting_regressor_MLP.pkl` (~15 MB)
- `Fe-Mo/results/voting_regressor_RandomForest.pkl` (~198 MB)
- `Fe-Mo/results/regressors_bag_KernelRidge.pkl`
- `Fe-Mo/results/KernelRidge_inportances.pkl`

---

## Upload checklist

```bash
# Zenodo — upload via web UI at https://zenodo.org/deposit
# Files to upload (from repository root):
Fe-Mo/Descriptors/parallel_Fe-Mo_initial_0.7projections_0.5os_table_WUBIND_20.pkl
Fe-Mo/Descriptors/parallel_Fe-Mo_initial_canonical_table_WUBIND_16.pkl
Fe-Mo/Descriptors/parallel_Fe-Mo_relaxed_0.7projections_0.5os_table_WUBIND_20.pkl
Fe-Mo/Descriptors/parallel_Fe-Mo_relaxed_canonical_table_WUBIND_16.pkl
Fe-Mo/Descriptors/PREDICTION_Fe-Mo_R_0.7dprojections_0.5os_table_WUBIND_16.pkl
Fe-Mo/Descriptors/PREDICTION_Fe-Mo_M_0.7dprojections_0.5os_table_WUBIND_16.pkl
Fe-Mo/Descriptors/PREDICTION_Fe-Mo_P_0.7dprojections_0.5os_table_WUBIND_16.pkl
Fe-Mo/Descriptors/PREDICTION_Fe-Mo_delta_0.7dprojections_0.5os_table_WUBIND_16.pkl

# Sciebo — upload concatenation_results_*.pkl files (see table above)
```
