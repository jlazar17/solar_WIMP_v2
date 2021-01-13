from base_dist_maker import BaseDistMaker

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
