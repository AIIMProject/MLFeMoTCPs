from Tools.DatasetTools.Commoms import * 
from sklearn.model_selection import train_test_split
from Tools.DatasetTools.MLConveniences import *
from itertools import product
from tqdm.auto import tqdm

class  Dataset():

    def  __init__(self, dataset:str ='Fe-Mo'):
        """initiate the dataset
        arguments
        =========
        dataset: str 'Fe-Mo'

        """

        self.dataset = dataset
        self.system = dataset.replace('-','')
        self.components = dataset.split('-')

        self.BS = load_fully_curated_briefsummary(dataset)

        self.resultslocation = load_results_location(dataset)

        self.Features = load_features(dataset)

        self.allindex = pd.concat(list(self.Features.values())+[self.BS], axis=1).dropna().index

        self.Features = {group: feature.loc[self.allindex] for group, feature in self.Features.items()}
        self.target = self.BS['EF']

        split_random_state = 42

        indextrain, indextest = train_test_split(self.allindex, shuffle=True, random_state = split_random_state)

        self.samplesplit = {'test': indextest, 'train': indextrain}
#        samplelocation = os.path.join(dataset, 'samplesplit.pkl')

    def make_recursivity_anbn(self, 
            model: RegressorMixin  = Pipeline([(  'scaler', MinMaxScaler()), ('regressor', MLPRegressor() ) ] )
           ):

        test_scores : dict[str,  pd.core.frame.DataFrame ] = {}

        progress = tqdm(self.Features.items())

        indextrain = self.samplesplit['train']
        indextest = self.samplesplit['test']

        for group, features in progress:

            if 'BOP' not in group:
                continue

            recursion_coefficients_a = features.filter( regex='an_[0-9]+_0' )
            recursion_coefficients_b = features.filter( regex='bn_[1-9]+_0' )

            this_scores : dict[int, list[dict[str, float]]] = {} 

            for i in range(recursion_coefficients_a.shape[1]):
                Xa = recursion_coefficients_a.iloc[:, :i+1]
                Xb = recursion_coefficients_b.iloc[:, :i+1]
                X = pd.concat([Xa, Xb], axis = 1)
                model.fit(X.loc[indextrain], self.target[indextrain])
                this_scores[i] = score_fitted_model(model, X.loc[indextrain], X.loc[indextest], self.target.loc[indextrain], self.target.loc[indextest])

            test_scores[group] = pd.DataFrame.from_dict(this_scores,  orient='index')

        self.test_scores = test_scores

    def cvsearch(self, model: RegressorMixin, params: dict[str, list]):

        cvscores = {}
        cv_test_scores = {}
        cvaler = GridSearchCV(model,params,scoring = 'neg_root_mean_square', cv = 5,verbose=1, return_train_score=True)
        for name, features in self.Features.items():
            cvaler.fit(features.loc[samplesplit['train']], self.target[samplesplit[test]])
            cvscores[name] = pd.DataFrame( cvaler.cv_results_, orient = 'index' )






# test fitting only one feature

if __name__ == '__main__':
    DS = Dataset()

#
