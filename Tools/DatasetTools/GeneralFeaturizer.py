import numpy as np
import pandas as pd
from tqdm.auto import tqdm
import pdb

neighbours  = {'CN12': 12, 'CN13': 13, 'CN14': 14, 'CN15': 15, 'CN16': 16}

def cn_average(vectorfeature, coordination): # *args): #iterable, coordinations, axis=1):
    """
    vectorfeature should be one value per site, the array for one site only should be given
    """
    average = {}
    index, atomarray = vectorfeature
    _, coord = coordination
    natoms = len(atomarray)
    for polyhedra, nneighbours in neighbours.items():
        average['_0'] = np.sum(atomarray)/natoms
        average[f'_{polyhedra}'] = np.array(atomarray)[np.array(coord) == nneighbours].sum()/natoms
    AveragedFeatures  = {index: average}
    return AveragedFeatures

def cnaverage_dataframe(_Features, colids, _Coordinations, nworkers = 3):
    result = {}
    progress = tqdm(colids)
    for colid in progress:
        progress.set_description(colid)
        iterator  = zip(_Features[colid].iteritems(), _Coordinations.iteritems())
        thisresult = [cn_average(atomfeature, atomcoordinations) for atomfeature, atomcoordinations in iterator]
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

