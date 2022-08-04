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

    def  test_thekeys(self):
        print(mod.Features.keys())

    def test_train_on_an0(self):
        self.assertGreater(mod.test_scores['Canonical BOP'].shape[0],  0)
        for group, scores in mod.test_scores.items():
            print(group)
            print(scores)



if __name__ == '__main__':
    unittest.main()
