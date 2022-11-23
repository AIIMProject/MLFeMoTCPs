#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.dirname( os.path.dirname(os.path.dirname(__file__)) ))
sys.path.insert(1, '/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer')
from BopFoxFeaturizer.Featurizer import Featurizer
import pyace
from Tools.DatasetTools.DatasetOperator import Dataset
from Tools.DatasetTools.Commoms import load_atoms_objects
import Tools.DatasetTools.GeneralFeaturizer as gf
import unittest
import warnings
warnings.filterwarnings('error')
import ase
from ase.build import bulk

class MyPyACECalculator(object):
    
    def __init__(self, components:list[str] = ['Fe', 'Mo']):

        self.bbasis_configuration = pyace.create_multispecies_basis_config(
            {
            'deltaSplineBins': 0.001,
            'elements': ['Mo', 'Fe'],

            'embeddings': {'ALL': {
                                   'fs_parameters': [1, 1],
                                   'ndensity': 1,
                                   'npot': 'FinnisSinclair',
                                   },                   

                           },

            'bonds': {'ALL': {'NameOfCutoffFunction': 'cos',
                              'core-repulsion': [10000.0, 5.0],
                              'dcut': 0.01,
                              'radbase': 'SBessel',
                              'radparameters': [2.0],
                              'rcut': 7},
                      },

            'functions': {        

                'ALL': {
                    'nradmax_by_orders': [15, 3, 2, 1,1],
                    'lmax_by_orders':    [0,  3, 2, 1, 0]
                }
            }
        }
            )
        self.configured_calculator = pyace.PyACECalculator(self.bbasis_configuration)

    def get_ace_projections(self, thisatoms: ase.atoms.Atoms):
        thisatoms.calc = self.configured_calculator
        thisatoms.get_potential_energy()
        thisprojections = np.array(thisatoms.calc.ace.projections)
        return thisprojections

    def featurize_many(self, theatoms: pd.core.series.Series(ase.atoms.Atoms)) -> pd.core.series.Series(ase.atoms.Atoms):
        thefeatures = {}
        for name, atom in theatoms.items():
            thefeatures[name] = self.get_ace_projections(atom)
        return pd.Series(thefeatures)

dataset = 'Fe-Mo'
DS : Dataset = Dataset(dataset)
AtomsObjects = load_atoms_objects(dataset)


class TestMyPyAce(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ACE = MyPyACECalculator()
        pass

    def test_bcc_projections(self):
        bccfemo : ase.atoms.Atoms = bulk('Fe', crystalstructure='bcc', a=2.842, cubic=True)
        bccfemo[0].symbol='Mo'
        projections = self.ACE.get_ace_projections(bccfemo)
        self.assertEqual(bccfemo.get_global_number_of_atoms(), projections.shape[0])

    def test_hast_atoms_objects(self):
        types = AtomsObjects['atoms'].map(type)
        self.assertTrue(np.all(types == ase.atoms.Atoms ))

    def test_can_calculate_one(self):
        thisatom : ase.atoms.Atoms= AtomsObjects['atoms'].sample(n=1)[0]  
        thisprojections = self.ACE.get_ace_projections(thisatom)
        self.assertEqual(thisatom.get_global_number_of_atoms(), thisprojections.shape[0])

    def test_featurize_many(self):
        sample = AtomsObjects['atoms'].sample (n=10)
        sample_features = sample.map(self.ACE.get_ace_projections)
        natoms = sample.map(lambda a: a.get_global_number_of_atoms())
        nfeatures = sample_features.map(lambda a: a.shape[0])
        samesizes = nfeatures == natoms
        self.assertTrue(np.all(samesizes))

    def test_featurize_Mo_bulk(self):
        F = Featurizer(DS.BS)
        selection = ( F.StrucNames == 'bcc' ) 
        selection &= ( DS.BS.num_atoms == 1 ) 
        selection &= DS.BS.loc[selection].atom_A.str.contains('Mo')
        selection_features = AtomsObjects['atoms'][selection].map(self.ACE.get_ace_projections)
        print(selection_features)


#FeMo_structure.get_potential_energy()

#projections=np.array(calc.ace.projections)
#
#print(' ACE projections shape :', projections.shape)
#
#print('first projection: ', projections[0])
#print('second  projection: ', projections[1])

if __name__ == '__main__' :
    unittest.main()



