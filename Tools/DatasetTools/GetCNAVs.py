import os
import sys
import pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import GeneralFeaturizer as gf


dataset = 'Cr-Co-W'
models = ['canonical','projections', 'projections_os']
DescriptorLocation = os.path.join(dataset, 'Descriptors')
bopdescriptorlocation = { model: os.path.join(DescriptorLocation, f'CNAV_parallel_CrCoW_initial_{model}_table_WUBIND_16.pkl')  for model in models}
cndescriptorlocation = os.path.join(DescriptorLocation, 'CNList.pkl' )
cnlist = pd.read_pickle(cndescriptorlocation)
bopdescriptors = { model:  pd.read_pickle(location) for model,  location in bopdescriptorlocation.items()}
SF = {model: gf.get_shape_factors(bops) for model, bops in bopdescriptors.items()}
