import numpy as np
import h5py
from os import path


class MCReader():

    def __init__(self, filepath, slc=slice(None), options='00'):
        self.nu_e = None
        self.filepath    = filepath
        self._rescale  = int(options[0])
        self._scramble = int(options[1])
        self.slc       = slc
        self.set_event_selection()
        
        if self.event_selection=='intracks':
            self.mcf = np.load(self.filepath)
        elif self.event_selection=='oscNext':
            self.mcf = h5py.File(self.filepath, 'r')

        self.set_mc_quantities()

        if self.event_selection=='oscNext':
            self.mcf.close()

    def set_event_selection(self):
        if 'hmniederhausen/' in self.filepath:
            self.event_selection = 'intracks'
        elif 'oscNext' in self.filepath:
            self.event_selection = 'oscNext'
        else:
            print('Event selection not recognized')
            quit()

    def set_mc_quantities(self):
        if self.event_selection=='intracks':
            self.nu_e      = self.mcf['trueE'][self.slc]
            self.nu_az     = self.mcf['trueAzi'][self.slc]
            self.nu_zen    = self.mcf['trueDec'][self.slc]+np.pi/2
            self.reco_e    = np.power(10, self.mcf['logE'])[self.slc]
            self.reco_az   = self.mcf['azi'][self.slc]
            self.reco_zen  = self.mcf['dec'][self.slc]+np.pi/2
            self.oneweight = self.mcf['ow'][self.slc]
            self.ptype     = np.where(np.random.rand(len(self.nu_az))<0.4511734444723442, 14,-14)
        elif self.event_selection=='oscNext':
            self.nu_e      = []
            self.nu_az     = []
            self.nu_zen    = []
            self.reco_e    = []
            self.reco_az   = []
            self.reco_zen  = []
            self.ptype     = []
            self.trackprob = []
            self.oneweight = []
            for key in self.mcf.keys():
                self.nu_e      = np.append(self.nu_e, self.mcf[key]['MCInIcePrimary.energy'][()])
                self.nu_az     = np.append(self.nu_az, self.mcf[key]['MCInIcePrimary.dir.azimuth'][()])
                self.nu_zen    = np.append(self.nu_zen, np.arccos(self.mcf[key]['MCInIcePrimary.dir.coszen'][()]))
                self.reco_e    = np.append(self.reco_e, self.mcf[key]['L7_reconstructed_total_energy'][()])
                self.reco_az   = np.append(self.reco_az, self.mcf[key]['L7_reconstructed_azimuth'][()])
                self.reco_zen  = np.append(self.reco_zen, np.arccos(self.mcf[key]['L7_reconstructed_coszen'][()]))
                self.ptype     = np.append(self.ptype, self.mcf[key]['MCInIcePrimary.pdg_encoding'][()])
                self.trackprob = np.append(self.trackprob, self.mcf[key]['L7_PIDClassifier_FullSky_ProbTrack'][()])
                self.oneweight = np.append(self.oneweight, self.mcf[key]['I3MCWeightDict.OneWeight'][()] / (self.mcf[key]['I3MCWeightDict.NEvents'][()] * self.mcf[key]['I3MCWeightDict.gen_ratio'][()]))


if __name__=='__main__':
    from  sys import argv as args
    filepath = args[1]
    mcr = MCReader(filepath)
    print(len(mcr.nu_e))
