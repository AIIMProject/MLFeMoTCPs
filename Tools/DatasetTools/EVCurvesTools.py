#!/usr/bin/env python
# coding: utf-8

import json
import re
import glob
import os
import numpy as np
import pickle as pkl
import gzip
from gzip import BadGzipFile
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure as FigureType
from tqdm.auto import tqdm
import pandas as pd
from pandas.core.series import Series as SeriesType
#from BopFoxFeaturizer.brief_summary_parser import StructSummaryParser
#from BopFoxFeaturizer.Featurizer import Featurizer
# types
from numpy import ndarray as ArrayType
plt.rc('figure', figsize=(15,8))
plt.rc('font',size=22)
import pdb
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
from ase.eos  import EquationOfState, birchmurnaghan

def need_to_update(file):
    return  not os.path.exists(file) # and (os.path.getmtime(file) > os.path.getmtime(__file__))

def load_parsed(Parsed_Briefsummary):
    if os.path.exists(os.path.join(os.path.dirname(__file__),Parsed_Briefsummary)): #not_need_to_update(Parsed_Briefsumary):
        with open(Parsed_Briefsummary,'rb') as f:
            BOPF = pkl.load(f)
    else:
        BS =  StructSummaryParser().BriefSummary
        BOPF = Featurizer(BS)
        with open(Parsed_Briefsummary, 'wb') as f:
            pkl.dump(BOPF, f)
    return BOPF

def plot_sample_curves(thecurves: pd.core.series.Series, location='.') -> FigureType:
    multipdf = os.path.join(location, 'evcurves_multipage.pdf')
    with PdfPages(multipdf) as pdf:
        progress = tqdm(thecurves.iteritems(), total = len(thecurves))
        for index, data in progress:
            fig, ax = plt.subplots(1,1)
            ax.set_xlabel(index, fontsize=12)
            for params, curve in data.items():
                try:
                    ax.plot(curve['evcurve']['V'], curve['evcurve']['E'],'o', label=params)
                except IndexError as E:
                    pass
            ax.legend(fontsize=8)
            fig.tight_layout()
            pdf.savefig(fig)


def get_eos_goodness(thecurve):
    if thecurve == thecurve  and len(thecurve['ev_fit_results']) > 0:
        V0 = thecurve['ev_fit_results']['V_murn']
        E0 = thecurve['ev_fit_results']['E_murn']
        B0 = thecurve['ev_fit_results']['B_murn']
        B0p = thecurve['ev_fit_results']['Bdev_murn']
        param_guess = [E0, B0, B0p, V0]
        vdata = thecurve['evcurve']['V']
        edata = thecurve['evcurve']['E']
        try:
            results, pcov = curve_fit(birchmurnaghan, vdata, edata, param_guess)
            e =  birchmurnaghan(vdata, *results) 
        except RuntimeError as RE:
            results = [np.mean(edata),  0, 0, np.mean(vdata)]
            e = [np.mean(edata)]*len(vdata)
        r2 = r2_score(edata, e)
    else:
        results = None
        r2 = -np.Inf
    return results, r2
    
def plot_fitted_curve(evcurve, thefit, r2, fig=None,  ax=None):
    l = []
    if thefit is not None:
        v = np.linspace(min(evcurve['V']), max(evcurve['V']), 100)
        e =  birchmurnaghan(v,*thefit) #  thefit[0], thefit[1], thefit[2], thefit[3])
        thecovlabel = f'fit $R^2 = $ {r2:.3f}' 
        l.append(ax.plot(v,e,'-', label = thecovlabel)[0])
        l.append(ax.plot(evcurve['V'], evcurve['E'], 'o', color=l[-1].get_color(), label='calculations'))
        fig.tight_layout()
    return l

def get_goodness(EVcurves):
    goodness = {}
    fiteos = {}
    r2 = {}
    progress = tqdm(EVcurves.iteritems(), total = len(EVcurves))
    for thisid, curvedata in progress:
        goodness[thisid] =  {}
        fiteos[thisid] = {}
        r2[thisid] = {}
        for paramspec, paramcurve in curvedata.items():
            fiteos[thisid][paramspec], r2[thisid][paramspec] = get_eos_goodness(paramcurve)
            if fiteos[thisid][paramspec] is None:
                goodness[thisid].update({ paramspec: False })
                continue
            v0 = fiteos[thisid][paramspec][-1]
            vmax = np.max( curvedata[paramspec]['evcurve']['V'] )
            vmin = np.min( curvedata[paramspec]['evcurve']['V'] )
            if  r2[thisid][paramspec] < 0.95 or (v0 < vmin or v0 > vmax):
                goodness[thisid].update({ paramspec: False })
            else:
                goodness[thisid].update({ paramspec: True })
    df = pd.Series(goodness)
    df.to_json('goodness.json')
    return df, pd.Series(fiteos), pd.Series(r2)

def plot_the_sample(theindex, thedata, thefit_data, r2_data):
    fig, ax = plt.subplots(1,1)
    ax.set_title(theindex)
    ax.set_xlabel('V ($\AA ^3$)')
    ax.set_ylabel('E (eV)')
    legendhandles = []
    for (params, curve), fit, r2 in zip(thedata.items(), thefit_data.values(), r2_data.values()):
        l = plot_fitted_curve(curve['evcurve'], fit, r2, ax=ax, fig=fig)
    ax.legend()
    return fig, ax

def plot_curves(thesample: pd.core.series.Series, thefits: pd.core.series.Series, ther2s: pd.core.series.Series):
    fig_collection = []
    ax_collection = []
    for (index, data ), fit_data, r2_data in zip(thesample.items(), thefits.values, ther2s.values):
        fig, ax = plot_the_sample(index, data, fit_data, r2_data)
        fig_collection.append(fig)
        ax_collection.append(ax)
    return fig_collection, ax_collection

def plot_curves_topdf(thecurves: pd.core.series.Series, thefits: pd.core.series.Series, ther2: pd.core.series.Series, pdffile: str):
    collection = zip(thecurves.iteritems(), thefit.values, ther2s.values)
    progress = tqdm(collection, total = len(collection))
    with PdfPages(pdffile) as pdf:
        for thisid, curvedata in progress:
            fig, ax = plot_the_sample(thisid, curvedata)
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

def invert_goodness(thegoodness):
    return thegoodness.map(lambda d: {key: not value for key, value in d.items()} )



class Evcurves(object):

    def __init__(self, dataset, Indexes = None,  atoms = ['Co', 'Ti', 'W'], search_str = '**/volume-energy.dat'):
        self.Indexes = Indexes
        self.dataset = dataset
        self.search_str = search_str
        self.atoms = atoms
        self.EVFILES = self.load_files_matching()
        self.Paths = pd.DataFrame(np.vstack(self.EVFILES.str.split('/')), index = self.EVFILES.index)
        self.Roots = pd.Series(
                self.Paths.iloc[:,:-2].apply(lambda p: '/'.join(p), axis = 1).unique(),
                name='-'.join(atoms)
                )
#        self.Index = self.Roots.str.replace('/bulk/','_').str.replace('/volume_relaxed','')

    @staticmethod
    def read_index(theindex):
        composition, structure, mag =  theindex.split('.')
        remove_count_last_element = re.sub('[0-9]$','', composition)
        elements_without_counts = re.sub('[0-9]+', '-', remove_count_last_element)
        elements_without_trailing_slash = re.sub('-$','', elements_without_counts)
        return elements_without_trailing_slash, structure, mag

    def make_selection(self, theindex, thisdeltaks, thisencut):
        elements, structure, mag = self.read_index(theindex)
        select_elements = self.EVFILES.str.contains(elements) & (~ self.EVFILES.str.contains(elements+'-'))
        select_structure = self.EVFILES.str.contains(structure)
        if mag == 'FM':
            select_mag = self.EVFILES.str.contains(mag)
        elif ( 'U' in mag ) or ( 'D' in mag ):
            select_mag = self.EVFILES.str.contains(mag)
        else:
            select_mag = ~self.EVFILES.str.contains('FM')
        select_params = self.EVFILES.str.contains(thisdeltaks) & self.EVFILES.str.contains(thisencut) 
        return select_elements & select_structure & select_mag & select_params

    def get_ev_fit_results(self, params, curve_files):
        results_dict = {} 
        for curvefile in curve_files:
            directory = os.path.dirname(curvefile)
            fit_result_file = os.path.join(directory, 'fit_results.dat')
            if os.path.exists(fit_result_file):
                results = pd.read_csv(fit_result_file, sep = '\s+', header=None, comment='#')
            results_dict={res[0]: float(res[1]) for _, res in results.iterrows() if '_murn' in res[0]}
        return results_dict

    def get_curves_for_params(self, param, curve_files):
        curves = {}
        if len(curve_files) > 0:
        #    try:
            curves = pd.read_csv(
                    curve_files[curve_files.str.contains(param)].values[0], 
                    sep='\s',
                    header=None)
        #    except pd.errors.EmptyDataError as E:
        #        curves = pd.DataFrame(np.array([[np.nan]*3]))
        #        pass
            curves = {'V': curves[0].values, 'E': curves[1].values} 
        return curves

    def get_evcurves(self, Indexes = None, deltaks=None, encuts=None):
        EVCURVES = {}
        progress = tqdm(self.Indexes, total=len(self.Indexes))# 
        for thisindex in progress:
            progress.set_description(thisindex)
            selection = self.make_selection(thisindex, deltaks[thisindex], encuts[thisindex])
            curve_files = self.EVFILES[selection]
            if self.Paths.shape[1] > 1:
                params = self.Paths[selection].iloc[:,-2]
            else:
                params = pd.Series(['dk']*len(selection))
            EVCURVES[thisindex] ={}
            for param in params.values:
                EVCURVES[thisindex][param] ={
                        'evcurve': self.get_curves_for_params(param, curve_files),
                        'ev_fit_results': self.get_ev_fit_results(params, curve_files)
                        }
        return pd.Series(EVCURVES)

    def load_evcurves(self, deltaks=None, encuts=None):
        self.evcurves = self.get_evcurves(self, deltaks, encuts)

    def load_files_matching(self):
        saved_list = os.path.join(self.dataset, 'list_of_outcars.csv')
        fullsearchstring = f'{self.dataset}/rawdata/**/volume_relaxed/{self.search_str}'
        if not need_to_update(saved_list):
            list_of_files = pd.read_csv(saved_list, squeeze=True, header=None)
        else:
            list_of_files = pd.Series(glob.glob(fullsearchstring,  recursive=True))
            list_of_files.name = 'full_path'
            list_of_files.to_csv(saved_list, header=False, index=False)
        if len( list_of_files ) > 0:
            return list_of_files
        else:
            return pd.Series(['']*len(self.Indexes), index=self.Indexes)
