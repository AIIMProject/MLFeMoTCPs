#!/usr/env python3
import glob
import pandas as pd 
import numpy as np
from ase.visualize import  view

list_atoms_objects = glob.glob('**AtomsObjects.pkl')

all_list  = [ pd.read_pickle(thisfile) for thisfile in list_atoms_objects ]

for thislist, thisframe in zip(list_atoms_objects, all_list):
    print(thislist, thisframe['atoms'].isna().any())

