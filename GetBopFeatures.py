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
#from SourceDevelopementVersion import StructSummaryParser, Featurizer, BopfoxFeatures

cutoffs = { 'table': 'TABLECUTOFF','histogram': 'HISTCUTOFF' }
models = { 'canonicalTB':'CANONICAL', 'orthogonal_TB': 'ORTHOGONAL' }
modelsfile = { 'canonicalTB': 'canonicaltb.bx' , 'orthogonal_TB': 'models_dimers.bx'}
atoms = {'initial': 'INITIAL', 'relaxed':'RELAXED'}


for keymodel, keyatoms, keycutof in product(models.keys(), atoms.keys(), cutoffs.keys()):
    print('atoms: ', atoms[keyatoms], 'model: ', models[keymodel], '  cutoff: ', cutoffs[keycutof])
    atomspickle = f'CrCoW-sorted-POSCAR-{keyatoms}-rescaled-AtomsObjects.pkl'
    resultspickle = f'CRCOW_{atoms[keyatoms]}_NSC_{models[keymodel]}_{cutoffs[keycutof]}_WENERGY.pkl'
    AtomsObjects = pd.read_pickle(atomspickle).dropna(how='any')
    BOPC = BopfoxFeatures(
            AtomsObjects['atoms'],modelsfile[keymodel], modelname=keymodel,
            cutoffby='table', 
            binary = '/home/storage/fortimtb/CuadernoTrabajo/oldrepobopfox/src/bopfox_mpi'
            )
    BOPC.calculate_bop_forall(ForceKeepSpecies=True,
            input_pickle = resultspickle
            )
    BOPC.RESULTS.to_pickle(resultspickle)
