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
    Selection.OSCNEXT: 11 * 10**7.5,
    Selection.POINTSOURCE: 11 * 10**7.5,
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
        type=str,
        required=True
    )
    parser.add_argument(
        "--bgfile",
        type=str,
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
        nargs="+",
        dest="key"
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

#def run_trials(
#    nominal_sig: np.ndarray,
#    nominal_bg: np.ndarray,
#    signal_norm: float,
#    seed,
#    n_realizations: int=10_000,
#):
#    if nominal_sig.shape!=nominal_bg.shape:
#        raise ValueError("Signal and background shapes don't match")
#    true_model = signal_norm * nominal_sig + nominal_bg
#    realizations = np.zeros((n_realizations, ) + true_model.shape)
#    np.random.seed(seed)
#    for idx in range(n_realizations):
#        realizations[idx, ...] = np.random.poisson(lam=true_model)
#    # This line is dirt...
#    #arr = realizations.reshape(-1, realizations.shape[0]).sum(axis=0)
#    signal_results = []
#    null_results = []
#    deltas = []
#    for idx in tqdm(range(n_realizations)):
#        data = realizations[idx, ...]
#        f_signal = lambda x: poisson_nllh(data, nominal_bg + np.exp(x) * nominal_sig)
#        #~f_signal = lambda x: poisson_nllh(data, np.exp(x[0]) * background + np.exp(x[1]) * nominal_sig)
#        sres = differential_evolution(f_signal, [(-10, 10)])
#        signal_results.append(sres)
#        #f_null = lambda x: poisson_nllh(data, np.exp(x) * background)
#        #nres = differential_evolution(f_null, [(-2, 2)])
#        #null_results.append(nres)
#        delta_2llh = -2 * (
#            poisson_nllh(data, nominal_bg + np.exp(sres.x) * nominal_sig) - poisson_nllh(data, nominal_background)
#            #poisson_nllh(data, np.exp(sres.x[0]) * nominal_bg + np.exp(sres.x[1]) * nominal_sig) - \
#            #~poisson_nllh(data, np.exp(nres.x) * nominal_bg)
#        )
#        deltas.append(delta_2llh)
#    return signal_results, null_results, np.array(deltas)

def run_trials(
    nominal_sig: np.ndarray,
    nominal_bg: np.ndarray,
    norm: float,
    nrealizations: int
) -> np.ndarray:
    """
    Function to run an input number of trials for an input signal normalization.
    The true model is assumed to be `norm * nominal_sig + nominal_bg`, i.e.
    the true background normalization will always be one.

    params
    ______
    nominal_sig: array giving mean number of events for nominal signal model
    nominal_bg: array giving the expected number of events for the nominal
        background model
    norm: normalization by which to scale the nominal signal model
    nrealizations: number of pseudo experiments to do

    returns
    _______
    res: numpy array with shape (nrealizations, 4). The columns are the signal and
        background normalizations for the signal fit, the background normalization
        from the bg only fit, and 2 * (llh_{sig + bg} - llh_{bg})
    """
    mask = nominal_bg > 0
    true_model = norm * nominal_sig + nominal_bg
    res = np.empty((nrealizations, 4))
    
    for idx in tqdm(range(nrealizations)):

        data = np.random.poisson(lam=true_model)

        bg_likelihood = lambda x: -poisson_loglikelihood(data[mask], x * nominal_bg[mask])
        g = lambda x: bg_likelihood(x).sum()
        fitg = minimize(g, [1], bounds=[(0.99, 1.01)], tol=1e-20)

        sig_likelihood = lambda x: -poisson_loglikelihood(data[mask], x[0] * nominal_sig[mask] + x[1] * nominal_bg[mask])
        f = lambda x: sig_likelihood(x).sum()
        fitf = minimize(f, [0.5, fitg.x[0]], bounds=[(0.0, max(10, norm+2)), (0.99, 1.01)], tol=1e-20)

        delta = -2 * (sig_likelihood(fitf.x) - bg_likelihood(fitg.x)).sum()
        res[idx, :2] = fitf.x
        res[idx, 2] = fitg.x
        res[idx, 3] = delta
    return res

def get_fluxenames(sigfile: str) -> List[str]:
    """
    Utility file for finding all signal fluxes contained within
    a signal file

    params
    ______
    sigfile: path to signal file from which to extract fluxes

    returns
    _______
    fluxnames: list of all flux prefixes
    """
    fluxnames = []
    with h5.File(sigfile, "r") as h5f:
        for k in h5f.keys():
            fluxname = "_".join(k.split("_")[:-1])
            if fluxname in fluxnames:
                continue
            fluxnames.append(fluxname)
    return fluxnames

#def save_minimization_res(res, pklfile, **kwargs) -> None:
#    kwargs["res"] = res
#    with open(pklfile, "wb") as pkl_f:
#        pkl.dump(kwargs, pkl_f)

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
    outfile: str,
    seed: int,
    norm: float,
    n: int,
    fluxnames=None
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
    fluxnames: list of flux names to use as nominal signal. If left as
        `None`, the procedure will be done for all fluxes in `sigfile`
    """
    if not os.path.exists(outfile):
        with h5.File(outfile, "w") as _:
            pass

    selection = determine_selection(bgfile)

    livetime = DELTA_T_DICT[selection]
    yearmaker = YEARMAKER_DICT[selection]

    with h5.File(bgfile, "r") as h5f:
        nominal_bg = prepare_data_distribution(h5f, yearmaker)
    mask = nominal_bg > 0

    if fluxnames is None:
        fluxnames = get_fluxenames(sigfile)

    meta_params = {
        "sigfile": sigfile,
        "bgfile": bgfile,
        "seed": seed,
        "norm": norm,
        "n": n
    }

    for fluxname in tqdm(fluxnames):
        np.random.seed(seed)
        with h5.File(sigfile, "r") as h5f:
            nominal_sig = livetime * prepare_simulation_distribution(h5f, fluxname)
        print(f"Expected number of events={norm * nominal_sig.sum()}")
        res = run_trials(nominal_sig, nominal_bg, norm, n)
        print(np.quantile(res[:, 3], [0.5, 0.9]))
        save_deltas(res, outfile, fluxname, **meta_params)

if __name__=="__main__":
    args = initialize_parser()
    main(args.sigfile, args.bgfile, args.outfile, args.seed, args.norm, args.n, fluxnames=args.key)
