import os
import csv
import pytest
import pandas as pd
import numpy as np

# Ordered execution (requires pytest-order plugin)
pytestmark = pytest.mark.order("session")


def run_notebook(nbmake, notebook, env=None):
    """Helper to run notebook with optional environment variables."""
    old_env = os.environ.copy()

    try:
        if env:
            os.environ.update(env)
        nbmake(notebook)
    finally:
        os.environ.clear()
        os.environ.update(old_env)


# ---- 03 ----
@pytest.mark.order(1)
def test_03(nbmake, repo_root):
    run_notebook(nbmake, "03_PrepareDataset.ipynb")
    assert (repo_root / "Fe-Mo/FullyCuratedParsedBriefSummary.json").exists()


# ---- 04 ----
@pytest.mark.order(2)
def test_04(nbmake, repo_root):
    run_notebook(nbmake, "04_ComputeACEFeatures.ipynb")
    assert (repo_root / "Fe-Mo/Descriptors/Fe-Mo-ACE-CNAV.csv").exists()
    run_notebook(nbmake, "04_ComputeLibraryFeatures.ipynb")
    assert (repo_root / "Fe-Mo/Descriptors/soap_features__specific__r_cut_4__n_max_6__l_max_5__sigma_0.1__rbf_gto__periodic_True.csv").exists()


# ---- 05 (special env) ----
@pytest.mark.order(3)
def test_05(nbmake, repo_root):
    run_notebook(nbmake, "05_ComputeBOPFeatures.ipynb")
    assert (repo_root / "Fe-Mo/Descriptors/CNAV_parallel_Fe-Mo_relaxed_0.7projections_0.5os_table_WUBIND_16.csv").exists()


# ---- 07 (multiple configs) ----
@pytest.mark.order(4)
@pytest.mark.parametrize(
    "MODELNAME",
    ["Kernel Ridge", "Random Forest", "MLP"],
    ids=["KR", "RF", "MLP"],
)
def test_07A(nbmake, repo_root, MODELNAME):
    run_notebook(nbmake, "07_MachineLearn-ModelSelection.ipynb",
        env={"MODELNAME": MODELNAME, "SKIP_IMPORTANCES": "SKIP"},
    )
    name = MODELNAME.replace(' ','')
    assert os.path.exists(f"Fe-Mo/results/voting_regressor_{name}.pkl")

@pytest.mark.order(5)
def test_07B(nbmake, repo_root):
    run_notebook(nbmake, "07_MachineLearn.ipynb")
    assert os.path.exists(repo_root / "Fe-Mo/graphs/Fe-Mo_CNAV_only.pdf")


# ---- 08 ----
@pytest.mark.order(6)
def test_08(nbmake):
    run_notebook(nbmake, "08_AnalysisModels.ipynb")

@pytest.mark.order(7)
def test_09(nbmake, repo_root):
    run_notebook(nbmake, "09_PrepareFeaturesPrediction.ipynb")
    delta_path = repo_root / "Fe-Mo/data/Validation/inchull/delta"
    assert os.path.exists(delta_path / "Fe_pv56.delta-AAAAAAAAAAAAAA.NM.vasp")
    assert os.path.exists(delta_path / "Mo_sv56.delta-BBBBBBBBBBBBBB.NM.vasp")
    # Validate a known inchull member from the saved dataframe index.
    csv_path = delta_path / "EF_nmhcp__ACE.csv"
    assert os.path.exists(csv_path)
    inchull_delta = pd.read_csv(delta_path / 'EF_nmhcp__ACE.csv', index_col=0)
    assert "Mo_sv56.delta-BBBBBBBBBBBBBB.NM" in inchull_delta.index
    P_path = repo_root / "Fe-Mo/data/Validation/inchull/P/EF_nmhcp__ACE.csv"
    assert os.path.exists(P_path)
    inchull_P = pd.read_csv(P_path, index_col=0)
    assert 'Fe_pv20Mo_sv36.P-ABBBBABABBAB.NM' in inchull_P.index
    assert np.isclose(
        inchull_P['EF_nmhcp__ACE']['Fe_pv20Mo_sv36.P-ABBBBABABBAB.NM'], 
        0.0039, 
        atol=0.0001
    )


@pytest.mark.order(8):
def test_10(nbmake, "10_ValidateValidationData.ipynb"):
    run_notebook(nbmake, "10_ValidateValidationData.ipynb")