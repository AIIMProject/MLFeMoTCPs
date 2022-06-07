import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(__file__))
import GetCNforsites as mod
from pandas.util.testing import assert_series_equal, assert_contains_all
import pandas.testing as pdt
import numpy as np

class TestGeneralFeaturizer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_sample = mod.df.index[mod.df.index.str.contains('C14')][0]

    def test_surters_and_tags(self):
        self.assertEqual(len(mod.sublaticetags), len(mod.sublaticesorters))

    def test_correct_indexing(self):
        self.assertEqual(len(mod.relevantsorters), len(mod.AtomsObjects))

    def test_df(self):
        self.assertGreater(len(mod.df), 0)

    def test_equal_df(self):
        self.assertEqual(len(mod.df), len(mod.relevantsorters))

    def test_df_has_all_files(self):
        self.assertSequenceEqual(list(mod.relevantsorters.index), list( mod.df.file.values))


    def test_phase_in_bs(self):
        self.assertIn('Phase', mod.BS)

#    def test_allsampleshavephases(self):
#        pdt.assert_index_equal(mod.samplephase.index, mod.df.index)

    def test_atoms_files_exist(self):
        paths = mod.AtomsObjects.file.map(lambda v: v[0])
        exists = paths.map(os.path.exists)
        self.assertTrue(all(exists))

#    def test_relevat_sorters_are_lists(self):
#        self.assertTrue(all( mod.relevantsorters.map(type) == list))

    def test_one_sorter_per_atom(self):
        self.assertSequenceEqual(list(mod.df.sorters.map(len).values), list( mod.AtomsObjects.atoms.map(len).values ))

#    def test_one_tag_per_atom(self):
#        self.assertSequenceEqual(list(mod.df.sublaticetags.map(len).values), list( mod.AtomsObjects.atoms.map(len).values ))

    def test_cn_in_df(self):
        self.assertIn('CNList', mod.df)

    def test_df_sorters_fromzero(self):
        np.testing.assert_equal(mod.df.sorters.map(min).values, np.zeros_like(mod.df.sorters))

    def test_samplec14_has_order(self):
        samplec14order = np.array([12, 12, 16, 16, 16, 16, 12, 12, 12, 12, 12, 12])
        np.testing.assert_equal(samplec14order, mod.df.CNList[self.test_sample])
        #self.assertSequenceEqual(samplec14order, mod.df.sitecn[self.test_sample])



if __name__ == '__main__' :
    unittest.main()
