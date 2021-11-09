#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
import re
import pdb
sys.path.insert(
0,
'/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer/'
)

from BopFoxFeaturizer.struct_db import struct_db

import pandas as pd

import numpy as np

from BopFoxFeaturizer.FeatureConcatenate import stackdata

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.colheader_justify', 'center')
pd.set_option('display.precision', 1)
np.set_printoptions(precision=1)

# In[2]:


DB = struct_db().sites_by_structures

# In[3]:


BOP = pd.read_pickle('CRCOW_INITIAL_NSC_CANONICAL_TABLECUTOFF_WUBIND_5.pkl')

strucs = pd.Series(BOP.index.str.split('.').map(lambda s: s[1].split('-')[0]), index=BOP.index)

def get_structure_from_index(thisindex):
    fields = re.split('-|\.', thisindex)
    structure = fields[1]
    return structure

def get_average_of(thephase, thebop, thecnsh):
    if phase not in DB.columns:
        return 0
    thisphasedb = DB[phase].dropna()
    thisindexes = thisphasedb[thecnsh == thisphasedb.index]
    if thisindexes.size > 0:
        return np.array(thebop)[np.hstack(thisindexes)].mean(axis=0)
    else:
        return [0]*np.array(thebop).shape[1]

# valid coordination shell tags
#cnshs = DB.index.get_level_values(0).unique().sort_values()
cnshs = DB.index.sort_values()

CNSHAV = {}
for item, bop in BOP['NSC_moments'].sample(n=10).iteritems():
    phase =  get_structure_from_index(item)
    CNSHAV[item] = {}
    CNSHAV[item]['all'] = np.average(bop, axis=0) # average across all lattice sites
    CNSHAV[item].update({thiscnsh: get_average_of( phase, bop, thiscnsh) for thiscnsh in cnshs})
CNAV_BOP = pd.DataFrame.from_dict(CNSHAV, orient='index')
CNAV_BOP.columns = ['moment'+'_'.join(v) if isinstance(v, tuple) else v  for v in CNAV_BOP.columns.values ]
CNAV_STACK, CNAV_STACK_COLS = stackdata(CNAV_BOP, CNAV_BOP.columns)
print(CNAV_STACK)
#print (['_'.join(s) for s in CNAV_BOP.columns.values if len(s) > 1])
#    if phase not in DB.columns:
#        CNSHAV[item] += [0]*DB.shape[0]
#        print(item, CNSHAV[item])
#    else:
#        thisaverages = []
#        for CSH, sublattice in DB[phase].iteritems():
#            print (item, CSH, sublattice)#, thisindexes)
#
#    U_list = BOP [BOP.index.str.contains('A15')]['NSC_U_bond_atom_list'].map(np.array) 
#    U_CN14 = U_list.map(lambda v: v[indexes_cn14].mean())
#
#
#    U_list.map(lambda v: v[indexes_cn14])
