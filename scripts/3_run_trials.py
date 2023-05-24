import numpy as np
import h5py as h5
import os
import pickle as pkl

from scipy.optimize import differential_evolution
from tqdm import tqdm
from typing import List

from solar_common.event_reader import Selection
from solar_common.utils import (
    oscnext_yearmaker,
    ps_yearmaker,
    prepare_data_distribution,
    prepare_simulation_distribution
)
from solar_common.sensitivity.poisson_nllh import poisson_nllh

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
        "--resfile",
        type=str,
        required=True
    )
    parser.add_argument(
        "--deltafile",
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
        default=10000,
        type=int
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

def run_trials(
    nominal_signal: np.ndarray,
    nominal_background: np.ndarray,
    signal_norm: float,
    seed,
    n_realizations: int=10_000,
):
    if nominal_signal.shape!=nominal_background.shape:
        raise ValueError("Signal and background shapes don't match")
    true_model = signal_norm * nominal_signal + nominal_background
    realizations = np.zeros((n_realizations, ) + true_model.shape)
    np.random.seed(seed)
    for idx in range(n_realizations):
        realizations[idx, ...] = np.random.poisson(lam=true_model)
    # This line is dirt...
    #arr = realizations.reshape(-1, realizations.shape[0]).sum(axis=0)
    signal_results = []
    null_results = []
    deltas = []
    for idx in tqdm(range(n_realizations)):
        data = realizations[idx, ...]
        f_signal = lambda x: poisson_nllh(data, nominal_background + np.exp(x) * nominal_signal)
        #~f_signal = lambda x: poisson_nllh(data, np.exp(x[0]) * background + np.exp(x[1]) * nominal_signal)
        sres = differential_evolution(f_signal, [(-10, 10)])
        signal_results.append(sres)
        #f_null = lambda x: poisson_nllh(data, np.exp(x) * background)
        #nres = differential_evolution(f_null, [(-2, 2)])
        #null_results.append(nres)
        delta_2llh = -2 * (
            poisson_nllh(data, nominal_background + np.exp(sres.x) * nominal_signal) - poisson_nllh(data, nominal_background)
            #poisson_nllh(data, np.exp(sres.x[0]) * nominal_background + np.exp(sres.x[1]) * nominal_signal) - \
            #~poisson_nllh(data, np.exp(nres.x) * nominal_background)
        )
        deltas.append(delta_2llh)
    return signal_results, null_results, np.array(deltas)

def get_fluxenames(sigfile: str) -> List[str]:
    fluxnames = []
    with h5.File(sigfile, "r") as h5f:
        for k in h5f.keys():
            fluxname = "_".join(k.split("_")[:-1])
            if fluxname in fluxnames:
                continue
            fluxnames.append(fluxname)
    return fluxnames

def save_minimization_res(res, pklfile, **kwargs):
    kwargs["res"] = res
    with open(pklfile, "wb") as pkl_f:
        pkl.dump(kwargs, pkl_f)

def save_deltas(deltas, outfile, fluxname, **kwargs):
    with h5.File(outfile, "r+") as h5f:
        h5f.create_dataset(fluxname, data=deltas)
        for k, v in kwargs.items():
            h5f[fluxname].attrs[k] = v
            
def main(sigfile: str, bgfile: str, resfile: str, deltafile: str, seed: int, norm: float, n: int=10_000, fluxname=None):
    """
    Main function

    params
    ______

    returns
    _______
    """
    if not os.path.exists(deltafile):
        with h5.File(deltafile, "w") as _:
            pass

    selection = determine_selection(bgfile)

    livetime = DELTA_T_DICT[selection]
    yearmaker = YEARMAKER_DICT[selection]

    with h5.File(bgfile, "r") as h5f:
        nominal_bg = prepare_data_distribution(h5f, yearmaker)

    fluxnames = get_fluxenames(sigfile)
    if fluxname is not None:
        fluxnames = [fluxname]

    meta_params = {
        "sigfile": sigfile,
        "bgfile": bgfile,
        "seed": seed,
        "norm": norm,
        "n": n
    }
    for fluxname in tqdm(fluxnames):
        with h5.File(sigfile, "r") as h5f:
            nominal_signal = livetime * prepare_simulation_distribution(h5f, fluxname)

        signal_results, null_results, delta = run_trials(
            nominal_signal,
            nominal_bg,
            norm,
            seed,
            n_realizations=n,
        )

        save_minimization_res(
            signal_results,
            resfile.replace(".pkl", f"_{fluxname}.pkl"),
            fluxname=fluxname,
            **meta_params
        )
        save_deltas(delta, deltafile, fluxname, **meta_params)

if __name__=="__main__":
    args = initialize_parser()
    main(args.sigfile, args.bgfile, args.resfile, args.deltafile, args.seed, args.norm, args.n)
