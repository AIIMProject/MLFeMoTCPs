#!/usr/bin/env python
# coding: utf-8

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from Tools.DatasetTools.Commoms import *
from Tools.DatasetTools.MLConveniences import *
from Tools.DatasetTools.ModelSelection import ModelOptions
from Tools.DatasetTools.DatasetOperator import Dataset
from Tools.DatasetTools.FeatureConcatenate import NewFeatureConcatenate
from importlib.machinery import SourceFileLoader
import unittest


class  TestNewConcatenation(unittest.TestCase):

    @classmethod
    def  setUp(cls):
        cls.ModelName = 'Random Forest'
        cls.dataset = 'Fe-Mo'
        cls.DS = Dataset(cls.dataset)
        cls.fittedmodelslocation = os.path.join(cls.DS.resultslocation, f'{cls.ModelName}_FittedCVSearch.pkl')
        if os.path.exists(cls.fittedmodelslocation):
            with open(cls.fittedmodelslocation, 'rb') as pkl:
                cls.FittedModels = pickle.load(pkl)
        cls.Models = {
                'MLP' : Pipeline([('scaler', StandardScaler()), ('regressor', MLPRegressor())]),
                'Random Forest' : Pipeline([('regressor', RandomForestRegressor())]),

                }
        cls.group = 'Projections OS BOP'
        cls.combi =  (cls.ModelName, cls.group)
        cls.FC = NewFeatureConcatenate(cls.DS, cls.Models[cls.ModelName], model_params = cls.FittedModels[cls.combi].best_params_)

                
    def test_definitions(self):
        param_grid = {param: [value] for param, value in self.FittedModels[self.combi].best_params_.items()}

    def test_fcseesplit(self):
        self.assertTrue(hasattr(self.FC, 'samplesplit'))
        self.assertTrue(hasattr(self.DS, 'samplesplit'))

    def no_test_concat_equals_fit(self):
        nfeatures  = self.DS.Features[self.group].shape[1]
        best_feature_list = self.FC.get_best_features_list(self.group, 10)
        model = copy.deepcopy(self.FC.model)
        model.set_params(**self.FittedModels[ self.combi ].best_params_)
        xtrain, xtest, ytrain, ytest = self.DS.train_test_split(group)
        trainfeatures = best_feature_list.index
        model.fit(xtrain[trainfeatures], ytrain)
        scores = score_fitted_model(model, xtrain[trainfeatures], xtest[trainfeatures], ytrain, ytest)
        self.assertAlmostEqual(best_feature_list['test'][-1], scores['test'])
        print(best_feature_list['test'])
        print ( scores )

    def test_full_fit(self):
        model = copy.deepcopy(self.FC.model)
        model.set_params(**self.FittedModels[ self.combi ].best_params_)
        xtrain, xtest, ytrain, ytest = self.DS.train_test_split(self.group)
        model.fit(xtrain, ytrain)
        scores = score_fitted_model(model, xtrain, xtest, ytrain, ytest)
        self.assertAlmostEqual(scores['test'], 0.05, delta=0.05)

    def test_paralelizes(self):
        print("============ Test for parallel execution ===============")
        model = copy.deepcopy(self.Models[self.ModelName])
        nf = 1
        FC = NewFeatureConcatenate(self.DS, model, self.FittedModels[self.combi].best_params_)
        import time
        FC.get_best_features_list(self.combi[1], num_features=nf, max_workers=2)
        FC.get_best_features_list(self.combi[1], num_features=nf, max_workers=4)

    def  test_saves_pickle(self):
        FCResultsLocatoion=f'Fe-Mo/results/concatenation_results.pkl'
        if os.path.exists(FCResultsLocatoion):
            with open(FCResultsLocatoion, 'rb') as pkl:
                FCresults = pickle.load(pkl)
        else:
            FCresults = {}

        for (modelname, group) in self.FittedModels.keys():
            if 'BOP' not in group and 'dataset' not in group:
                continue
            model = copy.deepcopy(self.Models[self.ModelName])
            combi = (modelname, group)
            nf = self.DS.Features[group].shape[1]
            if combi in FCresults.keys():
                if FCresults[combi].shape[0] == nf:
                    continue
            FC =  NewFeatureConcatenate(self.DS, model, self.FittedModels[combi].best_params_,)
            FCresults[combi] = FC.get_best_features_list(group, num_features=nf, max_workers=3)
            with open(FCResultsLocatoion, 'wb') as pkl:
                pickle.dump(FCresults, pkl)

        
        

#    def test_finds_best_with_afixed(self):
#        best_feature = self.FC.get_best_feature(self.combi[1], fixed_features=['Structure'])
#        print ( best_feature )
#        self.assertEqual(len(best_feature.name), 2)



if __name__ == '__main__':
    unittest.main()
