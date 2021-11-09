import matplotlib.pyplot as plt
import pandas as pd

RESULT = pd.read_pickle('CRCOW_INITIAL_NSC_ORTHOGONALOS_TABLECUTOFF_WUBIND.pkl')
ATOMS = pd.read_pickle('CrCoW-sorted-POSCAR-initial-rescaled-AtomsObjects.pkl')

Volumes = ATOMS['atoms'].map(lambda a: a.get_volume())

DFTV0  = pd.read_pickle('ParsedBriefsummary.pkl')['V0']

plt.plot(Volumes, DFTV0, 'o')
plt.plot(DFTV0, DFTV0)

print(RESULT.info())
