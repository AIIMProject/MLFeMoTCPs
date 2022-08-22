import os
import sys
sys.path.insert(0, os.path.dirname( os.path.dirname(__file__) ))
from sklearn.feature_selection import RFECV, SequentialFeatureSelector
from Tools.DatasetTools.DatasetOperator  import Dataset
from Tools.DatasetTools.Commoms import *
from Tools.DatasetTools.MLConveniences import *
from colorama import Fore, Style
from importlib.machinery import SourceFileLoader
FC = SourceFileLoader('FC', '/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer/BopFoxFeaturizer/FeatureConcatenate.py').load_module().FeatureConcatenate

DS = Dataset('Fe-Mo')

BS = DS.BS 
 
Features = DS.Features
FittedModels = {}
params = {
    'RF': {
        'max_depth': 10,
        'max_leaf_nodes': None,
        'min_samples_leaf': 1,
        'min_samples_split': 2
    },
    'MLP': {
        'activation': 'logistic',
        'alpha': 0.04,
        'hidden_layer_sizes': (20, 4),
        'learning_rate': 'adaptive',
        'learning_rate_init': 0.001,
        'max_iter': 1000,
        'random_state': 20091116,
        'solver': 'lbfgs'
    },
}
#estimator = Pipeline([('scaler', StandardScaler()), ( 'regressor',  MLPRegressor(**params['MLP']))])
estimator = Pipeline([( 'regressor', RandomForestRegressor(**params['RF']))])

def wrapselection(DS: Dataset, estimator: RegressorMixin, params: dict[str, object]):
    for featurename, thisfeature in Features.items():
        print(Fore.RED + featurename+'=========================='+Style.RESET_ALL)
        folds = list(DS.get_folds())
        selector = RFECV(estimator, cv=folds, scoring = 'neg_root_mean_squared_error', n_jobs=3, importance_getter='named_steps.regressor.feature_importances_' )
        selector.fit(thisfeature, DS.target)
        FittedModels[featurename] = selector
    return FittedModels


def myfeatureselection():

if __name__=='__main__':
    FittedModels = wrapselection(DS, estimator, params)
    fitted_rcecv_file=os.path.join(DS.resultslocation, 'FeatureElimination.pkl')
    with open(fitted_rcecv_file, 'wb') as pkl:
        pickle.dump(FittedModels,pkl) 
