import pandas as pd
import numpy as np
from typing import List


def validate_briefsummary(bs : pd.core.frame.DataFrame):

    mandatory_columns = ['atom_A', 'atom_B', 'num_atom_A',  'num_atom_B', 'E0', 'V0', 'B0', 'num_atoms']
    for colname in mandatory_columns:
        if colname not in bs.columns:
            raise ValueError(f'{colname} not in brief summary')



class briefsummary_normalizer:
    
    def __init__(self, ground_states: dict = None, init_bs: pd.core.frame.DataFrame = None, atomA : str =  None, atomB : str = None):
        validate_briefsummary(init_bs)
        self._ground_states = ground_states
        self._init_bs = init_bs
        self._atomA = atomA
        self._atomB = atomB

    @property
    def ground_states(self):
        return self._ground_states

    @ground_states.setter
    def ground_states(self, value: dict):
        self._ground_states = value

    @property
    def init_bs(self):
        return self._init_bs

    @init_bs.setter
    def init_bs(self, value):
        validate_briefsummary(value)
        self._init_bs = value

    @property
    def atomA(self):
        return self._atomA

    @atomA.setter
    def atomA(self, value):
        self._atomA = value

    @property
    def atomB(self):
        return self._atomB

    @atomB.setter
    def atomB(self, value):
        self._atomB = value

    def get_formation_energies(self) -> pd.core.frame.DataFrame:
        formation_energy = self.init_bs['E0'] - (
                        self.init_bs['num_atom_A']*self.init_bs['atom_A'].map(self.get_anatom_energy_contrib) 
                        +
                        self.init_bs['num_atom_B']*self.init_bs['atom_B'].map(self.get_anatom_energy_contrib) 
                )/self.init_bs['num_atoms']

        return formation_energy

    def get_atom_composition(self) -> pd.core.frame.DataFrame:

        XA = self.init_bs['num_atom_A']/self.init_bs['num_atoms']
        XA.name = f'x_{self.atomA}'
        XB = self.init_bs['num_atom_B']/self.init_bs['num_atoms']
        XB.name = f'x_{self.atomB}'
        return pd.concat([XA, XB], axis = 1)


    
    def get_anatom_energy_contrib(self, theatom: str):
            if len(theatom) == 0:
                return 0
            return self.ground_states[(theatom, 'NM')]

