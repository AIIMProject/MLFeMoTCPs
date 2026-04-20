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
    delta_csv_path = "Fe-Mo/results/CHULL_PREDICTION__delta__ACE__MAG=0.csv"
    assert os.path.exists(delta_csv_path)
    inchull_delta = pd.read_csv(delta_csv_path, index_col=0)
    assert "Mo_sv56.delta-BBBBBBBBBBBBBB.NM" in inchull_delta.index


    ace_P_path = repo_root / "Fe-Mo/results/NEARHULL_PREDICTION__P__ACE__MAG=0.csv"
    assert os.path.exists(ace_P_path)
    inchull_ace_P = pd.read_csv(ace_P_path, index_col=0)
    assert 'Fe_pv56.P-AAAAAAAAAAAA.NM' in inchull_ace_P.index
    soap_P_path = repo_root / "Fe-Mo/results/NEARHULL_PREDICTION__P__SOAP__MAG=0.csv"
    assert os.path.exists(ace_P_path)
    inchull_soap_P = pd.read_csv(soap_P_path, index_col=0)
    assert 'Fe_pv56.P-AAAAAAAAAAAA.NM' in inchull_soap_P.index
    assert np.isclose(
        inchull_soap_P['EF_nmhcp__SOAP']['Fe_pv28Mo_sv28.P-AAABBBAABBAB.NM'], 
        0.008, 
        atol=0.003
    )

    ace_R_path = repo_root / "Fe-Mo/results/CHULL_PREDICTION__R__ACE__MAG=0.csv"
    assert os.path.exists(ace_R_path)
    inchull_ace_R = pd.read_csv(ace_R_path, index_col=0)
    assert 'Fe_pv53.R.NM' in inchull_ace_R.index
    assert 'Mo_sv53.R.NM' in inchull_ace_R.index
    testchull = [
        ('Fe_pv50Mo_sv3.R-BAAAAAAAABA.NM', 0.124),
        ('Fe_pv47Mo_sv6.R-AAAAAAAAAAB.NM', 0.086),
        ('Fe_pv45Mo_sv8.R-AAAAAAAAABB.NM', 0.063),
        ('Fe_pv38Mo_sv15.R-BAAAAAAABBB.NM', 0.013)
    ]
    for testindex, testval in testchull:
        assert testindex in inchull_ace_R.index
        assert np.isclose(
            inchull_ace_R['EF_nmhcp__ACE'][testindex], 
            testval, 
            atol=0.005
        )


@pytest.mark.order(9)
def test_10(nbmake, repo_root):
    run_notebook(nbmake, "10_ValidateValidationData.ipynb")

@pytest.mark.order(10)
def test_11(nbmake, repo_root):
    run_notebook(nbmake, "11_ValidatePredictions.ipynb")
    assert os.path.exists('Fe-Mo/graphs/Figure_Fe-Mo_Predictions_Validation.pdf')
    assert os.path.exists('Fe-Mo/data/Validation/rmse__MAG=0.json')
    validation_rmse = pd.read_json('Fe-Mo/data/Validation/rmse__MAG=0.json', typ='series', orient='index')
    ref_rmse = {
 "('0.7dprojections_0.5os', 'R')":0.0214393604,
 "('0.7dprojections_0.5os', 'P')":0.0357590895,
 "('0.7dprojections_0.5os', 'delta')":0.0616466451,
 "('0.7dprojections_0.5os', 'M')":0.0472114773,
 "('ACE', 'R')":0.03,
 "('ACE', 'P')":0.02,
 "('ACE', 'delta')":0.05,
 "('ACE', 'M')":0.01,
 "('SOAP', 'R')":0.015,
 "('SOAP', 'P')":0.02,
 "('SOAP', 'delta')":0.07,
 "('SOAP', 'M')":0.01
}
    assert len(validation_rmse) == len(ref_rmse)
    for index, val in ref_rmse.items():
        assert np.isclose(val, validation_rmse[index], 
    rtol=0.5)


@pytest.mark.order(10)
def test_15(nbmake, repo_root):
    run_notebook(nbmake, "15_A_Thermodynamics.ipynb")
    assert os.path.exists(repo_root/'Fe-Mo/results/OCCUPANCY_PREDICTION__R__T=1700__ACE__MAG=0.csv')
    DG=pd.read_csv('Fe-Mo/results/OCCUPANCY_PREDICTION__R__T=1700__ACE__MAG=0.csv', index_col=0)
    assert 'A@$c_2$' in DG.columns

