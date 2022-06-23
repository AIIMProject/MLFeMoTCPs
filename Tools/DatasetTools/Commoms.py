""" 
This is just a convenience tool for importing the same group of modules in the notebooks
"""
import os
import sys
import re
import numpy as np
import pandas as pd
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
plt.style.use('default')
plt.rc('figure', figsize=(15,10))
plt.rc('font', size=22)
plt.rc('text', usetex=True)
import pdb
from itertools import product
import copy
from tqdm.auto import tqdm
import glob
from itertools import permutations


def load_atoms_objects(dataset: str):
    system = dataset.replace('-', '')
    atoms_object_location = os.path.join(dataset, 'Atomsobjects', f'{system}-POSCAR-initial-rescaled-AtomsObjects.pkl')
    return pd.read_pickle(atoms_object_location)
