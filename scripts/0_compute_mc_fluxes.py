import os
import h5py as h5
from glob import glob
from tqdm import tqdm

from solar_atmospherics.solar_common.event_reader import Selection, DataType, event_reader_from_file
from solar_atmospherics.solar_common.flux import SolarAtmSurfaceFlux

def determine_selection(datafile: str) -> Selection:
    # This is jank but I don't have an alternative at present :-)
    # Only the point source uses numpy files
    if datafile.endswith(".npy"):
        return Selection.POINTSOURCE
    # oscNext uses h5 files as labels them verbosely
    elif datafile.endswith(".hdf5"):
        return Selection.OSCNEXT

def main(mcfile: str, outfile: str, force :bool=False) -> None:
    """Writes an h5 file with all available solar atmospheric fluxes

    params
    ______
    mcfile: mcfile for which to calculate fluxes
    outfile: h5file to put all the fluxes in
    force: If True, all fluxes will be recaluclated even if extant
    """
    selection = determine_selection(mcfile)
    events = event_reader_from_file(mcfile, selection, DataType.MC)
    fs = sorted(glob(
        "/data//user/jlazar/solar/solar_WIMP_v2/data/solar_atm/PostPropagation/*"
    ))
    
    if os.path.exists(outfile):
        openchar = "r+"
    else:
        openchar = "w"
    with h5.File(outfile, openchar) as h5f:
        
        for nufile, nubarfile in tqdm(zip(fs[0::2], fs[1::2])):
            desc = nufile.split("/")[-1].replace("_nu.txt", "")
            if desc in h5f.keys() and not force:
                continue
            flux = SolarAtmSurfaceFlux(nufile, nubarfile)
            mcflux = flux.to_event_flux(events)
            if desc in h5f.keys():
                h5f[desc][:] = mcflux.flux
            else:
                h5f.create_dataset(desc, data=mcflux.flux)
            h5f[desc].attrs["Distribution"] = mcflux.distribution.name
            h5f[desc].attrs["MC File"] = mcfile

if __name__=="__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        "--mcfile",
        dest="mcfile",
        required=True
    )
    parser.add_argument(
        "--outfile",
        dest="outfile",
        required=True
    )
    parser.add_argument(
        "-f",
        "--force",
        dest="f",
        action='store_true',
        default=False
    )
    args = parser.parse_args()
    main(args.mcfile, args.outfile, force=args.f)
