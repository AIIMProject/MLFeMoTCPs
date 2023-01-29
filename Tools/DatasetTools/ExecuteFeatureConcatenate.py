from pandas import Index
from Commoms import *
sys.path.insert(0, os.path.dirname(( os.path.dirname(os.path.dirname(__file__)) )))

import copy
from DatasetOperator import Dataset, DatasetTester

import warnings
warnings.simplefilter('ignore')


target_case = 'EF_nmhcp'

suffix = 'CV_params'

DS = Dataset('Fe-Mo', target_name=target_case)

ModelName = 'Kernel Ridge'


from MLConveniences import *

resultslocation = DS.resultslocation

Features = DS.Features  # {name: pd.read_pickle(filename) for name, filename in DescriptorFileList.items()}


Features['ACE'] = Features['ACE_CNAV'].filter(regex='_0$|Mag|Structure')
Features['Projections OS BOP'] = Features['Projections OS BOP'].filter(regex = '^(?!^moments)')
Features['Canonical BOP'] = Features['Canonical BOP'].filter(regex = '^(?!^moments)')
Features['Projections BOP'] = Features['Projections BOP'].filter(regex = '^(?!^moments)')
Features['Projections sOS BOP'] = Features['Projections sOS BOP'].filter(regex = '^(?!^moments)')


def clean_CNAVS(name: str, features: pd.core.frame.DataFrame):
    if 'BOP' in name:
        return features.filter(regex='^(?!.*_CN)')
    else:
        return features


def clean_zeros(name: str, features: pd.core.frame.DataFrame):
    if 'BOP' in name:
        return features.filter(regex='^(?!.*_0$)')
    else:
        return features

def notyetclean(name: str):
    return ('BOP' in name) and ('CNAV' not in name) and ('Zeros' not in name)

Features.update({name+' no CNAV': clean_CNAVS(name, features) for name, features in Features.items() if notyetclean(name)})

samplesplit = DS.get_samplesplit()

# In[20]:


Models = {
    'Kernel Ridge': Pipeline([('scaler', StandardScaler()), ('regressor', KernelRidge())]),
    'MLP': Pipeline([('scaler', StandardScaler()), ('regressor', MLPRegressor())]),
    'Random Forest': Pipeline([('regressor', RandomForestRegressor())]),
    'Gaussian Process': Pipeline([('regressor', GaussianProcessRegressor())])
}


# In[21]:


from importlib.machinery import SourceFileLoader
MO = SourceFileLoader('MO', 'Tools/DatasetTools/ModelSelection.py').load_module().ModelOptions(DS.dataset)


from sklearn.gaussian_process.kernels import RBF, WhiteKernel, RationalQuadratic, ConstantKernel, ExpSineSquared, DotProduct, Product


MO.load_model_options(ModelName)

samplefolds = list(DS.get_folds())

fittedmodelslocation = os.path.join(DS.resultslocation, f'{ModelName}_{target_case}__FittedCVSearch{suffix}.pkl')

FittedModels = {}

FeatureConcatenate = SourceFileLoader('FeatureConcatenate', 'Tools/DatasetTools/FeatureConcatenate.py').load_module().NewFeatureConcatenate
# from BopFoxFeaturizer.FeatureConcatenate import FeatureConcatenate


# In[59]:


feature_concat_resul_loc = os.path.join(DS.dataset, 'results', f'concatenation_results_{target_case}{suffix}.pkl')  

if os.path.exists(feature_concat_resul_loc):
    with open(feature_concat_resul_loc, 'rb') as pkl:
        FCresults = pickle.load(pkl)
else:
    FCresults = {}

#iwanttoplot = ['atomic', 'dataset', 'Canonical BOP', 'dataset + Canonical BOP', 'Projections BOP', 'dataset + Projections BOP', 'Projections sOS BOP', 'dataset + Projections sOS BOP' ]

iwanttoplot = ['Projections OS BOP', '0.7 Projections OS BOP', 'Projections sOS BOP', 'Projections BOP',  'Canonical BOP', 'ACE','SOAP_specific', 'dataset', 'atomic']#, 'ACE_CNAV']

TestCV = GridSearchCV(Models[ModelName], MO.modeloptions[ModelName], cv = 5, return_train_score=True, scoring='neg_root_mean_squared_error')

FittedGS = {}

import  numpy as np
# DS.Features.keys(): #['Canonical BOP']:
for featurename in iwanttoplot:
    print(featurename)
    if 'random' not in Features[featurename].columns:
        Features[featurename]['random'] = np.random.rand(Features[featurename].shape[0])
    corrs = pd.concat([Features[featurename],DS.target], axis = 1).corr()[target_case].abs()
    reasonable_features = corrs[corrs>0.1].index.difference([target_case])#.append(Index(['Mag']))
    if 'Mag' not in reasonable_features:
        raise(  ValueError('Mag eliminated too soon ') )
    combi  = (ModelName, featurename)
    FittedGS[combi] = copy.deepcopy(TestCV)
    if combi in FCresults.keys():
        #    if FCresults[combi].shape[0] >= len(reasonable_features):
        continue
    FC = FeatureConcatenate(DS, FittedGS[combi], model_params_grid = MO.modeloptions[ModelName] ) #fmodel.best_params_,)
    FCresults[combi] = FC.get_best_features_list(combi[1], num_features = DS.Features[combi[1]].shape[1], max_workers=3, search_only = reasonable_features)
    with open(feature_concat_resul_loc, 'wb') as pkl:
        pickle.dump(FCresults, pkl)


from Tools.DatasetTools.Tools import get_str_formatted

pallete = sns.color_palette(n_colors=len(iwanttoplot))

colors = {name: c for name, c in zip(iwanttoplot, pallete)}


from matplotlib.ticker import FormatStrFormatter
fig, axes = plt.subplots(figsize=(15,10))
for combi, result in FCresults.items():
    if combi[0] != ModelName:
        continue
    if combi[1] not in iwanttoplot:
        continue
#    if ' OS ' in combi[1]:
#        continue
    nfeats = result.shape[0]
    x=np.linspace(1,nfeats, nfeats)
    legend = combi[1].replace('dataset', 'polyhedra')
    legend = legend.replace('atomic', 'Matminer')
    y = result['test']*1000
    axes.plot(x, y ,'o',c=colors[combi[1]], label=legend)
    text = axes.text(x[-1], y[-2], legend, horizontalalignment='left')#, backgroundcolor='white', alpha=0.5)
    text.set_bbox(dict(facecolor=colors[combi[1]], alpha=0.5,edgecolor='white'))
axes.set_xscale('log')
axes.set_ylabel(r'test RMSE@$\Delta E_f$ (meV/atom)')
axes.set_xlabel('Number of Features')
axes.tick_params(axis='y', which='minor')
axes.set_yscale('log')
axes.yaxis.set_minor_formatter(FormatStrFormatter("%.0f"))
axes.yaxis.set_major_formatter(FormatStrFormatter("%.0f"))
#plt.legend(bbox_to_anchor=(0.6,0.5))
axes.set_xlim([0.5, 1e4])
fig.suptitle(ModelName)
fig.tight_layout()
nameforfile = ModelName.replace(' ','')
fig.savefig(f'{DS.dataset}/graphs/{DS.dataset}_{nameforfile}_LearningCurves_{target_case}{sufix}.pdf')


# In[67]:


selected_pos = FCresults[(ModelName, 'Projections OS BOP')].index[0]
y_pos = FCresults[(ModelName, 'Projections OS BOP')]['test']*1000
x = np.linspace(1, len(y_pos), len(y_pos))
axes.annotate(get_str_formatted(selected_pos), (x[0], y_pos[0]-5), xytext=(x[0]-0.1, y_pos[0]-40), arrowprops={'facecolor':'black'})
selected_next = FCresults[(ModelName, 'Projections OS BOP')].index[1]
axes.annotate(get_str_formatted(selected_next), (x[1], y_pos[1]), xytext=(x[1]*2, y_pos[1]+20), arrowprops={'facecolor':'black'})
ymag = y_pos[y_pos.index=='Mag']['Mag']
xmag = x[y_pos.index=='Mag']
axes.annotate('Mag', (xmag-0.1, ymag-1), xytext=(xmag/5, ymag-40), arrowprops={'facecolor':'black'})
fig.tight_layout()
nameforfile = ModelName.replace(' ','')
fig.savefig(f'{DS.dataset}/graphs/{DS.dataset}_{nameforfile}_LearningCurves_annotated_{target_case}_CV.pdf')


# ## selections

# In[68]:


argmin = FCresults[(ModelName, 'Projections OS BOP')]['test'] .argmin()


# # Final learn after feature selection 

# In[69]:


OptimalFittedScores = {}
OptimalFittedModels = {}


# In[70]:


non_fitted_model[(ModelName, 'Projections OS BOP')]


# In[75]:


for combi in FCresults.keys():
    if ModelName not in combi:
        continue
    if combi not in FittedModels.keys():
        continue
    print (combi)
    OptimalFittedModels[combi]  = GridSearchCV(
        Models[ModelName],
        param_grid=MO.modeloptions[ModelName], 
        cv = test_folds_list, 
        scoring = 'neg_root_mean_squared_error', n_jobs=3, return_train_score=True)
        #copy.deepcopy(non_fitted_model[combi])
    #params = FittedModels[combi].best_params_
    #OptimalFittedModels[combi].set_params(**params) #= GridSearchCV(amodel, MO.modeloptions[ModelName], scoring = 'neg_root_mean_squared_error',return_train_score=True)
    atmin = FCresults[combi]['test'].argmin()
    selected = FCresults[combi].index[:atmin]
    X = DS.Features[combi[1]][selected]
    if 'random' in selected:
        print(f'random selected in {combi}')
    #if 'random' in selected:
    #    selected = selected.drop('random')
    OptimalFittedModels[combi].fit(X.loc[DS.samplesplit['train']], DS.target[DS.samplesplit['train']])
    OptimalFittedScores[combi] = score_fitted_model(OptimalFittedModels[combi], X.loc[DS.samplesplit['train']], X.loc[DS.samplesplit['test']], DS.target[DS.samplesplit['train']], DS.target[DS.samplesplit['test']] )


# In[78]:


type(OptimalFittedModels[('Kernel Ridge', 'SOAP_specific')])


# In[ ]:





# In[ ]:


OptimalFittedScores = pd.DataFrame.from_dict(OptimalFittedScores, orient='index')#.sort_values(by='test')
OptimalFittedScores.sort_values(by='test', ascending=False, inplace=True)


# In[ ]:


OptimalFittedFile = f'{DS.dataset}/results/{DS.dataset}_{ModelName}_OptimalModels_{target_case}.pkl'
with open(OptimalFittedFile, 'wb') as pkl:
    pickle.dump(OptimalFittedModels, pkl)
OptimalFittedScoresFile = f'{DS.dataset}/results/{DS.dataset}_{ModelName}_OptimalScores_{target_case}.pkl'
with open(OptimalFittedScoresFile, 'wb') as pkl:
    pickle.dump(OptimalFittedScores, pkl)


# In[83]:


plot_best_scores = SourceFileLoader('plot_best_scores', 'Tools/DatasetTools/MLConveniences.py').load_module().plot_best_scores
ax = plot_best_scores(OptimalFittedScores, ModelName=ModelName)
ax.tick_params(axis='y', which = 'minor')
ax.yaxis.set_minor_formatter(FormatStrFormatter("%.0f"))
ax.yaxis.set_major_formatter(FormatStrFormatter("%.0f"))
ax.legend(title='')


# # Prediction line 

# In[84]:


Prediction = {}
for combi, model in OptimalFittedModels.items():
    atmin = FCresults[combi]['test'].argmin()
    selected = FCresults[combi].index[:atmin]
    X = DS.Features[combi[1]][selected]
    Prediction[combi] = model.predict(X)


# In[85]:


#iwanttoplot = {'atomic':'Matminer',
iwanttoplot = {'Canonical BOP': 'Canonical BOP', 'Projections OS BOP':'Projections OS BOP'}
#iwanttoplot = {'dataset': 'dataset', 'Projections OS BOP':'Projections OS BOP'}


# In[86]:


x_y = np.linspace(DS.target.min()-0.1, DS.target.max()+0.1, 2)
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(x_y, x_y, '--k', lw=2)
for name, legend in iwanttoplot.items():
    print(name, legend)
    legend = legend.replace('dataset', 'polyhedra')
    combi = (ModelName, name)
    if combi not in Prediction.keys():
        print(f'{combi} has not been processed yet')
        continue
    ax.plot(Prediction[combi], DS.target, 'o', markersize=8, markeredgecolor='k', color=colors[name], label=legend)
#    sns.scatterplot(Prediction[name], DS.target,ax=ax) #, markersize=8, markeredgecolor='k',  color = color, label=legend)
ax.set_xlabel(r'predicted $\Delta E_f$ (eV/atom)')
ax.set_ylabel(r'True $\Delta E_f$ (eV/atom)')
ax.legend()
fig.savefig(os.path.join(DS.dataset,'graphs', f'{DS.dataset}_{ModelName}_predictionline_{target_case}.pdf'))


# # Feature Importances 

# In[87]:


importances = {}
for combi, estimator in OptimalFittedModels.items():
    print(combi[1])
    atmin = FCresults[combi]['test'].argmin()
    selected = FCresults[combi].index[:atmin]
    if 'random' in selected:
        print(f'random selected in {combi}')
    X = DS.Features[combi[1]][selected]
    allimportances = get_importances(estimator , X,  DS.target)
    importances[combi] =allimportances #  [allimportances['importances_mean']>=allimportances['importances_mean']['random']]


# In[88]:


for (modelname, name),timportances in importances.items():
    timportances.sort_values(by='importances_mean', inplace=True, ascending=False)


# In[89]:


#for (model, name), timp in importances.items():
for (model, name), timp in importances.items(): #['Projections OS BOP', 'dataset + Projections OS BOP']:
#    pimp = timp[timp.index != 'Mag']
    fig, ax = plt.subplots(figsize=(18, 15))
    x = timp['importances_mean'][:20]
    sns.barplot(y=timp.index[:20], x=x , ax=ax, color='Purple')
    ylabels = [get_str_formatted(fname) for fname in x.index]
    ax.set_xlabel('permutation importance')
    ax.set_yticklabels(ylabels, fontsize=28)
    fig.suptitle(name.replace('dataset', 'polyhedra'))
    fig.tight_layout()
    nameforfile  = name.replace(' ','')
    fig.savefig(f'{DS.dataset}/graphs/{DS.dataset}_permutation_importance_{nameforfile}.pdf')


# # Errors by phase by model

# In[90]:


train_errors = {}
rmse = {}


# In[91]:


OptimalFittedScores.sort_values(by='test', inplace=True)


# In[92]:


for combi, errors in OptimalFittedScores.iterrows():
    if 'sOS' in combi[1]:
        continue
    print(combi)
    model = OptimalFittedModels[combi]
    nselected = FCresults[combi]['test'].argmin()
    selected = FCresults[combi].index[:nselected]
    predictions = model.predict(DS.Features[combi[1]][selected].loc[DS.samplesplit['test']])
    train_errors[combi] = np.abs(predictions - DS.target[DS.samplesplit['test']])*1000
    rmse[combi] = {}
    for phase in DS.BS.Phase.unique():
        thiserrors = train_errors[combi][DS.BS.Phase == phase]**2
        rmse[combi][phase] =  np.sqrt(thiserrors.sum()/len(thiserrors))
    rmse[combi]['total'] = errors['test']*1000


# In[93]:


fig, axes = plt.subplots(len(OptimalFittedScores)-1, 1, sharex=True, figsize=(10, 5*len(train_errors)))
#for (combi, errors), ax in zip(train_errors.items(), axes):
for (combi, thisrmse), ax in zip(OptimalFittedScores.iterrows(), axes):
    if 'sOS' in combi [1]:
        continue
    sns.violinplot(
        x = np.log10(np.abs(train_errors[combi])),
        y = DS.StructureNames,
        hue=DS.Features['dataset']['Mag'], 
        ax=ax, split=True)
    ax.axvline(np.log10(thisrmse['test']*1000),color='k', label='rmse')
    ax.get_legend().remove()
    ax.set_xlabel('')
    ax.set_ylabel(combi[1].replace('_specific', ''))
fig.tight_layout()
label = axes[-1].set_xlabel(r'$log_{10}(| \Delta E_{f}^{predict} - \Delta E_{f}^{DFT}|)$ (meV)')
handles, labels = axes[0].get_legend_handles_labels()
axes[0].legend(handles , ['NM','FM', 'test RMSE'], bbox_to_anchor = (0.9, 1.2), ncol = 3)
fig.savefig(os.path.join(DS.dataset,'graphs',f'{DS.dataset}_violinerrors_{target_case}_testing.eps'))


# In[94]:


rmsedf = pd.DataFrame.from_dict(rmse, orient = 'index')


# In[95]:


rmsedf.sort_values(by=('Kernel Ridge', 'Projections OS BOP'), axis = 1, inplace=True)


# In[96]:


rmsedf.sort_values(by='total', inplace=True)


# In[98]:


sns.heatmap(rmsedf.loc['Kernel Ridge'])


# # Errors by Mag 

# In[100]:


for combi,thiserrors in train_errors.items():
    fm_errors = thiserrors[thiserrors.index.str.contains('FM$',regex=True)]
    nm_errors = thiserrors[thiserrors.index.str.contains('NM$',regex=True)]
    break


# In[101]:


ax = nm_errors.hist()
fm_errors.hist(ax=ax)
ax.set_xlabel(r'$\Delta E_{FM} - \Delta E_{NM}$')


# # convex hulls (binaries only)

# In[108]:


from Tools.DatasetTools.Tools import Plotting
P = Plotting()


# In[109]:


from importlib.machinery import SourceFileLoader
P = SourceFileLoader('Plotting', 'Tools/DatasetTools/Tools.py').load_module().Plotting()


# In[110]:


components = DS.components


# In[111]:


predictedBS = copy.copy(DS.BS.loc[DS.target.index])


# In[118]:


predictedBS['EF'] = Prediction[combi]


# In[122]:


verts = {}
chulls = {}
phasepoints = {}

PhasesBS = {mag: {phase: predictedBS[(predictedBS.Phase == phase) & predictedBS.index.str.contains(mag)] for phase in predictedBS.Phase.unique()} for mag in ['FM', 'NM', '']}


# In[123]:


remove = []
for mag, phasesbs in PhasesBS.items():
    for phase, bs in phasesbs.items():
        if len(bs) < 3:
            remove.append((mag, phase))


# In[125]:


[PhasesBS[remove_mag].pop(remove_phase) for (remove_mag, remove_phase) in remove]


# In[128]:


for mag, PhaseBS in  PhasesBS.items():
    print(mag, [(phase, len(BS))  for phase, BS in PhaseBS.items()] )
    points = P.get_x_ef_points(PhaseBS, components, property=target_case)
    chulls = P.get_convex_hulls(PhaseBS, components, return_points = False, getproperty = target_case)
    pallette = sns.color_palette("Paired", n_colors=len(PhaseBS)+1)
    #pallette.pop(-2)
    colors = {phase: color for phase, color in zip(PhaseBS.keys(), pallette)}
    fig, ax = plt.subplots()
    labels=[]
    handles = []
    for phase, chull in chulls.items():
        for visible_facet in chull.simplices[chull.good]:
            ax.plot(points[phase][:,0] , points[phase][:,1], 'o', color = colors[phase])
            l = ax.plot(chull.points[visible_facet,0], chull.points[visible_facet,1], color=colors[phase])
        handles.append(l[0])
        labels.append(phase)
    leg = ax.legend(handles, labels, bbox_to_anchor=(1.01,1), title=mag)
    setlw = [ha.set_linewidth(5) for ha in leg.get_lines() ]
    ax.set_ylabel(r'$\Delta E _f$ (eV/atom)')
    ax.set_xlabel(rf'$x_{{{components[0]}}}$')
    fig.tight_layout()
    fig.savefig(os.path.join(DS.dataset, 'graphs',f'{DS.dataset}_ConvxHulls_{target_case}_{mag}.eps' ))

