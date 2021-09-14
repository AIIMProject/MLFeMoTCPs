import pdb
import pickle
import pandas as pd
from string import ascii_uppercase, ascii_lowercase

import pandas.core.series

from GetAtomsObjects import get_parser
from BopFoxFeaturizer.parsers import BopFoxParser
from BopFoxFeaturizer.brief_summary_parser import StructSummaryParser


class AverageByPhase:

    def __init__(self, atoms_objects_file='CrCoW-sorted-POSCAR-relaxed-noscaled-AtomsObjects.pkl'):
        Parsed = get_parser()
        self.atoms_objects = pd.read_pickle(atoms_objects_file)
        self.Strucs = Parsed.Struc[self.atoms_objects.index]
        self.RDATA = Parsed.data.loc[self.atoms_objects.index]
        self.SUBLATTICES = self.sublat_with_index_asin(self.atoms_objects.dropna())

    def sublat_with_index_asin(self, REFERENCE: pd.core.frame.DataFrame) -> pd.core.series.Series:
        SUBLATTICES = pd.read_pickle('SUBLATICETAGS.pkl')
        SUBLATTICES = SUBLATTICES.loc[REFERENCE['file'].apply(lambda f: f[0].replace('-sorted', '')).values]
        SUBLATTICES.index = REFERENCE.index
        return SUBLATTICES

    def average_by_phase(self,phase: str):
        selection = ( self.RDATA.nelem == 2 ) & self.RDATA[''].str.contains(phase)
        selected_sublatices = self.SUBLATTICES.loc[selection]
        selected_positions = self.atoms_objects[selection]['atoms'].map(lambda a: a.get_scaled_positions())
        IS = []
        Positions= dict()

        self.stds = {phase:dict()}
        self.averages = {phase:dict()}

        for TAG in ascii_uppercase:
            IS = selected_sublatices.map(lambda tags: TAG == tags)
            if IS[0].sum()>0:
                Positions[TAG] = pd.Series([ positions[_is_]  for positions, _is_ in zip (selected_positions.values, IS.values) ])

        for key in Positions.keys():
            self.averages[phase][key] = Positions[key].values.mean()
            self.stds[phase][key] = Positions[key].values.std()

        
if __name__=='__main__':
    AVRLX = AverageByPhase()
    AVRLX.average_by_phase('C14')


