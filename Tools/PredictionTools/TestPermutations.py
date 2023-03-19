import os
import sys
import unittest
import pdb
import mendeleev
import numpy as np 
import pandas as pd

sys.path.insert(0, os.path.dirname( os.path.dirname(os.path.dirname(__file__)) ))

from Tools.PredictionTools.MakeAtomsOjects import permutate, decoratePOSCAR, read_vasp, make_all_atoms_objects

class TestPermutationsPoscars(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.binaryr = permutate('R', 2,11)

    def test_get_POSCAR(self):
        this_poscar , replacings = decoratePOSCAR(self.binaryr[20], species_dict = {'A': 'Fe', 'B': 'Mo'}, return_replacings=True)
        #available_file = os.path.join(os.path.join(sys.path[0], 'R-structures', 'POSCAR.'+self.binaryr[20]))
        #available_poscar = read_vasp(available_file)
        rfe = mendeleev.element('Fe').atomic_radius/100
        rmo = mendeleev.element('Mo').atomic_radius/100
        nfe = 41
        nmo = 12
        total_vol = (4/3)*np.pi*(nfe*(rfe**3) + nmo*(rmo**3))
        self.assertAlmostEqual(total_vol, this_poscar.get_volume())

    def test_atoms_dataframe(self):
        atoms_objects = make_all_atoms_objects(self.binaryr)

        


if __name__ == '__main__':
    unittest.main()
