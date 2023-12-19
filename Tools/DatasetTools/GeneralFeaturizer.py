import numpy as np
import pandas as pd
from tqdm.auto import tqdm
import pdb
import re

neighbours  = {'CN12': 12, 'CN13': 13, 'CN14': 14, 'CN15': 15, 'CN16': 16}

cn_dict : dict = {
        'A15': [ 'Z14a', 'Z14a', 'Z14a', 'Z14b', 'Z14b', 'Z14b', 'Z12a', 'Z12b' ], 
        'C14': ['Z16', 'Z16', 'Z16', 'Z16', 'Z12a', 'Z12a', 'Z12b', 'Z12b', 'Z12b', 'Z12b', 'Z12b', 'Z12b' ],
        'C15':['Z16', 'Z16', 'Z12', 'Z12', 'Z12', 'Z12'],
        'C36': ['Z16a', 'Z16a', 'Z16a', 'Z16a', 'Z16b', 'Z16b', 'Z16b', 'Z16b', 'Z12a', 'Z12a', 'Z12a', 'Z12a', 'Z12b', 'Z12b', 'Z12b', 'Z12b', 'Z12b', 'Z12b', 'Z12c', 'Z12c', 'Z12c', 'Z12c', 'Z12c', 'Z12c'  ], 
        'bcc': ['Z14'],
        'chi': ['Z16a', 'Z16b', 'Z16b', 'Z16b', 'Z16b', 'Z13' , 'Z13' , 'Z13' , 'Z13' , 'Z13' , 'Z13' , 'Z13' , 'Z13' , 'Z13' , 'Z13' , 'Z13' , 'Z13' , 'Z12' , 'Z12' , 'Z12' , 'Z12' , 'Z12' , 'Z12' , 'Z12' , 'Z12' , 'Z12' , 'Z12' , 'Z12' , 'Z12'], 
        'fcc': ['Z12'],
        'hcp': ['Z12','Z12'],
        'mu': ['Z12a', 'Z12b', 'Z12b', 'Z12b', 'Z12b', 'Z12b', 'Z12b', 'Z15' , 'Z15' , 'Z16' , 'Z16' , 'Z14' , 'Z14'],

        'sigma': ['Z12a' , 'Z12a' , 'Z15a' , 'Z15a' , 'Z15a' , 'Z15a' , 'Z14a' , 'Z14a' , 'Z14a' , 'Z14a' , 'Z14a' , 'Z14a' , 'Z14a' , 'Z14a' , 'Z12b' , 'Z12b' , 'Z12b' , 'Z12b' , 'Z12b' , 'Z12b' , 'Z12b' , 'Z12b' , 'Z14b' , 'Z14b' , 'Z14b' , 'Z14b' , 'Z14b' , 'Z14b' , 'Z14b' , 'Z14b'  ], 
        'R': [
'Z12a', 'Z12b', 'Z12b', 'Z12c', 'Z12c', 'Z12c', 'Z12c', 'Z12c', 'Z12c', 'Z12d', 'Z12d', 'Z12d', 'Z12d', 'Z12d', 'Z12d', 'Z12e', 'Z12e', 'Z12e', 'Z12e', 'Z12e', 'Z12e', 'Z12f', 'Z12f', 'Z12f', 'Z12f', 'Z12f', 'Z12f', 'Z14a', 'Z14a', 'Z14a', 'Z14a', 'Z14a', 'Z14a', 'Z14b', 'Z14b', 'Z14b', 'Z14b', 'Z14b', 'Z14b', 'Z15a', 'Z15a', 'Z15a', 'Z15a', 'Z15a', 'Z15a', 'Z16a', 'Z16a', 'Z16b', 'Z16b', 'Z16b', 'Z16b', 'Z16b', 'Z16b'],
        'delta': []
        }

specialphases = ['hcp', 'bcc', 'fcc']

def tags_to_cns(cptaglist : list[str] ):
    return np.array( [re.sub('[A-Za-z]','', tag) for tag in cptaglist] ).astype(int)

cn_persite : dict = {structure:  tags_to_cns(sites) for structure, sites in cn_dict.items()}

def get_relevant_sorters(AtomsObjects : pd.core.frame.DataFrame , Sorters: pd.core.series.Series) -> pd.core.series.Series:
    return Sorters[AtomsObjects.file.map(lambda f: f[0])]

def sorting_feature(
        AtomsObjects: pd.core.frame.DataFrame,
        Sorters: pd.core.series.Series,
        SublatticeTags: pd.core.series.Series
        ) -> pd.core.frame.DataFrame:
    relevantsorters = get_relevant_sorters(AtomsObjects, Sorters)
    relevanttags = SublatticeTags[relevantsorters.index]
    df = {}
    for index, file in AtomsObjects.file.iteritems():
        df[index] = {'sorters': np.array(relevantsorters[file[0]]), 'sublatticetags': relevanttags[file[0]], 'file' : file[0]}
    return pd.DataFrame.from_dict(df, orient='index')

def correct_sortings_fromphases( 
    AtomsObjects: pd.core.frame.DataFrame,
    phase_feature: pd.core.series.Series,
    sorting_features: pd.core.series.Series
    ) -> pd.core.series.SeriesInfo:

    fixed_sorters = sorting_features.copy()
    samplephase = phase_feature[AtomsObjects.index]
    sampleinspecial = samplephase.map(lambda p: p in specialphases)
    fixed_sorters[sampleinspecial] = AtomsObjects.atoms[sampleinspecial].map(lambda a: np.arange(len(a)))
    samplenull = fixed_sorters.map(len)==0
    fixed_sorters[samplenull] = AtomsObjects.atoms[samplenull].map(lambda a: np.arange(len(a)))
    return  fixed_sorters.map(lambda s: np.array(s-s.min()))

def correct_occupation_fromphases(
        phase_feature: pd.core.series.Series,
        sublattice_feature: pd.core.series.Series,
        AtomsObjects: pd.core.series.Series
        ) -> pd.core.series.Series:
    fixed_tags = sublattice_feature.copy()
#    samplephase = phase_feature[sublattice_feature]
    hasempty = fixed_tags.map(lambda v : '' in v or len(v) == 0)
    fixed_tags[hasempty] = AtomsObjects.loc[hasempty].map(lambda a: ['A']*len(a))

    return fixed_tags

def get_sitecn(
        phase_feature: pd.core.series.Series,
        atoms_objects: pd.core.series.Series, 
        sorters_feature: pd.core.series.Series, 
        ) -> pd.core.series.Series:
    sitecn = {}
    progress = tqdm(phase_feature.iteritems(), total=phase_feature.shape[0])
    for index, phase in progress:
        if phase in specialphases:
            sitecn[index] = np.tile(np.unique(cn_persite[phase]), len(atoms_objects[index]))
        elif len(cn_persite[phase] ) == 0:
            sitecn[index] = []
        else:
            sitecn[index] = np.zeros_like(sorters_feature[index])
            sitecn[index][sorters_feature[index]]  = cn_persite[phase]
    return pd.Series(sitecn)


def get_normalization(_normoption : str, _coincidences : pd.core.series.Series) -> float:
    norma_ = len(_coincidences)
    # this is overkill but this works like this. 
    # if I want to normalize averages over all atoms, len coincidence works.
    if _normoption == 'NCP':
    # otherwise, I want to normalize the average tothe number of sites with same CP, I need the 
    # len of coincidence == true
        norma_ = len(_coincidences[_coincidences]) # get_normalization(normalization, coincidences)
    # but if there are no coincidences for this CP, I just return one so the average is not NaN
    return np.max([1,norma_])

def get_array_average(_array : np.array,  _coincidence: pd.core.series.Series, _norma: float) -> float:
    cases = _array[_coincidence]
    return np.sum(cases)/_norma

def cn_average(
        vectorfeature: np.array , coordination : tuple, normalization : str = 'natoms', return0 = True
        ) -> dict[str,float]: 
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
        norma = get_normalization(normalization, coincidences)
        average[f'_{polyhedra}'] = np.array(atomarray)[coincidences].sum()/norma

    return {index: average}

def cn_composition(_chemicalsymbols : list[str], _coordination : tuple ):
    compo = {}
    index, chemicalsymbols = _chemicalsymbols
    _, coordination = _coordination
    for polyhedra, nneighbours in neighbours.items():
        compo[f'_{polyhedra}'] = np.unique(np.array(chemicalsymbols)[ np.array(coordination) == nneighbours ])
    return {index: compo}

def get_shape_factors(
        BOP: pd.core.frame.DataFrame
        ) -> pd.core.frame.DataFrame:
    B1 = BOP.filter(regex='bn_1_.*')
    B2 = BOP.filter(regex='bn_2_.*')
    SF = pd.DataFrame([], index=B1.index)
    for (name, B1CN), (_, B2CN ) in zip(B1.iteritems(), B2.iteritems()):
        sfname = name.split('_')[-1]
        VALIDB2 = B2CN != 0
        SF['sf_'+sfname] = B1CN
        SF['sf_'+sfname][VALIDB2] = B1CN[VALIDB2] / B2CN[VALIDB2]
    return SF

def featurize_series(
        _Feature: pd.core.series.Series, 
        _Coordinations: pd.core.series.Series , 
        featurizer=cn_average,
        debug = False, 
        **kwargs
        ) -> pd.core.frame.DataFrame:
    iterator  = zip(_Feature.items(), _Coordinations.items())
    thisresult = [] 
    if debug:
        pdb.set_trace()
    for atomfeature, atomcoordinations in iterator:
        try:
            newresult = featurizer(atomfeature, atomcoordinations, **kwargs)
        except Exception as E:
            pdb.set_trace()
            newresult = featurizer(atomfeature, atomcoordinations, **kwargs)
        thisresult.append(newresult)
    thisresult =  dict(map(dict.popitem, thisresult))
    return pd.DataFrame.from_dict(thisresult,orient='index' )

def featurize_dataframe(
        _Features : pd.core.frame.DataFrame, 
        _coordination : pd.core.series.Series, 
        featurizer=cn_average, 
        debug = False,
        **kwargs) -> pd.core.frame.DataFrame:
    result = []
    if debug:
        pdb.set_trace()
    for colid, feature in _Features.items():
        try:
            result.append(featurize_series(feature, _coordination[feature.index], featurizer, debug = debug, **kwargs))
        except  Exception as E:
            pdb.set_trace()
            pass
        columns = result[-1].columns
        newcolumns = [f'{colid}{thiscol}' for thiscol in columns]
        result[-1].columns = newcolumns
    return pd.concat(result, axis=1)
        
def featurize_many(
        _Features : pd.core.frame.DataFrame, 
        _Coordinations : pd.core.series.Series,
        featurizers : list[object] = [cn_average],
        **kwargs) -> pd.core.frame.DataFrame:
    progress = tqdm(featurizers) #,  bar_format='{percentage:3.0f}%|{bar:100}{r_bar}{desc}')
    result = []
    for featurizer  in progress:
        progress.set_description(f'{featurizer.__name__}')
        result.append(featurize_dataframe(_Features, _Coordinations, featurizer = featurizer))
        #columns = result[-1].columns
        #newcolumns = [f'{featurizer.__name__}{thiscol}' for thiscol in columns]
        #result[-1].columns = newcolumns
    return pd.concat(result, axis=1)

def get_dimensions(thefeature : pd.core.frame.DataFrame) -> tuple[int] :
    theshape = thefeature.shape
    if len(theshape) == 2:
        dimensions = theshape
    elif len(theshape) == 1:
        dimensions = (theshape, 1)
    return dimensions

def cnav_column_name_fix (dict_of_features : dict[str, pd.core.frame.DataFrame]):
    for key, features in dict_of_features.items():
        col_replacements = {col: f'{key}{col}' for col in features.columns}
        features.rename(columns=col_replacements, inplace=True)
        
def array_expansions(
        Features :dict[str, pd.core.frame.DataFrame], 
        columnstoexpand : list[str]
        ) -> pd.core.frame.DataFrame:
    df = {}
    for feature in columnstoexpand:
        df[feature] = {}
        for index, compound in Features[feature].items():
            m = np.array(compound)
            if len(m.shape) == 1:
                m = np.vstack([ np.zeros_like(m), m ]).transpose()
            if None not in m:
                natoms, nm = m.shape #eget_dimensions(m)
                df[feature][index] = {f'{feature}_{this}' :  m[:,this] for this in range(0,nm)} # achnung moments !
            else:
                df[feature][index] = {feature: None}
        df[feature] = pd.DataFrame.from_dict(df[feature], orient='index')
    return pd.concat(df.values(), axis=1)

