import pytest
from pathlib import Path

@pytest.mark.parametrize('fname', [
    'Fe-Mo/FullyCuratedParsedBriefSummary.json', 
    'Fe-Mo/graphs/Fe-Mo-PredictionDifferences.pdf', 
    'Fe-Mo/graphs/Figure_Fe-Mo_NMConvexHulls_ExpRanges_NM.pdf', 
    'Fe-Mo/graphs/Figure_Fe-Mo_Predictions_Validation.pdf, 
    'Fe-Mo/graphs/Figure_Fe-Mo_compare_predictions.pdf'
    ])

def test_files_exists(fname):
    assert Path(fname).exists(), f"File {fname} is missing."
