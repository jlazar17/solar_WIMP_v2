import numpy as np

import nuSQUIDSpy as nsq
from mc_reader import MCReader
from controls import units

class BaseMCFluxMaker:

    def __init__(self, mc, fluxtype):
        self.mc   = mc
        self.fluxtype = fluxtype
        self.mcdata   = self.read_mc()
        self.mcflux   = None
        self.nsq_atm  = None

    def read_mc(self):
        mcdata = np.array(zip(self.mc.nu_e,
                              np.cos(self.mc.nu_zen),
                              self.mc.ptype
                             ),
                          dtype=[('NuEnergy', float), 
                                 ('CosNuZenith', float), 
                                 ('PrimaryType', int)
                                ]
                         )
        return mcdata

    def _make_initial_data(self):
        pass

    def initialize_nuSQuIDS(self):
        czens, energies, initial_flux = self._make_initial_data()
        interactions = True
        self.nsq_atm = nsq.nuSQUIDSAtm(czens, energies*units.GeV, 3, nsq.NeutrinoType.both, interactions)
        self.nsq_atm.Set_initial_state(initial_flux, nsq.Basis.flavor)
        
        self.nsq_atm.Set_rel_error(1.0e-15)
        self.nsq_atm.Set_abs_error(1.0e-15)
        if self.mc.event_selection=='MEOWS':
            self.nsq_atm.EvolveState()

    def get_flux(self, cz, e, ptype):
        pass
    
    def interp_mc(self):
        mcflux = [self.get_flux(*tup) for tup in zip(self.mcdata['CosNuZenith'],
                                                     self.mcdata['NuEnergy'],
                                                     self.mcdata['PrimaryType']
                                                    )
                 ]
        self.mcflux = mcflux
