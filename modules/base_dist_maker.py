import numpy as np

import solar_position_calc as sc
from controls import dist_calc_params

class BaseDistMaker():

    def __init__(self, mc, flux, bins):

        self.mc         = mc
        self.flux       = flux
        self.bins       = bins
        self.gamma_hist = None
        #self._seed      = abs(hash(self.mc.path)) % (2**32)

    def make_hist(self):
        pass

    def do_calc(self):
        hist_shape = tuple([len(b)-1 for b in self.bins])
        hist = np.zeros(hist_shape)
        for az, jd in zip(dist_calc_params['azimuths'], dist_calc_params['jds']):
            x      = sc.nParameter(jd)
            obl    = sc.solarObliquity(x)
            L      = sc.L(x)
            G      = sc.g(x)
            lamb   = sc.solarLambda(L,G)
            rad    = sc.solarR(G)
            zenith = sc.equatorialZenith(obl, lamb)

            h     = self.make_hist(rad, zenith, az)
            hist += h[0]
            
        self.gamma_hist = np.divide(hist, len(dist_calc_params['jds'])) # returns a rate
