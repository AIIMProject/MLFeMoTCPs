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
def test_03(nbmake):
    run_notebook(nbmake, "03_PrepareDataset.ipynb")


# ---- 04 ----
@pytest.mark.order(2)
def test_04(nbmake):
    run_notebook(nbmake, "04_ComputeACEFeatures.ipynb")
    run_notebook(nbmake, "04_ComputeLibraryFeatures.ipynb")


# ---- 05 (special env) ----
@pytest.mark.order(3)
def test_05(nbmake):
    run_notebook(nbmake,"05_ComputeBOPFeatures.ipynb")
    )


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
    run_notebook(nbmake, "07_MachineLearn.ipynb",


# ---- 08 ----
@pytest.mark.order(5)
def test_08(nbmake):
    run_notebook(nbmake, "08_AnalysisModels.ipynb")
