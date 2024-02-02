import h5py as h5
import numpy as np
import os

from typing import List
from scipy.optimize import minimize, ridder
from tqdm import tqdm

# My stuff
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
        "--trials_file",
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
        "-n",
        "--n_realizations",
        dest="n",
        default=5_000,
        type=int
    )
    parser.add_argument(
        "--key",
        type=str,
        dest="key",
        required=True
    )
    parser.add_argument(
        "--solar_atm_model",
        type=str,
        default="SIBYLL2.3_ppMRS_CombinedGHAndHG_H4a"
    )
    args = parser.parse_args()
    return args


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
    nrealizations: int,
    bg_ts_90: float
):
    masks = [sol_bg + iso_bg > 0 for sol_bg, iso_bg in zip(nominal_solar_bg, nominal_atm_bg)]
    true_model = [
       bg + sbg for bg, sbg in zip(nominal_atm_bg, nominal_solar_bg)
    ]
    res = np.empty(nrealizations)
    for idx in tqdm(range(nrealizations)):
        data = []
        for model in true_model:
            data.append(np.random.poisson(lam=model))
        g = lambda x: np.sum([
            x.sum() for x in bg_likelihood(x, data, nominal_atm_bg, nominal_solar_bg, masks)
        ])
        fitg = minimize(g, [1, 1], bounds=[(0.99, 1.01), (0.0, 5)], tol=1e-20)
        llh0 = [x.sum() for x in bg_likelihood(fitg.x, data, nominal_atm_bg, nominal_solar_bg, masks)]
        llh1 = lambda lx: [
            x.sum() for x in sig_likelihood(
                [np.exp(lx), fitg.x[0], fitg.x[1]],
                data,
                nominal_sig,
                nominal_atm_bg,
                nominal_solar_bg,
                masks
            )
        ]
        f = lambda lx: np.sum(llh1(lx)) - np.sum(llh0) - bg_ts_90
        
        res[idx] = np.exp(ridder(f, -10, 10))
        if idx % 100==99:
            print(np.quantile(res[:idx], [0.05, 0.16, 0.5, 0.84, 0.95]))
    return res

def main(
    fluxname: str,
    bgfiles: List[str],
    sigfiles: List[str],
    solar_bgfiles: List[str],
    trials_file: str,
    outfile: str,
    nrealizations: int,
    solar_atm_model: str
):

    if not os.path.exists(outfile):
        with h5.File(outfile, "w") as _:
            pass

    with h5.File(trials_file, "r") as h5f:
        print(h5f.keys())
        for key in h5f.keys():
            print(key)
            print("_".join(key.split("_")[:-1]))
            print(fluxname)
            if "_".join(key.split("_")[:-1])!=fluxname:
                continue
            val = h5f[key]
            print(val.attrs.items())
            if val.attrs["norm"]!=0:
                continue

            bg_ts_90 = np.quantile(val[:, 5], 0.9)
    print(bg_ts_90)
    nominal_atm_bg = []
    for f in bgfiles:
        selection = determine_selection(f)
        yearmaker = YEARMAKER_DICT[selection]
        with h5.File(f, "r") as h5f:
            nominal_atm_bg.append(prepare_data_distribution(h5f, yearmaker))

    nominal_sig = []
    for f in sigfiles:
        selection = determine_selection(f)
        livetime = DELTA_T_DICT[selection]
        with h5.File(f, "r") as h5f:
            nominal_sig.append(livetime * prepare_simulation_distribution(h5f, fluxname))

    nominal_solar_bg = []
    for f in solar_bgfiles:
        selection = determine_selection(f)
        livetime = DELTA_T_DICT[selection]
        with h5.File(f, "r") as h5f:
            nominal_solar_bg.append(livetime * prepare_simulation_distribution(h5f, solar_atm_model))

    meta_params = {
        "sigfile": sigfiles,
        "bgfile": bgfiles,
        "seed": args.seed,
        "n": nrealizations
    }

    np.random.seed(args.seed)

    res = run_trials(nominal_sig, nominal_atm_bg, nominal_solar_bg, nrealizations, bg_ts_90)
    save_deltas(res, outfile, fluxname, **meta_params)

if __name__=="__main__":
    args = initialize_parser()
    main(
        args.key,
        args.bgfile,
        args.sigfile,
        args.solar_bgfile,
        args.trials_file,
        args.outfile,
        args.n,
        args.solar_atm_model
    )
