import numpy as np
import h5py
from os import path

from path_gen import PathGen



class MCReader():

    def __init__(self, mcpath, slc=slice(None), options='00'):
        self.nu_e = None
        self.mcpath    = mcpath
        self._rescale  = int(options[0])
        self._scramble = int(options[1])
        self.slc       = slc
        self.set_event_selection()
        self.mcfg      = PathGen(self.mcpath)
        
        if self.event_selection=='MEOWS':
            self.num_files = float(mcpath.split('_')[-1][:-3])/5.
            self.h5f = h5py.File(mcpath, "r")
        elif self.event_selection=='LowUp':
            self.num_files = float(mcpath.split('_')[-1][:-3])/5.
            self.h5f = h5py.File(mcpath, "r")
        elif self.event_selection=='PSTracks':
            self.h5f = np.load(self.mcpath)
            self.num_files = 1.
        elif self.event_selection=='Hans':
            self.h5f = np.load(self.mcpath)
            self.num_files = 1.
        elif self.event_selection=='oscNext':
            self.h5f = h5py.File(mcpath, 'r')
        self.set_mc_quantities()
        if (self.event_selection=='MEOWS') or (self.event_selection=='oscNext'):
            self.h5f.close()

    def set_event_selection(self):
        if ('SterileNeutrino' in self.mcpath):
            self.event_selection = 'MEOWS'
        elif ('xlevel' in self.mcpath):
            self.event_selection = 'LowUp'
        elif 'IC86_2012_MC.npy' in self.mcpath:
            self.event_selection = 'PSTracks'
        elif 'hmniederhausen/' in self.mcpath:
            self.event_selection = 'Hans'
        elif 'oscNext' in self.mcpath:
            self.event_selection = 'oscNext'
        else:
            print('Event selection not recognized')
            quit()

    def set_mc_quantities(self):
        if (self.event_selection=='MEOWS') or (self.event_selection=='LowUp'):
            import weight_MC as wmc
            self.nu_e = self.h5f["NuEnergy"]["value"][self.slc]
            if self._scramble:
                delta_az = np.random.rand(len(self.nu_e))*2*np.pi
            else:
                delta_az = np.zeros(len(self.nu_e))
            self.nu_zen    = self.h5f["NuZenith"]["value"][self.slc]
            self.nu_az     = self.h5f["NuAzimuth"]["value"][self.slc]
            self.reco_e    = self.h5f["MuExEnergy"]["value"][self.slc]
            if not self._rescale:
                self.reco_zen  = self.h5f["MuExZenith"]["value"][self.slc]
                _ = self.h5f["MuExAzimuth"]["value"][self.slc]
                self.reco_az   = np.mod(_+delta_az, 2*np.pi)
            else:
                from gen_rescale_az_zen import gen_new_zen_az
                reco_az, reco_zen = gen_new_zen_az(self.h5f["NuEnergy"]["value"])
                self.reco_az = np.mod(reco_az[self.slc]+delta_az,2*np.pi)
                self.reco_zen = reco_zen[self.slc]
            self.set_oneweight()
            self.ptype = self.h5f['PrimaryType'][()]
        elif (self.event_selection=='PSTracks'):
            self.nu_e      = self.h5f['trueE'][self.slc]
            delta_ra       = self.h5f['trueRa'][self.slc]-self.h5f['ra'][self.slc]
            self.nu_az     = np.random.rand(len(self.nu_e))*np.pi*2
            self.nu_zen    = self.h5f['trueDec'][self.slc]+np.pi/2
            self.reco_e    = np.power(10, self.h5f['logE'])[self.slc]
            self.reco_az   = (self.nu_az-delta_ra) % (2*np.pi)
            self.reco_zen  = self.h5f['dec'][self.slc]+np.pi/2
            self.oneweight = self.h5f['ow'][self.slc]
            self.ptype     = np.where(np.random.rand(len(self.nu_az))<0.4511734444723442, 14,-14)
        elif self.event_selection=='Hans':
            self.nu_e      = self.h5f['trueE'][self.slc]
            self.nu_az     = self.h5f['trueAzi'][self.slc]
            self.nu_zen    = self.h5f['trueDec'][self.slc]+np.pi/2
            self.reco_e    = np.power(10, self.h5f['logE'])[self.slc]
            self.reco_az   = self.h5f['azi'][self.slc]
            self.reco_zen  = self.h5f['dec'][self.slc]+np.pi/2
            self.oneweight = self.h5f['ow'][self.slc]
            self.ptype     = np.where(np.random.rand(len(self.nu_az))<0.4511734444723442, 14,-14)
        elif self.event_selection=='oscNext':
            keys_to_read = ['nue_cc', 'nue_nc', 'nuebar_cc', 'nuebar_nc', 'numu_nc', 'numubar_nc', 'nutau_nc', 'nutaubar_nc']
            for key in self.h5f.keys():
                if key in keys_to_read:
                    if self.nu_e is None:
                        self.nu_e      = self.h5f[key]['MCInIcePrimary.energy'][()]
                        self.nu_az     = self.h5f[key]['MCInIcePrimary.dir.azimuth'][()]
                        self.nu_zen    = np.arccos(self.h5f[key]['MCInIcePrimary.dir.coszen'][()])
                        self.reco_e    = self.h5f[key]['L7_reconstructed_total_energy'][()]
                        self.reco_az   = self.h5f[key]['L7_reconstructed_azimuth'][()]
                        self.reco_zen  = np.arccos(self.h5f[key]['L7_reconstructed_coszen'][()])
                        self.ptype     = self.h5f[key]['MCInIcePrimary.pdg_encoding'][()]
                        self.oneweight = self.h5f[key]['I3MCWeightDict.OneWeight'][()] / (self.h5f[key]['I3MCWeightDict.NEvents'][()] * self.h5f[key]['I3MCWeightDict.gen_ratio'][()])
                    else:
                        self.nu_e      = np.append(self.nu_e, self.h5f[key]['MCInIcePrimary.energy'][()])
                        self.nu_az     = np.append(self.nu_az, self.h5f[key]['MCInIcePrimary.dir.azimuth'][()])
                        self.nu_zen    = np.append(self.nu_zen, np.arccos(self.h5f[key]['MCInIcePrimary.dir.coszen'][()]))
                        self.reco_e    = np.append(self.reco_e, self.h5f[key]['L7_reconstructed_total_energy'][()])
                        self.reco_az   = np.append(self.reco_az, self.h5f[key]['L7_reconstructed_azimuth'][()])
                        self.reco_zen  = np.append(self.reco_zen, np.arccos(self.h5f[key]['L7_reconstructed_coszen'][()]))
                        self.ptype     = np.append(self.ptype, self.h5f[key]['MCInIcePrimary.pdg_encoding'][()])
                        self.oneweight = np.append(self.oneweight, self.h5f[key]['I3MCWeightDict.OneWeight'][()] / (self.h5f[key]['I3MCWeightDict.NEvents'][()] * self.h5f[key]['I3MCWeightDict.gen_ratio'][()]))
                else:
                    print('Not including %s' % (key))
            #n_events = 0
            #i0       = 0
            #slices   = []
            #for key in self.h5f.keys():
            #    if key in keys_to_read:
            #        n         = len(self.h5f[key]['L7_reconstructed_total_energy'][()])
            #        n_events += n
            #        i1       = i0+n
            #        slices.append(slice(i0,i1))
            #        i0       = i1
            #    else:
            #        print('Not including %s' % (key))
            #print(n_events)
            #if self._scramble:
            #    delta_az = np.random.rand(n_events)*2*np.pi
            #else:
            #    delta_az = np.zeros(n_events)
            #self.nu_e      = np.zeros(n_events)
            #self.nu_az     = np.zeros(n_events)
            #self.nu_zen    = np.zeros(n_events)
            #self.reco_e    = np.zeros(n_events)
            #self.reco_az   = np.zeros(n_events)
            #self.reco_zen  = np.zeros(n_events)
            #self.oneweight = np.zeros(n_events)
            #self.ptype     = np.zeros(n_events)
            #for key, slc in zip(self.h5f.keys(), slices):
            #    if key in keys_to_read:
            #        self.nu_e[slc]      = self.h5f[key]['MCInIcePrimary.energy'][()]
            #        self.nu_az[slc]     = self.h5f[key]['MCInIcePrimary.dir.azimuth'][()]
            #        self.nu_zen[slc]    = np.arccos(self.h5f[key]['MCInIcePrimary.dir.coszen'][()])
            #        self.reco_e[slc]    = self.h5f[key]['L7_reconstructed_total_energy'][()]
            #        self.reco_az[slc]   = self.h5f[key]['L7_reconstructed_azimuth'][()]
            #        self.reco_zen[slc]  = np.arccos(self.h5f[key]['L7_reconstructed_coszen'][()])
            #        self.oneweight[slc] = self.h5f[key]['I3MCWeightDict.OneWeight'][()] / (self.h5f[key]['I3MCWeightDict.NEvents'][()] * self.h5f[key]['I3MCWeightDict.gen_ratio'][()])
            #        self.ptype[slc] = self.h5f[key]['MCInIcePrimary.pdg_encoding'][()]
            #    else:
            #        print('Not including %s' % (key))
            #self.reco_az +=delta_az
        
    def set_oneweight(self):
        if path.exists(self.mcfg.get_ow_path()):
            ow = np.load(self.mcfg.get_ow_path())[self.slc]/self.num_files
        elif 'oneweight' in self.h5f.keys():
            ow = self.h5f["oneweight"]["value"][self.slc]/self.num_files
        else:
            ow = wmc.weight_mc(self.mcfg)[self.slc]/self.num_files
        self.oneweight = ow

    def set_compare():
        self.oneweight = np.where(self.nu_e>3000, 0, self.oneweight)
        

if __name__=='__main__':
    from  sys import argv as args
    mcpath = args[1]
    slc = slice(None, None, int(args[2]))
    mcr = MCReader(mcpath, slc)
