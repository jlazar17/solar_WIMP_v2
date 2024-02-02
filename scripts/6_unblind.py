import numpy as np
import h5py as h5
import os
import pickle as pkl

from scipy.optimize import minimize
from tqdm import tqdm
from typing import List

from solar_common.event_reader import Selection
from solar_common.utils import (
    oscnext_yearmaker,
    ps_yearmaker,
    prepare_data_distribution,
    prepare_simulation_distribution
)
from solar_common.sensitivity.poisson_nllh import poisson_loglikelihood

DELTA_T_DICT = {
    Selection.OSCNEXT: 308_056_760.53081256,
    Selection.POINTSOURCE: 328673673.7984125, # Compute by summing livetime from /data/ana/analyses/northern_tracks/version-005-p01/GRL/IC86_{YEAR}_exp.npy
}

def bg_likelihood(x, data, nominal_atm_bg, nominal_solar_bg, masks, sig_norm=0.0):
    nominal_sig = [np.zeros(d.shape) for d in nominal_atm_bg]
    out = sig_likelihood([sig_norm, x[0], x[1]], data, nominal_sig, nominal_atm_bg, nominal_solar_bg, masks)
    return out

def sig_likelihood(
    x: np.ndarray,
    data: List[np.ndarray],
    nominal_sig: List[np.ndarray],
    nominal_atm_bg: List[np.ndarray],
    nominal_solar_bg: List[np.ndarray],
    masks: List[np.ndarray]
):
    out = []
    for d, sig, bg, sbg, m in zip(data, nominal_sig, nominal_atm_bg, nominal_solar_bg, masks):
        model = x[0] * sig[m] + x[1] * bg[m] + x[2] * sbg[m]
        #print(x)
        #print(model.shape, d[m].shape)
        #print(d[m][model==0])
        #print(sig[m][model==0])
        out.append(-poisson_loglikelihood(d[m], model))
    return out

def run_fit(
    nominal_sig: List[np.ndarray],
    nominal_atm_bg: List[np.ndarray],
    nominal_solar_bg: List[np.ndarray],
    data: List[np.ndarray]
) -> np.ndarray:
    
    masks = [
        sol_bg + iso_bg > 0 for sol_bg, iso_bg in zip(nominal_solar_bg, nominal_atm_bg)
    ]
    HACK = 1e-10
    g = lambda x: np.sum([
        x.sum() for x in bg_likelihood(x, data, nominal_atm_bg, nominal_solar_bg, masks, sig_norm=HACK)
    ])
    f = lambda x: np.sum([
        x.sum() for x in sig_likelihood(x, data, nominal_sig, nominal_atm_bg, nominal_solar_bg, masks)
    ])
    fitg = minimize(g, [1, 1], bounds=[(0.99, 1.01), (HACK, 5)], tol=1e-20)
        
    fitf = minimize(f, [1.5, fitg.x[0], fitg.x[1]], bounds=[(HACK, 100), (0.99, 1.01), (HACK, 5)], tol=1e-20)

    we = [
        (x-y).sum() for x, y in zip(
            sig_likelihood(fitf.x, data, nominal_sig, nominal_atm_bg, nominal_solar_bg, masks),
            bg_likelihood(fitg.x, data, nominal_atm_bg, nominal_solar_bg, masks),
        )
    ]
    delta = -2 * np.sum(we)
    return delta, fitg, fitf
