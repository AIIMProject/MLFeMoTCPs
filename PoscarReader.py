#!/usr/bin/env python
# coding: utf-8

# In[1]:

import os
import glob
import pandas as pd
import pdb
import matplotlib.pyplot as plt
import numpy as np
import re
import sys
from string import ascii_lowercase, ascii_uppercase
from tqdm import tqdm

#if __name__ == '__main__':
#    searchs = sys.argv[1]

# files = glob.glob('**/POSCAR-relaxed/**/'+searchs, recursive=True)
columns = ['header', 'scaled_positions']
# Files = pd.DataFrame([], columns=columns)
def get_raw_positions(thisfile):
# for thisfile in tqdm(files):
    POSCAR = pd.read_csv(thisfile, sep='\n', dtype='str', header=None)[0]
    wheredirect = POSCAR[POSCAR.str.contains('\s*dir|\s*CAR', regex = True, flags=re.IGNORECASE)].index.values[0]
    thisnspecs = np.fromstring(POSCAR[wheredirect-1], sep=' ', dtype=int)
    natoms = thisnspecs.sum()
#    thispositions = np.fromstring('\n'.join(POSCAR[wheredirect+1:wheredirect+1+natoms].values), sep=' ', dtype=float)
    try:
        thispositions =  POSCAR[wheredirect+1:wheredirect+1+natoms].str.findall('-?[01]\.[0-9]+').map(lambda s: [float(si) for si in s] )
        thispositions = np.vstack(thispositions.to_numpy())
    except Exception as E:
        pdb.set_trace()
        pass
#    POSCAR[wheredirect+1:wheredirect+1+natoms].str.match('([0-9]\.[0-9]+\s*){3}')
#    try:
#        thispositions = thispositions.reshape(natoms, int(thispositions.shape[0]/natoms))
#    except ValueError as VE:
#        pdb.set_trace()
#        pass
##    thisposcar = pd.Series([thispositions])
    return thispositions
    











