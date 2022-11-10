#!/usr/bin/env python
# coding: utf-8

# In[1]:

import os
import glob
import pandas as pd
import pdb
import numpy as np
import re
import sys
from string import ascii_lowercase, ascii_uppercase
import os
from tqdm.auto import tqdm
from .Tools import need_to_update


def get_file_paths(dataset, searchs, csvfile ='LIST_OF_files.csv') -> list:
    csvfile = os.path.join(dataset, csvfile)
    if os.path.exists(os.path.join(dataset, 'data')):
        globsearch = f'{dataset}/data/**/{searchs}'
    else:
        globsearch = f'{dataset}/**/{searchs}'
    if not need_to_update(csvfile):
        with open(csvfile, 'r') as f:
            files = f.readlines()
    else:
        files = glob.glob(globsearch, recursive=True)
        with open(csvfile, 'w') as f:
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

def get_sublatticetags_sorted(thisposcarsorted, wheredirect, natoms):
    return thisposcarsorted[wheredirect+1:wheredirect+1+natoms].str.findall('[A-Z]').map(get_real_sublattice).values

def get_sorter_and_sorted_tags(_thisfile, THISSORTER=None, THISSUBLATICETAGS=None):
    TORETURN = ()
    POSCAR = pd.read_csv(_thisfile, dtype='str', header=None)[0] #, sep='\n'
    wheredirect = get_coord_type_line(POSCAR)
    natoms = get_number_of_atoms(POSCAR, wheredirect)
    if THISSORTER is None: # return sorter
        THISSORTER= get_sorted_sites_indexes(POSCAR)
        TORETURN += (THISSORTER, )
    POSCAR_SORTED = get_sorted_poscar(POSCAR, THISSORTER, _wheredirect=wheredirect)
    POSCAR_SORTED.to_csv(_thisfile+'-sorted', sep='\n', index=False, header=None)
    if THISSUBLATICETAGS is None:
        THISSUBLATICETAGS = get_sublatticetags_sorted(POSCAR_SORTED, wheredirect, natoms)
        TORETURN+=(THISSUBLATICETAGS,)
    return TORETURN

def init_sortersfile():
    sortersfile = 'SORTERS.pkl'
    if os.path.exists(sortersfile):
        SORTERS = pd.read_pickle(sortersfile)
    else:
        SORTERS = {}
    return SORTERS

def init_sublatsfile():
    sortersfile = 'SUBLATICETAGS.pkl'
    if os.path.exists(sortersfile):
        SUBLATICETAGS = pd.read_pickle(sortersfile)
    else:
        SUBLATICETAGS = {}
    return SUBLATICETAGS

def get_all_sorters_and_tags(dataset, files):
    sublatsfile = os.path.join(dataset, 'Atomsobjects','SUBLATICETAGS.pkl')
    SORTERS = init_sortersfile()
    SUBLATICETAGS = init_sublatsfile()
    for thisfile in tqdm(files):
        if need_to_update(thisfile):
            SORTERS[thisfile], SUBLATICETAGS[thisfile]=get_sorter_and_sorted_tags(thisfile.strip())
        thisfile_relax = thisfile.replace('-initial','-relaxed').replace('.initial','.relaxed-all')
        if need_to_update(thisfile_relax):
            try:
                get_sorter_and_sorted_tags(thisfile_relax, SORTERS[thisfile], SUBLATICETAGS[thisfile])
                SORTERS[thisfile_relax] =SORTERS[thisfile]
                SUBLATICETAGS[thisfile_relax]=SUBLATICETAGS[thisfile]
            except FileNotFoundError as E:
                pass
    return pd.Series(SORTERS), pd.Series(SUBLATICETAGS)

if __name__ == '__main__' and len(sys.argv[1]) > 1:
    searchs = sys.argv[2]
    dataset = sys.argv[1]

    files = get_file_paths(dataset, searchs)
    SORTERS, SUBLATICETAGS = get_all_sorters_and_tags(files)
    SORTERS.to_pickle('SORTERS.pkl')
    SUBLATICETAGS.to_pickle('SUBLATICETAGS.pkl')
    print('could sort only ', len(SORTERS[SORTERS.index.str.contains('relaxed-all')]),' relaxations of ',len(files)) 
