import pdb
import pandas as pd
from ase.eos  import EquationOfState, birchmurnaghan
import numpy as np

from sklearn.metrics import mean_absolute_percentage_error
from scipy.optimize import curve_fit


EVcurves = pd.read_json('evcurves.json', orient='index')

def get_eos_goodness(thecurve):
    try:
        V0 = thecurve['ev_fit_results']['V_murn']
        E0 = thecurve['ev_fit_results']['E_murn']
        B0 = thecurve['ev_fit_results']['B_murn']
        B0p = thecurve['ev_fit_results']['Bdev_murn']
    except Exception as E:
        pdb.set_trace()
        pass
    results, pcov = curve_fit(birchmurnaghan, thecurve['V'], thecurve['E'], [E0, B0, B0p, V0] )
    return results, pcov
    
goodness = {}
for id, curvedata in EVcurves.iterrows():
    goodness[id]={}
    for key in curvedata['evcurve'].keys():
        fiteo, pcov = get_eos_goodness(curvedata['evcurve'][key])
        goodness[id][key]=np.sqrt(np.diag(pcov))
        pdb.set_trace()
        pass


