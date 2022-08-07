from Tools.DatasetTools.Commoms import * 
from sklearn.model_selection import train_test_split
from Tools.DatasetTools.MLConveniences import *
from itertools import product
from tqdm.auto import tqdm

class  Dataset():

    def  __init__(self, dataset:str ='Fe-Mo', split_random_state=42):
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
        self.samplesplit = self.load_indexsplit(split_random_state)
        self.split_random_state = split_random_state
#        samplelocation = os.path.join(dataset, 'samplesplit.pkl')


    def  read_samplesplit(location):
        with open(location, 'rb') as pkl:
            saved_split_random_state = pickle.load(pkl)
            savedsamplesplit = pickle.load(pkl)
        return saved_split_random_state, savedsamplesplit

    def  load_indexsplit(self, split_random_state):
        indexsplitloc = os.path.join(self.dataset, 'samplsplit.pkl')
        indextrain, indextest = train_test_split(self.allindex, shuffle=True, random_state = split_random_state)
        samplesplit = {'test': indextest, 'train': indextrain}
        with open(indexsplitloc, 'wb') as pkl:
            pickle.dump(split_random_state, pkl)
            pickle.dump(samplesplit, pkl)
        return samplesplit
        
    def train_test_split(self, name:str)-> tuple[pd.core.frame.DataFrame,pd.core.frame.DataFrame,pd.core.series.Series,pd.core.series.Series]:
        xtrain = self.Features[name].loc[self.samplesplit['train']]
        xtest = self.Features[name].loc[self.samplesplit['test']]
        if not hasattr(self, 'ytrain'):
            self.ytrain = self.target.loc[self.samplesplit['train']]
        if not hasattr(self, 'ytest'):
            self.ytest = self.target.loc[self.samplesplit['test']]
        return xtrain, xtest, self.ytrain, self.ytest


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



    def cvsearch(self, model: RegressorMixin, params: dict[str, list], vsearch_random_state=42):

        cvscores = {}
        cv_test_scores = {}
        cv_best_params = {}

        cvaler = GridSearchCV(model,params,scoring = 'neg_mean_squared_error', cv = 5,verbose=1, return_train_score=True, n_jobs=4)
        for name, features in self.Features.items():
            xtrain, xtest, ytrain, ytest = self.train_test_split(name)
            cvaler.fit(xtrain, ytrain)
            cvscores[name] = pd.DataFrame.from_dict( cvaler.cv_results_, orient = 'index' )
            cv_test_scores[name] =score_fitted_model(cvaler, xtrain, xtest, ytrain, ytest)
            cv_best_params[name] =cvaler.best_params_
        self.cv_test_scores = pd.DataFrame.from_dict(cv_test_scores, orient='index')
        self.cv_test_scores.sort_values('test', inplace=True, ascending=False)
        self.best_params = cv_best_params






# test fitting only one feature

if __name__ == '__main__':
    DS = Dataset()

#
