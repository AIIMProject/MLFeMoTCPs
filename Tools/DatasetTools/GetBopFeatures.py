#!/usr/bin/env python
# coding: utf-8

# #  Computation of BOP Features
# 
# - input: atoms objects
# - output here: all the descriptors comming from BOP (averages, atomic site based, etc)
# 
# #  Calculation of features from available libraries
# 
# - input curated BS
# 
# 
# 
# **TODO**
# - Imports
# - make onefile for each model for each dataset: CrCoW_canonical.bx, CrCoW_projection.bx, CrCoW_projection_os.bx
# - in the file : model = canonical
# - files location in function of the dataset
# - **options: dataset, model** #,  dataset+model -> modelsfile name + modelsfile section : one modelfile per dataset.
# - generate modelsname from dataset+model
# - TODO: remove s related params from models files: onsite levels and bond integrals

# In[1]:


import os
import sys
sys.path.insert(0, '/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer/')
from BopFoxFeaturizer.Featurizer import Featurizer, BopfoxFeatures
import pandas as pd


# ## options:

# In[2]:


dataset = 'Cr-Co-W'
components = dataset.replace('-','')
models = ['canonical','projections', 'projections_os']
cutoff = 'table'
atoms = 'initial'
moments = 16


# In[3]:


# only loop over the models
#for keymodel, keyatoms, keycutof, moments in product(models.keys(), atoms.keys(), cutoffs.keys(), nmoments):
atomspickle =  os.path.join(dataset, f'{components}-sorted-POSCAR-{atoms}-rescaled-AtomsObjects.pkl')


# In[4]:


AtomsObjects = pd.read_pickle(atomspickle).dropna(how='any')


# In[5]:


from time import time


# In[6]:


results = {}
for model in models:
    modelsfile = os.path.join('models', f'{components}_{model}.bx')
    print('atoms: ', atoms, 'model: ', model, '  cutoff: ', cutoff, ' moments:', moments)
    resultspickle = os.path.join(dataset, 'Descriptors', f'{components}_{atoms}_{model}_{cutoff}_WUBIND_{moments}.pkl')
    BOPC = BopfoxFeatures(
            AtomsObjects['atoms'],modelsfile, modelname=model,
            cutoffby=cutoff, 
            binary = '/home/storage/fortimtb/CuadernoTrabajo/oldrepobopfox/src/bopfox_mpi',
            moments = moments
            )
    BOPC.calculate_bop_forall(ForceKeepSpecies=True,
            input_pickle = resultspickle
            )
    results[model] = BOPC.RESULTS
    BOPC.RESULTS.to_pickle(resultspickle)


# In[ ]:





# In[ ]:


upper = {}


# In[ ]:


lower1 = {1: {'a': 'lista'}}
lower2 = {1: {'b': 'listb'}}


# In[ ]:


upper.update(lower1)


# In[ ]:


upper.update(lower2)


# In[ ]:


upper


# In[ ]:


results['canonical']['sigma']


# In[ ]:


import re


# In[ ]:


import tarfile


# In[ ]:


import gzip


# In[ ]:


with tarfile.open('bopfoxASE_Co10Cr8W6_2022-03-31_11:22:11gmt.out.tar.gz','r') as thistar:
    logbx = thistar.extract('log.bx')
    with open('log.bx', 'r') as f:
        loglines = f.readlines()


# In[ ]:


sigmalines = [re.match(' sigma \( atom = (.*), orbital = (.*)\) (.*)', logline) for logline in loglines]


# In[ ]:


import numpy as np


# In[ ]:


sigmas = {}
for (atom, orbital, thissigmas) in [sigmaline.groups() for sigmaline in sigmalines if sigmaline != None]:
    sigmas[atom+' '+orbital] = np.fromstring(thissigmas.strip(), sep=' ')


# In[ ]:


sigmas


# In[ ]:




