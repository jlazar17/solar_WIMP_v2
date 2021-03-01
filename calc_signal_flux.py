#!/cvmfs/icecube.opensciencegrid.org/py2-v3/RHEL_7_x86_64/bin/python 

import numpy as np
import os, sys, argparse
sys.path.append('/home/jlazar/programs/charon/local/lib/')
sys.path.append('/data/user/jlazar/charon/charon/')
sys.path.append('/data/user/jlazar/solar_WIMP_v2/modules/')

import propa
import charon
from physicsconstants import PhysicsConstants
from controls import charon_params


def initialize_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--flux",
                        type=str,
                        help="Signal flux to be generated, e.g. ch5-m1000",
                        default='ch5-m1000'
                       )
    parser.add_argument("--whichgen",
                        type=str,
                        default='BRW'
                       )
    parser.add_argument('--where',
                       default='1AU'
                      )
    parser.add_argument('-o',
                        dest='outdir',
                        default='/data/user/jlazar/solar_WIMP_v2/data/charon_fluxes/',
                        help='Directory in which to save the output'
                       )
    args = parser.parse_args()
    return args

qr_ch_dict = {5:"bb", 8:"WW", 11:"tautau"}
ws_cn_dict = {"bb":5, "WW":8, "tautau":11}

class FluxCalculator():
    
    def __init__(self, ch, m, where, gen):
        self.ch    = ch
        self.m     = m
        self.where = where
        self.gen   = gen
        self.evolved_flux = None

    def calc_flux(self):
        if self.gen=='BRW':
            flux = propa.NuFlux(qr_ch_dict[self.ch], self.m, **charon_params)
            #flux = propa.NuFlux(qr_ch_dict[self.ch], self.m, nodes, Emin=e_min, Emax=self.m, bins=nodes,
            #                     process='ann', theta_12=theta_12, theta_13=theta_13, 
            #                     theta_23=theta_23, delta=delta, delta_m_12=delta_m_12, 
            #                     delta_m_13=delta_m_13, interactions=True)
        elif self.gen=='pythia':
            flux = propa.NuFlux(qr_ch_dict[self.ch], self.m, nodes, Emin=e_min, Emax=self.m, bins=nodes,
                                 process='ann', theta_12=theta_12, theta_13=theta_13, 
                                 theta_23=theta_23, delta=delta, delta_m_12=delta_m_12, 
                                 delta_m_13=delta_m_13, interactions=True, pathFlux='/data/user/qliu/DM/DMFlux/Pythia/no_EW/Sun/results/%s_%d_Sun.dat' % (ch_dict[ch], m))
        else:
            print('Generator %s not supported. Must be "BRW" or "pythia"')
            quit()
        evolved_flux = flux.Sun(self.where)
        self.evolved_flux = evolved_flux
        return evolved_flux

if __name__=="__main__":
    args = initialize_args()
    ch   = int(args.flux.split('-')[0][2:])
    m    = int(args.flux.split('-')[1][1:])
    fc   = FluxCalculator(ch, m, args.where, args.whichgen)
    flux = fc.calc_flux()
    np.save('%s/%s_%s_%s' % (args.outdir, args.flux, args.where, args.whichgen), flux)
    
