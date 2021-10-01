from SourceDevelopementVersion import Featurizer, FeatureConcatenate


# In[2]:


from BopFoxFeaturizer.FeatureConcatenate import FeatureConcatenate


# In[49]:


DensitiFeatures


# In[50]:


AtomicFeaturesMagpie


# In[62]:


CompositionFeatures


# In[66]:


AllFeatures = pd.concat([AtomicFeaturesMagpie, DensitiFeatures, CompositionFeatures], axis = 1)


# In[67]:


AllFeatures


# In[38]:


from SourceDevelopementVersion import Featurizer, StructSummaryParser
BS = pd.read_pickle('parsedbs.pkl')
Features = Featurizer(BS)
groundstates = Features.get_ground_states_energies()
BS['EF'] = Features.get_formation_energy(groundstates)


# In[33]:


bestfeats = {}
bestscores = {}
FC = {}


# In[40]:


from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split


# In[68]:


X_train, Y_train, X_test, Y_test = train_test_split(AllFeatures, BS['EF'])


# In[70]:


FC['RandomForest_atomic'] = FeatureConcatenate(
    pd.concat([X_train, Y_train], axis=1), #DATA, 
    RandomForestRegressor(),
    model_params=param_grid,
    feature_list=AllFeatures.columns,
    data_target='EF',
#    sample_weights = w_train, #Classes['Weights']
)

Bestfeats['RandomForest_atomic'], Bestscores['RandomForest_atomic'] = FC['RandomForest_atomic'].build_features_list(
#    best_feature_proposal=['NSC_bn_1'],
    pass_force_refit=True,
    report_prefix='RandomForest_atomic_'+CASE,
)


# In[ ]:




