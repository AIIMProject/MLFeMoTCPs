#!/usr/bin/env python
# coding: utf-8

import json
from importlib.machinery import SourceFileLoader
import pandas as pd
import re
import glob
import os
import numpy as np
import pickle as pkl
import gzip
from gzip import BadGzipFile
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from tqdm import tqdm
import pdb
from BopFoxFeaturizer.brief_summary_parser import StructSummaryParser
from BopFoxFeaturizer.Featurizer import Featurizer
# types
from matplotlib.figure import Figure as FigureType
from pandas.core.series import Series as SeriesType
from numpy import ndarray as ArrayType
plt.rc('figure', figsize=(15,8))
plt.rc('font',size=22)

def need_to_update(file):
    return  not os.path.exists(file) # and (os.path.getmtime(file) > os.path.getmtime(__file__))

def load_parsed(Parsed_Briefsummary):
    if os.path.exists(os.path.join(os.path.dirname(__file__),Parsed_Briefsumary)): #not_need_to_update(Parsed_Briefsumary):
        with open(Parsed_Briefsumary,'rb') as f:
            BOPF = pkl.load(f)
    else:
        BS =  StructSummaryParser().BriefSummary
        BOPF = Featurizer(BS)
        with open(Parsed_Briefsumary, 'wb') as f:
            pkl.dump(BOPF, f)
    return BOPF

class Evcurves(object):

    def __init__(self, atoms = ['Co', 'Ti', 'W'], search_str = '**/volume-energy.dat'):
        self.EVFILES = self.load_files_matching(search_str)
        self.Paths = pd.DataFrame(np.vstack(self.EVFILES.str.split('/')))
        self.Roots = pd.Series(
                self.Paths.iloc[:,:-2].apply(lambda p: '/'.join(p), axis = 1).unique(),
                name='-'.join(atoms)
                )
        self.Index = self.Roots.str.replace('/bulk/','_').str.replace('/volume_relaxed','')
        self.atoms = atoms
    

    @staticmethod
    def read_index(theindex):
        composition, structure, mag =  theindex.split('.')
        remove_count_last_element = re.sub('[0-9]$','', composition)
        elements_without_counts = re.sub('[0-9]+', '-', remove_count_last_element)
        return elements_without_counts, structure, mag

    def make_selection(self, theindex, thisdeltaks, thisencut):
        elements, structure, mag = self.read_index(theindex)
        select_elements = self.EVFILES.str.contains(elements) & (~ self.EVFILES.str.contains(elements+'-'))
        select_structure = self.EVFILES.str.contains(structure)
        select_mag = self.EVFILES.str.contains(mag)
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
        try:
            curves = pd.read_csv(
                    curve_files[curve_files.str.contains(param)].values[0], 
                    sep='\s',
                    header=None)
        except pd.errors.EmptyDataError as E:
            curves = pd.DataFrame(np.array([[np.nan]*3]))
            pass
        curves = {'V': curves[0].values, 'E': curves[1].values} 
        return curves

    def get_evcurves(self, Indexes = None, deltaks=None, encuts=None):
        EVCURVES = {}
        progress = tqdm(Indexes, total=len(Indexes))
        for thisindex in progress:
            selection = self.make_selection(thisindex, deltaks[thisindex], encuts[thisindex])
            curve_files = self.EVFILES[selection]
            params = self.Paths[selection].iloc[:,-2]
            EVCURVES[thisindex] ={}
            for param in params.values:
                EVCURVES[thisindex][param] ={
                        'evcurve': self.get_curves_for_params(param, curve_files),
                        'ev_fit_results': self.get_ev_fit_results(params, curve_files)
                        }
        return pd.Series(EVCURVES)

    def load_evcurves(self, Indexes = None, deltaks=None, encuts=None):
        self.evcurves = self.get_evcurves(Indexes, deltaks, encuts)

    def load_files_matching(self, search_str):
        saved_list = 'list_of_outcars.csv'
        if not need_to_update(saved_list):
            list_of_files = pd.read_csv(saved_list, squeeze=True, header=None)
        else:
            list_of_files = pd.Series(glob.glob(search_str, recursive=True))
            list_of_files.name = 'full_path'
            list_of_files.to_csv(saved_list, header=False, index=False)
        return list_of_files

def plot_sample_curves(thecurves: pd.core.series.Series) -> FigureType:
    with PdfPages('evcurves_multipage.pdf') as pdf:
        progress = tqdm(thecurves.iteritems(), total = len(thecurves))
        for index, curve in progress:
            fig, ax = plt.subplots(1,1)
            ax.set_xlabel(index, fontsize=12)
            for subcurve in curve.keys():
                try:
                    ax.plot(curve[subcurve]['V'], curve[subcurve]['E'],'o', label=subcurve)
                except IndexError as E:
                    pass
            ax.legend(fontsize=8)
            fig.tight_layout()
            pdf.savefig(fig)

if __name__ == '__main__':

    Parsed_Briefsumary = 'ParsedBS.pkl'
    BOPF = load_parsed(Parsed_Briefsumary)
    EV = Evcurves(atoms=['Cr','Co','W'], search_str='data/**/volume_relaxed/**/volume-energy.dat')
    EV.load_evcurves(BOPF.data.index, deltaks = BOPF.data['deltak'], encuts = BOPF.data['encut'])
    EV.evcurves.to_json('evcurves.json')
#    plot_sample_curves(EV.evcurves)
