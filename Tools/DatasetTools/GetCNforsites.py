import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(1, '/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer/')
from BopFoxFeaturizer.Featurizer import Featurizer
import GeneralFeaturizer as gf
import pandas as pd
import numpy as np
from tqdm.auto import tqdm

rootlocation = '/home/storage/fortimtb/DatasetsML/Fe-Mo/'
BS = pd.read_pickle(os.path.join(rootlocation,  'FullyCuratedParsedBriefSummary.pkl' ))
Features = Featurizer(BS)
sublaticetags = pd.read_pickle(  os.path.join(rootlocation, 'Atomsobjects', 'SUBLATICETAGS.pkl') )
sublaticetags.index = sublaticetags.index.str.strip()
sublaticesorters =  pd.read_pickle(os.path.join( rootlocation, 'Atomsobjects','SORTERS.pkl' ))
sublaticesorters.index = sublaticesorters.index.str.strip()

AtomsObjects = pd.read_pickle(os.path.join(rootlocation, 'Atomsobjects', 'FeMo-POSCAR-initial-rescaled-AtomsObjects.pkl'))
Features = Featurizer(BS)

# atoms objects have multiple entries in the file list if there is no occupation string in 
# file name, because they match the search criterial
# I have to fix the file path so that in those cases, I choose allways the one with min len (no occupation string)

AtomsObjects.file = AtomsObjects.file.map(lambda v: min(v, key=len))

relevantsorters = sublaticesorters[AtomsObjects.file]
relevanttags = sublaticetags[relevantsorters.index]


df = {}
for index, file in AtomsObjects.file.iteritems():
    df[index] = {'sorters': np.array(relevantsorters[file]), 'sublaticetags': relevanttags[file], 'file' : file}
df = pd.DataFrame.from_dict(df, orient='index')

df['CNList'] = df['sublaticetags']

specialphases = ['hcp', 'bcc', 'fcc']

samplephase = BS['Phase'][df.index]

sampleinspecial = samplephase.map(lambda p: p in specialphases)

df.sorters[sampleinspecial] = AtomsObjects.atoms[sampleinspecial].map(lambda a: np.arange(len(a)))


df.sorters = df.sorters.map(lambda s: s-s.min())

sitecn = {}
#import pdb
progress = tqdm(BS['Phase'].iteritems(), total=BS.shape[0])
for index, phase in progress:
    if phase in specialphases:
        sitecn[index] = np.tile(gf.cn_persite[phase], len(AtomsObjects.atoms[index]))
    elif len(gf.cn_persite[phase] ) == 0:
        sitecn[index] = []
    else:
        sitecn[index] = np.zeros_like(df.sorters[index])
        sitecn[index][df.sorters[index]]  = gf.cn_persite[phase]

df['sitecn'] = pd.Series(sitecn)


