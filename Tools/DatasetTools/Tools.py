import os
import sys
import re
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
plt.style.use('default')
plt.rc('figure', figsize=(15,10))
plt.rc('font', size=22)
import pdb

def need_to_update(afile):
    result = True
    if os.path.exists(afile):
        if os.path.getmtime(afile) > os.path.getmtime(__file__):
            result = False
    return result



class CaseNamer:

    def __init__(self,
            CASE, MODEL, 
            CUTOFF = 'TABLECUTOFF', 
            EMODE ='WUBIND',
            CRITERION = 'test_score', 
            SEARCHMODE='score_only',
            TARGET = 'EF'
            ):
        """
        CASE: Initial | relaxed
        MODEL: CANONICAL | ORTHOGONAL | FULL (orthogonal + onsites)
        CUTOFF: 'TABLECUTOFF | HISTCUTOFF'
        EMODE: 'WENERGY' | ''
        CIRTERION :'test_score | train_score | error'
        SEARCHMODE: 'score_only|index_too'
        """
        self.id_string = f'{TARGET}_{CRITERION}_{SEARCHMODE}_{MODEL}_{EMODE}_{CASE}_{CUTOFF}.pdf'
        
    def get_plot_filename(self, plotname, minorcase):
        return f'graphs/{plotname}_{minorcase}_{self.id_string}.pdf'#.format(plotname, minorcase, CASE, MODEL, CUTOFF, MODE)

    def get_table_filename(self, tablename, minorcase):
        return f'tables/{tablename}_{minorcase}_{self.id_string}.csv'

class Plotting:


    def with_and_without_outliers(thisfeature: pd.core.series.Series, low = None, hig = None, title = '$E_f$'):
        pread = thisfeature.max() - thisfeature.min()
        if low == None:
            low = thisfeature.min()-spread*0.05
        if hig == None:
            hig = thisfeature.max()+spread*0.05

        fig, ax = plt.subplots(1,2,figsize=(30,10))
        h3=thisfeature.hist(bins=100, fill='k', ax=ax[1], density=True, label='data with outliers')
        h1=thisfeature[(thisfeature>low) & (thisfeature<hig)].hist(bins=100, ax=ax[0],density=True,label='current curated data (no outliers)')
        ax[0].legend()
        ax[0].set_xlabel(title, x=1, labelpad=20)
        ax[0].set_ylabel('density counts', labelpad = 20)
        l = ax[1].legend()
        return fig


    def compare_features(featureone, titleone, featuretwo, titletwo):
        fig, ax = plt.subplots(1,2,figsize=(30,10))
        h3=featureone.hist(bins=100, fill='k', ax=ax[1], density=True, label='total eneregy')
        h1=featuretwo.hist(bins=100, ax=ax[0],density=True,label='$\Delta E_f$')
        ax[1].set_xlabel(titleone, labelpad=20)
        ax[0].set_xlabel(titletwo, labelpad = 20)
        return fig
        #l = ax[1].legend()

    def plot_pair(feature1, feature2, huefeature=None):
        if huefeature is None:
            huefeature = 'Class'
        fig, ax = plt.subplots()
        sns.scatterplot(data = data_w_classes, 
                        x=feature1,
                        y = feature2, ax = ax, hue=huefeature,
                        s=200)
        ax.set_xlabel(feature_titles[feature1])
        ax.set_ylabel(feature_titles[feature2])
        ax.legend(bbox_to_anchor=[1,1], markerscale=2)
        return figV

    def histoff_realfeatures(DATA, columns, titles, figsize_, ncols = 5, fig_ax = None):
        if fig_ax == None:
            axg = []
            nrows = np.ceil(len(columns)/ncols).astype(int)
            fig = plt.figure(figsize=figsize_) 
        else: 
            fig, axg = fig_ax
        feature = []
        for c, col in enumerate(columns):
            bins, edges = np.histogram(DATA[col], bins=100)#, density=True)
            if len(axg) < c+1:
                axg.append( fig.add_subplot(nrows, ncols, c+1 ) ) 
            axg[c].bar(edges[:-1], bins,width=np.diff(edges)) # color='steelblue'
            t = axg[c].text(0.5, 0.5, titles.iloc[c], fontsize=24 , transform=axg[c].transAxes)
            t.set_bbox(dict(facecolor='white', alpha=0.75))
            axg[c].set_yticks([])
            axg[c].set_xticks([])
            feature.append(col)
        fig.subplots_adjust(hspace=0.1, wspace=0.1)
        return fig, axg

    def plot_learning_curve(
            thescores, 
            feature_titles,
            ax=None, modelname='RandomForest',dothelabels = True, 
            Labels_Dict = {'ylabel':'RMSE', 'xlabel':'number of features'}
            ):
        if ax is None:
            fig, ax = plt.subplots()
        ax.plot(np.arange(1,len(thescores)+1),thescores) 
        ax.set_ylabel (Labels_Dict['ylabel'])
        ax.set_xlabel (Labels_Dict['xlabel'])
        if dothelabels:
            for i in range(feature_titles.shape[0]):
                t = plt.annotate(
                    feature_titles.iloc[i],
                    ((i+1), thescores[i]),
                    ((i+1), thescores[i]),
                    fontsize=22,
                )
                t.set_bbox(dict(facecolor='white', alpha=0.5))
#        plt.savefig(FileNames.get_plot_filename('LearningCurve', modelname))
        return ax

     

