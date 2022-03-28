import pickle
import pdb
import pandas as pd
from matminer.featurizers.base import MultipleFeaturizer
from matminer.featurizers.composition import ElementProperty, Stoichiometry, ValenceOrbital, IonProperty, AtomicOrbitals,  \
        BandCenter,  OxidationStates, ElectronegativityDiff, Stoichiometry, TMetalFraction, ElementProperty,\
        AtomicPackingEfficiency, ElectronAffinity
from matminer.featurizers.conversions import DictToObject
from tqdm import tqdm_notebook as tqdm
from matminer.featurizers.conversions import StrToComposition, CompositionToOxidComposition
from matminer.featurizers.composition import ElementProperty
from matminer.featurizers.structure import DensityFeatures
from matminer.featurizers.structure import SiteStatsFingerprint
from matminer.featurizers.structure import StructuralHeterogeneity
from matminer.featurizers.structure import ChemicalOrdering 
from matminer.featurizers.structure import StructureComposition
from matminer.featurizers.structure import MaximumPackingEfficiency
from matminer.featurizers.structure import RadialDistributionFunction
from matminer.featurizers.structure import ElectronicRadialDistributionFunction
#from SourceDevelopementVersion import BopfoxFeatures, Featurizer, StructSummaryParser
from matminer.featurizers.conversions import DictToObject
from matminer.featurizers.site import SOAP, AGNIFingerprints, CrystalNNFingerprint, VoronoiFingerprint, ChemEnvSiteFingerprint


import os

def run_list_of_featurizers (list_of_featurizers, _BS, colid):
    return [ featurizer.featurize_dataframe(_BS, col_id=colid, ignore_errors=True) for featurizer in list_of_featurizers ]

def need_to_update(filename):
    if (not os.path.exists(filename) ):
        return True 
    elif ( os.path.getmtime(filename) < os.path.getmtime(__file__)  ):
        return True
    else:
        return False

def load_radial_distriutions(_BS):
    Featurizers = [
            RadialDistributionFunction(), 
            ElectronicRadialDistributionFunction()
            ]
    DFS = run_list_of_featurizers(Featurizers, _BS, 'atoms_objects')
    return pd.concat(DFS, axis=1)

def load_structure_features(_BS):
    Featurizers = [
            SiteStatsFingerprint.from_preset("CoordinationNumber_ward-prb-2017"),
            SiteStatsFingerprint.from_preset("LocalPropertyDifference_ward-prb-2017"),
            #StructureComposition(),
            StructuralHeterogeneity(),
            ChemicalOrdering(), 
            MaximumPackingEfficiency()
            ]
    DFS = run_list_of_featurizers(Featurizers, _BS, 'atoms_objects')
    result = pd.concat(DFS, axis=1)
    return result

def load_atomic_features(_BS):
    ep_feat = ElementProperty.from_preset(preset_name="magpie")
    result =  ep_feat.featurize_dataframe(_BS, col_id="composition",inplace=False) 
    result.drop(columns=_BS.columns, inplace=True)
    return result

def load_density_features(_BS):
    result = DensityFeatures().featurize_dataframe(_BS, col_id='atoms_objects',inplace=False, ignore_errors=True)
    result.drop(columns=_BS.columns, inplace=True)
    return result

def load_composition_features(_BS):
    Featurizers = [
        AtomicOrbitals(),
        BandCenter(),
        IonProperty(),
        Stoichiometry(),
        ElectronegativityDiff(),
        ElementProperty.from_preset(preset_name='magpie')
    ]
    #ED = ElectronegativityDiff().featurize_dataframe(BS, col_id='composition', inplace=False, ignore_errors=True)
    #Odf = CompositionToOxidComposition().featurize_dataframe(_BS, 'composition', ignore_errors=True)
    #OS = OxidationStates.featurize_dataframe(Odf, 'composition_oxid')
    result = run_list_of_featurizers(Featurizers, _BS, 'composition')
    return pd.concat(result, axis=1)


def load_soap_features(_BS):
    SOAPER = SOAP(rcut=4 ,nmax=10,lmax=5, sigma=0.1, rbf='gto', periodic=True, crossover=True) 
    SOAPF = SOAPER.fit_featurize_dataframe(_BS.dropna(), col_id = 'atoms_objects', ignore_errors=True)
    return SOAPF

def load_features(thepickle, thedata, which='atomic'):
    if need_to_update(thepickle):
        if which == 'atomic':
            Features = load_atomic_features(thedata)
        elif which == 'density':
            Features = load_density_features(thedata)
        elif which == 'composition':
            Features = load_composition_features(thedata)
        elif which == 'structure':
            Features = load_structure_features(thedata)
        elif which == 'soap':
            Features = load_soap_features(thedata)
        common_columns = thedata.columns.intersection(Features.columns)
        if len(common_columns) > 0:
            try:
                Features.drop(columns=common_columns, inplace=True)
            except Exception as E:
                pdb.set_trace()
        try:
            Features.to_pickle(thepickle)
        except AttributeError as AE:
            with open(thepickle,'wb') as f:
                pickle.dump(Features, f)
    else:
        Features = pd.read_pickle(thepickle)
    return Features

def make_magnetic_feature(MagInfo):
    if MagInfo == 'NM':
        return 0
    elif MagInfo == 'NM':
        return 1
    else:
        return 2

def get_chemical_formula(_BS):
    CHEMFOR =  _BS['atom_A'].str.replace('.*','')
    for atom in ['atom_A', 'atom_B', 'atom_C']:
        CHEMFOR += _BS[atom].str.replace('_.*','') + _BS['num_'+atom].map(lambda n: '{}'.format(n))
    return CHEMFOR

case = 'initial'
mmflatomic = os.path.join(case,'matminer_atomic_features.pkl')
mmfdensity = os.path.join (case, 'matminer_density_features.pkl')
mmfcomposition =  os.path.join (case,'matminer_composition_features.pkl')
mmfstructure =  os.path.join (case,'matminer_structure_features.pkl')
mmsoapfeatures = os.path.join(case, 'matminer_soap_features.pkl')

if  __name__ == '__main__':
    BS = pd.read_pickle('CuratedParsedBriefSummary.pkl').dropna()
    BS['atoms_objects' ] = pd.read_pickle(f'CrCoW-sorted-POSCAR-initial-rescaled-PymatgenStructures.pkl')
    BS['chemical_formula'] = get_chemical_formula(BS)
    Features = Featurizer(BS)
    BS['Mag'] = Features.Mag[BS.index].map(make_magnetic_feature)
    groundstates=Features.get_ground_states_energies()
    BS['EF'] = Features.get_formation_energy(ground_states_dic=groundstates)
    BS['composition'] = StrToComposition().featurize_dataframe(BS, "chemical_formula")['composition']
    BSsample=BS.sample(n=100)
    AtomicFeaturesMagpie = load_features(mmflatomic, BS, which='atomic')
    DensitiFeatures= load_features(mmfdensity, BS, which='density')
    CompositionFeatures = load_features(mmfcomposition, BS, which='composition')
    #StructureFeatures = load_features(mmfstructure, BS, which='structure')
    #SOAPFeatures = load_features(mmsoapfeatures,BS.dropna(),  which ='soap')
