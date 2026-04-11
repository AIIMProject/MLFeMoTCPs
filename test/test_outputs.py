import os
import pytest

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

def test_07(nbmake, MODELNAME):
    run_notebook(nbmake, "07_MachineLearn-ModelSelection.ipynb",
        env={"MODELNAME": MODELNAME, "SKIP_IMPORTANCES": "SKIP"},
    )
#    assert os.path.exists("Fe-Mo/results/voting_regressor_KernelRidge.pkl")
#    assert os.path.exists("Fe-Mo/results/voting_regressor_MLP.pkl")
#    assert os.path.exists("Fe-Mo/results/voting_regressor_RandomForest.pkl")
#    assert os.path.exists("Fe-Mo/graphs/Figure_Fe-Mo_VotedRegressor_EF_nmhcp_KernelRidge.pdf")
    run_notebook(nbmake, "07_MachineLearn.ipynb")
#    assert os.path.exists("Fe-Mo/graphs/Fe-Mo_CNAV_only.pdf")


# ---- 08 ----
@pytest.mark.order(5)
def test_08(nbmake):
    run_notebook(nbmake, "08_AnalysisModels.ipynb")

@pytest.mark.order(6)
def test_08(nbmake):
    run_notebook(nbmake, "09_PrepareFeaturesPrediction.ipynb")
