import numpy as np

from base_mc_fluxmaker import BaseMCFluxmaker
from controls import datadir

class ConvNumuMCFluxMaker(BaseMCFluxMaker):

    def _make_initial_data(self):
        surface_flux_file = np.genfromtxt('%s/AIRS_flux_sib_HG.dat' % (datadir))
        czens             = surface_flux_file[:,0][::350]
        energies          = surface_flux_file[:,1][:350]
        
        initial_flux = np.zeros((len(czens), len(energies), 2, 3), dtype=float)
        for ic in range(len(czens)):
            initial_flux[ic,:,0,0] = surface_flux_file[:,2][350*ic:350*(ic+1)]
            initial_flux[ic,:,1,0] = surface_flux_file[:,3][350*ic:350*(ic+1)]
            initial_flux[ic,:,0,1] = surface_flux_file[:,4][350*ic:350*(ic+1)]
            initial_flux[ic,:,1,1] = surface_flux_file[:,5][350*ic:350*(ic+1)]
            initial_flux[ic,:,0,2] = 0.0
            initial_flux[ic,:,1,2] = 0.0
        del surface_flux_file

        return czens, energies, initial_flux

    def get_flux(self, cz, e, ptype):
        if e>1e6:
            print('returning 0 cuz of energy')
            return 0.0
        elif cz>0.2:
            print('returning 0 cuz of zenith')
            return 0.0
        elif ptype==14:
            return self.nsq_atm.EvalFlavor(1, cz, e*units.GeV, 0)
        elif ptype==-14:
            return self.nsq_atm.EvalFlavor(1, cz, e*units.GeV, 1)
        else:
            print('wrong ptype doggo')
            return 0
