#!/usr/bin/env python3
# coding: utf-8
import numpy as np
import pandas as pd
import os
import sys
import pickle
from sklearn.model_selection import train_test_split
from sklearn.kernel_ridge import KernelRidge
from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer
from sklearn.metrics import r2_score, mean_squared_error 
from sklearn import preprocessing
from sklearn.tree import DecisionTreeRegressor
from sklearn.base import RegressorMixin
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from copy import deepcopy
# debug:
import pdb
# tqdm for progress bars:
from tqdm.auto import tqdm
from tqdm.contrib.concurrent import process_map
# from tqdm import tqdm
import os.path
import re
import warnings
import time
warnings.filterwarnings('ignore')
"""
This module contains some functions to process datasets and generate regressions.

classes
==========
FeatureConcatenate: bundles feature concatenation with a given method.

Methods
===========
stackdata :   transforms vector features to arrays.
feature_average : gets average weighted by given feature

"""

def stackdata(data, addfeatures, prevdata=np.array([]), debug=False):
    """
    This function transforms vector features into arrays. 
    another possiblility might be to use fit_transform().to_array(), but should check same results
    If input features are vector, a dataframe of scalar features is returned.
    example:
    DATA = pd.DataFrame({ 'f1': [ f1_1, f1_2, f1_3 ] , 'f2' : [ f2_1, f2_2, f2_3, f2_4 ] })
    alldata = np.array( [f1_1, f1_2, f1_3, f2_1, f2_2, f2_3, f2_4 ] )

    PARAMS:
    DATA: pandas dataframe with samples and features with its names. vector features will be scalarized.
    addfeatures: list of strings, name of features of self.data to concatenate
    prevdata: possibly previous dataframe with list of already selected features
    debug: wether to stop for debugging

    RETURNS:
    alldata: numpy array of scalar features. all the features were converted to scalar values.
    """
    alldata = prevdata.copy()
    names = [] 
    if debug:
        pdb.set_trace()
    for bf, addfeature in enumerate (addfeatures):
        newdata = np.vstack(data[addfeature].values)
        for i in range(newdata.shape[1]):
            names.append(addfeature+'_{:d}'.format(i))
        if alldata.size:
            alldata = np.hstack((alldata, newdata))
        else:
            alldata = newdata

    return alldata, names

def load_report(reportpath):
    if os.path.exists(reportpath): # and not forcerefit:
        #print('reading existing report ... ')
        try:
            report = pd.read_csv(reportpath)
        except Exception as E:
            report = pd.read_pickle(reportpath)
        #print ("__ Model read from file ___")
    else:
        report = pd.DataFrame([])
    return report

class FeatureConcatenate(object):
    """
    this class is a collection of functions that concatenate different features
    over a dataframe DATA. the model MODEL is used rogression to fit TARGET

    Params:
    =======
    data: dataframe of data, size nsamples*nfeatures. features can ve vector.
    model: regressor used to fit.
    model_params: dic of parameters to pass to GridSearchCV

    Methods
    =======
    stackdata: concatenates a list of features. possibly replace with feature_extraction.
    getbestfeature: tries from a list of features over data to get best regression.
    build feature_list: concatenates up to n features to build best list of features

    attributes
    =============
    data: dataframe of nsamples x nfeatures
    model: regressor used to fit.
    model_params: dic of parameters to pass to GridSearchCV
    target: target allways defaults to formation energy
    """
    def __init__(self,
            data: pd.core.frame.DataFrame,
            model,
            model_params,
            feature_list,
            sample_weights=None,
            data_target='E_f',
            report_path='reports/',
            criterion = 'test_score',
            sort_criteria = 'score_only'
            ):
        """
        Params
        ======
        data: dataframe of features and target
        model: sklearn model with fit and predict methods and cv interface
        feature_list: list of features to try
        sample_weights: series with sample weights
        data_target: column name for target
        report_path: path to pickle the reports
        criterion: score criteria for taking best feature, 'test_score', 'train_score', 'error' or 'best_score'
        sort_criteria: additional sort criteria, i.e. best the lowest order feature among the best by criterion. quite tricky
                        'score_only', 'index_too'
        """
        self.data = data
        self.sample_weights = sample_weights
        # from data, get the target feature
        self.target = data[data_target]  
        self.model = model
        self.model_params  = model_params
        self.feature_list = feature_list
        self.report_path = report_path
        self.criterion = criterion
        self.sort_criteria = sort_criteria
        

    def getbestfeature(self,
        featurelist,  paramgrid,
        previousbest = [],
        forcerefit=False,
        csvreport='report_1.csv',
        model=KernelRidge(kernel='rbf'),
        scorer=make_scorer(mean_squared_error),
        min_max_scaler=preprocessing.MinMaxScaler(),
        debug=False,
    ):
        """
        This Function takes the responsibility to concatenate each feature in featurelist to previousbest
        and report the fitting performance of each fit for [previousbest, feature]. This very same 
        function can be used to make progressive tests

        possible replacing: sklearn.feature_selection.SelectKBest

        PARAMS:
        DATA: dataframe of features. features might be vector values.
        featurelist: list of features to try.
        paramgrid: grid of parameters to pass to GridSearchCV
        TARGET: pandas dataframe with values to fit from featureslist (target values)
        previousbest: list of preselected features (probably ad-hoc)
        forcerefit=False: wether to force the refit even if previous result was found
        cvsreport='report_1.csv': name of cvs file where to report the results
        model=KernelRidge(kernel='rbf'): model to train 
        scorer=make_scorer(r2_score) : score to use at feature selection
        min_max_scaler=preprocessing.MinMaxScaler(): scaler to use in pipeline to preprocess data. 
            todo: change var name to just scaler!

        RETURNS:
        report: csv self.report_path+'/'report with fit result for each feature

        """
        TARGET = self.target
        progressbar = tqdm(featurelist, ascii=True, ncols=120)
        bestdata , _ = stackdata(self.data, previousbest)
        if self.sample_weights is not None:
            pass
        else:
            self.sample_weights = pd.Series(np.ones_like(TARGET), index=TARGET.index)
        report_path =self.report_path+'/'+csvreport
        report = load_report(report_path)
        print('Refitting if necesary..')
        for feature in progressbar:
            currentfeatures = previousbest.copy()
            currentfeatures.append(feature)
            if debug:
                pdb.set_trace()
            progressbar.set_description(f'procesing \'{previousbest}\' with \'{feature}\' ... :')
            feature_union, _ = stackdata(self.data, [feature], prevdata=bestdata)
            X_train, X_test, y_train, y_test = train_test_split(  # w_train, w_test,
                feature_union, 
                TARGET, 
                test_size=0.2, 
                shuffle=True, 
                random_state=42, 
                stratify=self.sample_weights
                )
            clf = GridSearchCV(model, param_grid=paramgrid, scoring='neg_root_mean_squared_error') 
            clf.fit(X_train, y_train)

            y_train_pred = clf.predict(X_train)
            y_test_pred = clf.predict(X_test)
            y_pred = clf.predict(feature_union)
            score_train = mean_squared_error(y_train, y_train_pred, squared=False)
            score_test = mean_squared_error(y_test, y_test_pred, squared=False)
            thisscore = mean_squared_error(TARGET, y_pred, squared=False)
            report = pd.concat(
                    [
                        report, 
                        pd.DataFrame.from_dict(data={
                            feature:{
                                'best_estimator': deepcopy(clf.best_estimator_),
                                'best_score': np.abs(clf.best_score_),
                                'error': thisscore,
                                'train_score': score_train,
                                'test_score': score_test
                                }
                            },
                            orient='index'
                            )
                    ], 
                    #                    ignore_index=False
            )
        print ('fitting has finished, ', self.criterion, ' = ', report.iloc[0][self.criterion])
        report = self.sort_report(report) 
        with open(os.path.join(self.report_path, csvreport), 'wb') as f:
            pickle.dump(report, f)
        return report
    
    def sort_report(self, thereport):
        thereport.sort_values(by=self.criterion, inplace=True)
        if self.sort_criteria == 'score_only':
            return thereport
        elif self.sort_criteria == 'index_too':
            return self.sort_report_by_score_and_index(thereport)

    def sort_report_by_score_and_index (self, thereport):
        bestsreport = thereport.iloc[0]
        selection_of_bests = thereport[(thereport[self.criterion]-bestsreport[self.criterion]).abs()<0.01]
        selection_of_bests['order'] = selection_of_bests.index.str.split('_').map(lambda l: int(l[-1]))
        selection_of_bests.sort_values(by='order', inplace=True)
        theremaining_index = selection_of_bests.index.difference(thereport.index)
        return thereport.loc[selection_of_bests.index.append(theremaining_index)] 
    
    def build_features_list(self,
        best_feature_proposal=[], 
        try_feature_list=None,
        report_suffix='',
        report_prefix='',
        pass_force_refit=False,
        pass_debug=False,
        maxnumfeatures=10
    ):
        """
        this function uses stack_data and get_best_feature to test different concatenations of features and actually mkae the fits.

        PARAMS: 
        =======
        DATA: dataframe with the data of features
        best_feature_proposal: probably ad-hoc selected list of features. all other features will add to this list.
        try_feature_list: list of features to try.
        report_suffix, report_prefix: identification of report files
        param_grid: grid of parameters to pass to getbestfeature()
        pass_force_refit: wether to tell getbestfeature to force the refit
        pass_debug: wether  to tell getbestfeature to debug

        RETURNS
        ========
        best_feature: list of best features found
        bet_score: list of scores for the concatenation up to the best features.
        
        """
        if try_feature_list is None:
            try_feature_list = self.feature_list
        best_feature = [] 
        #MDF-COMMENT this I was doing before:
        prev_feature_list=list(set(try_feature_list) - set(best_feature))
        #MDF-COMMENT the bad thing about this is that all the best_feature_proposal are added 
        #MDF-COMMENT one by one, what I expect now is to make a full fit of best_feature_proposal
        #MDF-COMMENT at once and then start trying try_feature_list one by one
        best_score = []
        DATA = self.data,
        #MDF-COMMENT naively check correlations
        CORRS = self.data.corr()
        paramgrid = self.model_params
        if pass_debug:
            pdb.set_trace()
        if len(best_feature_proposal) > 0:
            best_feature = []
            for feature in best_feature_proposal:
                if feature in best_feature:
                    continue
                report = self.getbestfeature(
                        [feature], #[best_feature_proposal[-1]],
                        paramgrid, 
                        previousbest=best_feature, #best_feature_proposal[:-1],
                        model=self.model,
                        csvreport='{}report_{}{}.csv'.format(report_prefix,'proposal_', report_suffix),
                        forcerefit=pass_force_refit,
                        )
                best_feature.append(feature)
                best_score.append(report[self.criterion].loc[feature].min())
                pass

        for i in range(len(best_feature), min(len(try_feature_list),maxnumfeatures)):
            new_feature_list = prev_feature_list.copy()
            if len(best_feature) > 0:
                #for feature_to_remove in CORRS[CORRS[best_feature[-1]] > 0.4].index :
                #    if feature_to_remove in new_feature_list:
                #        new_feature_list.remove(feature_to_remove)
                if  best_feature[-1] in new_feature_list :
                    new_feature_list.remove(best_feature[-1])
            if len(new_feature_list) == 0:
                break
            reportfile = '{}report_{}{}.csv'.format(report_prefix, i, report_suffix)
            report = self.getbestfeature(
                                      new_feature_list,
                                      paramgrid, 
                                      previousbest=best_feature.copy(),
                                      model=self.model,
                                      csvreport=reportfile,
                                      forcerefit=pass_force_refit
                                   )
            if pass_debug:
                pdb.set_trace()
#            if len(best_feature) > 0 and report.iloc[0][self.criterion] > best_score[-1]:
#                continue
            best_feature.append( report.iloc[0].name )
            best_score.append( report.iloc[0][self.criterion])
            prev_feature_list = new_feature_list.copy()
        self.report = report # save the last report as an object property
        return best_feature, best_score

import sys
sys.path.insert(0, os.path.dirname(__file__))
from DatasetOperator import Dataset 
from MLConveniences import score_fitted_model, cross_val_score
import copy

def check_mag_in_index(feature_list : pd.Index, compare_with):
    add_description = ''
    if 'Mag' in feature_list:
        add_description = ' Mag In '
    elif 'Mag' not in compare_with:
        add_description = ' warning, Mag removed !' 
    return add_description

class NewFeatureConcatenate():

    def __init__(self, dataset: Dataset, model: RegressorMixin , model_params = {}, model_params_grid={}):
        self.model = model
        self.DS : Dataset = dataset
        self.samplesplit = dataset.get_samplesplit()
        if isinstance(self.model, GridSearchCV):
            self.model.set_params(param_grid = model_params_grid)
        elif isinstance(self.model, Pipeline):
            self.model.set_params(**model_params)
        else:
            raise ValueError('undetermined model')

    def discard_correlated_features(self, thegroupname, the_best_feature_name, current_list):
        corrs = self.DS.Features[thegroupname].corr().abs()[the_best_feature_name]
        return corrs.index[corrs < 0.99].intersection(current_list)


    def  get_best_features_list(
            self,
            groupname: str,
            num_features = 2,
            max_workers=1,
            max_features: int = 200, 
            search_only : pd.core.indexes.base.Index = None):
        if search_only is not None:
            max_features = len(search_only)
        feature_list = pd.DataFrame()
        max_num_features = min(num_features, max_features)
        progress = tqdm(range(max_num_features))
        for step in progress:
            this_best_feature : pd.core.frame.DataFrame = self.get_best_feature(groupname, feature_list.index.tolist(), max_workers=max_workers, search_within = search_only)
            feature_list  = pd.concat([ feature_list, this_best_feature ], axis=0) #i#, axis=1, ignore_index=False)
            last_train = this_best_feature['train'][0]
            last_test = this_best_feature['test'][0]
            best = feature_list.sort_values(by='test').iloc[0]
            best_test = best['test']
            if last_test > 1.5*best_test:
                break
            description = f'      train: {last_train:.3f}, test: {last_test:.3f} , best = {best.name}, {best_test:.3f}' 
            search_only = self.discard_correlated_features(
                    groupname, this_best_feature.index[0], search_only
                    )
            description += check_mag_in_index(feature_list.index, search_only)
            if len(search_only) < 1:
                break
            progress.set_postfix({this_best_feature.index[0]: description})
            progress.total = min(len(search_only), max_num_features)
            progress.refresh()
        return feature_list

    def train_fixed_plus_try(self, feature):
        if feature in self.fixed_features:
            return None
        if isinstance(self.model, GridSearchCV):
            pass
        else:
            raise('not a grid search')
        thismodel : sklearn.model_selection._search.GridSearchCV = copy.deepcopy(self.model)
        thismodel.fit(self.xtrain[self.fixed_features + [ feature ]], self.ytrain)
        score2 =  score_fitted_model(
                thismodel, 
                self.xtrain[self.fixed_features + [ feature ]], 
                self.xtest[self.fixed_features + [ feature ]], 
                self.ytrain, 
                self.ytest
                )
        score = { 'train1': abs(thismodel.cv_results_['mean_train_score'].max()), 'test1': abs(thismodel.cv_results_['mean_test_score'].max()), 'params' : thismodel.best_params_}
        score.update(score2)
        return {feature: score}

    def get_best_feature(self, groupname: str, fixed_features = [], max_workers = 3, search_within : pd.core.indexes.base.Index = None) -> list[str]:
        self.fixed_features = fixed_features
        self.xtrain, self.xtest, self.ytrain,  self.ytest = self.DS.train_test_split(groupname)
        if search_within is None:
            inspect_features : pd.core.index.Index = self.DS.Features[groupname].columns 
        else:
            inspect_features = search_within
        try_feature_list = inspect_features.difference(self.fixed_features)
        scores: list[dict[str,dict[str, float]]] = process_map(self.train_fixed_plus_try, try_feature_list, max_workers=max_workers,  leave=False)# max_workers,
        scores: dict[str, dict[str,float]] = dict(map(dict.popitem, scores))
        scores = pd.DataFrame.from_dict(scores, orient='index')
        scores.sort_values(by='test', inplace=True)
        return scores.loc[scores.index[[0]]]
