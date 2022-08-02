import unittest
import sys
import os
currentlocation = os.path.dirname(__file__)
projectroot = os.path.dirname(currentlocation)
sys.path.insert(0, currentlocation)
sys.path.insert(1, projectroot)
import Recursivity as mod


class TestRecursivity(unittest.TestCase):

    @classmethod
    def setUp(cls):
        pass

    def test_an_selection(self):
        print(mod.recursion_coefficients_a)
        print(mod.recursion_coefficients_b)

    def test_train_on_an0(self):
        self.assertGreater(len( mod.test_scores ), 0)
        print(mod.test_scores)


if __name__ == '__main__':
    unittest.main()
