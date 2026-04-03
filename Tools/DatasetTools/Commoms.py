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
import pdb
from itertools import product
import copy
from tqdm.auto import tqdm
import glob
from itertools import permutations

plt.rc('text', usetex=True)
plt.rc('figure', figsize=(7, 5))
plt.rc('font', size=20)
plt.rc('xtick', labelsize=18)
plt.rc('ytick', labelsize=18)
plt.rc('axes', labelsize=18)
from matplotlib.lines import Line2D

# fully curated briefsumary
def load_fully_curated_briefsummary(dataset: str) -> pd.core.frame.DataFrame:
    BSFile = os.path.join(f'{dataset}','FullyCuratedParsedBriefSummary.pkl')
    return pd.read_pickle(BSFile)


def load_atoms_objects(dataset: str, case='inital', scaling='rescaled')-> pd.core.frame.DataFrame:
    system = dataset.replace('-', '')
    # Normalise case: files on disk use hyphens (POSCAR-initial) not dots (POSCAR.initial)
    case_normalised = case.replace('.', '-')
    atoms_object_location = os.path.join(dataset, 'Atomsobjects', f'{dataset}-{case_normalised}-{scaling}-AtomsObjects.pkl')
    return pd.read_pickle(atoms_object_location)

