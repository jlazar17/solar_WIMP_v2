import numpy as np

from base_mc_fluxmaker import BaseMCFluxmaker
from controls import datadir

class SolarAtmMCFluxMaker(BaseMCFluxMaker):
    
    def _make_initial_data(self):
        pp_HG_nu    = np.genfromtxt('%s/SIBYLL2.3_pp_HillasGaisser_H4a_nu.txt' % datadir)
        pp_HG_nubar = np.genfromtxt('%s/SIBYLL2.3_pp_HillasGaisser_H4a_nubar.txt' % datadir)
        czens       = np.linspace(-1, 1, 150)
        energies    = pp_HG_nu[:,0]
        initial_flux = np.zeros((len(czens), len(energies), 2, 3))

        for ic in range(len(czens)):
            initial_flux[ic,:,0,0] = pp_HG_nu[:,1]
            initial_flux[ic,:,1,0] = pp_HG_nu[:,2]
            initial_flux[ic,:,0,1] = pp_HG_nu[:,3]
            initial_flux[ic,:,1,1] = pp_HG_nubar[:,1]
            initial_flux[ic,:,0,2] = pp_HG_nubar[:,2]
            initial_flux[ic,:,1,2] = pp_HG_nubar[:,3]
        del pp_HG_nu
        del pp_HG_nubar
        return czens, energies, initial_flux

    def get_flux(self, cz, e, ptype):
        if e>1e5:
            return 0.0
        elif cz>0.2:
            return 0.0
        elif ptype==14:
            return self.nsq_atm.EvalFlavor(1, cz, e*units.GeV, 0)
        elif ptype==-14:
            return self.nsq_atm.EvalFlavor(1, cz, e*units.GeV, 1)
        else:
            print('wrong ptype doggo')
            return 0
