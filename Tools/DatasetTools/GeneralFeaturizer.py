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

def cn_average(vectorfeature, coordination, normalization = 'natoms', return0 = True): # *args): #iterable, coordinations, axis=1):
    """
    vectorfeature should be one value per site, the array for one site only should be given
    normaliztion = ['natoms', 'NCP'] where NCP stands for number of vertices in coordination polyhedra.
    """
    average = {}
    index, atomarray = vectorfeature
    _, coord = coordination
    norma = []
    if return0:
        average['_0'] = np.sum(atomarray)/len(atomarray)
    for polyhedra, nneighbours in neighbours.items():
        coincidences = np.array(coord) == nneighbours
        norma = get_normalization(normalization, coincidences, nneighbours)
        average[f'_{polyhedra}'] = np.array(atomarray)[coincidences].sum()/norma
    return {index: average}

def cn_composition(_chemicalsymbols, _coordination):
    compo = {}
    index, chemicalsymbols = _chemicalsymbols
    _, coordination = _coordination
    for polyhedra, nneighbours in neighbours.items():
        compo[f'_{polyhedra}'] = np.unique(np.array(chemicalsymbols)[ np.array(coordination) == nneighbours ])
    return {index: compo}

def featurize_series(_Feature, _Coordinations, featurizer=cn_average, **kwargs):
    iterator  = zip(_Feature.iteritems(), _Coordinations.iteritems())
    thisresult = [featurizer(atomfeature, atomcoordinations, **kwargs) for atomfeature, atomcoordinations in iterator]
    thisresult =  dict(map(dict.popitem, thisresult))
    return pd.DataFrame.from_dict(thisresult,orient='index' )

def featurize_dataframe(_Features, _coordination, featurizer=cn_average, **kwargs):
    result = []
    for colid, feature in _Features.iteritems():
        try:
            result.append(featurize_series(feature, _coordination, featurizer, **kwargs))
        except Exception as E:
            pdb.set_trace()
            featurize_series(feature, _coordination, featurizer, **kwargs)
            pass

        columns = result[-1].columns
        newcolumns = [f'{colid}{thiscol}' for thiscol in columns]
        result[-1].columns = newcolumns
    return pd.concat(result, axis=1)
        

def featurize_many(_Features, _Coordinations, featurizers=[cn_average], **kwargs):
    progress = tqdm(featurizers) #,  bar_format='{percentage:3.0f}%|{bar:100}{r_bar}{desc}')
    result = []
    for featurizer  in progress:
        progress.set_description(f'{featurizer.__name__}')
        result.append(featurize_dataframe(_Features, _Coordinations, featurizer = featurizer))
        #columns = result[-1].columns
        #newcolumns = [f'{featurizer.__name__}{thiscol}' for thiscol in columns]
        #result[-1].columns = newcolumns
    return pd.concat(result, axis=1)



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
            if len(m.shape) == 1:
                m = np.vstack([ np.zeros_like(m), m ]).transpose()
            natoms, nm = m.shape #eget_dimensions(m)
            df[feature][index] = {f'{feature}_{this}' :  m[:,this] for this in range(1,nm)}
        df[feature] = pd.DataFrame.from_dict(df[feature], orient='index')
    return pd.concat(df.values(), axis=1)

