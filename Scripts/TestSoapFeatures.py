import sys
import os

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from Tools.DatasetTools.Commoms import *
from Tools.DatasetTools.DatasetOperator import Dataset
from Tools.DatasetTools.MLConveniences import *
from sklearn.kernel_ridge import KernelRidge
import unittest
from dscribe.descriptors import SOAP


class  TestGetSoap(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.dataset = 'Fe-Mo'
        cls.components = cls.dataset.replace('-','')
        cls.BS = pd.read_pickle(os.path.join(cls.dataset,'FullyCuratedParsedBriefSummary.pkl'))
        cls.BS['atoms_objects'] = pd.read_pickle(os.path.join(cls.dataset, 'Atomsobjects', f'{cls.components}-POSCAR-initial-rescaled-AtomsObjects.pkl'))['atoms']
#        cls.BS['structures'] = pd.read_pickle(os.path.join(cls.dataset, 'Atomsobjects', f'{cls.components}-POSCAR-initial-rescaled-PymatgenStructures.pkl'))
#        cls.BS['chemical_formula'] = mod.get_chemical_formula(cls.BS)
#        cls.BS['composition'] = mod.StrToComposition().featurize_dataframe(cls.BS, "chemical_formula")['composition']
        cls.SINGLESOAPER = SOAP(species=[26, 42], rcut=4 ,nmax=1,lmax=1, sigma=0.1, rbf='gto', periodic=True, crossover=True)
        soaps = cls.SINGLESOAPER.create(cls.BS['atoms_objects'])
        cls.SOAPED = cls.BS['atoms_objects'].map(cls.SINGLESOAPER.create).map(

    def test_has_atoms(self):
        self.assertTrue(hasattr(self.BS, 'atoms_objects'))

    def no_test_soaps_dims(self):
        dims = self.SOAPED.map(lambda s: s.shape[1])
        plt.hist(dims)
        plt.show()

    def test_no_nan(self):
        self.assertEqual(self.SOAPED.dropna().shape, self.SOAPED.shape)
        print(self.SOAPED)

    def test_which_zeros(self):

        def remove_zeros(array):
            pdb.set_trace()
            pass
            return array[array != 0]

        SOAPED_NON_ZERO = self.SOAPED.map(remove_zeros)
        print(SOAPED_NON_ZERO)

        newdims = SOAPED_NON_ZERO.map(lambda a: a.shape[1])
        dims = self.SOAPED.map(lambda a: a.shape[1])

        self.assertEqual(dims, newdims)




if __name__ == '__main__':
    unittest.main()
