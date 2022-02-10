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
    pdb.set_trace()
    if len(thecurve['ev_fit_results']) > 0:
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
            results = [np.mean(edata),  1e36, 1e36, np.mean(vdata)]
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
        l.append(ax.plot(v,e,'-', label = 'fit')[0])
        thecovlabel = f'$R^2 = $ {r2:.3f}' 
        l.append(ax.plot(evcurve['V'], evcurve['E'], 'o', color=l[-1].get_color(), label=thecovlabel))
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
        for key in curvedata.keys():
            fiteos[thisid][key], r2[thisid][key] = get_eos_goodness(curvedata[key])
            if fiteos[thisid][key] is None:
                goodness[thisid].update({ key: False })
                continue
            v0 = fiteos[thisid][key][-1]
            vmax = np.max( curvedata[key]['evcurve']['V'] )
            vmin = np.min( curvedata[key]['evcurve']['V'] )
            if  r2[thisid][key] < 0.99 or (v0 < vmin or v0 > vmax):
                goodness[thisid].update({ key: False })
            else:
                goodness[thisid].update({ key: True })
    df = pd.Series(goodness)
    df.to_json('goodness.json')
    return df, fiteos, r2
    
if __name__ == '__main__':
    EVcurves = pd.read_json('evcurves.json') 
    goodness, fiteos, r2  = get_goodness(EVcurves)         
    progress = tqdm(EVcurves.iteritems(), total = len(EVcurves))
    with PdfPages('multipage_fitted_curves.pdf') as pdf:
#        with PdfPages('bad_evcurves_multipage.pdf') as badpdf:
        for thisid, curvedata in progress:
            if any(goodness[thisid].values()):
                fig, ax = plt.subplots(1,1)
                plotted_lines = []
                for key, thisdata in curvedata.items():
                    if goodness[thisid][key]:
                        plotted_lines += plot_fitted_curve (thisdata['evcurve'], fiteos[thisid][key],r2[thisid][key],  fig=fig, ax=ax)
                try:
                    ax.legend()
                except Exception as E:
                    pdb.set_trace()
                    pass
                fig.suptitle(thisid)
                fig.tight_layout()
                pdf.savefig(fig)
                plt.close(fig)
