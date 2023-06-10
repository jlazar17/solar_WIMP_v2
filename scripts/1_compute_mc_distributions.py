import os
import numpy as np
import h5py as h5

from tqdm import tqdm
from typing import Iterable, Optional, Union
from datetime import datetime

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
    elif datafile.endswith(".h5") and "oscnext" in datafile.lower():
        return Selection.OSCNEXT
    raise ValueError(f"Could not determine selection from {datafile}")

def get_event_flux(fluxfile: str, key: str) -> EventFlux:
    """Makes EventFlux object input h5 file name where fluxes are stored
    and a given key

    params
    ______
    fluxfile: h5file where fluxes are stored
    key: Name of the field in h5 file where flux and metadata are stored

    returns
    _______
    event_flux: EventFlux object
    """
    with h5.File(fluxfile, "r") as h5f:
        event_flux = EventFlux(
            h5f[key][:],
            getattr(SkyDistribution, h5f[key].attrs["Distribution"])
        )
    return event_flux

def get_events(fluxfile: str, key: str) -> EventReader:
    """Makes an events reader from metadata of input fluxfile

    params
    ______
    fluxfile: h5file where fluxes are stored
    key: Name of the field in h5 file where flux and metadata are stored

    returns
    _______
    events: EventReader object corresponding to flux
    """
    with h5.File(fluxfile, "r") as h5f:
        eventsfile = h5f[key].attrs["MC File"]
    selection = determine_selection(eventsfile)
    events = event_reader_from_file(eventsfile, selection, DataType.MC)
    return events
    

def save_output(
    outfile: str,
    key_prefix: str,
    average_dist: np.ndarray,
    **kwargs
) -> None:
    """Saves output to file at input string. Adds any metadata which may be supplied
    as a kwarg

    params
    ______
    outfile: h5 file to save information to
    key_prefix: where to save the dataset in the file. Integers will be added 
        to make it a unique key each time
    average_dist: average distribution
    kwargs: key, value pairs to add to the `attrs` of the dataset
    """

    with h5.File(outfile, "r+") as h5f:
        idx = 0
        key = f"{key_prefix}_{idx}"
        while key in h5f.keys():
            idx += 1
            key = f"{key_prefix}_{idx}"
        h5f.create_dataset(key, data=average_dist)
        for k, v in kwargs.items():
            h5f[key].attrs[k] = v

def main(
    fluxfile: str,
    outfile: str,
    seed: int,
    keys: Optional[Union[None, Iterable[str]]] = None,
    mjdmin: Optional[float] = MJDMIN,
    mjdmax: Optional[float] = MJDMAX,
    ndays: Optional[int] = 1_000,
    eventsfile: Optional[Union[None, str]] = None,
    scramble: bool=False
) -> None:
    """Computes the analysis level distributions in \Delta\psi, E_{reco},
    and potentially other variables averaged over an input number
    of days. These days are sampled uniformly from a range which can 
    be optionally specified

    params
    ______
    fluxfile: h5file where fluxes are stored
    outfile: h5 file where we should save the output
    keys: keys from h5file to generate distributions for. If `None`, distributions will be
        generated for all keys
    seed: random number generation seed
    mjdmin: minimum modified Julian date for uiform sampling range
    mjdmax: maximum modified Julian date for uiform sampling range
    eventsfile: mc file for which the flux was generated. If `None`
        this file will be pulled from the fluxfile metadata. This
        is time-consuming though
    """
    # Get the keys from the outfile if not provided
    if keys is None or len(keys)==0:
        with h5.File(fluxfile, "r") as h5f:
            keys = list(h5f.keys())

    # Make the output file if it doesn't exist
    if not os.path.exists(outfile):
        with h5.File(outfile, "w") as _:
            pass

    if eventsfile is not None:
        selection = determine_selection(eventsfile)
        events = event_reader_from_file(eventsfile, selection, DataType.MC)


    # Set the RNG seed
    for key in tqdm(keys):
        if eventsfile is None:
            events = get_events(fluxfile, key)
        if scramble:
            events.scramble_azimuth(seed=seed)
        flux = get_event_flux(fluxfile, key)
        np.random.seed(seed)
        mjds = np.random.uniform(mjdmin, mjdmax, ndays)
        dist = compute_distribution(events, sun, flux=flux, mjds=mjds)
        print(np.sum(dist))
        save_output(
            outfile,
            key, 
            dist,
            ndays=ndays,
            mjdmin=mjdmin,
            mjdmax=mjdmax,
            seed=seed,
            dtstr=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            fluxfile=fluxfile,
            scramble=str(scramble)
        )
        seed += 1

if __name__=="__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        "--fluxfile",
        required=True
    )
    parser.add_argument(
        "--outfile",
        required=True
    )
    parser.add_argument(
        "--seed",
        "-s",
        dest="seed",
        type=int
    )
    parser.add_argument(
        "--keys",
        nargs="+"
    )
    parser.add_argument(
        "--mjdmin",
        default=MJDMIN
    )
    parser.add_argument(
        "--mjdmax",
        default=MJDMAX
    )
    parser.add_argument(
        "-n",
        "--ndays",
        dest="ndays",
        default=1000,
        type=int
    )
    parser.add_argument(
        "--eventsfile",
    )
    parser.add_argument(
        "--scramble",
        action="store_true",
        default=False
    )
    args = parser.parse_args()
    main(
        args.fluxfile,
        args.outfile,
        args.seed,
        keys=args.keys,
        mjdmin=args.mjdmin,
        mjdmax=args.mjdmax,
        ndays=args.ndays,
        eventsfile=args.eventsfile,
        scramble=args.scramble
    )
