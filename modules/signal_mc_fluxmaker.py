import numpy as np

from base_mc_fluxmaker import BaseMCFluxmaker
from controls import datadir

class SignalMCFluxMaker(BaseMCFluxMaker):

    def _make_initial_data(self):
        pg       = PathGen(self.mcpath)
        fluxfile = np.load('%s/charon_fluxes/%s_1AU_BRW.npy' % (datadir, self.fluxtype))
            
        czens    = np.linspace(-1, 1, 150)
        energies = fluxfile['Energy']
        print(energies)

        initial_flux = np.zeros((len(czens), len(energies), 2, 3), dtype=float)
        for ic in range(len(czens)):
            initial_flux[ic,:,0,0] = fluxfile['nu_e']
            initial_flux[ic,:,1,0] = fluxfile['nu_e_bar']
            initial_flux[ic,:,0,1] = fluxfile['nu_mu']
            initial_flux[ic,:,1,1] = fluxfile['nu_mu_bar']
            initial_flux[ic,:,0,2] = fluxfile['nu_tau']
            initial_flux[ic,:,1,2] = fluxfile['nu_tau_bar']
        del fluxfile
        return czens, energies, initial_flux

    def get_flux(self, cz, e, ptype):
        m = float(self.fluxtype.split('-')[1][1:])
        if e>m:
            return 0
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
