import numpy as np

from DM import DMAnnihilationJungmanSD
from base_dist_maker import BaseDistMaker
from helper_functions import opening_angle
from controls import dist_calc_params


class SignalDistMaker(BaseDistMaker):

    def __init__(self, mc, flux, bins, fluxtype):
        BaseDistMaker.__init__(self, mc, flux, bins, fluxtype)
        self.mass = int(self.fluxtype.split('-')[1][1:])
        self.rate = DMAnnihilationJungmanSD(self.mass, 1.0e-39) # Annihlation rate for xs=1 femtobarn

    def make_hist(self, rad, zen, az):
        solar_solid_angle = 2*np.pi*(1-np.cos(dist_calc_params['r_sun']/rad))
        gamma_cut         = np.arctan(dist_calc_params['r_sun'] / rad)
        zmax              = zen+gamma_cut
        zmin              = zen-gamma_cut
        amax              = az+gamma_cut
        amin              = az-gamma_cut
        m1                = np.logical_and(self.mc.nu_zen>zmin, self.mc.nu_zen<zmax)
        m2                = np.logical_and((self.mc.nu_az>amin%(2*np.pi)), self.mc.nu_az<amax%(2*np.pi))
        m3                = True
        #m3                = self.mc.nu_e<=float(self.mass)
        m12               = np.logical_and(m1, m2)
        m                 = np.logical_and(m12, m3)
        nu_gamma          = opening_angle(self.mc.nu_zen[m], self.mc.nu_az[m], zen, az)
        reco_gamma        = opening_angle(self.mc.reco_zen[m], self.mc.reco_az[m], zen, az)
        
        n = np.where(nu_gamma <= gamma_cut,
                     self.flux[m] *             \
                     self.mc.oneweight[m] *    \
                     (1. / solar_solid_angle) * \
                     (1. / (4*np.pi*np.power(rad, 2))) * \
                     (1. / self.mass) * \
                     self.rate,
                     0
                    )

        if len(self.bins)==2:
            h = np.histogram2d(np.cos(reco_gamma), self.mc.reco_e[m], bins=self.bins, weights=n)
        elif len(self.bins)==3:
            data = np.array([np.cos(reco_gamma), self.mc.reco_e[m], self.mc.trackprob[m]])
            h    = np.histogramdd(data.T, bins=self.bins, weights=n)
        
        return h
