---
applyTo: "**"
---

# DFT dataset accompanying publication of research paper:

Data-efficient machine-learning of complex Fe–Mo intermetallics using domain knowledge of chemistry and crystallography 
doi: 10.5281/zenodo.19427673
accepted in NPJ computational materials.

authors
``` latex
\author{Mariano Forti} \email{mariano.forti@rub.de}
\affiliation{Interdisciplinary Centre for Advanced Materials Simulation (ICAMS), Ruhr-Universit{\"a}t Bochum, 44801 Bochum, Germany}

\author{Alesya Malakhova} 
\affiliation{Interdisciplinary Centre for Advanced Materials Simulation (ICAMS), Ruhr-Universit{\"a}t Bochum, 44801 Bochum, Germany}

\author{Yury Lysogorskiy} \affiliation{Interdisciplinary Centre for Advanced Materials Simulation (ICAMS), Ruhr-Universit{\"a}t Bochum, 44801 Bochum, Germany}

\author{Wenhao Zhang}
\affiliation{CNRS-Saint-Gobain-NIMS, IRL 3629, Laboratory for Innovative Key Materials and Structures (LINK), 1-1 Namiki, Tsukuba, 305-0044, Ibaraki, Japan}
\affiliation{Research Center for Structural Materials, National Institute for Materials Science, 1-2-1 Sengen, Tsukuba, 305-0047, Ibaraki, Japan}

\author{Jean-Claude Crivello}
\affiliation{CNRS-Saint-Gobain-NIMS, IRL 3629, Laboratory for Innovative Key Materials and Structures (LINK), 1-1 Namiki, Tsukuba, 305-0044, Ibaraki, Japan}
\affiliation{Univ Paris Est Creteil, CNRS, ICMPE, UMR 7182, 2 rue Henri Dunant, 94320, Thiais, France}

\author{Jean-Marc Joubert}
\affiliation{Univ Paris Est Creteil, CNRS, ICMPE, UMR 7182, 2 rue Henri Dunant, 94320, Thiais, France}

\author{Ralf Drautz} \affiliation{Interdisciplinary Centre for Advanced Materials Simulation (ICAMS), Ruhr-Universit{\"a}t Bochum, 44801 Bochum, Germany}

\author{Thomas Hammerschmidt} 
\affiliation{Interdisciplinary Centre for Advanced Materials Simulation (ICAMS), Ruhr-Universit{\"a}t Bochum, 44801 Bochum, Germany}
```

# Data sharing policies

Data will be shared through a zenodo upload. 
Upload should contain only the files that can not be reproduced in a reasonable time frame.

zenodo doi is 10.5281/zenodo.19427673 (data still not published)
one link is https://zenodo.org/records/19427673?preview=1&token=eyJhbGciOiJIUzUxMiIsImlhdCI6MTc3NTQwMDE3NiwiZXhwIjoxNzc3NTA3MTk5fQ.eyJpZCI6IjRmMzQ1MjAxLTNmYjYtNDgwYS1iM2JjLTlhZjgyNTNhMWI1NiIsImRhdGEiOnt9LCJyYW5kb20iOiI3OGQ3NWU3ZDcwYmNmYzBlZTFkZDgyYjJmYzAxOTBjNyJ9.VecEIoXMCIo7UiOmkoIqOrQ4G2vTkdkiNRjUBqHoTNKc9v_3jb3wDoaV0nCPL2G6gaBcEUmgvUDpd7TBNUa49w

or alternatively from sciebo:


## Files to share

Stored as pkl files, maybe it is good idea to share them in zipped jsons. 

### Raw dft data

- `Fe-Mo/FullyCuratedParsedBriefSummary.pkl` (curated DFT results)
- `Fe-Mo/Atomsobjects/Fe-Mo-POSCAR-initial-rescaled-AtomsObjects.pkl` (guess atoms where descriptors are calculated)
- `Fe-Mo/Atomsobjects/Fe-Mo-POSCAR-relaxed-all-rescaled-AtomsObjects.pkl` (relaxed atoms objects)
- `Fe-Mo/Atomsobjects/SUBLATICETAGS_POSCAR-initial.pkl` (markers for atomic sublattice used later for CNAV averaging)
- `Fe-Mo/Atomsobjects/SUBLATICETAGS_POSCAR-relaxed-all.pkl`
- `Fe-Mo/validation_data/ValidationFullyCuratedParsedBriefSummary.pkl`  (curated DFT results for validation structures)   
- `Fe-Mo/inchulldft/BriefSummary.pkl.gz` extra dft data validation, comming from a different HT framework (same DFT setup)

### Raw descriptors

This are also stored as pkl files, but best option would be to share them as zipped jsons also.
These are BOP descriptors that can not be calculated without BOPFOX. BOPFOX can be shared upon reasonable request. 
All other descriptor files can be reproduced from the Atoms objects 

**Descriptors for raw dft data**
- `Fe-Mo/Descriptors/parallel_Fe-Mo_initial_0.7projections_0.5os_table_WUBIND_20.pkl`
- `Fe-Mo/Descriptors/parallel_Fe-Mo_relaxed_0.7projections_0.5os_table_WUBIND_20.pkl`
**Descriptors used for predicting on guess structures of complex TCPs**
- `Fe-Mo/Descriptors/PREDICTION_Fe-Mo_M_0.7dprojections_0.5os_table_WUBIND_16.pkl`
- `Fe-Mo/Descriptors/PREDICTION_Fe-Mo_P_0.7dprojections_0.5os_table_WUBIND_16.pkl`
- `Fe-Mo/Descriptors/PREDICTION_Fe-Mo_R_0.7dprojections_0.5os_table_WUBIND_16.pkl`
- `Fe-Mo/Descriptors/PREDICTION_Fe-Mo_delta_0.7dprojections_0.5os_table_WUBIND_16.pkl`



# git policy

Notebooks, scripts and packages will be shared through github, in the repository:

https://github.com/AIIMProject/MLFeMoTCPs.git

Current dificulty is that the repository tracks big files and can not be uploaded directly. It is necesary to clean big files from project history. 
Raw DFT data in Fe-Mo/rawdata/ can be ignored for the moment. 

Files shared in zenodo can be removed from git history. 

# workflow adaptation to file availability

In the workflow, First option should be allways to use files from uploads. 
The user should be able to choose for instance if bopfox is available. 

In the case of validation data, maybe notebook 10 10_ValidateValidationData.ipynb can be tagged as requiring raw data, as it uses e-v curves from raw dft to validate samples. 

Maybe it is good idea to add an introduction code snippet to download all data if they are not available.

