# # Pyscal features 

# In[1]:


import pyscal as pc
import pandas as pd
import numpy as np
import multiprocessing as mp
from tqdm.notebook import tqdm_notebook
from time import time
import pickle
import pdb
tqdm_notebook.pandas()

CNS = {'CN12': 12, 'CN14': 14, 'CN15': 15, 'CN16': 16}

def load_pyscal(thisatoms):
    thesys = pc.System()
    thesys.read_inputfile(thisatoms, format='ase')
    return thesys

def get_sys_cn(thissys):
    thissys.find_neighbors(method='cutoff', cutoff = 'adaptive')
    return [atom.coordination for atom in thissys.atoms]

def get_sys_steinhardt(thissys):
    thissys.calculate_q([4,6])
    return thissys.get_qvals([4,6])

def get_cn(theatoms):
    thissys = load_pyscal(theatoms)
    return get_sys_cn(thissys)

def get_steinhardt(theatoms):
    thesys = load_pyscal(theatoms)
    return get_sys_steinhardt(thesys)

def featurize_row (theatoms, atomfeaturizer = [get_cn]):
    return atomfaturizer(theatoms)
    

from tqdm.contrib.concurrent import process_map

def timeit(func):
    def inner(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        print( time() - t1 )
        return result
    return inner

def featurize_dataframe(df, colid='atoms', featurizer=get_cn, max_workers=3):
    cz = int(len(df) / max_workers)
    print(featurizer.__name__)
    Result = process_map(featurizer, df[colid],  max_workers = max_workers, chunksize=1)
    return Result

if __name__=='__main__':
    AtomsObjects = pd.read_pickle('Cr-Co-W/CrCoW-sorted-POSCAR-initial-rescaled-AtomsObjects.pkl').dropna()
    CNS = {}
    featurizers = [get_cn, get_steinhardt]
    CNS =  {thisfeaturizer.__name__: featurize_dataframe(AtomsObjects,featurizer=thisfeaturizer, max_workers=3) for thisfeaturizer in featurizers}
    with open('pyscal_features.kpl','wb') as pkl:
        pickle.dump(CNS, pkl)
