import numpy as np
import pandas as pd
from tqdm.auto import tqdm
import pdb



neighbours  = {'CN12': 12, 'CN14': 14, 'CN15': 15, 'CN16': 16}

def cn_average(vectorfeature, coordination): # *args): #iterable, coordinations, axis=1):
    average = {}
    index, atomarray = vectorfeature
    _, coord = coordination
    natoms = len(atomarray)
    for polyhedra, nneighbours in neighbours.items():
        average[f'_{polyhedra}'] = atomarray[np.array(coord) == nneighbours].sum()/natoms
    AveragedFeatures  = {index: average}
    return

def cnaverage_dataframe(_Features, colids, _Coordinations, nworkers = 3):
    result = {}
    for colid in colids:
        print(f'cnaverage {colid}')
        progress = tqdm(zip(_Features[colid].iteritems(), _Coordinations.iteritems()), total=_Features.shape[0])
        thisresult = [cn_average(atomfeature, atomcoordinations) for atomfeature, atomcoordinations in progress]
        thisresult =  dict(map(dict.popitem, thisresult) )
        result.update({colid: pd.DataFrame.from_dict(thisresult,orient='index' )})
    return  result
