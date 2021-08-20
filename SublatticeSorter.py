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

if __name__ == '__main__':
    searchs = sys.argv[1]

files = glob.glob('**/'+searchs, recursive=True)


def get_sorted_poscar(poscar_orig: pd.core.series.Series, thissorter: list = [], _wheredirect: int=7):
    POSCAR_corrected = poscar_orig.copy()
    thisnspecslist = np.array(poscar_orig.iloc[_wheredirect-1].strip().split(), dtype=float)
    thissymbsfullist = np.hstack([ [ascii_lowercase[i]]*int(thisnspecs[i]) for i in range(len(thisnspecs)) ])
    if len(thissorter) > 0:
            thissymbsfullistsorted = thissymbsfullist[np.array(thissorter) - min(thissorter)]
    sorted_species=[1]

    for e in range(1, len(thissymbs)):
        if thissymbs[e] == thissymbs[e-1]:
            sorted_species[-1]+=1
        else:
            sorted_species.append(1)

    POSCAR_corrected.iloc[_wheredirect-1] = str(sorted_species)[1:-1].replace(',','')

    if len(thissorter) > 0:
        POSCAR_corrected.iloc[np.sort(thissorter)]= poscar_orig.iloc[ thissorter ]
    else:
        POSCAR_corrected.iloc[_wheredirect+1:]= poscar_orig.iloc[_wheredirect+1:]

    return POSCAR_corrected

SORTERS = {}

#TODO: make function and check existence of pickle.

for thisfile in tqdm(files):
    #MDF-COMMENT in this loop I am only collecting the sorters for each file
    #MDF-COMMENT and getting the new poscar from the function above.
    #MDF-COMMENT - I am not correcting the positionsa
    #MDF-COMMENT pandas make your life easier:
    POSCAR = pd.read_csv(thisfile, sep='\n', dtype='str', header=None)[0]
    wheredirect = POSCAR[POSCAR.str.contains('\s*dir|\s*CAR', regex = True, flags=re.IGNORECASE)].index.values[0]
    SORTER = []
    for SITE in ascii_uppercase:
        SORTER +=  POSCAR[POSCAR.str.contains('[0-9]\s+'+SITE, regex=True)].index.tolist()
    POSCAR_SORTED = get_sorted_poscar(POSCAR, SORTER, _wheredirect=wheredirect)

    POSCAR_SORTED.to_csv(thisfile+'-sorted', sep='\n', index=False, header=None)

    thisfile_relax = thisfile.replace('-initial','-relaxed').replace('.initial','.relaxed-all')
    try:
        POSCAR_RLX = pd.read_csv(thisfile_relax, sep='\n', dtype='str', header=None)[0]
#        wheredirect_rlx = POSCAR[POSCAR.str.contains('\s*dir|\s*CAR', regex = True)].index.values[0]
        POSCAR_RLX_SORTED = get_sorted_poscar(POSCAR_RLX, SORTER, _wheredirect=wheredirect)
        POSCAR_RLX_SORTED.to_csv(thisfile_relax+'-sorted', index=False, sep='\n', header=None)
        SORTERS[thisfile_relax]=SORTER
    except FileNotFoundError as E:
        pass
        #print('relaxation nof found for '+thisfile)

print('could sort only ', len(SORTERS),' of ',len(files))
