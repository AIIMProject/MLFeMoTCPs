import os
import csv
import pytest
import pandas as pd
import numpy as np
import pdb

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
def test_04A(nbmake, repo_root):
    run_notebook(nbmake, "04_ComputeACEFeatures.ipynb")
    assert (repo_root / "Fe-Mo/Descriptors/Fe-Mo-ACE-CNAV.csv").exists()

@pytest.mark.order(3)
def test_04B(nbmake, repo_root):
    run_notebook(nbmake, "04_ComputeLibraryFeatures.ipynb")
    assert (repo_root / "Fe-Mo/Descriptors/soap_features__specific__r_cut_4__n_max_5__l_max_4__sigma_0.1__rbf_gto__periodic_True.pkl").exists()
    soap_cnav_file = repo_root / "Fe-Mo/Descriptors/CNAV_soap_features__specific__r_cut_4__n_max_5__l_max_4__sigma_0.1__rbf_gto__periodic_True.csv"
    assert (soap_cnav_file).exists()
    soap_descrptors = pd.read_csv(soap_cnav_file, index_col=0)
    assert 'Fe_pv4Mo_sv20.C36-ABBBB.FM' in soap_descrptors.index
    np.isclose(soap_descrptors['SOAP_0_0']['Fe_pv4Mo_sv20.C36-ABBBB.FM' ], 0.0033, atol=1e-4)
    assert 'Fe_pv53.R.NM' in soap_descrptors.index
    np.isclose(soap_descrptors['SOAP_0_0']['Fe_pv53.R.NM' ], 0.0197, atol=1e-4)



# ---- 05 (special env) ----
@pytest.mark.order(4)
def test_05(nbmake, repo_root):
    run_notebook(nbmake, "05_ComputeBOPFeatures.ipynb")
    assert (repo_root / "Fe-Mo/Descriptors/CNAV_parallel_Fe-Mo_relaxed_0.7projections_0.5os_0scf_table_WUBIND_16.csv").exists()
    assert (repo_root / "Fe-Mo/Descriptors/CNAV_parallel_Fe-Mo_initial_0.7projections_0.5os_0scf_table_WUBIND_16.csv").exists()


# ---- 07 (multiple configs) ----
@pytest.mark.order(5)
@pytest.mark.parametrize(
    "MODELNAME",
    ["Kernel Ridge", "Random Forest", "MLP"],
    ids=["KR", "RF", "MLP"],
)
def test_07A(nbmake, repo_root, MODELNAME):
    name = MODELNAME.replace(' ','')
    assert os.path.exists(f"Fe-Mo/results/voting_regressor_{name}.pkl")
    run_notebook(nbmake, "07_MachineLearn-ModelSelection.ipynb",
        env={"MODELNAME": MODELNAME}#, "CALC_IMPORTANCES": "NO"},
    )
    assert os.path.exists(f"Fe-Mo/results/refitted_voting_regressor_{name}.pkl")

@pytest.mark.order(6)
def test_07B(nbmake, repo_root):
    run_notebook(nbmake, "07_MachineLearn.ipynb")
    assert os.path.exists(repo_root / "Fe-Mo/graphs/Fe-Mo_CNAV_only.pdf")


# ---- 08 ----
@pytest.mark.order(7)
def test_08(nbmake):
    run_notebook(nbmake, "08_AnalysisModels.ipynb")

@pytest.mark.order(8)
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
    ace_P_path = repo_root / "Fe-Mo/data/Validation/inchull/P/EF_nmhcp__ACE.csv"
    assert os.path.exists(ace_P_path)
    inchull_ace_P = pd.read_csv(ace_P_path, index_col=0)
    assert 'Fe_pv20Mo_sv36.P-ABBBBABABBAB.NM' in inchull_ace_P.index
    assert np.isclose(
        inchull_ace_P['EF_nmhcp__ACE']['Fe_pv20Mo_sv36.P-ABBBBABABBAB.NM'], 
        0.0039, 
        atol=0.0001
    )
    soap_P_path = repo_root / "Fe-Mo/data/Validation/inchull/P/EF_nmhcp__SOAP_specific_small.csv"
    assert os.path.exists(ace_P_path)
    inchull_soap_P = pd.read_csv(soap_P_path, index_col=0)
    assert 'Fe_pv28Mo_sv28.P-AAABBBAABBAB.NM' in inchull_soap_P.index
    assert np.isclose(
        inchull_soap_P['EF_nmhcp__SOAP_specific_small']['Fe_pv28Mo_sv28.P-AAABBBAABBAB.NM'], 
        0.0064, 
        atol=0.0001
    )


@pytest.mark.order(9)
def test_10(nbmake, repo_root):
    run_notebook(nbmake, "10_ValidateValidationData.ipynb")

@pytest.mark.order(10)
def test_11(nbmake, repo_root):
    run_notebook(nbmake, "11_ValidatePredictions.ipynb")
    assert os.path.exists('Fe-Mo/graphs/Figure_Fe-Mo_Predictions_Validation.pdf')
    assert os.path.exists('Fe-Mo/data/Validation/rmse.json')
    validation_rmse = pd.read_json('Fe-Mo/data/Validation/rmse.json', typ='series', orient='index')
    ref_rmse = {
 "('0.7dprojections_0.5os_16_MAG=0', 'R')":0.0214393604,
 "('0.7dprojections_0.5os_16_MAG=0', 'P')":0.0357590895,
 "('0.7dprojections_0.5os_16_MAG=0', 'delta')":0.0616466451,
 "('0.7dprojections_0.5os_16_MAG=0', 'M')":0.0472114773,
 "('ACE_lmax=321_MAG=0', 'R')":0.0345354761,
 "('ACE_lmax=321_MAG=0', 'P')":0.0251519909,
 "('ACE_lmax=321_MAG=0', 'delta')":0.0532422492,
 "('ACE_lmax=321_MAG=0', 'M')":0.0167460524,
 "('SOAP_specific_small_specific_small_MAG=0', 'R')":0.0170015054,
 "('SOAP_specific_small_specific_small_MAG=0', 'P')":0.0277703918,
 "('SOAP_specific_small_specific_small_MAG=0', 'delta')":0.0680979289,
 "('SOAP_specific_small_specific_small_MAG=0', 'M')":0.0109298833
}
    assert len(validation_rmse) == len(ref_rmse)
    for index, val in ref_rmse.items():
        assert np.isclose(val, validation_rmse[index])
