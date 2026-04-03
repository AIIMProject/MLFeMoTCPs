import sys
import os
sys.path.insert(0, os.path.dirname(( os.path.dirname(os.path.dirname(__file__)) )))
from Tools.DatasetTools.Commoms import *
os.environ['PATH']+=':'+os.path.join(os.getcwd(),'dependencies/bopfox/src/')
from dependencies.bopfoxfeaturizer.BopFoxFeaturizer.Featurizer import Featurizer, BopfoxFeatures

from dependencies.bopdftprojections.bopdftprojections.projections import Projections, Canonicalmodel
import shutil


from Tools.DatasetTools import GeneralFeaturizer as gf
from sklearn.feature_selection import VarianceThreshold
from tqdm.auto import tqdm



# In[3]:

dataset = 'Fe-Mo' #  'Cr-Co-W'# 'Fe-Mo'
elements = dataset.split('-')
atomsobjectloc = os.path.join(dataset, 'Atomsobjects')
components = dataset.replace('-','')
globalmoments = 16
model_definitions = {
    'canonical': {
        'replace atoms' : {'Fe': 'W', 'Mo': 'W'},
        'moments' : globalmoments
    },
    '0.7projections_0.5os': {
        'model_maker_options' : {
            'element_pairs_kwargs' : {
                'bond_integral_scale': 0.7,
            },
            'atom_blocks_kwargs': {
                'onsite_levels_scale' : 0.5,
                'select_orbitals' : {'Fe': 'd', 'Mo' : 'd'},
            },
        },
        'calculator_options' : {
            'moments' : globalmoments
        }
    },
    '0.7projections_0.5os_0scf': {
        'model_maker_options' : {
            'element_pairs_kwargs' : {
                'bond_integral_scale': 0.7,
            },
            'atom_blocks_kwargs': {
                'onsite_levels_scale' : 0.5,
                'select_orbitals' : {'Fe': 'd', 'Mo' : 'd'},
            },
        },
        'calculator_options':{
            'moments' : globalmoments,
            'scfsteps' : 0,
        }
    },
    '0.7projections_0.5os_10scf_jii8.0': {
        'model_maker_options' : {
            'element_pairs_kwargs' : {
                'bond_integral_scale': 0.7,
            },
            'atom_blocks_kwargs': {
                'onsite_levels_scale' : 0.5,
                'select_orbitals' : {'Fe': 'd', 'Mo' : 'd'},
                'onsite_energy' : {'Fe': 8.0, 'Mo': 8.0}
            },
        },
        'calculator_options':{
            'moments' : globalmoments,
            'scfsteps' : 10,
        }
    },
    '0.7projections_0.5os_100scf_jii8.0': {
        'model_maker_options' : {
            'element_pairs_kwargs' : {
                'bond_integral_scale': 0.7,
            },
            'atom_blocks_kwargs': {
                'onsite_levels_scale' : 0.5,
                'select_orbitals' : {'Fe': 'd', 'Mo' : 'd'},
                'onsite_energy' : {'Fe': 8.0, 'Mo': 8.0}
            },
        },
        'calculator_options':{
            'moments' : globalmoments,
            'scfsteps' : 100,
        }
    },
}
cutoff = 'table'
atoms = ['initial', 'relaxed']
retry = False


# In[5]:

target_case = 'EF_nmhcp' # only for correlation plots


# In[6]:


try:
    AtomsObjects = {'initial' : load_atoms_objects(dataset,case='POSCAR.initial', scaling='rescaled'),
                    'relaxed' : load_atoms_objects(dataset, case='POSCAR.relaxed-all', scaling='noscaled')}
except Exception as _e:
    import warnings
    warnings.warn(f"GetBopFeatures: could not load AtomsObjects ({_e}). Set AtomsObjects={{}}")
    AtomsObjects = {}
BS = load_fully_curated_briefsummary(dataset)

# In[8]:



# In[9]:

P = Projections()
C = Canonicalmodel()
P.readbxmodels()
P.get_bond_chunks()
P.get_autobonds()
P.get_all_onsite_levels()
P.get_restructured_projections()


# In[10]:
def create_modelfile(acompound, target_model_filename, modelname='projections', element_pairs_kwargs={}, atom_blocks_kwargs={} ):
    print(acompound)
    if modelname is not 'canonical':
        model_filename = P.save_abond_bx(acompound, return_filename=True,
                                         modelname=modelname, 
                                         element_pairs_kwargs=element_pairs_kwargs,
                                         atom_blocks_kwargs=atom_blocks_kwargs)
        print(model_filename)
    else:
        model_filename = C.base_canonical #f'models/W_canonical.bx'
    shutil.copy(model_filename, target_model_filename)


# In[11]:


def replace_symbols(theatoms, replacements=None):
    new_symbols = theatoms.get_chemical_symbols()
    if replacements is not None:
        for original, replacement in replacements.items():
            new_symbols = [s.replace(original, replacement) for s in new_symbols]
    new_atoms = theatoms.copy()
    new_atoms.set_chemical_symbols(new_symbols)
    return new_atoms

# In[13]:


results = {}
resultspickle = {}

# In[14]:

for (model, definition), (case, atoms_df) in product(model_definitions.items(), AtomsObjects.items()):
    if 'moments' in definition.keys():
        thismoments = definition['moments']
    else:
        thismoments = 16
    if (model, thismoments, case) in results.keys():
        continue
    create_model_options = {}
    if 'model_maker_options' in definition.keys():
        create_model_options.update(definition['model_maker_options'])
    use_elements = copy.copy(elements)
    if 'replace atoms' in definition.keys():
        for realelement, targetelement in definition['replace atoms'].items():
            use_elements = set([s.replace(realelement, targetelement) for s in use_elements])
    components = ''.join(use_elements)
    modelsfile = os.path.join('models', f'{dataset}-{components}_{model}.bx')
    create_modelfile(use_elements,modelsfile, modelname=model, **create_model_options,   )
    if 'replace atoms' in definition.keys():
        ApplyOnAtoms = atoms_df['atoms'].apply(replace_symbols, replacements = definition['replace atoms'])
    else:
        ApplyOnAtoms = atoms_df.atoms
    print('atoms: ', case, 'model: ', model, '  cutoff: ', cutoff, ' moments:', thismoments)
    resultspickle[(model, thismoments, case)] = os.path.join(dataset, 'Descriptors', f'parallel_{dataset}_{case}_{model}_{cutoff}_WUBIND_{thismoments}.pkl')
    log_files_loc = os.path.join(dataset, 'results', model)
    if not os.path.exists(log_files_loc):
        os.makedirs(log_files_loc)
    if not os.path.exists(resultspickle[(model, thismoments, case)]):
        cwd = os.getcwd()
        BOPC = BopfoxFeatures(
            ApplyOnAtoms,modelsfile, modelname=model,
            cutoffby=cutoff, 
            binary = os.path.join(cwd, 'dependencies', 'bopfox','src', 'bopfox'),
            savelog=True,
            printsc=True,
            **definition['calculator_options']
            )
        BOPC.featurize_dataframe(input_pickle=resultspickle, output_pickle=resultspickle, max_workers=12)
        logfiles = glob.glob('bopfoxASE*gz')
        if len(logfiles) > 0:
            for file in logfiles:
                os.rename(file, os.path.join(log_files_loc, file))
        results[(model, thismoments, case)] = BOPC.RESULTS #pd.read_pickle(resultspickle[model]) 
        results[(model, thismoments, case)].to_pickle(resultspickle[(model, thismoments, case)])
    else:
        results[(model, thismoments, case)] = pd.read_pickle(resultspickle[(model, thismoments, case)])


#In[]
np.set_printoptions(precision=2,linewidth=125)


removenans = [result.dropna(inplace=True) for (model, moments, case), result in results.items()]


examplemodel = ('0.7projections_0.5os', 16, 'initial')


# In[34]:


descriptorlocation = os.path.join(dataset, 'Descriptors' )
CNListLocation = os.path.join(descriptorlocation,'CNList.pkl')
CNList = pd.read_pickle(CNListLocation)



resultscnav = {}
specialcolumns =['U_bind','U_bond_atom', 'modelsfile', 'logfile']#, 'U_bond_atom_list'] 
remake = False
progress = tqdm(results.items())
for (model, moments, case), model_result in progress: # tqdm(results.items()):
    averaged_bop_file = os.path.join(descriptorlocation,'CNAV_'+os.path.basename(resultspickle[(model, moments, case)].replace('.pkl','.csv')))
    if os.path.exists(averaged_bop_file) and not remake:
        print('read file')
        resultscnav[(model, moments, case)] = pd.read_csv(averaged_bop_file, index_col=0).astype(float)  # for some reason some values are objects
    else:
        progress.set_description(model)
        columnstoexpand = model_result.columns.drop(specialcolumns, errors='ignore')
        df = gf.array_expansions(model_result[columnstoexpand],columnstoexpand)# columnstoexpand)
        ThisCoordination = CNList#[result.index]
        df = gf.featurize_dataframe(df, ThisCoordination, featurizer=gf.cn_average)
        shape_factors = gf.get_shape_factors(df)
        selector = VarianceThreshold()
        selector.fit(df)
        transformed_df = df.loc[:, selector.get_support()].astype(np.single)
        resultscnav[(model, moments, case)] = pd.concat([transformed_df, shape_factors, model_result[['U_bind', 'U_bond_atom']]], axis=1)  # for some reason some values are objects
        resultscnav[(model, moments, case)].to_csv(averaged_bop_file)

