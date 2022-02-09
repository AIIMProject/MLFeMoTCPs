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
    if len(thecurve['ev_fit_results']) > 0:
        V0 = float(thecurve['ev_fit_results']['V_murn'])
        E0 = float(thecurve['ev_fit_results']['E_murn'])
        B0 = float(thecurve['ev_fit_results']['B_murn'])
        B0p = float(thecurve['ev_fit_results']['Bdev_murn'])
        try:
            results, pcov = curve_fit(birchmurnaghan, thecurve['V'], thecurve['E'], [E0, B0, B0p, V0] )
            e =  birchmurnaghan(thecurve['V'], results[0], results[1], results[2], results[3])
        except RuntimeError as RE:
            results = [np.mean( thecurve['E'] ),  1e36, 1e36, np.mean( thecurve['V'] )]
            e = [np.mean(thecurve['E'])]*len(thecurve['V'])
        except Exception as E:
            pdb.set_trace()
            pass
        r2 = r2_score(thecurve['E'], e)
    else:
        results = None
        r2 = -np.Inf
    return results, r2
    
def plot_fitted_curve(evcurve, thefit, r2, fig=None,  ax=None):
    l = []
    if thefit is not None:
        try: 
            v = np.linspace(min(evcurve['V']), max(evcurve['V']), 100)
            e =  birchmurnaghan(v, thefit[0], thefit[1], thefit[2], thefit[3])
        except Exception as E:
            pdb.set_trace()
            pass
        l.append(ax.plot(v,e,'-', label = 'fit')[0])
        thecovlabel = f'$R^2 = $ {r2:.3f}' 
        l.append(ax.plot(evcurve['V'], evcurve['E'], 'o', color=l[-1].get_color(), label=thecovlabel))
        fig.tight_layout()
    else:
        pass
    return l


if __name__ == '__main__':
    goodness = {}
    EVcurves = pd.read_json('evcurves.json', orient='index')
    progress = tqdm(EVcurves.iterrows(), total = len(EVcurves))
#    with PdfPages('multipage_fitted_curves.pdf') as pdf:
#        with PdfPages('bad_evcurves_multipage.pdf') as badpdf:
    for thisid, curvedata in progress:
#        fig, ax = plt.subplots(1,1)
#            plotted_lines = {}
        goodness[thisid] =  {}
        for key in curvedata['evcurve'].keys():
            fiteo, r2 = get_eos_goodness(curvedata['evcurve'][key])
#                plotted_lines.append(plot_fitted_curve (curvedata['evcurve'][key], fiteo, r2, fig=fig, ax=ax))
            if  r2 < 0.99:
                goodness[thisid].update({ key: False })
            else:
                goodness[thisid].update({ key: True })
#           if len(plotted_lines) > 0:
#               ax.legend()
#               fig.suptitle(thisid)
#               fig.tight_layout()
#           plt.close(fig)
    df = pd.Series(goodness)
    df.to_json('goodness.json')
    
    


