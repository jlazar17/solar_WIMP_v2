import os
import h5py as h5
from glob import glob
from tqdm import tqdm

from solar_common.event_reader import Selection, DataType, event_reader_from_file
from solar_common.flux import SolarAtmSurfaceFlux

def determine_selection(datafile: str) -> Selection:
    # This is jank but I don't have an alternative at present :-)
    # Only the point source uses numpy files
    if datafile.endswith(".npy"):
        return Selection.POINTSOURCE
    elif "oscnext" in datafile.lower() and datafile.endswith(".h5"):
        return Selection.OSCNEXT
    raise ValueError("Unable to determine which selection {datafile} belongs to")

def main(mcfile: str, fluxfile: str, outfile: str, force :bool=False) -> None:
    """Writes an h5 file with all available solar atmospheric fluxes

    params
    ______
    mcfile: mcfile for which to calculate fluxes
    fluxfile: file with tabulated flux data
    outfile: h5file to put all the fluxes in
    force: If True, all fluxes will be recaluclated even if extant
    """
    selection = determine_selection(mcfile)
    events = event_reader_from_file(mcfile, selection, DataType.MC)
    
    openchar = "w"
    if os.path.exists(outfile):
        openchar = "r+"

    with h5.File(outfile, openchar) as h5f:
        
        desc = fluxfile.split("/")[-1].replace(".txt", "")
        if desc in h5f.keys() and not force:
            return
        flux = SolarAtmSurfaceFlux(fluxfile)
        mcflux = flux.to_event_flux(events)
        if desc not in h5f.keys():
            h5f.create_dataset(desc, data=mcflux.flux)
        h5f[desc][:] = mcflux.flux
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
        "--fluxfile",
        dest="fluxfile",
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
    main(args.mcfile, args.fluxfile, args.outfile, force=args.f)
