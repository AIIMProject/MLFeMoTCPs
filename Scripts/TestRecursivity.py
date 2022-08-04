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
    def test_train_on_an0(self):
        self.assertGreater(mod.test_scores.shape[0], 0)
        print(  mod.test_scores )


if __name__ == '__main__':
    unittest.main()
