import time
t0 = time.time()
import numpy as np
import solar_position_calc as sc
from controls import *
from path_gen import PathGen
from os import path
import argparse
import weight_MC as wmc
from mc_reader import MCReader
import h5py
import gen_rescale_az_zen as gaz

def initialize_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mcfile',
                        type=str,
                        help='path to mcfile to be used'
                       )
    parser.add_argument('--fluxtype',
                        type=str,
                        help='fluxtype to be used, e.g. conv-numu or ch5-m1000'
                       )
    parser.add_argument('--options',
                        type=str,
                        default='00'
                       )
    parser.add_argument('--test',
                        action='store_true',
                        default=False
                       )
    
    args = parser.parse_args()
    return args


class BaseGamma():

    def __init__(self, mcpath, fluxtype, options, _skip, _test=False):

        self.mcpath     = mcpath
        self.fluxtype   = fluxtype
        self.options    = options
        self._skip      = _skip
        self._test      = _test
        if 'oscNext' in mcpath:
            self.e_bins = le_e_bins
        else:
            self.e_bins = e_bins
        self.gamma_hist = None
        self.slc        = slice(None, None, _skip)
        self.mcfg       = PathGen(self.mcpath)
        self._seed      = abs(hash(self.mcfg.get_mc_dn_dz_path(self.fluxtype))) % (2**32)
        self.mcr        = MCReader(self.mcpath, self.slc, options=options)
        self.flux       = self.load_flux()

    def make_hist(self):
        pass

    def load_flux(self):
        return np.load(self.mcfg.get_mc_dn_dz_path(self.fluxtype))[self.slc]

    def save_hist(self):
        if self.gamma_hist is None:
            print('Gamma hist is not yet defined. Did not save')
        else:
            if self._test:
                np.save('%s_%s_test' % (self.mcfg.get_e_d_theta_path(self.fluxtype), self.options), self.gamma_hist)
            else:
                np.save('%s_%s' % (self.mcfg.get_e_d_theta_path(self.fluxtype), self.options), self.gamma_hist)

    def do_calc(self):
        hist = np.zeros((len(gamma_bins)-1, len(self.e_bins)-1))
        for i, jd in enumerate(jds):
            x = sc.nParameter(jd)
            obl = sc.solarObliquity(x)
            L = sc.L(x)
            G = sc.g(x)
            lamb = sc.solarLambda(L,G)
            rad = sc.solarR(G)
            zenith = sc.equatorialZenith(obl, lamb)

            h = self.make_hist(rad, zenith, azimuths[i])
            hist += h[0]
            
        self.gamma_hist = hist*self._skip*delta_t

class SignalGamma(BaseGamma):
        

    def make_hist(self, rad, zen, az):
        solar_solid_angle = 2*np.pi*(1-np.cos(r_sun/rad))
        gamma_cut = np.arctan(r_sun / rad)
        zmax      = zen+gamma_cut
        zmin      = zen-gamma_cut
        amax      = az+gamma_cut
        amin      = az-gamma_cut
        m1        = np.logical_and(self.mcr.nu_zen>zmin, self.mcr.nu_zen<zmax)
        m2        = np.logical_and((self.mcr.nu_az>amin%(2*np.pi)), self.mcr.nu_az<amax%(2*np.pi))
        m3        = self.mcr.nu_e<=float(self.fluxtype.split('-')[-1][1:])
        m12       = np.logical_and(m1, m2)
        m         = np.logical_and(m12, m3)
        nu_gamma  = gaz.opening_angle(self.mcr.nu_zen[m], self.mcr.nu_az[m], zen, az)
        reco_gamma = gaz.opening_angle(self.mcr.reco_zen[m], self.mcr.reco_az[m], zen, az)
        n = np.where(nu_gamma <= gamma_cut,
                     self.flux[m] *             \
                     self.mcr.oneweight[m] *    \
                     (1. / solar_solid_angle) * \
                     (1. / (4*np.pi*np.power(rad, 2))),
                     0
                    )
        h = np.histogram2d(reco_gamma, self.mcr.reco_e[m], bins=[gamma_bins, self.e_bins], weights=n)
        
        return h
class SolarAtmGamma(BaseGamma):
        

    def make_hist(self, rad, zen, az):
        solar_solid_angle = 2*np.pi*(1-np.cos(r_sun/rad))
        gamma_cut = np.arctan(r_sun / rad)
        zmax      = zen+gamma_cut
        zmin      = zen-gamma_cut
        amax      = az+gamma_cut
        amin      = az-gamma_cut
        m1        = np.logical_and(self.mcr.nu_zen>zmin, self.mcr.nu_zen<zmax)
        m2        = np.logical_and((self.mcr.nu_az>amin%(2*np.pi)), self.mcr.nu_az<amax%(2*np.pi))
        m         = np.logical_and(m1, m2)
        nu_gamma  = gaz.opening_angle(self.mcr.nu_zen[m], self.mcr.nu_az[m], zen, az)
        reco_gamma = gaz.opening_angle(self.mcr.reco_zen[m], self.mcr.reco_az[m], zen, az)
        n = np.where(nu_gamma <= gamma_cut,
                     self.flux[m] *             \
                     self.mcr.oneweight[m],
                     0
                    )
        h = np.histogram2d(reco_gamma, self.mcr.reco_e[m], bins=[gamma_bins, self.e_bins], weights=n)
        
        return h

class ConvNuMuGamma(BaseGamma):

    def make_hist(self, rad, zen, az):
        reco_gamma = gaz.opening_angle(self.mcr.reco_zen, self.mcr.reco_az, zen, az)
        h = np.histogram2d(reco_gamma, self.mcr.reco_e, bins=[gamma_bins, self.e_bins], weights=self.flux*self.mcr.oneweight)
        return h


 
 
def main(mcpath, fluxtype, options, _skip, _test):
    if fluxtype=='conv-numu':
        gamma = ConvNuMuGamma(mcpath, fluxtype, options, _skip=_skip, _test=_test)
    elif fluxtype=='solar-atm':
        gamma = SolarAtmGamma(mcpath, fluxtype, options, _skip=_skip, _test=_test)
    else:
        gamma = SignalGamma(mcpath, fluxtype, options, _skip=_skip, _test=_test)
    print('doing calc')
    gamma.do_calc()
    gamma.save_hist()

if __name__=='__main__':
    args=initialize_args()
    if args.test:
        print('testing')
    else:
        print('not testing')
    main(args.mcfile, args.fluxtype, args.options, 1, args.test)
