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
    Selection.OSCNEXT: 345824815.4500002,
    Selection.POINTSOURCE: 328673673.7984125, # Compute by summing livetime from /data/ana/analyses/northern_tracks/version-005-p01/GRL/IC86_{YEAR}_exp.npy
}

YEARMAKER_DICT = {
    Selection.OSCNEXT: oscnext_yearmaker,
    Selection.POINTSOURCE: ps_yearmaker
}

def initialize_parser():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        "--sigfile",
        nargs="+",
        required=True
    )
    parser.add_argument(
        "--bgfile",
        nargs="+",
        required=True
    )
    parser.add_argument(
        "--solar_bgfile",
        nargs="+",
        required=True
    )
    parser.add_argument(
        "--outfile",
        type=str,
        required=True
    )
    parser.add_argument(
        "-s",
        "--seed",
        dest="seed",
        type=int,
        required=True,
    )
    parser.add_argument(
        "--norm",
        type=float,
        required=True
    )
    parser.add_argument(
        "-n",
        "--n_realizations",
        dest="n",
        default=50_000,
        type=int
    )
    parser.add_argument(
        "--key",
        type=str,
        dest="key"
    )
    parser.add_argument(
        "--solar_atm_model",
        type=str,
        default="SIBYLL2.3_ppMRS_CombinedGHAndHG_H4a"
    )
    args = parser.parse_args()
    return args

def determine_selection(datafile: str) -> Selection:
    # This is jank but I don't have an alternative at present :-)
    # Only the point source uses numpy files
    selection =  Selection.POINTSOURCE
    # oscNext uses h5 files as labels them verbosely
    if datafile.endswith(".h5") and "oscnext" in datafile.lower():
        selection = Selection.OSCNEXT
    return selection

def bg_likelihood(x, data, nominal_atm_bg, nominal_solar_bg, masks):
    nominal_sig = [np.zeros(d.shape) for d in nominal_atm_bg]
    out = sig_likelihood([0, x[0], x[1]], data, nominal_sig, nominal_atm_bg, nominal_solar_bg, masks)
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
        out.append(-poisson_loglikelihood(d[m], x[0] * sig[m] + x[1] * bg[m] + x[2] * sbg[m]))
    return out

def run_trials(
    nominal_sig: List[np.ndarray],
    nominal_atm_bg: List[np.ndarray],
    nominal_solar_bg: List[np.ndarray],
    norm: float,
    nrealizations: int
) -> np.ndarray:
    """
    Function to run an input number of trials for an input signal normalization.
    The true model is assumed to be `norm * nominal_sig + nominal_atm_bg`, i.e.
    the true background normalization will always be one.
    params
    ______
    nominal_sig: array giving mean number of events for nominal signal model
    nominal_atm_bg: array giving the expected number of events for the nominal
    background model
    norm: normalization by which to scale the nominal signal model
    nrealizations: number of pseudo experiments to do

    returns
    _______
    res: numpy array with shape (nrealizations, 4). The columns are the signal and
    background normalizations for the signal fit, the background normalization
    from the bg only fit, and 2 * (llh_{sig + bg} - llh_{bg})
    """
    
    res = np.empty((nrealizations, 6))
                                                                                                            
    masks = [bg > 0 for bg in nominal_atm_bg]
    true_model = [
        norm * sig + bg + sbg for sig, bg, sbg in zip(nominal_sig, nominal_atm_bg, nominal_solar_bg)
    ]

    for idx in tqdm(range(nrealizations)):

        data = []
        for model in true_model:
            data.append(np.random.poisson(lam=model))
                                                                                                                                                            
        g = lambda x: np.sum([
            x.sum() for x in bg_likelihood(x, data, nominal_atm_bg, nominal_solar_bg, masks)
        ])
        f = lambda x: np.sum([
            x.sum() for x in sig_likelihood(x, data, nominal_sig, nominal_atm_bg, nominal_solar_bg, masks)
        ])
        fitg = minimize(g, [1, 1], bounds=[(0.99, 1.01), (0.0, 5)], tol=1e-20)
            
        fitf = minimize(f, [0.5, fitg.x[0], fitg.x[1]], bounds=[(0, 100), (0.99, 1.01), (0.0, 5)], tol=1e-20)
        #fitg = minimize(g, [1, 1], bounds=[(0.99, 1.01), (0.)], tol=1e-20)

        #fitf = minimize(f, [0.5, fitg.x[0]], bounds=[(0, 30), (0.99, 1.01)], tol=1e-20)

                                                                                                                                                                                                                                        
        we = [
            (x-y).sum() for x, y in zip(
                sig_likelihood(fitf.x, data, nominal_sig, nominal_atm_bg, nominal_solar_bg, masks),
                bg_likelihood(fitg.x, data, nominal_atm_bg, nominal_solar_bg, masks),
            )
        ]
        delta = -2 * np.sum(we)
        res[idx, 0] = fitf.x[0]
        res[idx, 1] = fitf.x[1]
        res[idx, 2] = fitf.x[2]
        res[idx, 3] = fitg.x[0]
        res[idx, 4] = fitg.x[1]
        res[idx, 5] = delta
        if idx % 100 ==99:
            print(np.quantile(res[:idx, 0], [0.16, 0.5, 0.84]))
            print(np.quantile(res[:idx, 5], [0.5, 0.9]))
    return res

def save_deltas(deltas, outfile, fluxname, **kwargs) -> None:
    n = 0
    key = f"{fluxname}_{n}"
    with h5.File(outfile, "r+") as h5f:
        while key in h5f.keys():
            n += 1
            key = f"{fluxname}_{n}"
        h5f.create_dataset(key, data=deltas)
        for k, v in kwargs.items():
            h5f[key].attrs[k] = v
            
def main(
    sigfile: str,
    bgfile: str,
    solar_bgfile: str,
    outfile: str,
    seed: int,
    norm: float,
    n: int,
    fluxname: str,
    solar_atm_model: str
):
    """
    Main function

    params
    ______
    sigfile: path to h5 file where nominal signal analysis distributions are
        stored
    bgfile: path to h5 file where nominal background analysis distributions are
        stored
    outfile: path to h5 file where we store minimization results
    seed: seed for random number generation
    norm: normalization to scale nominal signal by
    n: number of realizations
    fluxname: list of flux names to use as nominal signal. If left as
        `None`, the procedure will be done for all fluxes in `sigfile`
    """
    if not os.path.exists(outfile):
        with h5.File(outfile, "w") as _:
            pass

    nominal_atm_bg = []
    for f in bgfile:
        selection = determine_selection(f)
        yearmaker = YEARMAKER_DICT[selection]
        with h5.File(f, "r") as h5f:
            nominal_atm_bg.append(prepare_data_distribution(h5f, yearmaker))

    nominal_sig = []
    for f in sigfile:
        print(f)
        selection = determine_selection(f)
        livetime = DELTA_T_DICT[selection]
        with h5.File(f, "r") as h5f:
            nominal_sig.append(livetime * prepare_simulation_distribution(h5f, fluxname))

    nominal_solar_bg = []
    for f in solar_bgfile:
        selection = determine_selection(f)
        livetime = DELTA_T_DICT[selection]
        with h5.File(f, "r") as h5f:
            nominal_solar_bg.append(livetime * prepare_simulation_distribution(h5f, solar_atm_model))

    meta_params = {
        "sigfile": sigfile,
        "bgfile": bgfile,
        "seed": seed,
        "norm": norm,
        "n": n
    }

    np.random.seed(seed)
    res = run_trials(nominal_sig, nominal_atm_bg, nominal_solar_bg, norm, n)
    save_deltas(res, outfile, fluxname, **meta_params)

if __name__=="__main__":
    args = initialize_parser()
    main(
        args.sigfile,
        args.bgfile,
        args.solar_bgfile,
        args.outfile,
        args.seed,
        args.norm,
        args.n,
        args.key,
        args.solar_atm_model
    )
