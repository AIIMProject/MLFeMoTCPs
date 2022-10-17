import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from Tools.DatasetTools.Commoms import *
from Tools.DatasetTools.DatasetOperator import Dataset
from Tools.DatasetTools.MLConveniences import *
from sklearn.kernel_ridge import KernelRidge
import Tools.DatasetTools.GetPymatgenFeatures as mod
import unittest
from dscribe.descriptors import SOAP


class  TestGetSoap(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.dataset = 'Fe-Mo'
        cls.components = cls.dataset.replace('-','')
        cls.BS = pd.read_pickle(os.path.join(cls.dataset,'FullyCuratedParsedBriefSummary.pkl'))
        cls.BS['atoms_objects'] = pd.read_pickle(os.path.join(cls.dataset, 'Atomsobjects', f'{cls.components}-POSCAR-initial-rescaled-AtomsObjects.pkl'))['atoms']
        cls.BS['structures'] = pd.read_pickle(os.path.join(cls.dataset, 'Atomsobjects', f'{cls.components}-POSCAR-initial-rescaled-PymatgenStructures.pkl'))
        cls.BS['chemical_formula'] = mod.get_chemical_formula(cls.BS)
        cls.BS['composition'] = mod.StrToComposition().featurize_dataframe(cls.BS, "chemical_formula")['composition']
        cls.SINGLESOAPER = SOAP(species=[26, 42], rcut=4 ,nmax=8,lmax=6, sigma=0.1, rbf='gto', periodic=True, crossover=True)
        cls.SOAPER = mod.SOAP(rcut=4 ,nmax=8,lmax=6, sigma=0.1, rbf='gto', periodic=True, crossover=True) 
#        cls.SOAPF = cls.SOAPER.fit_featurize_dataframe(cls.BS.dropna(), col_id = 'structures', ignore_errors=False, fit_args={'positions':None}).filter(regex='SOAP.*')

    def test_has_atoms(self):
        self.assertTrue(hasattr(self.BS, 'atoms_objects'))

    def test_one_soap(self):
        one_soap = self.SINGLESOAPER.create(self.BS['atoms_objects'][0])
        print(len(self.BS['atoms_objects'][0]))
        print(one_soap.shape)
        print(len(self.BS['atoms_objects'][1]))
        one_soap = self.SINGLESOAPER.create(self.BS['atoms_objects'][1])
        print(one_soap.shape)

    def test_many_soap(self):
        SOAPED = self.BS['atoms_objects'].map(self.SINGLESOAPER.create)
        print(SOAPED.map(np.shape))

    def no_test_chemical_formula(self):
        print(self.BS['chemical_formula'])

    def no_test_composition(self):
        print(self.BS['composition'])

    def no_test_SOAPF(self):
        self.assertEqual(self.SOAPF.dropna().shape, self.SOAPF.shape)



if __name__ == '__main__':
    unittest.main()
