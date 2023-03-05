from Commoms import *
sys.path.insert(0, os.path.dirname(( os.path.dirname(os.path.dirname(__file__)) )))

import copy
from DatasetOperator import Dataset, DatasetTester

import warnings
warnings.simplefilter('ignore')


target_case = 'EF_nmhcp'

DS = Dataset('Fe-Mo', target_name=target_case)

ModelName = 'Kernel Ridge'

from MLConveniences import *

resultslocation = DS.resultslocation

Features = DS.Features  # {name: pd.read_pickle(filename) for name, filename in DescriptorFileList.items()}

Features['ACE'] = Features['ACE_CNAV'].filter(regex='_0$|Mag|Structure')

def clean_zeros(name: str, features: pd.core.frame.DataFrame):
    if 'BOP' in name:
        return features.filter(regex='^(?!.*_0$)')
    else:
        return features

def notyetclean(name: str):
    return ('BOP' in name) and ('CNAV' not in name) and ('Zeros' not in name)

Features.update({name+' no CNAV': clean_CNAVS(name, features) for name, features in Features.items() if notyetclean(name)})

samplesplit = DS.get_samplesplit()

# In[20]:


Models = {
    'Kernel Ridge': Pipeline([('scaler', StandardScaler()), ('regressor', KernelRidge())]),
    'MLP': Pipeline([('scaler', StandardScaler()), ('regressor', MLPRegressor())]),
    'Random Forest': Pipeline([('regressor', RandomForestRegressor())]),
    'Gaussian Process': Pipeline([('regressor', GaussianProcessRegressor())])
}


# In[21]:


from importlib.machinery import SourceFileLoader
MO = SourceFileLoader('MO', 'Tools/DatasetTools/ModelSelection.py').load_module().ModelOptions(DS.dataset)


from sklearn.gaussian_process.kernels import RBF, WhiteKernel, RationalQuadratic, ConstantKernel, ExpSineSquared, DotProduct, Product


MO.load_model_options(ModelName)

FittedModels = {}

Tester = DatasetTester()



somecombi = (ModelName, 'Projections BOP')

# # Feature Concatenation 

# In[58]:

