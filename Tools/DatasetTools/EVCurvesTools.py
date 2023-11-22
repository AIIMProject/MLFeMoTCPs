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
import copy
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

eV_per_angstrom3_to_GPA = 160.21 # http://greif.geo.berkeley.edu/~driver/conversions.html @ 07/11/2023

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
        #        V0 = thecurve['ev_fit_results']['V_murn']
        #        E0 = thecurve['ev_fit_results']['E_murn']
        #        B0 = thecurve['ev_fit_results']['B_murn']
        #        B0p = thecurve['ev_fit_results']['Bdev_murn']
        vdata = thecurve['evcurve']['V']
        edata = thecurve['evcurve']['E']
        V0 = vdata.mean()
        E0 = edata.min()
        B0 = 100
        B0p = 1
        param_guess = [E0, B0, B0p, V0]

        try:
            results, pcov = curve_fit(birchmurnaghan, vdata, edata, param_guess)
            e =  birchmurnaghan(vdata, *results) 
            results[1] *= eV_per_angstrom3_to_GPA  # convert units of Bulk modulus
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
        e =  birchmurnaghan(v,*thefit/np.array([1, eV_per_angstrom3_to_GPA, 1, 1])) #  thefit[0], thefit[1], thefit[2], thefit[3])
        thecovlabel = f'fit $1- R^2 = $ {1-r2:.3e}' 
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
            goodness[thisid].update({ paramspec: False })
#            if len(curvedata[paramspec]['evcurve']['V']) < 1:
            if 'V' not in curvedata[paramspec]['evcurve'].keys():
                continue

            fiteos[thisid][paramspec], r2[thisid][paramspec] = get_eos_goodness(paramcurve)
            if fiteos[thisid][paramspec] is None:
                #    goodness[thisid].update({ paramspec: False })
                continue
            v0 = fiteos[thisid][paramspec][-1]
            vmax = np.max( curvedata[paramspec]['evcurve']['V'] )
            vmin = np.min( curvedata[paramspec]['evcurve']['V'] )
            if  ( 1-r2[thisid][paramspec] <= 1e-6 ) and is_common_sense_evcurve(curvedata[paramspec]['evcurve']['V'], curvedata[paramspec]['evcurve']['E'], fiteos[thisid][paramspec]):
                # (v0 >= vmin and v0 <= vmax):
                #                goodness[thisid].update({ paramspec: False })
#            else:
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

from itertools import combinations

def is_common_sense_evcurve(v, e, params, unitsofb0 = 'Pa'):
    bulk_modulus_is_good = False
    bdev_is_good = False
    volumes_are_good = False #False

    if v is not None:
        if ( v.min() < params[-1] ) and ( v.max() > params[-1] ):
            volumes_are_good  = True
    if 'Pa' in unitsofb0 :
        if ( params[1] > 140 ) and ( params[1] < 300 ):
            bulk_modulus_is_good = True
    elif 'eV' in unitsofb0:
        if ( params[1] > 1 ) and ( params[1] < 3 ) :
            bulk_modulus_is_good = True
    if params[2] > 0 :
        bdev_is_good = True

    return ( volumes_are_good and bulk_modulus_is_good and bdev_is_good )

def find_the_good_curve_inside(
        thebadcurve,
        make_plot_of_options = False,
        reset_guess_params = False
        ):

    betterv = thebadcurve['evcurve']['V']
    bettere = thebadcurve['evcurve']['E']
#    param_guess = np.array([ np.min(bettere), 1, 1, np.mean(betterv)])
    param_guess = copy.copy(thebadcurve['fit'])
    param_guess[1] /= eV_per_angstrom3_to_GPA
    param_guess[0] = bettere.min()
    param_guess[-1] = betterv.mean()
    betterr2 = [ thebadcurve['r2'] ]

    all_indexs = np.linspace(0, len(betterv)-1, len(betterv), dtype=int)

    nremove = 0

    while 1-np.max(betterr2) > 5e-6 and ~is_common_sense_evcurve(None, None, param_guess, unitsofb0 = 'ev' ) and nremove <= 4:

        nremove += 1

        betterr2 = []
        list_of_params = []
        list_of_reducedvs = [] 
        list_of_reducedes = []

        list_of_try_indexs = combinations(all_indexs, len(betterv) - nremove)

        for try_indexs in  list_of_try_indexs:

            reducedv = thebadcurve['evcurve']['V'][list(try_indexs)]
            reducede = thebadcurve['evcurve']['E'][list(try_indexs)]


            if reset_guess_params:
                themine = np.argmin(reducede)
                param_guess[0] = reducede[themine]
                param_guess[-1] = reducedv[themine]
                #param_guess[1] = 1
                params_orig = copy.copy(param_guess)

            try:
                param_guess, pcov = curve_fit(birchmurnaghan, reducedv, reducede, param_guess)
            except RuntimeError as E:
                continue
            reduced_prediction = birchmurnaghan(reducedv, *param_guess)
            betterr2.append(r2_score(reducede, reduced_prediction))
            list_of_reducedvs.append(reducedv)
            list_of_reducedes.append(reducede)
            list_of_params.append(param_guess)


        if make_plot_of_options:
            bestcombi = np.argmax(betterr2)
            fig, ax = plt.subplots()
            ax.plot(list_of_reducedvs[bestcombi][themine], list_of_reducedes[bestcombi][themine], 'sk', markersize=10)
            ax.plot(betterv, bettere, 'ok')
            ax.plot(list_of_reducedvs[bestcombi], list_of_reducedes[bestcombi], 'o', markersize = 10, markerfacecolor='None')
            vv = np.linspace (list_of_reducedvs[bestcombi].min(), list_of_reducedvs[bestcombi].max(), 100)
            ax.plot(vv, birchmurnaghan(vv, *param_guess), '--', label = f'R2 = {1-betterr2[-1]:.3e}')
            ax.set_title(f'{params_orig}')
            ax.set_xlabel(f'{param_guess}')
            ax.legend()

    if nremove == 0 :
        return thebadcurve['r2'], thebadcurve['fit'],betterv, bettere

    bestcombi = np.argmax(betterr2)
    return_v = list_of_reducedvs[bestcombi]
    return_e = list_of_reducedes[bestcombi]
    return_params = list_of_params[bestcombi]
    return_params[1] *= eV_per_angstrom3_to_GPA
    return betterr2[bestcombi], return_params, return_v, return_e


def improve_goodness(thecurve):
    """functin taken from thomas"""
    betterv = [ thecurve['evcurve']['V'] ]
    bettere = [ thecurve['evcurve']['E'] ]
    betterparams = [copy.copy(thecurve['fit'])]
    betterparams[-1][1] /= eV_per_angstrom3_to_GPA
    #predicte = birchmurnaghan(v, *params)
    betterr2 = [ thecurve['r2'] ]

    param_guess = thecurve['fit']

    def fit_in_all_minus_one(thexs, theys, the_param_guess):
        thesize = len(thexs)
        partialr2 = []
        params_of_fit_on_reduced = []
        reducedx = []
        reducedy = []
        for removethis in range(thesize):
            reducedx.append( [thisx for i, thisx in enumerate(thexs) if i != removethis ])
            reducedy.append( [thisy for i, thisy in enumerate(theys) if i != removethis ])
            if the_param_guess[1] < 0:
                the_param_guess[0] = np.mean(reducedy[-1])
                the_param_guess[1] = 100
                the_param_guess[2] = 1
                the_param_guess[3] = np.mean(reducedx[-1])
            try:
                newparams, pcov = curve_fit(birchmurnaghan, reducedx[-1], reducedy[-1], the_param_guess)
            except RuntimeError:
                continue
            params_of_fit_on_reduced.append(newparams)
            reduced_prediction = birchmurnaghan(reducedx[-1], *newparams)
            partialr2.append(r2_score(reduced_prediction, reducedy[-1]))

        return partialr2, params_of_fit_on_reduced, reducedx, reducedy

    while max(betterr2) < 0.995 and len(betterv[np.argmax(betterr2)]) > 5 :
        best_previous = np.argmax(betterr2)
        betterr2, betterparams, betterv, bettere = fit_in_all_minus_one(betterv[best_previous], bettere[best_previous], betterparams[best_previous])

    ibest = np.argmax(betterr2)

    betterparams[ibest][1] *= eV_per_angstrom3_to_GPA

    return  betterr2[ibest], betterparams[ibest], betterv[ibest], bettere[ibest]


class Evcurves(object):

    """this class creates compiles all the evcurves below dataset root directory and creates a json file accordingly."""

    def __init__(self, dataset, Indexes = None,  atoms = ['Co', 'Ti', 'W'], search_str = '**/volume-energy.dat'):
        """params :
            dataset : str = root directory where data is stored. 
            Indexes: pd.Index = INdexes indicating structures for which report should be made 
            atoms : list[str] = atoms in the system
            search_str : str = search string to use for finding the ev curves data"""

        self._Indexes : pandas.core.indexes.base.Index = Indexes
        self._dataset : str = dataset
        self._search_str :str = search_str
        self._atoms : list[str] = atoms
        self._EVFILES = self.load_files_matching()
        self._Paths : pd.core.frame.DataFrame = pd.DataFrame(np.vstack(self._EVFILES.str.split('/')), index = self._EVFILES.index)
        self._Roots : pd.core.frame.DataFrame = pd.Series(
                self.Paths.iloc[:,:-2].apply(lambda p: '/'.join(p), axis = 1).unique(),
                name='-'.join(atoms)
                )

    @property
    def Roots(self):
      return self._Roots

    @Roots.setter
    def Roots(self, value):
      """ Root directory for each structure """
      self._Roots = value
 
    @property
    def Paths(self):
      return self._Paths

    @Paths.setter
    def Paths(self, value):
      """ Paths, ie. evfiles splitted by / """
      self._Paths = value

    @property
    def EVFILES(self):
      return self._EVFILES

    @EVFILES.setter
    def EVFILES(self, value):
      """ This is the list of files where ev curves are being defined"""
      self._EVFILES = value

    @property
    def atoms(self):
      return self._atoms

    @atoms.setter
    def atoms(self, value):
      """ list of atoms in the system. Defaults to ['Cr', 'Co', 'W']"""
      self._atoms = value

    @property
    def search_str(self):
      return self._search_str

    @search_str.setter
    def search_str(self, value):
      """ search string as in glob syntax to search for e-v files. Default: '**/volume-energy.dat'"""
      self._search_str = value

    @property
    def Indexes(self) -> pd.core.indexes.base.Index:
        return self._Indexes

    @Indexes.setter
    def Indexes(self, value):
        """list of structures indexes for which to generate the EVcurves"""
        self._Indexes = value

    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self, value):
        """sting with relative path to the root of data structure"""
        self._dataset = value

    @staticmethod
    def read_index(theindex) -> tuple[str]:
        composition, structure, mag =  theindex.split('.')
        remove_count_last_element = re.sub('[0-9]$','', composition)
        elements_without_counts = re.sub('[0-9]+', '-', remove_count_last_element)
        elements_without_trailing_slash = re.sub('-$','', elements_without_counts)
        return elements_without_trailing_slash, structure, mag

    def make_selection(self, theindex, thisdeltaks, thisencut) -> pd.core.series.Series:
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

    def get_ev_fit_results(self, params, curve_files) -> dict:
        results_dict = {} 
        for curvefile in curve_files:
            directory = os.path.dirname(curvefile)
            fit_result_file = os.path.join(directory, 'fit_results.dat')
            if os.path.exists(fit_result_file):
                results = pd.read_csv(fit_result_file, sep = '\s+', header=None, comment='#')
                results_dict={res[0]: float(res[1]) for _, res in results.iterrows() if '_murn' in res[0]}
        return results_dict

    def get_curves_for_params(self, param, curve_files) -> dict:
        curves = {}
        if len(curve_files) > 0:
            thefile = curve_files[curve_files.str.contains(param)].values[0]
            if os.path.exists(thefile) and os.path.getsize(thefile)>0:
                curves = pd.read_csv(
                        curve_files[curve_files.str.contains(param)].values[0], 
                        sep='\s',
                        header=None)
                curves = {'V': curves[0].values, 'E': curves[1].values} 
        return curves

    def get_evcurves(self, Indexes = None, deltaks=None, encuts=None) -> pd.core.series.Series:
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
                thisevcurve = self.get_curves_for_params(param, curve_files)
                this_ev_fit_results = self.get_ev_fit_results(params, curve_files)
                if len (thisevcurve) > 0:
                    EVCURVES[thisindex][param] ={
                            'evcurve':  thisevcurve,
                            'ev_fit_results': this_ev_fit_results
                            }
        return pd.Series(EVCURVES)

    def load_evcurves(self, deltaks=None, encuts=None) -> pd.core.series.Series:
        self.evcurves = self.get_evcurves(self, deltaks, encuts)

    def load_files_matching(self) -> pd.core.series.Series:
        saved_list = os.path.join(self.dataset, 'list_of_outcars.csv')
        fullsearchstring = f'{self.dataset}/rawdata/*/bulk/*/volume_relaxed/{self.search_str}'
        if not need_to_update(saved_list):
            list_of_files = pd.read_csv(saved_list,  header=None).squeeze('columns')
        else:
            list_of_files = pd.Series(glob.glob(fullsearchstring,  recursive=True))
            list_of_files.name = 'full_path'
            list_of_files.to_csv(saved_list, header=False, index=False)
        if len( list_of_files ) > 0:
            return list_of_files
        else:
            result =  pd.Series(['']*len(self.Indexes), index=self.Indexes)
            return result[result.map(len)] # something strange happens in some files for FeMo
