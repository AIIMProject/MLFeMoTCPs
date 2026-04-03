# DatasetsML — Fe-Mo TCP Phase Stability from Machine Learning

**Paper**: *Data-efficient machine-learning of complex Fe–Mo intermetallics using domain knowledge of chemistry and crystallography*  
**Authors**: Mariano Forti, Alesya Malakhova, Yury Lysogorskiy, Wenhao Zhang, Jean-Claude Crivello, Jean-Marc Joubert, Ralf Drautz, Thomas Hammerschmidt  
**Journal**: npj Computational Materials (accepted)  
**DOI**: *(to be added upon publication)*  
**Data**: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX) *(to be updated)*

---

## Overview

This repository accompanies the above paper. 
It provides the machine-learning pipeline used to predict the formation energies and sublattice occupancies of complex TCP (topologically close-packed) intermetallic phases in the Fe–Mo binary system.

The core idea is that encoding **domain knowledge** at three levels — chemistry (Vegard's law volume scaling), crystallography (coordination-number-resolved averaging, CNavg), and local bonding (BOP, ACE, SOAP descriptors) — enables data-efficient predictions for complex TCP phases (R, M, P, δ with 11–14 Wyckoff sites) from models trained on only simple TCP phases (A15, C15, C14, C36, σ, χ, μ with 2–5 Wyckoff sites) using fewer than 300 DFT calculations.

---

## Repository Structure

```
DatasetsML_2.0/
├── Fe-Mo/
│   ├── FullyCuratedParsedBriefSummary.pkl   # Curated DFT dataset
│   ├── Atomsobjects/                        # ASE Atoms objects
│   ├── Descriptors/                         # Pre-computed feature files
│   ├── results/                             # Feature selection results, predictions
│   ├── graphs/                              # Generated figures
│   └── data/Validation/                     # DFT validation data
├── Tools/                                   # datasetsml-tools Python package
# Not Necesary ├── Scripts/                                 # Standalone scripts (feature selection)
# Not in public repository  ├── Manuscript/                              # LaTeX source of the paper 
# Not in public repository ├── models/                                  # BOPfox model parameter files (.bx)
├── dependencies/                            # External packages (see below)
├── environment.yaml                         # Full conda environment
└── environment_public.yaml                  # Environment without private packages
```

---

## Notebook Workflow

Notebooks are numbered to indicate execution order. The main publishable pipeline starts at **notebook 03**. Notebooks 00–02 require raw DFT output data and are preserved for future integration with the [NOMAD repository](https://nomad-lab.eu/).

| Notebook | Purpose | Prerequisites |
|----------|---------|---------------|
| `REQUIRE_RAW_DATA_00_ParseBriefsummary.ipynb` | Parse raw DFT output | Raw DFT data (not included; NOMAD planned) |
| `REQUIRE_RAW_DATA_01_CurateWithEVcurves.ipynb` | Curate dataset via E–V curve fits | Notebook 00 output |
| `REQUIRE_RAW_DATA_02_CharacterizeDataset.ipynb` | Dataset statistics | Notebook 01 output |
| `03_PrepareDataset.ipynb` | Prepare ASE Atoms objects and dataset splits | `FullyCuratedParsedBriefSummary.pkl` |
| `04_ComputeACEFeatures.ipynb` | Compute ACE descriptors | Atoms objects, `python-ace` |
| `04_ComputeLibraryFeatures.ipynb` | Compute SOAP, Magpie/matminer descriptors | Atoms objects, DScribe |
| `05_ComputeBOPFeatures.ipynb` | Compute or recover BOP moment descriptors | Atoms objects, **BOPfox** (see below) |
| `07_MachineLearn-ModelSelection.ipynb` | Build ensemble ML models from feature selection results | Descriptor files, `concatenation_results_*.pkl` |
| `08_AnalysisModels.ipynb` | Analyse and compare fitted models | Model outputs |
| `09_PrepareFeaturesPrediction.ipynb` | Prepare descriptors for complex phases | Zenodo data files |
| `10_ValidateValidationData.ipynb` | Validate against DFT reference data | Validation data + model predictions |
| `11_ValidatePredictions.ipynb` | Final prediction validation | Predictions + DFT validation |
| `15_A_Thermodynamics.ipynb` | Thermodynamic analysis (Bragg–Williams) | Model predictions |

# Not to be uploaded Legacy and experimental notebooks are in the `legacy/` folder.

---

## Installation

### 1. Clone the repository

```bash
git clone <repo-url> FeMo_TCP_ML
cd FeMo_TCP_ML
```

### 2. Create the conda environment

```bash
# Public environment (no BOPfox):
conda env create -f environment_public.yaml
conda activate FeMo_TCPs_ML

# Full environment (requires access to private BOPfox packages):
conda env create -f environment.yaml
conda activate datasets_ml
```


### 4. Download large data files from Zenodo

Download the data archive from [Zenodo DOI: 10.5281/zenodo.XXXXXXX](https://doi.org/10.5281/zenodo.XXXXXXX) and place the files in the appropriate directories as described in `ZENODO_MANIFEST.md`.

---

## Dependencies & Software

### Public packages (included in `environment_public.yaml`)
- [ASE](https://wiki.fysik.dtu.dk/ase/) — atomic simulation environment
- [DScribe](https://singroup.github.io/dscribe/) — SOAP descriptor generation
- [python-ace](https://github.com/ICAMS/python-ace) — ACE descriptor generation
- [scikit-learn](https://scikit-learn.org/) — machine learning
- [pymatgen](https://pymatgen.org/) — structure handling
- [matminer](https://hackingmaterials.github.io/matminer/) — Magpie descriptors

### BOPfox (available on request)
Notebooks `05_ComputeBOPFeatures.ipynb` and `09_PrepareFeaturesPrediction.ipynb` require the **BOPfox** software and associated Python wrappers (`bopfoxfeaturizer`, `bopdftprojections`).  
BOPfox is not openly distributed. Please contact the authors to request access.  
Pre-computed BOP descriptor files for the complex TCP phases are provided in the Zenodo archive so that notebooks 09–11 can be run without BOPfox.

### Install the Tools package

```bash
pip install -e Tools/
```

### Install python-ace

```bash
git clone https://github.com/ICAMS/python-ace.git dependencies/python-ace
cd dependencies/python-ace
# Apply compatibility patch for newer cmake/compilers (adds missing inttypes.h)
git apply ../../python-ace-cmake-compat.patch
pip install .
```

> **Note:** Without the patch, builds with cmake ≥ 3.20 may fail with an undefined type error in `yaml-cpp/emitterutils.cpp`. The patch adds a single `#include "inttypes.h"` line. The patch file is included in this repository at `python-ace-cmake-compat.patch`.

---

## Data Availability

- **Curated DFT dataset** (`FullyCuratedParsedBriefSummary.pkl`): included in this repository and in the Zenodo archive.
- **Pre-computed BOP descriptors** for complex TCP phases (R, M, P, δ): available in the Zenodo archive (see `ZENODO_MANIFEST.md`).
- **Raw DFT calculation data**: to be deposited in the [NOMAD repository](https://nomad-lab.eu/) (in preparation). This repository will be updated with NOMAD integration once available.
---

The notebooks should downlaod the data on demand. 

## Reproducing the Results

To reproduce the paper results without running BOPfox:

1. Install the environment (step 2–3 above)
3. Run notebooks **07 → 08 → 09 → 10 → 11** in order. All necesary data will be downloaded from zenodo and sciebo on demand. 
This includes curated DFT dataset and pre-computed BOP descriptors for the complex TCP phases, so BOPfox is not required to reproduce the main results of the paper.

To fully reproduce from descriptor computation (requires BOPfox):

1. Run notebooks **03 → 04 → 05** first
2. Run `Scripts/FeatureSelection.py` on a compute cluster (this is the expensive step)
3. Then continue with notebooks **07 → 11**

---

## Citation

If you use this repository, please cite:

> Forti, M., Malakhova, A., Lysogorskiy, Y., Zhang, W., Crivello, J.-C., Joubert, J.-M., Drautz, R. & Hammerschmidt, T.  
> *Data-efficient machine-learning of complex Fe–Mo intermetallics using domain knowledge of chemistry and crystallography.*  
> npj Computational Materials (2026). DOI: *(to be added)*

---

## License

MIT License — see [LICENSE](LICENSE).

