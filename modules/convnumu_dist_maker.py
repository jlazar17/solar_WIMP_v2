import numpy as np

from base_dist_maker import BaseDistMaker
from helper_functions import opening_angle
 
class ConvNuMuDistMaker(BaseDistMaker):

    def make_hist(self, rad, zen, az):
        reco_gamma = opening_angle(self.mc.reco_zen, self.mc.reco_az, zen, az)

        if len(self.bins)==2:
            h = np.histogram2d(np.cos(reco_gamma), self.mc.reco_e, bins=self.bins, weights=self.flux*self.mc.oneweight)
        elif len(self.bins)==3:
            data = np.array([np.cos(reco_gamma), self.mc.reco_e, self.mc.trackprob])
            h    = np.histogramdd(data.T, bins=self.bins, weights=self.flux*self.mc.oneweight)
        return h
