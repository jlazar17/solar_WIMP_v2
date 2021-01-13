import numpy as np

from mc_reader import MCReader
from base_mc_fluxmaker import BaseMCFluxMaker
from controls import datadir, conv_numu_params, units

class ConvNumuMCFluxMaker(BaseMCFluxMaker):

    def _make_initial_data(self):
        surface_flux_file = np.load('%s/sibyll23c_conv.npy' % (datadir))
        czens             = conv_numu_params['czz']
        energies          = conv_numu_params['ee']
        
        step         = len(energies)
        initial_flux = np.zeros((len(czens), len(energies), 2, 3), dtype=float)
        for ic in range(len(czens)):
            initial_flux[ic,:,0,0] = surface_flux_file[:,2][step*ic:step*(ic+1)]
            initial_flux[ic,:,1,0] = surface_flux_file[:,3][step*ic:step*(ic+1)]
            initial_flux[ic,:,0,1] = surface_flux_file[:,4][step*ic:step*(ic+1)]
            initial_flux[ic,:,1,1] = surface_flux_file[:,5][step*ic:step*(ic+1)]
            initial_flux[ic,:,0,2] = 0.0
            initial_flux[ic,:,1,2] = 0.0
        del surface_flux_file

        return czens, energies, initial_flux

    def get_flux(self, cz, e, ptype):
        if e>1e6:
            return 0.0
        elif ptype==12:
            return self.nsq_atm.EvalFlavor(0, cz, e*units.GeV, 0)
        elif ptype==-12:
            return self.nsq_atm.EvalFlavor(0, cz, e*units.GeV, 1)
        elif ptype==14:
            return self.nsq_atm.EvalFlavor(1, cz, e*units.GeV, 0)
        elif ptype==-14:
            return self.nsq_atm.EvalFlavor(1, cz, e*units.GeV, 1)
        elif ptype==16:
            return self.nsq_atm.EvalFlavor(2, cz, e*units.GeV, 0)
        elif ptype==-16:
            return self.nsq_atm.EvalFlavor(2, cz, e*units.GeV, 1)
        else:
            print('wrong ptype doggo')
            return 0
