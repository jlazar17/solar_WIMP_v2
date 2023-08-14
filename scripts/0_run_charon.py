#!/cvmfs/icecube.opensciencegrid.org/py2-v3/RHEL_7_x86_64/bin/python 

import numpy as np

from charon.propa import NuFlux
from charon.DM import DMAnnihilationJungmanSD

qr_channel_dict = {5:"bb", 8:"WW", 11:"tautau"}
SOLAR_SPHERE_SURFACE = 4 * np.pi * 1.495978707e13**2 * 1e-4 # m
CHARON_KWARGS = {
    "theta_13": 33.44,
    "theta_12": 49.0,
    "theta_23": 8.57,
    "delta_m_12": 7.42e-5,
    "delta_m_13": 2.514e-3,
    "delta": 195.0,
    "process": 'ann',
    "nodes": 200,
    "bins": 200,
    "Emin": 1.0,
    "interactions": True,
    "logscale":  True
}

def initialize_args():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        "--channel",
        dest="channel",
        type=int,
        required=True
    )
    parser.add_argument(
        "-m",
        "--mass",
        dest="mass",
        type=float,
        required=True
    )
    parser.add_argument(
        "-o",
        "--outfile",
        dest="outfile",
        required=True,
        type=str
    )
    args = parser.parse_args()
    return args

def calc_flux(channel: int, mass: float) -> np.recarray:
    prop_distance = "1AU"
    flux = NuFlux(qr_channel_dict[channel], mass, **CHARON_KWARGS)
    evolved_flux = flux.Sun(prop_distance)
    return evolved_flux

def main(channel: int, mass: float, outfile: str):
    flux = calc_flux(channel, mass)
    outarr = np.empty(
        flux.shape + (7,)
    )
    ref_rate = DMAnnihilationJungmanSD(mass, 1e-40)
    outarr[:, 0] = flux["Energy"]
    # Sorry about this dividing thing...
    outarr[:, 1] = flux["nu_e"] / mass * ref_rate / SOLAR_SPHERE_SURFACE
    outarr[:, 2] = flux["nu_e_bar"] / mass * ref_rate / SOLAR_SPHERE_SURFACE
    outarr[:, 3] = flux["nu_mu"] / mass * ref_rate / SOLAR_SPHERE_SURFACE
    outarr[:, 4] = flux["nu_mu_bar"] / mass * ref_rate / SOLAR_SPHERE_SURFACE
    outarr[:, 5] = flux["nu_tau"] / mass * ref_rate / SOLAR_SPHERE_SURFACE
    outarr[:, 6] = flux["nu_tau_bar"] / mass * ref_rate / SOLAR_SPHERE_SURFACE
    np.savetxt(outfile, outarr)

if __name__=="__main__":
    args = initialize_args()
    main(args.channel, args.mass, args.outfile)
