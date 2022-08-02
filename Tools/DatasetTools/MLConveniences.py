import os
import sys
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
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

# other conveniences

def load_features(dataset: str) -> dict[str, pd.core.frame.DataFrame]:
    system = dataset.replace('-', '')
    DescriptorList = {'atomic' : 'matminer_atomic_features.pkl',
    'dataset' : 'DatasetFeatures.pkl',
    'Pyscal' : 'CNAVPyscal.pkl',
    'Canonical BOP': f'curated_{system}_initial_canonical_table_WUBIND_16.pkl',
    'Projections BOP': f'curated_{system}_initial_projections_table_WUBIND_16.pkl',
    'Projections OS BOP': f'curated_{system}_initial_projections_os_table_WUBIND_16.pkl',
    'Projections sOS BOP': f'curated_{system}_initial_projections_sos_table_WUBIND_16.pkl',
#'Canonical BOP':'preselected_cnav_canonical_BOPds.pkl',
#'Projections BOP':'preselected_cnav_projections_BOPds.pkl' ,
#'Projections OS BOP':'preselected_cnav_projections_os_BOPds.pkl'
    }
    DescriptorFileList = {name: os.path.join( f'{dataset}','Descriptors',f'{basename}') for name, basename in DescriptorList.items()}
    return  {name: pd.read_pickle(filename) for name, filename in DescriptorFileList.items()}

def score_fitted_model(fittedmodel, xtrain,  xtest, ytrain,ytest):
    predict_train = fittedmodel.predict(xtrain)
    predict_test = fittedmodel.predict(xtest)
    return {'test': mean_squared_error(ytest, predict_test, squared = False), 'train':mean_squared_error(ytrain, predict_train, squared = False)}

def load_results_location(dataset:str) -> str:
    resultslocation = os.path.join(dataset, 'results')
    if not os.path.exists(resultslocation):
        os.makedirs(resultslocation)
    return resultslocation

def load_recursivity_results_location(dataset: str, restart: bool = False) -> str:
    resultslocation = load_results_location(dataset)
    recursivitresultslocation = os.path.join(resultslocation, 'recursivity.pkl')
    return recursivitresultslocation

def add_dataset(name, features:pd.core.frame.DataFrame):
    if 'BOP' in name and len(features.columns.intersection(Features['dataset'].columns)) < 1:
        X = Features['dataset'].drop(columns=['Mag'])
        return pd.concat([X, features], axis=1).dropna()
    else:
        return features
