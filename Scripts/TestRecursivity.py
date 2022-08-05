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
        cls.DS = mod.Dataset(dataset='Cr-Co-W')

    def  test_thekeys(self):
        print(self.DS.Features.keys())

    def test_train_on_an0(self):
        model = mod.Pipeline([('regressor', mod.RandomForestRegressor())])
        self.DS.make_recursivity_anbn()
        for group, scores in self.DS.test_scores.items():
            print(group)
            print(scores)


    def test_cvsearch():


if __name__ == '__main__':
    unittest.main()
