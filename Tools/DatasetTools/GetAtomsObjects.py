import sys
import os
sys.path.insert(0, '/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer/')
sys.path.insert(1, os.path.dirname(__file__))
import pandas as pd
from BopFoxFeaturizer.Featurizer import Featurizer
#from Tools import need_to_update
from pymatgen.io.ase import AseAtomsAdaptor

dataset = 'Fe-Mo'
case='POSCAR-initial' #, 'POSCAR-relaxed']
rescale_by_atoms=True #, False]
subcase = 'rescaled' # ,  'noscaled' ]
Force= True
CuratedBS = os.path.join(dataset,'CuratedParsedBriefSummary.pkl')
atomsobjectslocation = os.path.join(dataset,'Atomsobjects')

components = dataset.replace('-','')

BS = pd.read_pickle(CuratedBS)

Features = Featurizer(BS)

database = f'{dataset}/**/{case}'
AtomsFile = os.path.join(atomsobjectslocation,f'{components}-{case}-{subcase}-AtomsObjects.pkl')
Atoms_Objects, CantMake_Atoms_Object = Features.get_atoms_object(database=database,rescale_by_atoms=True, reset_chemistry=True,file_filter = 'initial$')
Atoms_Objects.to_pickle(AtomsFile)
Atoms_Objects.dropna(inplace=True)


