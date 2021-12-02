#!/usr/bin/env python
# coding: utf-8

# In[1]:

import sys
import os
import re
import pdb
sys.path.insert(
0,
'/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer/'
)

from BopFoxFeaturizer.struct_db import struct_db
from tqdm import tqdm
import pandas as pd
import numpy as np
from itertools import product

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


strucs = pd.Series(BOP.index.str.split('.').map(lambda s: s[1].split('-')[0]), index=BOP.index)

cnshs = DB.index.levels[0].sort_values()

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


def get_average_of(thephase, thebop, thecnsh, with_sublattice=False):
    # asume axis 1 is for order of the quantity
    R = [0]*orders_of_thebop(thebop)
    if phase in DB.columns:
        thisphasedb = DB[phase].dropna().reset_index()
        if with_sublattice:
            thisindexes = thisphasedb[thecnsh == thisphasedb.index]
        else:
            thisindexes = thisphasedb[thisphasedb['POLY']==thecnsh].iloc[:,-1]
        if thisindexes.size > 0 and isinstance(thebop, list):
            R = np.array(thebop)[np.hstack(thisindexes)].mean(axis=0)
        elif isinstance(thebop, float):
            R =  [thebop]
    return R

def single_string(thetuple, thefeat):
    if isinstance(thetuple, tuple):
        A =  '_'.join(thetuple)
    elif isinstance(thetuple, str):
        A = thetuple
    return A+'_'+thefeat

def average_by_cnsh(thephase, thebop, thefeat):
    return {single_string(thiscnsh, thefeat): get_average_of( phase, bop, thiscnsh) for thiscnsh in cnshs}

def average_all_sites(thefeat, thesample):
    Q = BOP[thefeat][thesample]
    if isinstance(Q, list):
        Q = np.average(Q, axis=0)
    return {'all_'+thisfeat: Q }

def average_features(BOP):
    CNAV = []
    progress = tqdm(BOP.columns)
    for thisfeat in progress:
        CNSHAV = {}
        for thissample, bop in BOP[thisfeat].iteritems():
            phase =  get_structure_from_index(thissample)
            CNSHAV[thissample] = {}
            CNSHAV[thissample].update(average_all_sites(thisfeat, thissample)) 
            if isinstance(bop, list) or isinstance(bop, np.ndarray):
                CNSHAV[thissample].update(average_by_cnsh(phase, bop, thisfeat))
        df = pd.DataFrame.from_dict(CNSHAV, orient='index')
        try:
            CNAV_STACK, CNAV_STACK_COLS = stackdata(df, df.columns)
        except Exception as E:
            pass
        CNAV.append( pd.DataFrame(data = CNAV_STACK, columns = CNAV_STACK_COLS, index = df.index) )
    CNAV_BOP = pd.concat(CNAV, axis=1)
    return CNAV_BOP

def load_features(picklefile):
    if os.path.exists(picklefile):
        return pd.read_pickle(picklefile)
    else:
        raise FileNotFoundError('pickle file does not exist. Should you calculate the moments ?')

if __name__ == ' __main__':
    case = 'CRCOW_INITIAL_NSC_ORTHOGONALOS_TABLECUTOFF_WUBIND_15.pkl'
    BS = pd.read_pickle('parsedbs.pkl')
    BOP = load_features(case)
    CNAV_BOP = average_features(BOP)
    CNAV_BOP.to_pickle('CNAveraged'+case)
