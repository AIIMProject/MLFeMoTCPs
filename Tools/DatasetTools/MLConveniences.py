import os
import sys
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.kernel_ridge import KernelRidge
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split, cross_val_score, cross_val_predict, GridSearchCV
from math import sqrt
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.svm import SVR
from sklearn.inspection import permutation_importance
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.linear_model import Lasso
from sklearn.neural_network import MLPRegressor
from sklearn.base import RegressorMixin

# other conveniences


def add_dataset_feature(features: pd.core.frame.DataFrame, datasetfeatures: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    """concatenates given dataset features to given features"""

    X = features.copy()
    for cname, cdata in datasetfeatures.iteritems():
        if cname not in features.columns:
            X = pd.concat([ cdata, X], axis = 1)
    return X
#    X = datasetfeatures.drop(columns=['Mag'])
#    return pd.concat([X, features], axis=1).dropna() 

def  add_mag(features: pd.core.frame.DataFrame, magfeature: pd.core.series.Series):
    if not 'Mag' in features.columns:
        return pd.concat([magfeature, features], axis=1).dropna()
    else:
        return features

def load_features(dataset: str) -> dict[str, pd.core.frame.DataFrame]:
    """loads features from prestablished pickles"""

    system = dataset.replace('-', '')
    DescriptorList = {'atomic' : 'matminer_atomic_features.pkl',
    'dataset' : 'DatasetFeatures.pkl',
    'Pyscal' : 'CNAVPyscal.pkl',
    'Canonical BOP': f'curated_{system}_initial_canonical_table_WUBIND_16.pkl',
    'Projections BOP': f'curated_{system}_initial_projections_table_WUBIND_16.pkl',
    'Projections OS BOP': f'curated_{system}_initial_projections_os_table_WUBIND_16.pkl',
    'Projections sOS BOP': f'curated_{system}_initial_projections_sos_table_WUBIND_16.pkl',
    }

    DescriptorFileList = {name: os.path.join( f'{dataset}','Descriptors',f'{basename}') for name, basename in DescriptorList.items()}
    Features = {name: pd.read_pickle(filename) for name, filename in DescriptorFileList.items()}
    Features.update({'dataset + '+name: add_dataset_feature(features, Features['dataset']) for name, features in Features.items() if 'BOP' in name})
    return  Features

def score_fitted_model(fittedmodel, xtrain,  xtest, ytrain,ytest):
    predict_train = fittedmodel.predict(xtrain)
    predict_test = fittedmodel.predict(xtest)
    return {'test': mean_squared_error(ytest, predict_test, squared = False), 'train':mean_squared_error(ytrain, predict_train, squared = False)}

def load_results_location(dataset:str) -> str:
    """simply makes the results location"""
    resultslocation = os.path.join(dataset, 'results')
    if not os.path.exists(resultslocation):
        os.makedirs(resultslocation)
    return resultslocation

def load_recursivity_results_location(dataset: str, restart: bool = False) -> str:
    resultslocation = load_results_location(dataset)
    recursivitresultslocation = os.path.join(resultslocation, 'recursivity.pkl')
    return recursivitresultslocation

