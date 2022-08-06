import unittest
import sys
import os
currentlocation = os.path.dirname(__file__)
projectroot = os.path.dirname(currentlocation)
sys.path.insert(0, currentlocation)
sys.path.insert(1, projectroot)
from Tools.DatasetTools import DatasetOperator as mod


class TestRecursivity(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.DS = mod.Dataset(dataset='Cr-Co-W')

    def  test_thekeys(self):
        print(self.DS.Features.keys())

#    def test_train_on_an0(self):
#        model = mod.Pipeline([('regressor', mod.RandomForestRegressor())])
#        self.DS.make_recursivity_anbn()
#        for group, scores in self.DS.test_scores.items():
#            print(group)
#            print(scores)


    def test_cvsearch(self):
        params = {
                'regressor__hidden_layer_sizes': [ (10, 20), (20,10), (33, 3), (20, 5)], 
                'regressor__alpha': [1e-4, 1e-6 , 1e-2],
                'regressor__learning_rate': [ 'constant', 'adaptive'],
                'regressor__learning_rate_init': [1e-3, 1e-4, 1e-5, 1e-1],
                'regressor__max_iter': [10000],
                }
        estimator = mod.Pipeline([('scaler', mod.StandardScaler()), ('regressor', mod.MLPRegressor())])
        self.DS.cvsearch(estimator, params, vsearch_random_state=23192)
        print(self.DS.cv_test_scores)
        for name, params in self.DS.best_params.items():
            print(name, params)


if __name__ == '__main__':
    unittest.main()
