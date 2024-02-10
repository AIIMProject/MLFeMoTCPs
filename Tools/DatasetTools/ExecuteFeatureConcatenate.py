import sys
import os
sys.path.insert(0, os.path.dirname(( os.path.dirname(os.path.dirname(__file__)) )))
from Commoms import (pd, pickle)
import logging
import copy
import  numpy as np
import socket

from sklearn.model_selection import StratifiedKFold

from DatasetOperator import Dataset
from ModelSelection import ModelOptions
from MLConveniences import (Pipeline, RandomForestRegressor, GaussianProcessRegressor, MLPRegressor, KernelRidge, StandardScaler, GridSearchCV)
from FeatureConcatenate import NewFeatureConcatenate as FeatureConcatenate

import warnings
warnings.simplefilter('ignore')

#from sklearnex import patch_sklearn
#patch_sklearn(verbose=False)

import pdb

hostname = socket.gethostname()

target_case = 'EF_nmhcp'

suffix = 'no_hcp_bcc_fcc'

DS = Dataset('Fe-Mo', target_name=target_case,  remove_phases_query = 'Phase != "bcc" and Phase != "fcc" and Phase !="hcp"')

AllModelNames = [ 'Kernel Ridge' , 'Random Forest', 'Gaussian Process', 'Kernel Ridge','MLP']

resultslocation = DS.resultslocation

Features = DS.Features  # {name: pd.read_pickle(filename) for name, filename in DescriptorFileList.items()}


samplesplit = DS.get_samplesplit()

Models = {
    'Kernel Ridge': Pipeline([('scaler', StandardScaler()), ('regressor', KernelRidge())]),
    'MLP': Pipeline([('scaler', StandardScaler()), ('regressor', MLPRegressor())]),
    'Random Forest': Pipeline([('regressor', RandomForestRegressor())]),
    'Gaussian Process': Pipeline([('regressor', GaussianProcessRegressor())])
}


samplefolds = list(DS.get_folds())

FittedModels = {}

n_repeats = 10
iwanttoplot = ['atomic','dataset']
iwanttoplot = ['atomic no CNAV','dataset no CNAV']
iwanttoplot += ['Canonical ACE' , 'Canonical BOP'] #, 'SOAP_canonicalW']
iwanttoplot += ['0.7dProjections 0.5OS BOP', '0.7spProjections 0.5OS BOP']
iwanttoplot += ['0.7dProjections 0.5OS BOP no CNAV', '0.7spProjections 0.5OS BOP no CNAV']
iwanttoplot  += [ 'ACE no CNAV' , 'ACE']
iwanttoplot  += ['SOAP', 'SOAP no CNAV']
iwanttoplot *= n_repeats


def load_fcresults(ModelName = "Random Forest"):
    #fittedmodelslocation = os.path.join(DS.resultslocation, f'{ModelName}_{target_case}__FittedCVSearch{suffix}.pkl')
    namefile = ModelName.replace(' ','')
    feature_concat_resul_loc = os.path.join(DS.dataset, 'results', f'concatenation_results_{target_case}_{suffix}_{namefile}.pkl')  

    if os.path.exists(feature_concat_resul_loc):
        with open(feature_concat_resul_loc, 'rb') as pkl:
            FCresults = pickle.load(pkl)
    else:
        FCresults = {(ModelName, featurename):[] for featurename in np.unique(iwanttoplot)}

    for featurename in iwanttoplot:
        if (ModelName, featurename) not in FCresults.keys():
            FCresults[(ModelName, featurename)] = []
    return FCresults, feature_concat_resul_loc

FittedGS = {}

def run_feature_selection(ModelName = "Random Forest", list_of_features = iwanttoplot, nprocs = 3, logger=None):
    MO = ModelOptions(DS.dataset)
    MO.load_model_options(ModelName)
    FCresults, feature_concat_resul_loc = load_fcresults(ModelName = ModelName)
    for i in range(n_repeats):
        for featurename in iwanttoplot:
            logger.info(featurename)
            combi  = (ModelName, featurename)
            if len(FCresults[combi]) >= n_repeats:
                continue
            if len(FCresults[combi]) >= i:
                continue
            folder = StratifiedKFold(n_splits=5, shuffle=True) # , random_state=1024)
            fold_generator = folder.split(DS.samplesplit['train'], DS.StructureNames[DS.samplesplit['train']])
            folds = list(fold_generator)
            TestCV = GridSearchCV(Models[ModelName], MO.modeloptions[ModelName], cv = folds, return_train_score=True, scoring='neg_root_mean_squared_error', refit=True, n_jobs = 1)
            if 'random' not in Features[featurename].columns:
                Features[featurename]['random'] = np.random.rand(Features[featurename].shape[0])
            Features[featurename]=Features[featurename].convert_dtypes(convert_floating=True)
            corrs = pd.concat([Features[featurename],DS.target], axis = 1).corr()[target_case].abs()
            reasonable_features = corrs[corrs>=corrs['Mag']/3].index.difference([target_case])
            if 'Mag' not in reasonable_features:
                raise(  ValueError('Mag eliminated too soon ') )
            FittedGS[combi] = copy.deepcopy(TestCV)
            FC = FeatureConcatenate(DS, FittedGS[combi], model_params_grid = MO.modeloptions[ModelName], logger=logger) #fmodel.best_params_,)
            logger.debug('init feature concatenate')
            logger.debug('get list of best features')
            #FCresults[combi].append(
            new_curve = FC.get_best_features_list(combi[1],
                                              num_features = DS.Features[combi[1]].shape[1],
                                              max_workers=nprocs,
                                              search_only = reasonable_features,
                                              max_features=250, 
                                              saveto = feature_concat_resul_loc.replace('.pkl', f'_{featurename}_{i}_{hostname}.pkl')
                                              ) 
            #        )
            if 'random' in new_curve.index:
                logger.info('skipping because random was found chosen')
            FCresults, feature_concat_resul_loc = load_fcresults(ModelName = ModelName)
            FCresults[combi].append(new_curve)
            with open(feature_concat_resul_loc, 'wb') as pkl:
                pickle.dump(FCresults, pkl)

if __name__ == '__main__' :
    ModelName = sys.argv[1]
    namefile = ModelName.replace(' ','')
    logging.basicConfig(filename=f'Feature_Concatenate_{namefile}_{hostname}.log', level=logging.INFO,)# 
    logger = logging.getLogger()
    nslots = int(sys.argv[2]) #int(os.environ["NSLOTS"])
    logger.info(f'NSLOTS = {nslots}')
    logging.debug('DEBUGGING')
    run_feature_selection(ModelName=ModelName, logger = logger, nprocs=nslots)
