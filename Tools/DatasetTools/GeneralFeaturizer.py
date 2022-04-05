import numpy as np
import pandas as pd
from tqdm.auto import tqdm


neighbours  = {'CN12': 12, 'CN14': 14, 'CN15': 15, 'CN16': 16}

def cn_average(steinhardt, coordination): # *args): #iterable, coordinations, axis=1):
    average = {}
    index, array = steinhardt
    _, coord = coordination
    natoms = len(array)
    for i, atomarray in enumerate(array):
        for polyhedra, nneighbours in neighbours.items():
            average[f'{str(i)}_{polyhedra}'] = np.array(atomarray)[np.array(coord) == nneighbours].sum()/natoms
    return  {index: average}

def cnaverage_dataframe(_Features, colids, _Coordinations, nworkers = 3):
    result = {}
    for colid in colids:
        print(f'cnaverage {colid}')
        progress = tqdm(zip(_Features[colid].iteritems(), _Coordinations.iteritems()), total=_Features.shape[0])
        thisresult = [cn_average(steinhardts, coordinations) for steinhardts, coordinations in progress]
        thisresult =  dict(map(dict.popitem, thisresult) )
        result.update({colid: pd.DataFrame.from_dict(thisresult,orient='index' )})
    return  result