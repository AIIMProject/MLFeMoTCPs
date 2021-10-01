from importlib.machinery import SourceFileLoader 
import pandas as pd
import sys
from math import pi
sys.path.insert(0, 
        '/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer/BopFoxFeaturizer/'
)

StructSummaryParser = SourceFileLoader(
        'BopFoxFeaturizer',
        '/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer/BopFoxFeaturizer/brief_summary_parser.py'
).load_module().StructSummaryParser

Featurizer = SourceFileLoader(
        'Featurizer',
        '/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer/BopFoxFeaturizer/Featurizer.py'
        ).load_module().Featurizer

BopfoxFeatures = SourceFileLoader(
        'BopfoxFeatures',
        '/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer/BopFoxFeaturizer/Featurizer.py'
        ).load_module().BopfoxFeatures
        

struct_db = SourceFileLoader(
        'struct_db',
        '/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer/BopFoxFeaturizer/struct_db.py'
        ).load_module().struct_db

FeatureConcatenate = SourceFileLoader(
        'FeatureConcatenate',
        '/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer/BopFoxFeaturizer/FeatureConcatenate.py'
        ).load_module().FeatureConcatenate

cutoffs_dict = pd.read_pickle(
        '/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer/BopFoxFeaturizer/tcp_cutoffs.pkl'
        )

cutoffs_dict.index = cutoffs_dict.index.str.split('.').map(lambda l: l[1])
cutoffs_dict['volume_factor'] = cutoffs_dict.apply(lambda l: l['rcutoff']**3/l['atoms'].get_volume(), axis = 1)
