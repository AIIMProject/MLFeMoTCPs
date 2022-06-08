import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, '/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer/')
from BopFoxFeaturizer.Featurizer import Featurizer
import GeneralFeaturizer as gf
import pandas as pd
import numpy as np
from tqdm.auto import tqdm

rootlocation = '/home/storage/fortimtb/DatasetsML/Fe-Mo/'
BS = pd.read_pickle(os.path.join(rootlocation,  'FullyCuratedParsedBriefSummary.pkl' ))
Features = Featurizer(BS)
sublaticetags = pd.read_pickle(  os.path.join(rootlocation, 'Atomsobjects', 'SUBLATICETAGS.pkl') )
sublaticetags.index = sublaticetags.index.str.strip()
sublaticesorters =  pd.read_pickle(os.path.join( rootlocation, 'Atomsobjects','SORTERS.pkl' ))
sublaticesorters.index = sublaticesorters.index.str.strip()

AtomsObjects = pd.read_pickle(os.path.join(rootlocation, 'Atomsobjects', 'FeMo-POSCAR-initial-rescaled-AtomsObjects.pkl'))
Features = Featurizer(BS)

relevantsorters = gf.get_relevant_sorters(AtomsObjects, sublaticesorters)
df = gf.sorting_feature(AtomsObjects, sublaticesorters)


df['sorters'] = gf.correct_sortings_fromphases(AtomsObjects, BS.Phase, df.sorters)

specialphases = gf.specialphases #['hcp', 'bcc', 'fcc']

df['CNList'] = gf.get_sitecn(BS.Phase, AtomsObjects.atoms, df.sorters)


