import pdb
import pandas as pd
from ase.eos  import EquationOfState, birchmurnaghan
import numpy as np
from tqdm import tqdm
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import warnings



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
    return goodness.map(lambda d: {key: not value for key, value in d.items()} )

if __name__ == '__main__':
    EVcurves = pd.read_json('evcurves.json', typ='series') 
    goodness, fiteos, r2  = get_goodness(EVcurves)         
    plot_curves_topdf (goodness, EVcurves, 'multipage_fitted_curves.pdf')
    plot_curves (invert_goodness(goodness), EVcurves, 'multipage_bad_curves.pdf')
    

