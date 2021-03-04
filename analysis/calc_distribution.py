import numpy as np
import argparse

import sys
sys.path.append('/data/user/jlazar/solar_WIMP_v2/modules/')
sys.path.append('/data/user/jlazar/charon/charon/')

from controls import datadir, dist_calc_params
from helper_functions import mc_fname
from mc_reader import MCReader

def initialize_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mcpath',
                        type=str,
                        help='path to mcfile to be used'
                       )
    parser.add_argument('--fluxtype',
                        type=str,
                        help='fluxtype to be used, e.g. conv-numu or ch5-m1000'
                       )
    parser.add_argument('--savedir',
                        type=str,
                        default='%s/distributions/' % datadir
                       )
    parser.add_argument('--options',
                        type=str,
                        default='00'
                       )
    parser.add_argument('--emin',
                        type=float,
                        default=0
                       )
    parser.add_argument('--emax',
                        type=float,
                        default=np.inf
                       )
    parser.add_argument('--skip',
                        type=int,
                        default=1
                       )
    
    args = parser.parse_args()
    return args
 
def main(mcpath, fluxtype, skip, savedir, emin=0, emax=np.inf, options='00'):
    # write placeholder files
    if emin!=0 or emax!=np.inf:
        np.save('%s/differntials/%s_%s_%s_%f-%f' % (savedir, fluxtype, mc_fname(mcpath), options, emin, emax), [])
    else:
        np.save('%s/%s_%s_%s' % (savedir, fluxtype, mc_fname(mcpath), options), [])

    slc     = slice(None, None, skip)
    flux = np.load('%s/mc_dn_dz/%s_%s.npy' % (datadir, fluxtype, mc_fname(mcpath)))
    mc      = MCReader(mcpath, flux=flux, slc=slc, emin=emin, emax=emax, options=options)
    

    if 'oscNext' in mcpath:
        bins = [dist_calc_params['cdtheta'], dist_calc_params['ee'], dist_calc_params['ptrackk']]
    else:
        bins = [dist_calc_params['cdtheta'], dist_calc_params['ee']]

    if fluxtype=='conv-numu':
        from bg_dist_maker import BGDistMaker
        gamma = BGDistMaker(mc, flux, bins, fluxtype)
    elif fluxtype=='muon':
        from bg_dist_maker import BGDistMaker
        gamma = BGDistMaker(mc, flux, bins, fluxtype)
    elif fluxtype=='solar-atm':
        from solaratm_dist_maker import SolarAtmDistMaker
        gamma = SolarAtmDistMaker(mc, flux, bins, fluxtype)
    else:
        from signal_dist_maker import SignalDistMaker
        gamma = SignalDistMaker(mc, flux, bins, fluxtype)

    gamma.do_calc()
    h = gamma.gamma_hist*skip
    if emin!=0 or emax!=np.inf:
        np.save('%s/differntials/%s_%s_%s_%f-%f' % (savedir, fluxtype, mc.fname, options, emin, emax), h)
    else:
        np.save('%s/%s_%s_%s' % (savedir, fluxtype, mc.fname, options), h)
    

if __name__=='__main__':
    args=initialize_args()
    main(args.mcpath, args.fluxtype, args.skip, args.savedir, emin=args.emin, emax=args.emax, options=args.options, )
