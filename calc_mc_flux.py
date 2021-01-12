import time
import h5py
import numpy as np

import nuSQUIDSpy as nsq
from path_gen import PathGen
from mc_reader import MCReader
import mc_reader
from controls import units, datadir

def initialize_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mcfile',
                        type=str,
                        help='path to mcfile to be used'
                       )
    parser.add_argument('--fluxtype',
                        type=str,
                        help='fluxtype to be used, e.g. conv-numu or ch5-m1000'
                       )
    args = parser.parse_args()
    return args

class BaseMCFluxMaker:

    def __init__(self, mcpath, fluxtype):
        self.mcpath   = mcpath
        self.fluxtype = fluxtype
        self.mcdata   = self.read_mc()
        self.pg       = PathGen(self.mcpath)
        self.mcflux   = None
        self.nsq_atm  = None

    def read_mc(self):
        mcreader = MCReader(self.mcpath)
        mcdata = np.array(zip(mcreader.nu_e,
                              np.cos(mcreader.nu_zen),
                              mcreader.ptype
                             ),
                          dtype=[('NuEnergy', float), 
                                 ('CosNuZenith', float), 
                                 ('PrimaryType', int)
                                ]
                         )
        #if 'SterileNeutrino' in self.mcpath:
        #    print('MEOWS MC')
        #    mcf = h5py.File(self.mcpath, 'r')
        #    mcdata = np.array(zip(mcf['NuEnergy'][()]['value'],
        #                          np.cos(mcf['NuZenith'][()]['value']),
        #                          mcf['PrimaryType'][()]['value']
        #                         ),
        #                      dtype=[('NuEnergy', float), 
        #                             ('CosNuZenith', float), 
        #                             ('PrimaryType', int)
        #                            ]
        #                     )
        #    mcf.close()
        #elif 'xlevel' in self.mcpath:
        #    print('MEWOW MC')
        #    mcf = h5py.File(self.mcpath, 'r')
        #    mcdata = np.array(zip(mcf['NuEnergy'][()]['value'],
        #                          np.cos(mcf['NuZenith'][()]['value']),
        #                          mcf['PrimaryType'][()]['value']
        #                         ),
        #                      dtype=[('NuEnergy', float), 
        #                             ('CosNuZenith', float), 
        #                             ('PrimaryType', int)
        #                            ]
        #                     )
        #    mcf.close()
        #elif 'oscNext' in self.mcpath:
        #    print('oscNext')
        #    mcf = h5py.File(self.mcpath, 'r')
        #    mcdata = np.array(zip(mcf['MCInIcePrimary.energy'][()],
        #                          mcf['MCInIcePrimary.dir.coszen'][()],
        #                          np.where(np.random.rand(len(mcf))<0.4511734444723442, 14,-14)
        #                         ),
        #                      dtype=[('NuEnergy', float), 
        #                             ('CosNuZenith', float), 
        #                             ('PrimaryType', int)
        #                            ]
        #                     )
        #elif 'hmniederhausen' in self.mcpath:
        #    print('Hans')
        #    mcf = np.load(self.mcpath)
        #    mcdata = np.array(zip(mcf['trueE'],
        #                          np.cos(mcf['trueDec']+np.pi/2),
        #                          np.where(np.random.rand(len(mcf))<0.4511734444723442, 14,-14)
        #                         ),
        #                      dtype=[('NuEnergy', float), 
        #                             ('CosNuZenith', float), 
        #                             ('PrimaryType', int)
        #                            ]
        #                     )
        #elif 'IC86_2012_MC.npy' in self.mcpath:
        #    print('PSTracks MC')
        #    mcf = np.load(self.mcpath)
        #    mcdata = np.array(zip(mcf['trueE'],
        #                          np.cos(mcf['trueDec']+np.pi/2),
        #                          np.where(np.random.rand(len(mcf))<0.4511734444723442, 14,-14)
        #                         ),
        #                      dtype=[('NuEnergy', float), 
        #                             ('CosNuZenith', float), 
        #                             ('PrimaryType', int)
        #                            ]
        #                     )
        #else:
        #    print('mcpath %s not recognized' % self.mcpath)
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
        if 'SterileNeutrino' in self.mcpath:
            self.nsq_atm.EvolveState()

    def save_flux(self):
        if self.mcflux is None:
            print('mcflux not set yet')
            self.interp_mc()
        print('saving to %s' % self.pg.get_mc_dn_dz_path(self.fluxtype))
        np.save(self.pg.get_mc_dn_dz_path(self.fluxtype), self.mcflux)

    def get_flux(self, cz, e, ptype):
        pass
    
    def interp_mc(self):
        mcflux = [self.get_flux(*tup) for tup in zip(self.mcdata['CosNuZenith'],
                                                     self.mcdata['NuEnergy'],
                                                     self.mcdata['PrimaryType']
                                                    )
                 ]
        self.mcflux = mcflux
        return mcflux

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

class SolarAtmMCFluxMaker(BaseMCFluxMaker):
    
    def _make_initial_data(self):
        pp_HG_nu    = np.genfromtxt('/data/user/jlazar/solar_WIMP/data/solar_atm/PostPropagation/SIBYLL2.3_pp_HillasGaisser_H4a_nu.txt')
        pp_HG_nubar = np.genfromtxt('/data/user/jlazar/solar_WIMP/data/solar_atm/PostPropagation/SIBYLL2.3_pp_HillasGaisser_H4a_nubar.txt')
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

class PromptMCFluxMaker(BaseMCFluxMaker):

    def _make_initial_data(self):
        surface_flux_file = np.load('/data/user/jlazar/solar_WIMP/data/prompt_flux.npy')
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
        if cz>0.2:
            return 0.0
        elif ptype==14:
            return self.nsq_atm.EvalFlavor(1, cz, e*units.GeV, 0)
        elif ptype==-14:
            return self.nsq_atm.EvalFlavor(1, cz, e*units.GeV, 1)
        else:
            print('wrong ptype doggo')
            return 0
    

def create_mc_fluxmaker(mcpath, fluxtype):
    if fluxtype=='conv-numu':
        fluxmaker = ConvNumuMCFluxMaker(mcpath, fluxtype)
    elif fluxtype=='solar-atm':
        fluxmaker = SolarAtmMCFluxMaker(mcpath, fluxtype)
    elif fluxtype=='prompt':
        fluxmaker = PromptMCFluxMaker(mcpath, fluxtype)
    else:
        fluxmaker = SignalMCFluxMaker(mcpath, fluxtype)
    return fluxmaker

def main(args):
    fluxmaker = create_mc_fluxmaker(args.mcfile, args.fluxtype)
    fluxmaker.initialize_nuSQuIDS()
    fluxmaker.save_flux()

if __name__=='__main__':
    args      = initialize_args()
    main(args)
