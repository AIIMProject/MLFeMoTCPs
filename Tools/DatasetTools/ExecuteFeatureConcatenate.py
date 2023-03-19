from pandas import Index
from Commoms import *
import copy
import  numpy as np

from sklearn.model_selection import StratifiedKFold
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, RationalQuadratic, ConstantKernel, ExpSineSquared, DotProduct, Product

sys.path.insert(0, os.path.dirname(( os.path.dirname(os.path.dirname(__file__)) )))
from DatasetOperator import Dataset, DatasetTester
from ModelSelection import ModelOptions
from MLConveniences import *
from FeatureConcatenate import NewFeatureConcatenate as FeatureConcatenate

import warnings
warnings.simplefilter('ignore')

target_case = 'EF_nmhcp'

suffix = 'FixedOS'

DS = Dataset('Fe-Mo', target_name=target_case)

#ModelName = 'Kernel Ridge' 
ModelName = 'Random Forest' 


resultslocation = DS.resultslocation

Features = DS.Features  # {name: pd.read_pickle(filename) for name, filename in DescriptorFileList.items()}


Features['Projections OS BOP'] = Features['Projections OS BOP'].filter(regex = '^(?!^moments)')
Features['Canonical BOP'] = Features['Canonical BOP'].filter(regex = '^(?!^moments)')
Features['Projections BOP'] = Features['Projections BOP'].filter(regex = '^(?!^moments)')
#Features['Projections sOS BOP'] = Features['Projections sOS BOP'].filter(regex = '^(?!^moments)')
for factor in 0.6, 0.7, 0.8:
    Features[f'{factor:.1f} Projections OS BOP'] = Features[f'{factor:.1f} Projections OS BOP'].filter(regex = '^(?!^moments)')

samplesplit = DS.get_samplesplit()

Models = {
    'Kernel Ridge': Pipeline([('scaler', StandardScaler()), ('regressor', KernelRidge())]),
    'MLP': Pipeline([('scaler', StandardScaler()), ('regressor', MLPRegressor())]),
    'Random Forest': Pipeline([('regressor', RandomForestRegressor())]),
    'Gaussian Process': Pipeline([('regressor', GaussianProcessRegressor())])
}

MO = ModelOptions(DS.dataset)

MO.load_model_options(ModelName)

samplefolds = list(DS.get_folds())

fittedmodelslocation = os.path.join(DS.resultslocation, f'{ModelName}_{target_case}__FittedCVSearch{suffix}.pkl')

FittedModels = {}

n_repeats = 8

#iwanttoplot = n_repeats*['SOAP_specific no CNAV']
iwanttoplot = ['0.7 Projections OS BOP no CNAV', 'Canonical BOP no CNAV', 'SOAP_specific no CNAV'] 
iwanttoplot += ['Canonical BOP', 'SOAP_canonicalFe',  '0.6 Projections OS BOP', '0.7 Projections OS BOP', '0.8 Projections OS BOP', 'Projections OS BOP'] 
iwanttoplot += ['SOAP_specific', 'dataset', 'atomic'] # ['0.7 Projections OS BOP', 'Projections OS BOP', 'ACE', 'Projections sOS BOP', 'Projections BOP',  'Canonical BOP','SOAP_specific', 'dataset', 'atomic']#, 'ACE_CNAV']
iwanttoplot += ['ACE no CNAV']
iwanttoplot *= n_repeats
iwanttoplot += 5*['ACE']

feature_concat_resul_loc = os.path.join(DS.dataset, 'results', f'concatenation_results_{target_case}_{suffix}.pkl')  

if os.path.exists(feature_concat_resul_loc):
    with open(feature_concat_resul_loc, 'rb') as pkl:
        FCresults = pickle.load(pkl)
else:
    FCresults = {(ModelName, featurename):[] for featurename in np.unique(iwanttoplot)}

for featurename in iwanttoplot:
    if (ModelName, featurename) not in FCresults.keys():
        FCresults[(ModelName, featurename)] = []

FittedGS = {}

def run_feature_selection(list_of_features = iwanttoplot):
    for featurename in iwanttoplot:
        print(featurename)
        combi  = (ModelName, featurename)
        if len(FCresults[combi]) >= n_repeats:
            continue
        folder = StratifiedKFold(n_splits=5, shuffle=True) # , random_state=1024)
        fold_generator = folder.split(DS.samplesplit['train'], DS.StructureNames[DS.samplesplit['train']])
        folds = list(fold_generator)
        TestCV = GridSearchCV(Models[ModelName], MO.modeloptions[ModelName], cv = folds, return_train_score=True, scoring='neg_root_mean_squared_error', refit=True)
        if 'random' not in Features[featurename].columns:
            Features[featurename]['random'] = np.random.rand(Features[featurename].shape[0])
        corrs = pd.concat([Features[featurename],DS.target], axis = 1).corr()[target_case].abs()
        reasonable_features = corrs[corrs>0.1].index.difference([target_case])
        if 'Mag' not in reasonable_features:
            raise(  ValueError('Mag eliminated too soon ') )
        FittedGS[combi] = copy.deepcopy(TestCV)
        FC = FeatureConcatenate(DS, FittedGS[combi], model_params_grid = MO.modeloptions[ModelName] ) #fmodel.best_params_,)
        FCresults[combi].append( FC.get_best_features_list(combi[1], num_features = DS.Features[combi[1]].shape[1], max_workers=3, search_only = reasonable_features) )
        with open(feature_concat_resul_loc, 'wb') as pkl:
            pickle.dump(FCresults, pkl)

if __name__ == '__main__' :
    run_feature_selection()
