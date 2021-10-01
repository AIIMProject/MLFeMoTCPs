import pdb
import pandas as pd
from matminer.featurizers.base import MultipleFeaturizer
from matminer.featurizers.composition import ElementProperty, Stoichiometry, ValenceOrbital, IonProperty, AtomicOrbitals
from matminer.featurizers.composition import BandCenter,  OxidationStates, ElectronegativityDiff, Stoichiometry, TMetalFraction, \
                                             ElementProperty, AtomicPackingEfficiency, ElectronAffinity
from matminer.featurizers.structure import (SiteStatsFingerprint,
                                            StructuralHeterogeneity,
                                            ChemicalOrdering, 
                                            StructureComposition,
                                            MaximumPackingEfficiency)
from matminer.featurizers.conversions import DictToObject
from tqdm import tqdm_notebook as tqdm
from matminer.featurizers.conversions import StrToComposition, CompositionToOxidComposition
from matminer.featurizers.composition import ElementProperty
from matminer.featurizers.structure import DensityFeatures
from SourceDevelopementVersion import BopfoxFeatures, Featurizer, StructSummaryParser
from matminer.featurizers.structure import (SiteStatsFingerprint, StructuralHeterogeneity,
                                            ChemicalOrdering, StructureComposition, MaximumPackingEfficiency )
from matminer.featurizers.conversions import DictToObject
import os

def calcuate_atomic_features(_BS):
    ep_feat = ElementProperty.from_preset(preset_name="magpie")
    result =  ep_feat.featurize_dataframe(_BS, col_id="composition",inplace=False) 
    result.drop(columns=_BS.columns, inplace=True)
    return result

def calculate_density_features(_BS):
    result = DensityFeatures().featurize_dataframe(_BS, col_id='atoms_objects',inplace=False, ignore_errors=True)
    result.drop(columns=_BS.columns, inplace=True)
    return result

def calculate_composition_features(_BS):
    AO = AtomicOrbitals().featurize_dataframe(BS, col_id='composition', inplace=False)[['HOMO_energy','LUMO_energy']]
    BC = BandCenter().featurize_dataframe(BS, col_id='composition', inplace=False)['band center']
    IP = IonProperty().featurize_dataframe(BS, col_id='composition', inplace=False, ignore_errors=True)
    ST = Stoichiometry().featurize_dataframe(BS, col_id='composition', inplace=False, ignore_errors=True)
    #ED = ElectronegativityDiff().featurize_dataframe(BS, col_id='composition', inplace=False, ignore_errors=True)
    #Odf = CompositionToOxidComposition().featurize_dataframe(_BS, 'composition', ignore_errors=True)
    #OS = OxidationStates.featurize_dataframe(Odf, 'composition_oxid')
    result = pd.concat([AO, BC, IP,ST ], axis=1)
    return result

def calculate_structure_features(_BS):
    featurizer = MultipleFeaturizer([
        SiteStatsFingerprint.from_preset("CoordinationNumber_ward-prb-2017"),
        SiteStatsFingerprint.from_preset("LocalPropertyDifference_ward-prb-2017"),
        StructureComposition(IonProperty(fast=True)),
    ])
    result  = featurizer.featurize_many(BS['atoms_objects'], ignore_errors=True)

def need_to_update(thefile):
    return (not os.path.exists(thefile)) or (os.path.getmtime(thefile) < os.path.getmtime(__file__))

def load_features(thepickle, thedata, which='atomic'):
    if need_to_update(thepickle):
        if which == 'atomic':
            Features = calcuate_atomic_features(thedata)
        elif which == 'density':
            Features = calculate_density_features(thedata)
        elif which == 'composition':
            Features = calculate_composition_features(thedata)
        elif which == 'structure':
            Features = calculate_structure_features(thedata)
        common_columns = thedata.columns.intersection(Features.columns)
        if len(common_columns) > 0:
            try:
                Features.drop(columns=common_columns, inplace=True)
            except Exception as E:
                pdb.set_trace()
        Features.to_pickle(thepickle)
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

case = 'relaxed'
mmflatomic = os.path.join(case,'matminer_atomic_features.pkl')
mmfdensity = os.path.join (case, 'matminer_density_features.pkl')
mmfcomposition =  os.path.join (case,'matminer_composition_features.pkl')
mmfstructure =  os.path.join (case,'matminer_structure_features.pkl')

if  __name__ == '__main__':
    BS = pd.read_pickle('parsedbs.pkl')
    BS['atoms_objects'] = pd.read_pickle('CrCoW-sorted-POSCAR-{}-rescaled-PymatgenStructures.pkl'.format(case)).dropna()
    BS['chemical_formula'] = get_chemical_formula(BS)
    Features = Featurizer(BS)
    BS['Mag'] = Features.Mag[BS.index].map(make_magnetic_feature)
    groundstates=Features.get_ground_states_energies()
    BS['EF'] = Features.get_formation_energy(ground_states_dic=groundstates)
    BS['composition'] = StrToComposition().featurize_dataframe(BS, "chemical_formula")['composition']
    AtomicFeaturesMagpie = load_features(mmflatomic, BS, which='atomic')
    DensitiFeatures= load_features(mmfdensity, BS, which='density')
    CompositionFeatures = load_features(mmfcomposition, BS, which='composition')
    StructureFeatures = load_features(mmfstructure, BS, which='structure')
