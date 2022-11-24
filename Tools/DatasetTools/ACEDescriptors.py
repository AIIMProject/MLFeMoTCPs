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
import copy 
import matplotlib.pyplot as plt
default_options_dict = \
            {
            'deltaSplineBins': 0.001,
            'elements': ['Mo', 'Fe'],

            'embeddings': {'ALL': {
                                   'fs_parameters': [10, 1],
                                   'ndensity': 1,
                                   'npot': 'FinnisSinclair',
                                   },                   

                           },

            'bonds': {'ALL': {'NameOfCutoffFunction': 'cos',
                              #                              'core-repulsion': [10000.0, 5.0],
                              'core-repulsion': [10000.0, 10],
                              'dcut': 0.01,
                              'radbase': 'SBessel',
                              'radparameters': [2.0],
                              'rcut': 7},
                      },

            'functions': {        

                'ALL': {
                    #                    'nradmax_by_orders': [15, 3, 2, 1,1],
                    #                    'lmax_by_orders':    [0,  3, 2, 1, 0]
                    'nradmax_by_orders': [15, 3, 2, 1,1],
                    'lmax_by_orders':    [0,  3, 2, 1, 0]
                }
            }
        }

class MyPyACECalculator(object):
    
    def __init__(self, 
                 components:list[str] = ['Fe', 'Mo'],
                 multispace_basis_config : dict  = default_options_dict, 
                 ):

        self.bbasis_configuration = pyace.create_multispecies_basis_config(
                multispace_basis_config
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

import pdb

class TestMyPyAce(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ACE = MyPyACECalculator()
        cls.dataset = 'Fe-Mo'
        cls.DS : self.dataset = Dataset(cls.dataset)
        cls.AtomsObjects = load_atoms_objects(cls.dataset)
        cls.F = Featurizer(cls.DS.BS)
        cls.selection = ( cls.F.StrucNames == 'bcc' ) | ( cls.F.StrucNames == 'hcp' )| ( cls.F.StrucNames == 'fcc' )
#        cls.selection &= ( cls.DS.BS.num_atoms == 1 ) 
        cls.selection_Mo = cls.selection & cls.DS.BS.loc[cls.selection].atom_A.str.contains('Mo')

        cls.selection_Fe = cls.selection & cls.DS.BS.loc[cls.selection].atom_A.str.contains('Fe')
        pass

    def test_bcc_projections(self):
        bccfemo : ase.atoms.Atoms = bulk('Fe', crystalstructure='bcc', a=2.842, cubic=True)
        bccfemo[0].symbol='Mo'
        projections = self.ACE.get_ace_projections(bccfemo)
        self.assertEqual(bccfemo.get_global_number_of_atoms(), projections.shape[0])

    def test_hast_atoms_objects(self):
        types = self.AtomsObjects['atoms'].map(type)
        self.assertTrue(np.all(types == ase.atoms.Atoms ))

    def test_can_calculate_one(self):
        thisatom : ase.atoms.Atoms= self.AtomsObjects['atoms'].sample(n=1)[0]  
        thisprojections = self.ACE.get_ace_projections(thisatom)
        self.assertEqual(thisatom.get_global_number_of_atoms(), thisprojections.shape[0])

    def test_featurize_many(self):
        sample = self.AtomsObjects['atoms'].sample (n=10)
        sample_features = sample.map(self.ACE.get_ace_projections)
        natoms = sample.map(lambda a: a.get_global_number_of_atoms())
        nfeatures = sample_features.map(lambda a: a.shape[0])
        samesizes = nfeatures == natoms
        self.assertTrue(np.all(samesizes))

    def test_featurize_Mo_bulk(self):
        selection_features = self.AtomsObjects['atoms'][self.selection].map(self.ACE.get_ace_projections)
        print(selection_features)

    def test_inverted_functions(self):
        new_multispace_config = copy.deepcopy(default_options_dict)
        new_multispace_config['bonds'] = { 
              'Fe': {'NameOfCutoffFunction': 'cos',
                       'core-repulsion': [10000.0, 10],
                       'dcut': 0.01,
                       'radbase': 'SBessel',
                       'radparameters': [2.0],
                       'rcut': 7},
              'FeMo': {'NameOfCutoffFunction': 'cos',
                       'core-repulsion': [10, 10000.0],
                       'dcut': 0.01,
                       'radbase': 'SBessel',
                       'radparameters': [2.0],
                       'rcut': 7},
              'MoFe': {'NameOfCutoffFunction': 'cos',
                       'core-repulsion': [10000.0, 10],
                       'dcut': 0.01,
                       'radbase': 'SBessel',
                       'radparameters': [2.0],
                       'rcut': 7},
              'Mo': {'NameOfCutoffFunction': 'cos',
                       'core-repulsion': [10000.0, 10],
                       'dcut': 0.01,
                       'radbase': 'SBessel',
                       'radparameters': [2.0],
                       'rcut': 7},
              }
        NewACE = MyPyACECalculator(multispace_basis_config = new_multispace_config)
        features_Mo = self.AtomsObjects['atoms'][self.selection_Mo].map(self.ACE.get_ace_projections)
        features_Fe = self.AtomsObjects['atoms'][self.selection_Fe].map(self.ACE.get_ace_projections)
        print(" features of selections with custom config " )
        print (features_Fe[0][features_Fe[0] != 0])
        print (features_Mo[0][features_Mo[0] != 0])
        fig, ax = plt.subplots()
        ax.plot(features_Fe[0][0], label =features_Fe.index[0])
        ax.plot(features_Mo[0][0], label =features_Mo.index[0])
        ax.set_yscale('log')
        ax.set_ylabel('ACE coef for 1st atom')
        ax.set_xlabel('ACE coef order')
        ax.legend()
        plt.show(block = True)



if __name__ == '__main__' :
    unittest.main()



