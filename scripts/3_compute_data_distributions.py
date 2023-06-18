import os
import numpy as np
import h5py as h5
from datetime import datetime
from typing import Optional
from tqdm import tqdm

from solar_common import sun, compute_distribution
from solar_common.flux import EventFlux, SkyDistribution
from solar_common.event_reader import EventReader, Selection, DataType, event_reader_from_file

MJDMIN = 56_293 # Jan. 1 2013
MJDMAX = 56_658.25 # Jan. 1 2014 + 0.25 days for stuff

def determine_selection(datafile: str) -> Selection:
    # This is jank but I don't have an alternative at present :-)
    # Only the point source uses numpy files
    if datafile.endswith(".npy"):
        return Selection.POINTSOURCE
    # oscNext uses h5 files as labels them verbosely
    
    elif "oscnext" in datafile.lower():
        return Selection.OSCNEXT
    raise ValueError(f"Unable to determine selection from {datafile}")

def save_output(
    outfile: str,
    key_prefix: str,
    dist: np.ndarray,
    **kwargs
) -> None:
    """Saves output to file at input string. Adds any metadata which may be supplied
    as a kwarg

    params
    ______
    outfile: h5 file to save information to
    key_prefix: where to save the dataset in the file. Integers will be added 
        to make it a unique key each time
    dist: average distribution
    kwargs: key, value pairs to add to the `attrs` of the dataset
    """
    with h5.File(outfile, "r+") as h5f:
        idx = 0
        key = f"{key_prefix}_{idx}"
        while key in h5f.keys():
            idx += 1
            key = f"{key_prefix}_{idx}"
        h5f.create_dataset(key, data=dist)
        for k, v in kwargs.items():
            h5f[key].attrs[k] = v

def main(
    eventsfile: str,
    outfile: str,
    seed: int,
    niter: int,
    scramble: bool
) -> None:
    """Computes the analysis level background distributions from 
    scrambled data in \Delta\psi, E_{reco}, and potentially other variables.
    This can be averaged over an input number of randomizations to
    fill in the distribution
    
    params
    ______
    eventsfile: file containing the data events
    outfile: h5 file where we will store the output
    seed: seed for RNG
    niter: Number of iterations to perform
    scramble: Whether to scramble the reconstructed azimuth
    """
    
    # Make the output file if it doesn't exist
    if not os.path.exists(outfile):
        with h5.File(outfile, "w") as _:
            pass

    selection = determine_selection(eventsfile)
    events = event_reader_from_file(eventsfile, selection, DataType.DATA)
    for _ in tqdm(range(niter)):
        if scramble:
            events.scramble_azimuth(seed=seed)
        dist = compute_distribution(events, sun) 
        save_output(
            outfile,
            eventsfile.split("/")[-1].split(".")[0], 
            dist,
            seed=seed,
            dtstr=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            eventsfile=eventsfile,
            scramble=str(scramble)
        )
        seed += 1

if __name__=="__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        "--eventsfile",
        required=True
    )
    parser.add_argument(
        "--outfile",
        required=True
    )
    parser.add_argument(
        "-s",
        "--seed",
        dest="seed",
        type=int,
        required=True
    )
    parser.add_argument(
        "-n",
        "--niter",
        dest="n",
        default=1,
        type=int
    )
    parser.add_argument(
        "--no_scramble",
        action="store_true",
        default=False
    )
    args = parser.parse_args()
    main(args.eventsfile, args.outfile, args.seed, args.n, not args.no_scramble)
