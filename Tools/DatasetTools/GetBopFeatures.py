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
models =['canonical_W','projections', 'projections_os']
cutoff = 'table'
atoms = 'initial'
moments = 16


# In[3]:


# only loop over the models
#for keymodel, keyatoms, keycutof, moments in product(models.keys(), atoms.keys(), cutoffs.keys(), nmoments):
atomspickle =  os.path.join(dataset, f'{components}-sorted-POSCAR-{atoms}-rescaled-AtomsObjects.pkl')


# In[4]:


AtomsObjects = pd.read_pickle(atomspickle).dropna(how='any')
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
    BOPC.RESULTS.to_pickle(resultspickle)


# In[ ]:


BOPC.RESULTS

