import pdb
import pandas as pd
from ase.eos  import EquationOfState, birchmurnaghan
import numpy as np
from tqdm import tqdm
from sklearn.metrics import mean_absolute_percentage_error
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np



def get_eos_goodness(thecurve):
    try:
        V0 = thecurve['ev_fit_results']['V_murn']
        E0 = thecurve['ev_fit_results']['E_murn']
        B0 = thecurve['ev_fit_results']['B_murn']
        B0p = thecurve['ev_fit_results']['Bdev_murn']
        results, pcov = curve_fit(birchmurnaghan, thecurve['V'], thecurve['E'], [E0, B0, B0p, V0] )
    except Exception as E:
        results = None
        pcov = [np.Inf]
    return results, pcov
    
def plot_fitted_curve(evcurve, thefit, thecov, fig=None,  ax=None):
    try:
        v = np.linspace(min(evcurve['V']), max(evcurve['V']), 100)
        e =  birchmurnaghan(v, thefit[0], thefit[1], thefit[2], thefit[3])
        l = ax.plot(v,e,'-', label = 'fit')[0]
        thecovlabel = ' '.join([f'{cov/val:.1e}' for cov, val  in zip(np.diag(thecov), thefit)])
        ax.plot(evcurve['V'], evcurve['E'], 'o', color=l.get_color(), label=thecovlabel)
        fig.tight_layout()
    except TypeError as E:
        print(E)
        pass
    except ValueError as E:
        print(E)
        pass

if __name__ == '__main__':
    goodness = {}
    EVcurves = pd.read_json('evcurves.json', orient='index')
    progress = tqdm(EVcurves.iterrows(), total = len(EVcurves))
    with PdfPages('multipage_fitted_curves.pdf') as pdf:
        with PdfPages('bad_evcurves_multipage.pdf') as badpdf:
            for id, curvedata in progress:
                goodness[id]={}
                fig, ax = plt.subplots(1,1)
                pcov = []
                for key in curvedata['evcurve'].keys():
                    fiteo, tpcov = get_eos_goodness(curvedata['evcurve'][key])
                    pcov.append(np.diag(tpcov))
                    goodness[id][key]=np.sqrt(np.diag(tpcov).sum())
                    plot_fitted_curve (curvedata['evcurve'][key], fiteo, tpcov, fig=fig, ax=ax)
                ax.legend()
                if len(tpcov) < 2 or abs(pcov[-1][-2]/fiteo[-2]) > 10:
                    badpdf.savefig(fig)
                else:
                    pdf.savefig(fig)
                plt.close(fig)
    
    


