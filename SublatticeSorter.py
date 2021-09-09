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
import os
from tqdm import tqdm

if __name__ == '__main__':
    searchs = sys.argv[1]

def get_file_paths( searchs, csvfile ='LIST_OF_files.csv'):
    if os.path.exists(csvfile) and os.path.getmtime(__file__) < os.path.getmtime(csvfile):
        with open('LIST_OF_files.csv', 'r') as f: 
            files = f.readlines('LIST_OF_files.csv')
    else:
        files = glob.glob('**/'+searchs, recursive=True)
        with open('LIST_OF_files.csv', 'w') as f:
            f.writelines('\n'.join(files))
    return files

def get_sorted_poscar(poscar_orig: pd.core.series.Series, thissorter: list = [], _wheredirect: int=7):
    POSCAR_corrected = poscar_orig.copy()
    thisnspecslist = np.array(poscar_orig.iloc[_wheredirect-1].strip().split(), dtype=float)
    thissymbsfullist = np.hstack([ [ascii_lowercase[i]]*int(thisnspecslist[i]) for i in range(len(thisnspecslist)) ])
    if len(thissorter) > 0:
            thissymbsfullistsorted = thissymbsfullist[np.array(thissorter) - min(thissorter)]
    sorted_species=[1]

    for e in range(1, len(thissymbsfullist)):
        if thissymbsfullist[e] == thissymbsfullist[e-1]:
            sorted_species[-1]+=1
        else:
            sorted_species.append(1)

    POSCAR_corrected.iloc[_wheredirect-1] = str(sorted_species)[1:-1].replace(',','')

    if len(thissorter) > 0:
        POSCAR_corrected.iloc[np.sort(thissorter)]= poscar_orig.iloc[ thissorter ]
    else:
        POSCAR_corrected.iloc[_wheredirect+1:]= poscar_orig.iloc[_wheredirect+1:]
    return POSCAR_corrected

def get_real_sublattice(string):
    if len(string) > 0:
        return string[0]
    else:
        return ''
def get_coord_type_line(thisposcar):
    return thisposcar[thisposcar.str.contains('\s*dir|\s*CAR', regex = True, flags=re.IGNORECASE)].index.values[0]

def get_number_of_atoms(thisposcar, num_line_coord_type):
    return sum( [ int(n) for n in  re.split('\s+', thisposcar[num_line_coord_type-1].strip()) ] )

def get_sorted_sites_indexes(thisposcar):
    SORTER = []
    for SITE in ascii_uppercase:
        SORTER +=  thisposcar[thisposcar.str.contains('[0-9]\s+'+SITE, regex=True)].index.tolist()
    return SORTER
def get_sublatticetags_sorted(thisposcarsorted):
    return POSCAR_SORTED[wheredirect+1:wheredirect+1+natoms].str.findall('[A-Z]').map(get_real_sublattice).values

def get_sorter_and_sorted_tags(_thisfile, THISSORTER=None, THISSUBLATICETAGS=None):
    TORETURN = ()
    POSCAR = pd.read_csv(_thisfile, sep='\n', dtype='str', header=None)[0]
    wheredirect = get_coord_type_line(POSCAR)
    natoms = get_number_of_atoms(POSCAR, wheredirect)
    if THISSORTER==None: # return sorter
        TORETURN += ( get_sorted_sites_indexes(POSCAR), )
    POSCAR_SORTED = get_sorted_poscar(POSCAR, THISSORTER, _wheredirect=wheredirect)
    POSCAR_SORTED.to_csv(_thisfile+'-sorted', sep='\n', index=False, header=None)
    if THISSUBLATICETAGS==None:
        TORETURN+=(get_sublatticetags_sorted(POSCAR_SORTED), )
    return TORETURN

def get_list_poscars(files):
    SORTERS = {}
    SUBLATICETAGS = {}

    for thisfile in tqdm(files):
        SORTER[thisfile], SUBLATICETAGS[thisfile]=get_sorter_and_sorted_tags (thisfile)

        thisfile_relax = thisfile.replace('-initial','-relaxed').replace('.initial','.relaxed-all')
        try:

 #           POSCAR_RLX = pd.read_csv(thisfile_relax, sep='\n', dtype='str', header=None)[0]
 #           wheredirect_rlx = get_coord_type_line(POSCAR_RLX) #POSCAR[POSCAR.str.contains('\s*dir|\s*CAR', regex = True)].index.values[0]
 #           natoms_rlx = get_number_of_atoms(POSCAR_RLX, wheredirect_rlx)
 #           POSCAR_RLX_SORTED = get_sorted_poscar(POSCAR_RLX, SORTER, _wheredirect=wheredirect_rlx)
 #           POSCAR_RLX_SORTED.to_csv(thisfile_relax+'-sorted', index=False, sep='\n', header=None)
 #           SORTERS[thisfile_relax]=SORTER
 #           THISSUBLATTICETAGS=
        except FileNotFoundError as E:
            pass
            #print('relaxation nof found for '+thisfile)

    return pd.Series(SORTERS), pd.Series(SUBLATICETAGS)

files = get_file_paths(searchs)
SORTERS, SUBLATICETAGS = get_list_poscars(files)
print('could sort only ', len(SORTERS),' of ',len(files))
