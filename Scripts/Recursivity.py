from Tools.DatasetTools.Commoms import * 
from sklearn.model_selection import train_test_split
from Tools.DatasetTools.MLConveniences import *
from itertools import product

def  RecursivityTest():

    def  init():
dataset = 'Fe-Mo' 
system = dataset.replace('-','')
components = dataset.split('-')

BS = load_fully_curated_briefsummary(dataset)

resultslocation = load_results_location(dataset)

Features = load_features(dataset)

allindex = pd.concat(list(Features.values())+[BS], axis=1).dropna().index

Features = {group: feature.loc[allindex] for group, feature in Features.items()}
target = BS['EF']

split_random_state = 42

indextrain, indextest = train_test_split(allindex, shuffle=True, random_state = split_random_state)

samplesplit = {'test': indextest, 'train': indextrain}
samplelocation = os.path.join(dataset, 'samplesplit.pkl')

# test fitting only one feature
test_scores : dict[str,  pd.core.frame.DataFrame ] = {}

progress = tqdm(Features.items())


for group, features in progress:

    if 'BOP' not in group:
        continue

    recursion_coefficients_a = features.filter( regex='an_[0-9]+_0' )
    recursion_coefficients_b = features.filter( regex='bn_[1-9]+_0' )

    this_scores : dict[int, list[dict[str, float]]] = {} 

    for i in range(recursion_coefficients_a.shape[1]):
        model = Pipeline([(  'scaler', MinMaxScaler()), ('regressor', MLPRegressor() ) ] )
       # model = Pipeline([('regressor', RandomForestRegressor(max_depth=30)) ] )
        Xa = recursion_coefficients_a.iloc[:, :i+1]
        Xb = recursion_coefficients_b.iloc[:, :i+1]
        X = pd.concat([Xa, Xb], axis = 1)
        model.fit(X.loc[indextrain], BS['EF'][indextrain])
        this_scores[i] = score_fitted_model(model, X.loc[indextrain], X.loc[indextest], target.loc[indextrain], target.loc[indextest])

    test_scores[group] = pd.DataFrame.from_dict(this_scores,  orient='index')
