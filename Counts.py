#!/usr/bin/env python
# coding: utf-8

# In[1]:


from importlib.machinery import SourceFileLoader
import pandas as pd
import glob
import re
import numpy  as np

import matplotlib.pyplot as plt
plt.style.use('seaborn')
plt.rc('figure',figsize=(15,10))
plt.rc('axes',labelsize=24)
plt.rc('xtick',labelsize=18)
plt.rc('ytick',labelsize=18)


from BopFoxFeaturizer.brief_summary_parser import StructSummaryParser as parser
#parser = SourceFileLoader(
#    'parser',
#    '/home/storage/fortimtb/CuadernoTrabajo/bopfoxfeaturizer/BopFoxFeaturizer/brief_summary_parser.py'
#).load_module().StructSummaryParser()

BS = parser().BriefSummary

fig = plt.figure()
plt.hist(
        BS['nelem'], 
        align='mid', 
        bins=[0.75, 1.25,1.75, 2.25,2.75, 3.25],
        )
plt.xticks(np.arange(1,4), np.arange(1,4).astype(int))
plt.xlabel('Number of elements in compound')
plt.ylabel('Sample counts')
plt.savefig('NumberElements.pdf')
plt.close(fig)

fig = plt.figure()
plt.hist(BS[ BS['atom_A'] != '' ]['atom_A'],alpha=0.5, density=True, align='left', label = 'as atom A')
plt.hist(BS[ BS['atom_B'] != '' ]['atom_B'],alpha=0.5, density=True, align='mid', label = 'as atom B')
plt.hist(BS[ BS['atom_C'] != '' ]['atom_C'],alpha=0.5, density=True, align='right', label = 'as atom C')
plt.legend()
plt.savefig('ElementCounts.pdf')
plt.close(fig)

elements = pd.concat([BS['atom_A'],BS['atom_B'],BS['atom_C']], axis=0).unique()

from  BopFoxFeaturizer.struct_db import struct_db
#with open('../Intermetallics_ML/clean/structures/binary/list.bcc', 'r') as f:
#    listbcc = f.readlines()[0].strip().split(' ')
structdb = struct_db()
dic, strings = structdb.get_dic_structures() 

#listbcc = ' '.join([re.sub('-.*','',s) for s in listbcc])
#
#with open('../Intermetallics_ML/clean/structures/binary/list.fcc', 'r') as f:
#    listfcc = f.readlines()[0].strip().split(' ')
#
#listfcc = ' '.join([re.sub('-.*','',s) for s in listfcc])
#
#with open('../Intermetallics_ML/clean/structures/binary/list.hcp', 'r') as f:
#    listhcp = f.readlines()[0].strip().split(' ')
#
#listhcp = ' '.join ([re.sub('-.*','',s) for s in listhcp])
#
Target_Class = pd.Series(
    BS.index.str.split('.').map(lambda l: l[1]).map(lambda s: s.split('-')[0]),
    index=BS.index
)

Target_Class[Target_Class.map(lambda s: s in strings['list.hcp'])]='hcp'
Target_Class[Target_Class.map(lambda s: s in strings['list.fcc'])]='fcc'
Target_Class[Target_Class.map(lambda s: s in strings['list.bcc'])]='bcc'

Target_Class[BS.index.str.contains('SQS-fcc')] = 'fcc'
Target_Class[BS.index.str.contains('SQS-L12')] = 'fcc'

Target_Class[    Target_Class.str.contains('Al42W') |    Target_Class.str.contains('Al9Co2') |    Target_Class.str.contains('Al5W') |    Target_Class.str.contains('Al12W') |    Target_Class.str.contains('Al4W') |    Target_Class.str.contains('Al5Co2')
] = 'others'

fig = plt.figure()
plt.hist(
    Target_Class,
    bins=80,
    density = True,
    width=0.5,
    align='left', 
    color = 'purple',
)
xticks = plt.xticks(rotation=90)
yticks = plt.yticks([])
plt.ylabel('Density Count')
plt.savefig('class_counts.pdf')
plt.close(fig)

# # Build the ground state energies

# In[31]:


elements = pd.concat([BS['atom_A'],BS['atom_B'],BS['atom_C']], axis = 0).unique()


BS[(BS['atom_A']==elements[0]) & (BS['nelem']==1)]
BS[(BS['atom_A']==elements[1]) & (BS['nelem']==1)]
BS[(BS['atom_A']==elements[2]) & (BS['nelem']==1)]

