import unittest
import os
import sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import GetCNAVs as mod


class TestCNAV(unittest.TestCase):

    def test_bopcnav(self):
        self.assertEqual( len(mod.bopdescriptors), len(mod.models) )

    def test_cnlist_is_loaded(self):
        self.assertTrue(hasattr(mod, 'cnlist'))

    def test_canonical_has_average_momnent_1 (self):
        self.assertTrue('moments_1_0' in mod.bopdescriptors['canonical'].columns)

    def test_sf_is_calculated(self):
        self.assertEqual(len(mod.SF), len(mod.models))

    def test_sf_has_no_nans(self):
        self.assertEqual(mod.SF['canonical'].isna().any().sum(), 0)
        self.assertEqual(mod.SF['projections'].isna().any().sum(), 0)
        self.assertEqual(mod.SF['projections_os'].isna().any().sum(), 0)


if __name__ == '__main__':
    unittest.main()

