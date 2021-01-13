import numpy as np

import sys
sys.path.append('/data/user/jlazar/solar_WIMP_v2/modules/')

from controls import datadir

def initialize_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mcpath',
                        type=str,
                        help='path to mcpath to be used'
                       )
    parser.add_argument('--fluxtype',
                        type=str,
                        help='fluxtype to be used, e.g. conv-numu or ch5-m1000'
                       )
    args = parser.parse_args()
    return args

def create_mc_fluxmaker(mcpath, fluxtype):
    if fluxtype=='conv-numu':
        from convnumu_mc_fluxmaker import ConvNumuMCFluxMaker
        fluxmaker = ConvNumuMCFluxMaker(mcpath, fluxtype)
    elif fluxtype=='solar-atm':
        from solaratm_mc_fluxmaker import SolarAtmMCFluxMaker
        fluxmaker = SolarAtmMCFluxMaker(mcpath, fluxtype)
    else:
        from signal_mc_fluxmaker import SignalMCFluxMaker
        fluxmaker = SignalMCFluxMaker(mcpath, fluxtype)
    return fluxmaker

def main(mcpath, fluxtype):
    fluxmaker = create_mc_fluxmaker(mcpath, fluxtype)
    fluxmaker.initialize_nuSQuIDS()
    fluxmaker.interp_mc()
    
    mcfname = mcpath.split('/')[-1].split('.')[0]
    np.save('%s/mc_dn_dz/%s_%s' % (datadir, fluxtype, mcfname), fluxmaker.mcflux)

if __name__=='__main__':
    args      = initialize_args()
    main(args.mcpath, args.fluxtype)
