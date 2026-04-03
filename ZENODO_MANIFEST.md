# Zenodo Data Archive — Fe-Mo TCP Phase Dataset

This file documents the data files that are archived on Zenodo as supplementary material to:

> M. Seiser et al., *Machine-learning prediction of Fe-Mo TCP phase stability from BOP descriptors*, npj Computational Materials (2025).

DOI: **TODO — insert Zenodo DOI after upload**

---

## Files included in Zenodo archive

### 1. Raw BOP training descriptors (~27 MB)

These are the raw BOPfox moment descriptor tables for all training structures
(simple TCP: A15, C14, C15, C36, σ, χ, μ and reference bcc/fcc/hcp phases).
They are the direct output of `REQUIRE_RAW_DATA_05_ComputeBOPFeatures.ipynb`.

The CNAV-averaged variants (`CNAV_parallel_Fe-Mo_*.csv`) are derived from these files and
are already included in the git repository, so they do not need to be downloaded separately
for the main ML workflow.

| File | Size | Description |
|------|------|-------------|
| `Fe-Mo/Descriptors/parallel_Fe-Mo_initial_0.7projections_0.5os_table_WUBIND_20.pkl` | 7.2 MB | BOP raw moments, initial geometry, 0.7d-projections/0.5os model, 20 moments |
| `Fe-Mo/Descriptors/parallel_Fe-Mo_initial_canonical_table_WUBIND_16.pkl` | 6.5 MB | BOP raw moments, initial geometry, canonical (W-like) model, 16 moments |
| `Fe-Mo/Descriptors/parallel_Fe-Mo_relaxed_0.7projections_0.5os_table_WUBIND_20.pkl` | 7.2 MB | BOP raw moments, relaxed geometry, 0.7d-projections/0.5os model, 20 moments |
| `Fe-Mo/Descriptors/parallel_Fe-Mo_relaxed_canonical_table_WUBIND_16.pkl` | 6.5 MB | BOP raw moments, relaxed geometry, canonical (W-like) model, 16 moments |

### 2. BOP prediction descriptors for complex TCP phases (~1.3 GB)

These are pre-computed BOP moment descriptors for the complex TCP phases
(R, M, P, δ) used in `09_PrepareFeaturesPrediction.ipynb`.
They require BOPfox to recompute; a download fallback is built into notebook 09.

| File | Size | Description |
|------|------|-------------|
| `Fe-Mo/Descriptors/PREDICTION_Fe-Mo_R_0.7dprojections_0.5os_table_WUBIND_16.pkl` | 104 MB | BOP prediction descriptors, R phase |
| `Fe-Mo/Descriptors/PREDICTION_Fe-Mo_M_0.7dprojections_0.5os_table_WUBIND_16.pkl` | 102 MB | BOP prediction descriptors, M phase |
| `Fe-Mo/Descriptors/PREDICTION_Fe-Mo_P_0.7dprojections_0.5os_table_WUBIND_16.pkl` | 220 MB | BOP prediction descriptors, P phase |
| `Fe-Mo/Descriptors/PREDICTION_Fe-Mo_delta_0.7dprojections_0.5os_table_WUBIND_16.pkl` | 877 MB | BOP prediction descriptors, δ phase |

---

## Files already in the git repository (not in Zenodo)

These files are tracked in git and do **not** need to be downloaded separately:

- `Fe-Mo/FullyCuratedParsedBriefSummary.pkl` — curated DFT dataset (used by all notebooks)
- `Fe-Mo/Descriptors/CNAV_parallel_Fe-Mo_*.csv` — CNAV-averaged BOP training descriptors (derived from raw pkl above)
- `Fe-Mo/Descriptors/Fe-Mo-*ACE-CNAV.csv` — ACE training descriptors
- `Fe-Mo/Descriptors/soap_features_*.csv` — SOAP training descriptors
- `Fe-Mo/results/concatenation_results_*.pkl` — trained ML pipeline objects
- `Fe-Mo/results/voting_regressor_*.pkl` — trained ensemble regressors
- `validation_data/FullyCuratedParsedBriefSummary.pkl` — curated DFT dataset for validation structures

---

## Upload instructions

```bash
# Install zenodo-upload or use the Zenodo web interface
# Recommended: upload via Zenodo API or web UI at https://zenodo.org/deposit

# Files to upload (from repository root):
Fe-Mo/Descriptors/parallel_Fe-Mo_initial_0.7projections_0.5os_table_WUBIND_20.pkl
Fe-Mo/Descriptors/parallel_Fe-Mo_initial_canonical_table_WUBIND_16.pkl
Fe-Mo/Descriptors/parallel_Fe-Mo_relaxed_0.7projections_0.5os_table_WUBIND_20.pkl
Fe-Mo/Descriptors/parallel_Fe-Mo_relaxed_canonical_table_WUBIND_16.pkl
Fe-Mo/Descriptors/PREDICTION_Fe-Mo_R_0.7dprojections_0.5os_table_WUBIND_16.pkl
Fe-Mo/Descriptors/PREDICTION_Fe-Mo_M_0.7dprojections_0.5os_table_WUBIND_16.pkl
Fe-Mo/Descriptors/PREDICTION_Fe-Mo_P_0.7dprojections_0.5os_table_WUBIND_16.pkl
Fe-Mo/Descriptors/PREDICTION_Fe-Mo_delta_0.7dprojections_0.5os_table_WUBIND_16.pkl
```
