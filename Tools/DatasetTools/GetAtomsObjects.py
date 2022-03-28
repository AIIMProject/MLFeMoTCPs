#!/usr/bin/env python
# coding: utf-8

from importlib.machinery import SourceFileLoader
import glob
import pandas as pd
import pdb
import os
import pickle
import sys
from pymatgen.io.ase import AseAtomsAdaptor
from itertools import product
# sys.path.insert(0, '/home/users/fortimtb/storage/CuadernoTrabajo/bopfoxfeaturizer/')
# from BopFoxFeaturizer.brief_summary_parser import irregular_file_parser, StructSummaryParser
# from BopFoxFeaturizer.parsers import BopFoxParser
StructSummaryParser = SourceFileLoader(
        'StructSummaryParser',
        '/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer/BopFoxFeaturizer/brief_summary_parser.py'
        ).load_module().StructSummaryParser
BopFoxParser = SourceFileLoader(
        'BopFoxParser',
        '/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer/BopFoxFeaturizer/parsers.py'
        ).load_module().BopFoxParser

from multiprocessing import Pool

def need_to_update(afile):
    return os.path.exists(afile) and os.path.getmtime(afile) < os.path.getmtime(__file__)
    
def get_parser() -> BopFoxParser:
    if need_to_update(parsed_file):
        with open(parsed_file, 'rb') as f:
            Parsed = pickle.load(f)
    #    Parsed = pd.read_pickle(parsed_file)
    else:
        BSparser = StructSummaryParser()
        BS = BSparser.BriefSummary
        Parsed = BopFoxParser(BS)
        with open(parsed_file,'wb') as f:
            pickle.dump(Parsed, f)
    return Parsed

case=['POSCAR-initial', 'POSCAR-relaxed']
rescale_by_atoms=[True, False]
subcase = [ 'rescaled' ,  'noscaled' ]
Force= True
parsed_file = 'parsed_briefsummaries.pkl'



if __name__ == '__main__':
    Parsed = get_parser()

    for thiscase, (thisrescale, thissubcase) in product(case, zip(rescale_by_atoms, subcase)):
        database = '**/'+thiscase
        print (thiscase, thissubcase, thisrescale, database)
        AtomsFile = 'CrCoW-sorted-'+thiscase+'-'+thissubcase+'-AtomsObjects.pkl'
        if need_to_update(AtomsFile):  #os.path.exists(AtomsFile) and not Force:
            Atoms_Objects = pd.read_pickle(AtomsFile)
        else:
            Atoms_Objects, CantMake_Atoms_Object = Parsed.get_atoms_object(database=database,rescale_by_atoms=thisrescale, reset_chemistry=True, file_filter = 'sorted')
            Atoms_Objects.to_pickle(AtomsFile)
# In[ ]:
        Atoms_Objects.dropna(inplace=True)
        pymatgenfile = AtomsFile.replace('AtomsObjects','PymatgenStructures')
        Pymatgen_Structures = Atoms_Objects.copy()
        if need_to_update(pymatgenfile):
            Pymatgen_Structures = pd.read_pickle(pymatgenfile)
        else:
            Pymatgen_Structures = Atoms_Objects['atoms'].apply(AseAtomsAdaptor.get_structure)
            Pymatgen_Structures['file'] = Atoms_Objects['file']
            Pymatgen_Structures.to_pickle(pymatgenfile)
