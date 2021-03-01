import numpy as np

from base_dist_maker import BaseDistMaker
from helper_functions import opening_angle
from controls import dist_calc_params

class SolarAtmDistMaker(BaseDistMaker):
        

    def make_hist(self, rad, zen, az):
        solar_solid_angle = 2*np.pi*(1-np.cos(dist_calc_params['r_sun']/rad))
        gamma_cut = np.arctan(dist_calc_params['r_sun'] / rad)
        zmax      = zen+gamma_cut
        zmin      = zen-gamma_cut
        amax      = az+gamma_cut
        amin      = az-gamma_cut
        m1        = np.logical_and(self.mc.nu_zen>zmin, self.mc.nu_zen<zmax)
        m2        = np.logical_and((self.mc.nu_az>amin%(2*np.pi)), self.mc.nu_az<amax%(2*np.pi))
        m         = np.logical_and(m1, m2)
        nu_gamma  = opening_angle(self.mc.nu_zen[m], self.mc.nu_az[m], zen, az)
        reco_gamma = opening_angle(self.mc.reco_zen[m], self.mc.reco_az[m], zen, az)
        n = np.where(nu_gamma <= gamma_cut,
                     self.flux[m] *             \
                     self.mc.oneweight[m],
                     0
                    )
        if len(self.bins)==2:
            h = np.histogram2d(np.cos(reco_gamma), self.mc.reco_e[m], bins=self.bins, weights=n)
        elif len(self.bins)==3:
            data = np.array([np.cos(reco_gamma), self.mc.reco_e[m], self.mc.trackprob[m]])
            h    = np.histogramdd(data.T, bins=self.bins, weights=n)
        
        return h
