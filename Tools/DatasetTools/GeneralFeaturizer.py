import numpy as np
import pandas as pd
from tqdm.auto import tqdm
import pdb

neighbours  = {'CN12': 12, 'CN13': 13, 'CN14': 14, 'CN15': 15, 'CN16': 16}

def get_normalization(_normoption, _coincidences, _n):
    norma_ = len(_coincidences)
    if _normoption == 'NCP':
        norma_ = _n  # get_normalization(normalization, coincidences)
    return norma_

def get_array_average(_array,  _coincidence, _norma):
    cases = _array[_coincidence]
    return np.sum(cases)/_norma

def cn_average(vectorfeature, coordination, normalization = 'natoms'): # *args): #iterable, coordinations, axis=1):
    """
    vectorfeature should be one value per site, the array for one site only should be given
    normaliztion = ['natoms', 'NCP'] where NCP stands for number of vertices in coordination polyhedra.
    """
    average = {}
    index, atomarray = vectorfeature
    _, coord = coordination
    norma = []
    average['_0'] = np.sum(atomarray)/len(atomarray)
    for polyhedra, nneighbours in neighbours.items():
        coincidences = np.array(coord) == nneighbours
        norma = get_normalization(normalization, coincidences, nneighbours)
        average[f'_{polyhedra}'] = np.array(atomarray)[coincidences].sum()/norma
    AveragedFeatures  = {index: average}
    return AveragedFeatures

def cn_composition(chemicalsymbols, coordination):
    compo = {}
    for polyhedra, nneighbours in neighbours.items():
        count[f'_{polyhedra}'] = chemicalsymbolas[ np.array(coord) == nneighbours ]
    return count

def cnaverage_dataframe(_Features, colids, _Coordinations, **kwargs):
    result = {}
    progress = tqdm(colids)
    for colid in progress:
        progress.set_description(colid)
        iterator  = zip(_Features[colid].iteritems(), _Coordinations.iteritems())
        thisresult = [cn_average(atomfeature, atomcoordinations, **kwargs) for atomfeature, atomcoordinations in iterator]
        thisresult =  dict(map(dict.popitem, thisresult) )
        result.update({colid: pd.DataFrame.from_dict(thisresult,orient='index' )})
    return  result

def get_dimensions(thefeature):
    theshape = thefeature.shape
    if len(theshape) == 2:
        dimensions = theshape
    elif len(theshape) == 1:
        dimensions = (theshape, 1)
    return dimensions

def cnav_column_name_fix (dict_of_features):
    for key, features in dict_of_features.items():
        col_replacements = {col: f'{key}{col}' for col in features.columns}
        features.rename(columns=col_replacements, inplace=True)
        
def array_expansions(Features, columnstoexpand):
    df = {}
    for feature in columnstoexpand:
        df[feature] = {}
        for index, compound in Features[feature].iteritems():
            m = np.array(compound)
            natoms, nm = get_dimensions(m)
            df[feature][index] = {f'{feature}_{this}' :  m[:,this] for this in range(1,nm)}
        df[feature] = pd.DataFrame.from_dict(df[feature], orient='index')
    return pd.concat(df.values(), axis=1)

