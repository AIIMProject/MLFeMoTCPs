from importlib.machinery import SourceFileLoader
import numpy as np
import pandas as pd
from ase import Atoms
import pdb
import pickle
import os
from tqdm import tqdm 
import sys
from itertools import product
from BopFoxFeaturizer.Featurizer import Featurizer, BopfoxFeatures
from SourceDevelopementVersion import StructSummaryParser, Featurizer, BopfoxFeatures

cutoffs = { 'table': 'TABLECUTOFF'} #,'histogram': 'HISTCUTOFF' }
#TODO: make only one models file inclung all models
#TODO: change orthogonal to specific or bond_specific or sthlt
models = { 'canonicalTB':'CANONICAL', 'orthogonal_TB': 'ORTHOGONAL', 'orthogonal_sd_os':'ORTHOGONALOS' }
modelsfile = { 'canonicalTB': 'canonicaltb.bx' , 'orthogonal_TB': 'models_dimers.bx', 'orthogonal_sd_os':'models-dimers-os.bx'}
atoms = {'initial': 'INITIAL'} #, 'relaxed':'RELAXED'}
nmoments = [16]

# only loop over the models
for keymodel, keyatoms, keycutof, moments in product(models.keys(), atoms.keys(), cutoffs.keys(), nmoments):
    print('atoms: ', atoms[keyatoms], 'model: ', models[keymodel], '  cutoff: ', cutoffs[keycutof], ' moments:', moments)
    atomspickle = f'CrCoW-sorted-POSCAR-{keyatoms}-rescaled-AtomsObjects.pkl'
    resultspickle = f'CRCOW_{atoms[keyatoms]}_NSC_{models[keymodel]}_{cutoffs[keycutof]}_WUBIND_{moments}.pkl'
    AtomsObjects = pd.read_pickle(atomspickle).dropna(how='any')
    BOPC = BopfoxFeatures(
            AtomsObjects['atoms'],modelsfile[keymodel], modelname=keymodel,
            cutoffby='table', 
            binary = '/home/storage/fortimtb/CuadernoTrabajo/oldrepobopfox/src/bopfox_mpi',
            moments = moments
            )
    BOPC.calculate_bop_forall(ForceKeepSpecies=True,
            input_pickle = resultspickle
            )
    BOPC.RESULTS.to_pickle(resultspickle)
