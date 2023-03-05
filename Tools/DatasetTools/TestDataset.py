from Commoms import *
sys.path.insert(0, os.path.dirname(( os.path.dirname(os.path.dirname(__file__)) )))

import copy
from DatasetOperator import Dataset, DatasetTester

import warnings
warnings.simplefilter('ignore')


target_case = 'EF_nmhcp'

DS : Dataset = Dataset('Fe-Mo', target_name=target_case)

ModelName = 'Kernel Ridge'

from MLConveniences import *

resultslocation = DS.resultslocation

Features = DS.Features  # {name: pd.read_pickle(filename) for name, filename in DescriptorFileList.items()}


samplesplit = DS.get_samplesplit()

# In[20]:


Models = {
    'Kernel Ridge': Pipeline([('scaler', StandardScaler()), ('regressor', KernelRidge())]),
    'MLP': Pipeline([('scaler', StandardScaler()), ('regressor', MLPRegressor())]),
    'Random Forest': Pipeline([('regressor', RandomForestRegressor())]),
    'Gaussian Process': Pipeline([('regressor', GaussianProcessRegressor())])
}


from importlib.machinery import SourceFileLoader
MO = SourceFileLoader('MO', 'Tools/DatasetTools/ModelSelection.py').load_module().ModelOptions(DS.dataset)


from sklearn.gaussian_process.kernels import RBF, WhiteKernel, RationalQuadratic, ConstantKernel, ExpSineSquared, DotProduct, Product


MO.load_model_options(ModelName)

FittedModels = {}

Tester = DatasetTester()


somecombi = (ModelName, 'Projections BOP')

import unittest

class TestDataset(unittest.TestCase):

    def test_nocnav_features(self):
        no_cnav_features = DS.Features['SOAP_specific no CNAV'].filter(regex='.*_CN..').columns
        self.assertTrue(len(no_cnav_features) < 1)


if __name__ == '__main__' :
    unittest.main()
