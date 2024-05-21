import os
import sys
import pandas as pd
import numpy as np
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
from matplotlib.ticker import FormatStrFormatter

# other conveniences


def add_dataset_feature(features: pd.core.frame.DataFrame, datasetfeatures: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    """concatenates given dataset features to given features"""

    X = features.copy()
    for cname, cdata in datasetfeatures.items():
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
    DescriptorList = {
    'atomic' : 'matminer_atomic_features.pkl',
    'dataset' : 'DatasetFeatures.pkl',
    'SOAP_canonicalW_small': 'soap_features__canonicalW__rcut_4__nmax_5__lmax_4__sigma_0.1__rbf_gto__periodic_True__crossover_True.csv',
    'SOAP_specific_small': 'soap_features__specific__rcut_4__nmax_5__lmax_4__sigma_0.1__rbf_gto__periodic_True__crossover_True.csv',
    'Pyscal' : 'CNAVPyscal.pkl',
    'ACE' :  f'{dataset}-ACE-CNAV.csv', 
    'NOZERO-ACE' :  f'{dataset}-NOZERO-ACE-CNAV.csv', 
    'NOZERO_NOONE-ACE' :  f'{dataset}-NOZERO_NOONE-ACE-CNAV.csv', 
    'NOZERO_NOONE_NOTWO-ACE' :  f'{dataset}-NOZERO_NOONE_NOTWO-ACE-CNAV.csv', 
    'NOTHREE-ACE' :  f'{dataset}-NOTHREE-ACE-CNAV.csv', 
    'NOTHREE-NOTWO-ACE' :  f'{dataset}-NOTHREE_NOTWO-ACE-CNAV.csv', 
    'NOTHREE-NOTWO_NOONE-ACE' :  f'{dataset}-NOTHREE_NOTWO_NOONE-ACE-CNAV.csv', 
    'Canonical ACE' : f'{dataset}-canonical-ACE-CNAV.csv', 
    'Canonical BOP': f'CNAV_parallel_{dataset}_initial_canonical_table_WUBIND_16.csv', 
    '0.7dProjections 0.5OS BOP': f'CNAV_parallel_{dataset}_initial_0.7projections_0.5os_table_WUBIND_16.csv', 
    '0.7spProjections 0.5OS BOP': f'CNAV_parallel_{dataset}_initial_0.7spProjections_0.5os_table_WUBIND_16.csv', 
    }


    DescriptorFileList = {name: os.path.join( f'{dataset}','Descriptors',f'{basename}') for name, basename in DescriptorList.items()}
    Features = {}
    for name, filename in DescriptorFileList.items():
        if filename[-3:] == 'pkl':
            Features[name] = pd.read_pickle(filename)
        elif filename[-3:] == 'csv': 
            Features[name] = pd.read_csv(filename, index_col = 0)
    Features.update({'dataset + '+name: add_dataset_feature(features, Features['dataset']) for name, features in Features.items() if 'BOP' in name})
#    for name, features in Features.items():
#        if 'BOP' not in name:
#            continue
#        Features[name] = features.filter('^(^moments)')
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

def collect_best_scores(FittedModels: dict[tuple, RegressorMixin]):
    best_scores = {}
    for key, fittedmodel in FittedModels.items():
        results = pd.DataFrame.from_dict(fittedmodel.cv_results_).sort_values(by='mean_test_score', ascending=False)[['mean_test_score', 'mean_train_score']]
        best_scores[key] = {'test': np.abs(results['mean_test_score']).min(), 'train':np.abs(results['mean_train_score']).min() }
    best_scores = pd.DataFrame.from_dict(best_scores, orient='index')
    best_scores.index = pd.MultiIndex.from_tuples(best_scores.index)
    best_scores.sort_values(by='test', ascending=True, inplace=True)
    best_scores.sort_index(level=0, sort_remaining=False, ascending=True, inplace=True)
    return best_scores

def get_importances(estimator, features, target):
    allimportances = permutation_importance(estimator,features, target, scoring = 'neg_root_mean_squared_error', )
    importances = pd.DataFrame(data = allimportances['importances_mean'],columns=['importances_mean'], index = features.columns) #, 'importances_std']]
    importances.sort_values(by='importances_mean', inplace=True)
    return importances

def mywrap(text:str): 
    newtext = text.replace('+', '+\n')
    return newtext

def plot_best_scores(best_scores: pd.core.frame.DataFrame, ModelName='Kernel Ridge'):
    unstack = best_scores.unstack(level=0).sort_values(by=('test',ModelName), ascending = False)
    ax = ( unstack*1000 ).plot.bar()
    xlabels = ax.get_xticklabels()
    newlabels = [l.get_text().replace('Pyscal','Steinhardt') for l in xlabels]
    newlabels = [l.replace('+','+\n') for l in newlabels]
    newlabels = [l.replace('atomic','Matminer') for l in newlabels]
    newlabels = [l.replace('dataset','polyhedra') for l in newlabels]
    ax.set_xticklabels(newlabels)
    ax.tick_params(axis='y', which = 'minor')
    ax.yaxis.set_minor_formatter(FormatStrFormatter("%.0f"))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.0f"))
    ax.set_yscale('log')
    ax.set_ylabel(r'test RMSE@$\Delta E_f$ (meV/at)')
    return ax


def clean_CNAVS(name: str, features: pd.core.frame.DataFrame):
    return features.filter(regex='^(?!.*_CN..$)')

def notyetclean(name: str):
    return ('no CNAV' not in name) and ('Zeros' not in name)

def clean_zeros(name: str, features: pd.core.frame.DataFrame):
    if 'BOP' in name:
        return features.filter(regex='^(?!.*_0$)')
    else:
        return features

def get_optimal_features(FeatureScoreData:pd.core.frame.DataFrame, remove_structure=False):
    thisatmin = FeatureScoreData['test'].argmin()
    optimal_features = FeatureScoreData.index[:thisatmin]
    if remove_structure:
        optimal_features=optimal_features[optimal_features != 'Structure']
    return optimal_features # FeatureScoreData.in
#    thisatmin = FeatureScoreData['test'].argmin()
#    return FeatureScoreData.index[:thisatmin]

def filter_features(Features_DF: pd.core.frame.DataFrame, learning_curve = pd.core.frame.DataFrame, remove_structure=False):
    if 'params' not in learning_curve.columns:
        raise ValueError('the learning curve provided is not an evaluation of best features')
    columns = get_optimal_features(learning_curve, remove_structure = remove_structure)
    return Features_DF[columns]
