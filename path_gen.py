from controls import datadir

class PathGen():

    def __init__(self, mcpath):
        
        self.mcpath = mcpath
        if 'IC86_2012_MC.npy' in mcpath:
            self.mctype = 'PSTracks'
        elif 'Sterile' in mcpath:
            self.mctype = mcpath.split("/")[7]
        elif 'xlevel' in mcpath:
            self.mctype = 'LowUp'
        elif 'oscNext' in self.mcpath:
            self.mctype = 'oscNext'

    def get_mcname(self):
        if self.mctype=="Systematics":
            mcname = self.mcpath.split("/")[8]
        elif self.mctype=="Nominal":
            mcname = "Nominal"
        elif 'hmniederhausen/' in self.mcpath:
            mcname = 'Hans'
        elif 'IC86_2012_MC.npy' in self.mcpath:
            mcname = 'PSTracks'
        elif 'xlevel' in self.mcpath:
            mcname = 'LowUp'
        elif 'oscNext' in self.mcpath:
            mcname = 'oscNext'
        else:
            print("mctype==%s is not a recognized mctype" % self.mctype)
            mcname=None
        return mcname

    def get_licfile_path(self):
        if self.mctype=="Nominal":
            licfile = "/data/ana/SterileNeutrino/IC86/HighEnergy/SPE_Templates/Nominal/Gen/00001-01000/Generation_data.lic"
        elif self.mctype=="Systematics":
            licfile = "/data/ana/SterileNeutrino/IC86/HighEnergy/MC/Systematics/%s/Gen/00001-01000/Generation_data.lic" % self.get_mcname()
        else:
            print("mctype==%s is not a recognized mctype" % self.mctype)
            licfile=None
        return licfile

    def get_mc_dn_dz_path(self, flux):
        return "%s/mc_dn_dz/%s_%s.npy" % (datadir, flux, self.get_mcname())

    def get_ow_path(self):
        path = '%s/mc_oneweight/%s.npy' % (datadir, self.get_mcname())
        return path
 
    def get_mcpath(self):
        return self.mcpath

    def get_e_d_theta_path(self, fluxtype):
        return '%s/e_d_theta_hist/%s_%s_e_d_theta' % (datadir, fluxtype, self.get_mcname())

    def get_uninterp_flux_path(self, fluxtype):
        if fluxtype=='conv-numu':
            path = "%s/AIRS_flux_sib_HG.dat" % datadir
        else:
            path =  '%s/qr_dn_dz/%s.npy' % (datadir, fluxtype)
        return path
