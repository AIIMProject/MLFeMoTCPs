import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__) )))
from Tools.DatasetTools.Commoms import * 
from sklearn.model_selection import train_test_split
from Tools.DatasetTools.MLConveniences import *
from itertools import product
from tqdm.auto import tqdm

def get_compound_composition(compound: pd.core.series.Series) -> dict:
    raise NotImplementedError

class  Dataset():

    def  __init__(
            self,
            dataset:str         ='Fe-Mo', 
            target_name : str   = 'EF_fmbcc',
            selectPhase         = None, 
            selectMag   : str   = None,
            remove_phases_query : str = None,
            load_features_only : list[str] = None
            ):
        """initiate the dataset
        arguments
        =========
        dataset: str 'Fe-Mo'
        target_name: str , one of the columns of BS, pref a DFT value (EF, E, B0, V0)
        selectPhase: weather to chunk BS to phase (select a phase)
        selectMag: wether to chunk a BS to a magnetic case (select magnetic)
        """

        self.dataset = dataset
        self.system = dataset.replace('-','')
        self.components = dataset.split('-')
        self.BS = load_fully_curated_briefsummary(dataset)
        if selectPhase is not None:
            self.BS = self.BS[self.BS['Phase'] == selectPhase]
        if remove_phases_query is not None:
            self.BS = self.BS.query(remove_phases_query)
        if selectMag is not None:
            if ( 'FM' != selectMag ) & ( 'NM' != selectMag ):
                raise ValueError(" selectMag option can only be 'FM' or 'NM' ")
            self.BS = self.BS[self.BS.index.str.contains(selectMag+'$', regex=True)]
        self.resultslocation = load_results_location(dataset)
        Features = self.load_features(dataset)
        if load_features_only is not None:
            Features = { this_feature: Features[this_feature] for this_feature in load_features_only}
        self.Features = Features
        self.allindex = pd.concat(list(self.Features.values())+[self.BS], axis=1).dropna().index
        self.Features = {group: feature.loc[self.allindex] for group, feature in self.Features.items()}
        self.Features.update({
            name: add_dataset_feature(features, self.Features['dataset'][['Mag', 'Structure']]) for name, features in self.Features.items()
            })
        self.target_name = target_name
        self.target = self.BS[target_name].loc[self.allindex]
        self.resultslocation = load_results_location(self.dataset)
        self.StructureNames = self.BS['Phase'].loc[self.allindex]
        rs = np.random.RandomState(np.random.MT19937(np.random.SeedSequence(42)))
        randomfeatures = np.random.rand(self.target.shape[0])
        for feature in self.Features.values():
            feature['random'] = randomfeatures
        
#        samplelocation = os.path.join(dataset, 'samplesplit.pkl')


    def load_features(self, dataset) -> dict[str, pd.core.frame.DataFrame]:
        features_dict = load_features_raw(dataset)
        features_dict.update({name+' no CNAV': clean_CNAVS(name, features) for name, features in features_dict.items() if notyetclean(name)})
        return features_dict

    def __str__(self):
        if not hasattr(self, 'description'):
            self.description  =  f'dataset: {self.dataset}\n'
            self.description  += f'Features: \n{[name for name in self.Features.keys()]}\n'
            self.description += f'number of samples: {len(self.allindex)}\n'
            self.description += f'results location: {self.resultslocation}\n'
        return self.description 

    def  read_samplesplit(location):
        with open(location, 'rb') as pkl:
            saved_split_random_state = pickle.load(pkl)
            savedsamplesplit = pickle.load(pkl)
        return saved_split_random_state, savedsamplesplit

    def  load_indexsplit(self, split_random_state, test_size=0.2):
        indexsplitloc = os.path.join(self.dataset, 'samplsplit.pkl')
        indextrain, indextest = train_test_split(self.allindex, shuffle=True, random_state = split_random_state, stratify=self.StructureNames, test_size=test_size)
        samplesplit = {'test': indextest, 'train': indextrain}
        with open(indexsplitloc, 'wb') as pkl:
            pickle.dump(split_random_state, pkl)
            pickle.dump(samplesplit, pkl)
        return samplesplit
        
    def train_test_split(self, name:str)-> tuple[pd.core.frame.DataFrame,pd.core.frame.DataFrame,pd.core.series.Series,pd.core.series.Series]:
        if not hasattr(self, 'samplesplit'):
            samplesplit = self.get_samplesplit()
        xtrain = self.Features[name].loc[self.samplesplit['train']]
        xtest = self.Features[name].loc[self.samplesplit['test']]
        if not hasattr(self, 'ytrain'):
            self.ytrain = self.target.loc[self.samplesplit['train']]
        if not hasattr(self, 'ytest'):
            self.ytest = self.target.loc[self.samplesplit['test']]
        return xtrain, xtest, self.ytrain, self.ytest


    def get_samplesplit(self, split_random_state: int=42,) -> dict[str, pd.core.indexes.base.Index]:
        self.samplesplit = self.load_indexsplit(split_random_state)
        self.split_random_state = split_random_state
        return self.samplesplit

    def get_folds(self, split_random_state: int=42, nfolds = 5):
        from sklearn.model_selection import StratifiedKFold
        self.nfolds = nfolds
        folder = StratifiedKFold(n_splits=self.nfolds)
        folds = folder.split(self.allindex, self.StructureNames)
        return folds





#        cvscores = {}
#        cv_test_scores = {}
#        cv_best_params = {}
#
#        cvaler = GridSearchCV(model,params,scoring = 'neg_mean_squared_error', cv = 5,verbose=1, return_train_score=True, n_jobs=4)
#        for name, features in self.Features.items():
#            xtrain, xtest, ytrain, ytest = self.train_test_split(name)
#            cvaler.fit(xtrain, ytrain)
#            cvscores[name] = pd.DataFrame.from_dict( cvaler.cv_results_, orient = 'index' )
#            cv_test_scores[name] =score_fitted_model(cvaler, xtrain, xtest, ytrain, ytest)
#            cv_best_params[name] =cvaler.best_params_
#        self.cv_test_scores = pd.DataFrame.from_dict(cv_test_scores, orient='index')
#        self.cv_test_scores.sort_values('test', inplace=True, ascending=False)
#        self.best_params = cv_best_params


from sklearn.model_selection import _search 

class DatasetTester(object):

    def __init__(self):
        self.RandomStates: list[int] = [42, 201203, 72015, 121180]

    @staticmethod
    def learn_vs_split_rs(
            DataSet: Dataset,
            model: RegressorMixin  = Pipeline([('regressor', RandomForestRegressor())] ),
            RandomStates: list[int] = [42, 201203, 72015, 121180]
            ):
        """learn on the input dataset , different train test splits  by changin the random states.
        Parameters:
            DataSet: Dataset , Dataset object including Features and targets
            model : a regressor model , possibly a pipeline (with fit and  predict methods)
        """

        scores  = {}
        progress = tqdm(RandomStates)
        for rs in progress:
            samplesplit = DataSet.get_samplesplit(split_random_state=RandomStates[0])
            for name, feature in DataSet.Features.items():
                xtrain, xtest, ytrain, ytest = DataSet.train_test_split(name)
                model.fit(xtrain, ytrain)
                scores[(rs,  name )]=score_fitted_model(model, xtrain, xtest, ytrain, ytest)

        return pd.DataFrame.from_dict(scores, orient='index').sort_values(by='test', ascending=False)\
                .sort_index(level=0)


    def make_recursivity_anbn_onefeature(self, 
            DS: Dataset, 
            featurename, 
            model: RegressorMixin  = Pipeline([(  'scaler', MinMaxScaler()), ('regressor', MLPRegressor() ) ] ),
            includemag : bool = False, 
            includestruc : bool = False
           ):
        """
        Make recursivity test
        """
        test_scores : dict[str,  pd.core.frame.DataFrame ] = {}

        NOS = [0, 1 ,2 ,3 , 4]

        Features = DS.Features[featurename]
#        progress = tqdm(product(DS.Features.items(), NOS), total=len(NOS)*len(DS.Features))
        progress = tqdm(product([( featurename, Features )], NOS), total=len(NOS))

        indextrain = DS.samplesplit['train']
        indextest = DS.samplesplit['test']

        theregexa = 'an_[0-9]+_0' 
        theregexb = 'bn_[1-9]+_0' 
        if includemag:
            theregexa+='|Mag'
            theregexb+='|Mag'
        if includestruc:
            theregexa+='|Struc'
            theregexb+='|Struc'

        test_scores : dict[int, list[dict[str, float]]] = {} 

        for (group, features), N0 in progress:

            if 'BOP' not in group:
                continue

            recursion_coefficients_a = features.filter( regex=theregexa)
            recursion_coefficients_b = features.filter( regex=theregexb)

            for i in range(N0, recursion_coefficients_a.shape[1]):
                order = 2*(i+1)
                Xa = recursion_coefficients_a.iloc[:,  N0:i+1]
                Xb = recursion_coefficients_b.iloc[:, N0:i+1]
                X = pd.concat([features['Mag'], Xa, Xb], axis = 1)
                model.fit(X.loc[indextrain], DS.target[indextrain])
                test_scores[(N0, order)] = score_fitted_model(
                        model, X.loc[indextrain], X.loc[indextest], DS.target.loc[indextrain], DS.target.loc[indextest]
                        )

#        test_scores = pd.DataFrame.from_dict(test_scores,  orient='index')

        return  test_scores

    def  make_recursivity_anbn(self,DS: Dataset, FittedModels: dict[tuple, _search.GridSearchCV ], kwargs):
        test_scores = {}
        for (model, feature), fittedmodel in FittedModels.items():
            if 'BOP' not in feature:
                continue
            thisscores = self.make_recursivity_anbn_onefeature(DS, feature, FittedModels[(model, feature)].best_estimator_, **kwargs)
            test_scores.update({(model, feature)+key: val for key, val in thisscores.items() })
        return pd.DataFrame.from_dict(test_scores, orient='index')

    @staticmethod
    def  plot_recursivity_curve(recursivity_scores: pd.core.frame.DataFrame, modelname:str):
        from matplotlib.lines import Line2D
        lines = {'Canonical BOP':'red', 'Projections BOP':'blue', 'Projections OS BOP':'green'}
        markers = {0: 'o', 1: 's', 2:'d', 3:'^', 4:'+'}#, 5:'P', 6:'*'}
        symbols = { 'recursion coeficients':r'$\langle a_n \rangle$ , $ \langle b_n \rangle$'}
        fig, axes = plt.subplots()
        for group in lines.keys():
            for n0 in recursivity_scores.index.get_level_values(2).unique():
                if n0>3:
                    continue
                axes.plot(
                        recursivity_scores.loc[(modelname, group, n0)]['test'],'o-',
                        markersize=10 , marker = markers[n0], color=lines[group],markeredgecolor='k'
                        )
        line_labels = {key: Line2D([], [], ls='-', color=value) for key, value in lines.items()}
        handles_labels = {
                key: Line2D([], [], color='k', marker=markers[key]) for key in recursivity_scores.index.get_level_values(2).unique()
                }
        axes.legend(handles = list(line_labels.values())+list(handles_labels.values()), labels=list(line_labels.keys())+list(handles_labels.keys()),
                      loc='right', bbox_to_anchor=[1.35,0.5], title=symbols['recursion coeficients']+'+Mag, KRR')
        axes.set_xlabel('number of features')
        axes.set_ylabel(r'test RMSE @ $\Delta E_f$')
        return fig, axes
        


# test fitting only one feature

if __name__ == '__main__':
    DS = Dataset()

#
