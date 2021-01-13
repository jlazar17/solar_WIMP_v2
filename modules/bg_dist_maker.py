import numpy as np

from base_dist_maker import BaseDistMaker
from helper_functions import opening_angle
 
class BGDistMaker(BaseDistMaker):

    def make_hist(self, rad, zen, az):
        reco_gamma = opening_angle(self.mc.reco_zen, self.mc.reco_az, zen, az)
        if self.fluxtype=='conv-numu':
            weights = self.flux*self.mc.oneweight
        elif self.fluxtype=='muon':
            weights = self.mc.rweight
        else:
            print("You shouldn't be here")

        if len(self.bins)==2:
            h = np.histogram2d(np.cos(reco_gamma), self.mc.reco_e, bins=self.bins, weights=weights)
        elif len(self.bins)==3:
            data = np.array([np.cos(reco_gamma), self.mc.reco_e, self.mc.trackprob])
            h    = np.histogramdd(data.T, bins=self.bins, weights=weights)
        return h
