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
import matplotlib
import matplotlib.pyplot as plt
default_options_dict = \
            {
            'deltaSplineBins': 0.001,
            'elements': ['Mo', 'Fe'],
            # to make bond specific, one can use same embeddings but different functions, but for Fe and Mo wont be much 
            # difference

            'embeddings': {'ALL': {   # somewhat canonical ?
                                   'fs_parameters': [10, 1],  # change to [1, 1, 1, 0.5] for the two densities [prefactor, exp]
                                   'ndensity': 1,  # change to 2 for two densities  
                                   'npot': 'FinnisSinclair', # FS shifted? 
                                   },                   
                           },


            'bonds': {'ALL': {'NameOfCutoffFunction': 'cos',
                              'core-repulsion': [10000.0, 10],  # tyrn off [0 0 ]
                              'dcut': 0.01,
                              'radbase': 'SBessel',  # also change to chev polys
                              'radparameters': [2.0],
                              'rcut': 7}, # change to lower probably 5 or 6
                      },

            'functions': {  # somewhat canonical ?
                'ALL': {
                    'nradmax_by_orders': [15, 3, 2, 1,1], # [ pairs, three body, four  body]
                    # take i.e [ 5 , 1,0,0,0] 
                    'lmax_by_orders':    [0,  3, 2, 1, 0]
                    #   [ 0, 1, 0, 0, 0 ] 
                    # try to choose to reproduce prev resul soap?
                }
            }
        }
from pyace.basisextension import construct_bbasisconfiguration

from pyace.basis import BBasisConfiguration

def filter_basisfuncs_for_ls(
        bbasis: BBasisConfiguration,
        selectionls: list[int] = None,
        is_select_exclusive : bool = False,
        excludels: list[int] = None
        ) -> BBasisConfiguration :
    new_blocks=[]
    for block in  bbasis.funcspecs_blocks:
        thefuncs = block.funcspecs

        if selectionls is not None:
            if  is_select_exclusive :
                chosenfuncs = [ thisfunc for thisfunc in thefuncs if len(set(selectionls).difference(thisfunc.ls)) == 0 ] #0 not in thisfunc.ls and 1 not in thisfunc.ls   ]
            else:
                chosenfuncs = [ thisfunc for thisfunc in thefuncs if len(set(selectionls).intersection(thisfunc.ls))>0 ] #0 not in thisfunc.ls and 1 not in thisfunc.ls   ]
        else:
            chosenfuncs = [ thisfunc for thisfunc in thefuncs ]

        if excludels is not None:
            chosenfuncs = [ thisfunc for thisfunc in chosenfuncs if len(set(excludels).intersection(thisfunc.ls)) == 0 ] 


        block.funcspecs=chosenfuncs
        new_blocks.append(block)
    bbasis.funcspecs_blocks = new_blocks
    return bbasis

class MyPyACECalculator(object):
    
    def __init__(self, 
                 components:list[str] = ['Fe', 'Mo'],
                 multispace_basis_config : dict  = default_options_dict, 
                 select_ls : list[int] = None, 
                 is_select_exclusive : bool = False,
                 exclude_ls : list[int] = None
                 ):

        self.multispace_basis_config : dict = multispace_basis_config
        self.bbasis_configuration : object = pyace.create_multispecies_basis_config(
                multispace_basis_config
            )
        self.raw_bbasis = construct_bbasisconfiguration(multispace_basis_config)
        if ( select_ls is None ) and ( exclude_ls is None ):
            self.configured_calculator : pyace.asecalc.PyACECalculator = pyace.PyACECalculator(self.bbasis_configuration)
        else :
            self.new_bbasis = filter_basisfuncs_for_ls(self.raw_bbasis, selectionls = select_ls, is_select_exclusive = is_select_exclusive, excludels = exclude_ls)
            self.configured_calculator : pyace.asecalc.PyACECalculator = pyace.PyACECalculator(self.new_bbasis)





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
        cls.ACE : MyPyACECalculator = MyPyACECalculator()
        cls.dataset : str = 'Fe-Mo'
        cls.DS : self.dataset = Dataset(cls.dataset)
        cls.AtomsObjects : pd.core.frame.DataFrame = load_atoms_objects(cls.dataset)
        cls.F : Featurizer = Featurizer(cls.DS.BS)
        cls.selection : pd.core.series.Series = ( cls.F.StrucNames == 'bcc' ) | ( cls.F.StrucNames == 'hcp' )| ( cls.F.StrucNames == 'fcc' )
#        cls.selection = cls.F.StrucNames == 'chi'
#        cls.selection &= ( cls.DS.BS.num_atoms == 1 ) 
        cls.selection_Mo: pd.core.series.Series  = cls.selection & cls.DS.BS.loc[cls.selection].atom_A.str.contains('Mo')
        cls.selection_Fe : pd.core.series.Series = cls.selection & cls.DS.BS.loc[cls.selection].atom_A.str.contains('Fe')
        cls.selection_binary : pd.core.series.Series = cls.selection & cls.DS.BS.loc[cls.selection].atom_B.str.contains('Mo|Fe')
        cls.default_multispace_config :dict = default_options_dict
        pass

    def compare_distros(self, Q1: pd.core.series.Series, Q2: pd.core.series.Series, L1: str, L2: str) \
            -> tuple[ plt.Figure, plt.Axes ]:
        _Q1 = np.abs(Q1)
        _Q2 = np.abs(Q2)
        fig, ax = plt.subplots()
        Q = np.hstack([_Q1[_Q1>1e-10], _Q2[_Q2>1e-10]])
        edges, bins = np.histogram(Q, bins = 100)
        logbins = np.logspace(np.log10(bins[0]), np.log10(bins[-1]), 10)
        ax.hist(np.abs(_Q1[_Q1>0]), label = L1, bins = logbins )
        ax.hist(np.abs(_Q2[_Q2>0]), hatch= '//' , label = L2, fill=False, bins = logbins )
        ax.set_xlabel('ACE coef for 1st atom')
        ax.set_yscale('log')
        ax.set_xscale('log')
        ax.legend()
        return fig,ax

    def compare_ace_projections(self, ace2_multispace_config):
        ACE2 = MyPyACECalculator(components = ['Fe','Mo'], multispace_basis_config = ace2_multispace_config)
        features1 =  self.AtomsObjects['atoms'][self.selection_binary].map(self.ACE.get_ace_projections)
        features2 = self.AtomsObjects['atoms'][self.selection_binary].map(ACE2.get_ace_projections)          
        return features1, features2

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
        self.assertNotEqual(0,   selection_features.map(np.ravel).map(lambda v: np.any(v !=0)).sum() )

    def test_change_fs_parameters(self):
        new_multispace_config = copy.deepcopy(default_options_dict)
        new_multispace_config['embeddings']['ALL'].update({'fs_parameters' : [1, 1, 1, 0.5],'ndensity': 2})
        features_bin_old , features_bin_new = self.compare_ace_projections(  new_multispace_config)
        fig, ax = self.compare_distros(features_bin_old[0][0], features_bin_new[0][0], 'scratch config' , '2 densities')
        fig.savefig('Fe-Mo/graphs/test_fs_params_1_hatches.pdf')

    def test_change_core_repulsion(self):
        new_multispace_config = copy.deepcopy(default_options_dict)
        new_multispace_config['bonds']['ALL']['core-repulsion'] = [0,0]
        features_bin_old, features_bin_new = self.compare_ace_projections(new_multispace_config)
        fig, ax = self.compare_distros(features_bin_old[0][0], features_bin_new[0][0], 'scratch config' , 'no core repulsion')
        fig.savefig('Fe-Mo/graphs/test_change_core_repulsion.pdf')


    def test_rcut(self):
        new_multispace_config = copy.deepcopy(default_options_dict)
        new_multispace_config['bonds']['ALL']['rcut'] = 6
        features_bin_old , features_bin_new = self.compare_ace_projections(new_multispace_config)
        fig, ax = self.compare_distros(features_bin_old[0][0], features_bin_new[0][0], 'scratch config' , 'rcut = 5')
        fig.savefig('Fe-Mo/graphs/test_change_rcut.pdf')

    def test_individual_embeddings(self):
        new_multispace_config = copy.deepcopy(default_options_dict)
        new_multispace_config['embeddings'] = {
                'Fe': {
                    'npot': 'FinnisSinclairShiftedScaled',
                    'fs_parameters': [1, 1, 1, 0.5], ## non-linear embedding function: 1*rho_1^1 + 1*rho_2^0.5
                    'ndensity': 2,
                    'rho_core_cut': 2000,
                    'drho_core_cut': 250
                    }, 

                'Mo': {
                    'npot': 'FinnisSinclairShiftedScaled', ## linear embedding function: 1*rho_1^1
                    'fs_parameters': [1, 1],
                    'ndensity': 1,
                    'rho_core_cut': 3000,
                    'drho_core_cut': 150
                    }
                }
        features_bin_old , features_bin_new = self.compare_ace_projections(new_multispace_config)
        fig, ax = self.compare_distros(features_bin_old[0][0], features_bin_new[0][0], 'scratch config' , 'individual embeddigns')
        fig.savefig('Fe-Mo/graphs/test_individual_embeddings.pdf')

    def test_equal_functions(self):
        new_multispace_config = copy.deepcopy(default_options_dict)
        new_multispace_config['functions'] = {
                'ALL':  {
                        'nradmax_by_orders': [15, 3, 2, 1, 1],
                        'lmax_by_orders': [ 0, 3, 2,1,0],
                        }
                }
        features_bin_old , features_bin_new = self.compare_ace_projections(new_multispace_config)
        fig, ax = self.compare_distros(features_bin_old[0][0], features_bin_new[0][0], 'scratch config' , 'new all functions')
        fig.savefig('Fe-Mo/graphs/test_equal_functions.pdf')
        return ax, fig

    def test_shorter_functions(self, new_multispace_config_functions :dict = None):
        new_multispace_config = copy.deepcopy(default_options_dict)
        if new_multispace_config_functions is None:
            new_multispace_config['functions'] = {
                                    'ALL':  {
                                            'nradmax_by_orders': [5, 1, 0, 0, 0],
                                            'lmax_by_orders': [ 0, 3, 2,1,0],
                                            }
                   }
        else:
            new_multispace_config['functions'] = new_multispace_config_functions

        features_bin_old , features_bin_new = self.compare_ace_projections(new_multispace_config) 
        fig, ax = self.compare_distros(features_bin_old[0][0], features_bin_new[0][0], 'scratch config' , 'new all functions')
        fig.savefig('Fe-Mo/graphs/test_shorter_functions.pdf')
        return fig, ax

    def test_unary_specific_functions(self,  _new_multispace_config = None):
        new_multispace_config = copy.deepcopy(default_options_dict)
        if _new_multispace_config is None:
            new_multispace_config['embeddings'] = {
                    'Fe': {
                        'npot': 'FinnisSinclairShiftedScaled',
                        'fs_parameters': [1, 1], ## non-linear embedding function: 1*rho_1^1 + 1*rho_2^0.5
                        'ndensity': 1,
                        'rho_core_cut': 2000,
                        'drho_core_cut': 250
                        }, 

                    'Mo': {
                        'npot': 'FinnisSinclairShiftedScaled', ## linear embedding function: 1*rho_1^1
                        'fs_parameters': [1, 1],
                        'ndensity': 1,
                        'rho_core_cut': 3000,
                        'drho_core_cut': 150
                        }
                    }
            new_multispace_config['functions'] = {
                                    'Fe':  {
                                            'nradmax_by_orders': [15, 4, 2, 2, 2],
                                            'lmax_by_orders': [ 0, 3, 2,1,0],
                                            },
                                    'Mo':  {
                                            'nradmax_by_orders': [15, 5, 3, 1, 1],
                                            'lmax_by_orders': [ 0, 3, 2,1,0],
                                            },
                                    'BINARY':  {
                                            'nradmax_by_orders': [5, 4, 3, 1, 1],
                                            'lmax_by_orders': [ 0, 3, 2,1,0],
                                            }
                   }
        else:
            new_multispace_config.update(_new_multispace_config)
        features_bin_old , features_bin_new = self.compare_ace_projections(new_multispace_config) 
        fig, ax = self.compare_distros(features_bin_old[0][0], features_bin_new[0][0], 'scratch config' , 'new all functions')
        fig.savefig('Fe-Mo/graphs/test_specific_unary.pdf')
        return fig, ax

    def test_new_funcs_fails(self):
        new_multispace_config = copy.deepcopy( self.default_multispace_config )
        new_multispace_config.update(
                {'embeddings':
                 {
                     'Fe': {
                         'npot': 'FinnisSinclairShiftedScaled',
                         'fs_parameters': [1, 1], ## non-linear embedding function: 1*rho_1^1 + 1*rho_2^0.5
                         'ndensity': 1,
                         'rho_core_cut': 2000,
                         'drho_core_cut': 250
                         },

                     'Mo': {
                         'npot': 'FinnisSinclairShiftedScaled', ## linear embedding function: 1*rho_1^1
                         'fs_parameters': [1, 1],
                         'ndensity': 1,
                         'rho_core_cut': 3000,
                         'drho_core_cut': 150
                         }
                     },
                 'functions':
                 {
                     'Fe':  {
                         'nradmax_by_orders': [15, 3, 1, 1, 1],
                         'lmax_by_orders': [ 0, 3, 2,1,0],
                         },
                     'Mo':  {
                         'nradmax_by_orders': [15, 4, 1, 1, 1],
                         'lmax_by_orders': [ 0, 3, 2,1,0],
                         },
                     'BINARY':  {
                         'nradmax_by_orders': [15, 5, 3, 2, 1],
                         'lmax_by_orders': [ 0, 3, 2,1,0],
                         }
                     }
                 }
                )
        NewFuncsACEer = MyPyACECalculator(multispace_basis_config=new_multispace_config ) # components = components,
        failed_projections = NewFuncsACEer.get_ace_projections(
                self.AtomsObjects['atoms'].iloc[2]
                )


    def test_plot_alternated_values(self):
        NewACE = MyPyACECalculator()
        fig, ax = plt.subplots()
        features_Mo = self.AtomsObjects['atoms'][self.selection_Mo].map(self.ACE.get_ace_projections)
        features_Fe = self.AtomsObjects['atoms'][self.selection_Fe].map(self.ACE.get_ace_projections)
        fig, ax = plt.subplots()
        ax.plot(features_Fe[0][0], label =features_Fe.index[0])
        ax.plot(features_Mo[0][0], label =features_Mo.index[0])
        ax.set_yscale('log')
        ax.set_ylabel('ACE coef for 1st atom')
        ax.set_xlabel('ACE coef order')
        ax.legend()
        fig.savefig('Fe-Mo/graphs/test_alternated_values.pdf')

    #from pyace import compute_B


if __name__ == '__main__' :
    unittest.main()



