import numpy as np
import argparse

from controls import datadir, dist_calc_params
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
    parser.add_argument('--skip',
                        type=int,
                        default=1
                       )
    
    args = parser.parse_args()
    return args
 
def main(mcpath, fluxtype, options, skip, savedir):
    slc = slice(None, None, skip)
    mc  = MCReader(mcpath, options=options, slc=slc)

    if 'oscNext' in mcpath:
        bins = [dist_calc_params['cdtheta'], dist_calc_params['ee'], dist_calc_params['ptrackk']]
    else:
        bins = [dist_calc_params['cdtheta'], dist_calc_params['ee']]

    if fluxtype=='conv-numu':
        flux = np.load('%s/mc_dn_dz/%s_%s.npy' % (datadir, fluxtype, mc.fname))[slc]
        from bg_dist_maker import BGDistMaker
        gamma = BGDistMaker(mc, flux, bins, fluxtype)
    elif fluxtype=='muon':
        flux = 1
        from bg_dist_maker import BGDistMaker
        gamma = BGDistMaker(mc, flux, bins, fluxtype)
    elif fluxtype=='solar-atm':
        flux = np.load('%s/mc_dn_dz/%s_%s.npy' % (datadir, fluxtype, mc.fname))[slc]
        from solaratm_dist_maker import SolarAtmDistMaker
        gamma = SolarAtmDistMaker(mc, flux, bins, fluxtype)
    else:
        flux = np.load('%s/mc_dn_dz/%s_%s.npy' % (datadir, fluxtype, mc.fname))[slc]
        from signal_dist_maker import SignalDistMaker
        gamma = SignalDistMaker(mc, flux, bins, fluxtype)

    gamma.do_calc()
    h = gamma.gamma_hist*skip
    np.save('%s/%s_%s' % (savedir, fluxtype, mc.fname), h)
    

if __name__=='__main__':
    args=initialize_args()
    main(args.mcpath, args.fluxtype, args.options, args.skip, args.savedir)
