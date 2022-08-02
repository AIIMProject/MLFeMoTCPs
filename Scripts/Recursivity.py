from Tools.DatasetTools.Commoms import * 
from sklearn.model_selection import train_test_split
from Tools.DatasetTools.MLConveniences import *
from itertools import product

dataset = 'Fe-Mo' 
system = dataset.replace('-','')
components = dataset.split('-')

BS = load_fully_curated_briefsummary(dataset)

resultslocation = load_results_location(dataset)

Features : dict[str, pd.core.frame.DataFrame] = load_features(dataset)

def add_dataset(name, features:pd.core.frame.DataFrame):
    if 'BOP' in name and len(features.columns.intersection(Features['dataset'].columns)) < 1:
        X = Features['dataset'].drop(columns=['Mag'])
        return pd.concat([X, features], axis=1).dropna()
    else:
        return features

Features.update({'dataset + '+name: add_dataset(name,features) for name, features in Features.items() if 'BOP' in name})

allindex = pd.concat(list(Features.values())+[BS], axis=1).dropna().index

Features = {group: feature.loc[allindex] for group, feature in Features.items()}

split_random_state = 201507

indextrain, indextest = train_test_split(allindex, shuffle=True)

samplesplit = {'test': indextest, 'train': indextrain}
samplelocation = os.path.join(dataset, 'samplesplit.pkl')


# test fitting only one feature

#model = Pipeline([(  'scaler', StandardScaler()), ('regressor', MLPRegressor() ) ] )
test_scores = [] 

recursion_coefficients_a = Features['Projections BOP'].filter( regex='an_[0-9]+_0' )
recursion_coefficients_b = Features['Projections BOP'].filter( regex='bn_[1-9]+_0' )

for i in range(recursion_coefficients_a.shape[1]):
    model = Pipeline([('regressor', DecisionTreeRegressor()) ] )
    Xa = recursion_coefficients_a.iloc[:, :i+1]
    Xb = recursion_coefficients_b.iloc[:, :i+1]
    X = pd.concat([Xa, Xb], axis = 1)
    model.fit(X.loc[indextrain], BS['EF'][indextrain])
    test_scores.append(score_fitted_model(model, X.loc[indextrain], X.loc[indextest], BS['EF'].loc[indextrain], BS['EF'][indextest]))
