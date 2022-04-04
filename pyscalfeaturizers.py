# # Pyscal features 

# In[1]:


import sys
import os
import pyscal as pc
import pandas as pd
import numpy as np
import multiprocessing as mp
from time import time
import pickle
import pdb
from tqdm.contrib.concurrent import process_map

CNS = {'CN12': 12, 'CN14': 14, 'CN15': 15, 'CN16': 16}

def load_pyscal(thisatoms):
    thesys = pc.System()
    thesys.read_inputfile(thisatoms, format='ase')
    return thesys

def get_sys_cn(thissys):
    thissys.find_neighbors(method='cutoff', cutoff = 'adaptive')
    return [atom.coordination for atom in thissys.atoms]

def get_sys_steinhardt(thissys):
    thissys.find_neighbors(method='cutoff', cutoff = 0)
    thissys.calculate_q([4,6])
    return thissys.get_qvals([4,6])

def pyscal_cn(theatoms):
    thissys = load_pyscal(theatoms)
    return get_sys_cn(thissys)

def pyscal_steinhardt(theatoms):
    thesys = load_pyscal(theatoms)
    return get_sys_steinhardt(thesys)


def featurize_dataframe(df, colid='atoms', featurizer=pyscal_cn, max_workers=3):
    print(featurizer.__name__)
    Result = process_map(featurizer, (df[colid]),  max_workers = max_workers, chunksize=1)
    return Result

def featurize_many(AtomsObjects, featurizerlist, colid='atoms'):
    Features = pd.DataFrame([], index=AtomsObjects.index, columns=[featurizer.__name__ for featurizer in featurizerlist])
    for thisfeaturizer in featurizerlist:
        Features[thisfeaturizer.__name__] = featurize_dataframe(AtomsObjects,featurizer=thisfeaturizer, colid=colid, max_workers=3)
    return Features

if __name__=='__main__':
    AtomsObjects = pd.read_pickle('Cr-Co-W/CrCoW-sorted-POSCAR-initial-rescaled-AtomsObjects.pkl').dropna()
    sys.path.insert(0, '/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer/')
    dataset = 'Cr-Co-W'
    AtomsObjects = pd.read_pickle('Cr-Co-W/CrCoW-sorted-POSCAR-initial-rescaled-AtomsObjects.pkl').dropna()
    featurizers = [pyscal_steinhardt, pyscal_cn] #, get_steinhardt]
    pyscal_features = [feature.__name__ for feature in featurizers]
    FeaturesFile = os.path.join(dataset, 'Descriptors', 'pyscal_features.kpl')
    Features = featurize_many(AtomsObjects,  featurizers, colid='atoms')
