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


BOP = pd.read_pickle('CRCOW_INITIAL_NSC_CANONICAL_TABLECUTOFF_WUBIND_10.pkl')

strucs = pd.Series(BOP.index.str.split('.').map(lambda s: s[1].split('-')[0]), index=BOP.index)

def get_structure_from_index(thisindex):
    fields = re.split('-|\.', thisindex)
    structure = fields[1]
    return structure

def orders_of_thebop(thisbop):
    try:
        atoms, orders = np.shape(thisbop)
        return orders
    except ValueError as E:
        return 1


def get_average_of(thephase, thebop, thecnsh):
    # asume axis 1 is for order of the quantity
    if phase not in DB.columns:
        return [0]*orders_of_thebop(thebop) # np.array(thebop).shape[-1]
    thisphasedb = DB[phase].dropna()
    thisindexes = thisphasedb[thecnsh == thisphasedb.index]
    if thisindexes.size > 0:
        return np.array(thebop)[np.hstack(thisindexes)].mean(axis=0)
    else:
        return [0]*orders_of_thebop(thebop)

cnshs = DB.index.sort_values()

SAMPLE = BOP
CNAV = []
for thisfeat in ['NSC_U_bond_atom_list', 'NSC_moments', 'NSC_an', 'NSC_bn', 'NSC_SIGMA', 'NSC_Ainf', 'NSC_Binf']:
    CNSHAV = {}
    for item, bop in SAMPLE[thisfeat].iteritems():
        phase =  get_structure_from_index(item)
        CNSHAV[item] = {}
        CNSHAV[item]['all'] = np.average(bop, axis=0) # average across all lattice sites
        CNSHAV[item].update({thiscnsh: get_average_of( phase, bop, thiscnsh) for thiscnsh in cnshs})
        pass
    CNAV_BOP = pd.DataFrame.from_dict(CNSHAV, orient='index')
    CNAV_BOP.columns = ['_'.join(v)+'_'+thisfeat if isinstance(v, tuple) else v  for v in CNAV_BOP.columns.values ]
    CNAV_STACK, CNAV_STACK_COLS = stackdata(CNAV_BOP, CNAV_BOP.columns)
    CNAV.append( pd.DataFrame(data = CNAV_STACK, columns = CNAV_STACK_COLS, index = CNAV_BOP.index) )
CNAV_BOP = pd.concat(CNAV, axis=1)

