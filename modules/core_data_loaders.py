
def core_lowup_data_patch(path):
    import h5py as h5
    mcf  = h5.File(path, 'r')
    data = [
            (mcf["TrueEnergy"][()],    'true_e',        '<f8'),
            (mcf["TrueZenith"][()],    'true_zen',      '<f8'),
            (mcf["TrueAzimuth"][()],   'true_az',       '<f8'),
            (mcf["RecoZenith"][()],    'reco_zen',      '<f8'),
            (mcf["RecoAzimuth"][()],   'reco_az',       '<f8'),
            (mcf["eff_oneweight"][()], 'oneweight',     '<f8'),
            (mcf["eff_oneweight"][()], 'eff_oneweight', '<f8'),
            (mcf['PrimaryType'][()],   'ptype',         '<f8'),
            (mcf['QTot'][()],          'qtot',          '<f8'),
            (mcf['RLogL'][()],         'rlogl',         '<f8'),
            (mcf['ZTravel'][()],       'ztravel',       '<f8'),
            (mcf['COGZ'][()],          'cogz',          '<f8'),
            (mcf['COGZSigma'][()],     'cogzsigma',     '<f8'),
           ]
    mcf.close()
    return data

def core_lowup_data(path):
    import h5py as h5
    mcf  = h5.File(path, 'r')
    data = [
            (mcf["TrueEnergy"][()],    'true_e',        '<f8'),
            (mcf["TrueZenith"][()],    'true_zen',      '<f8'),
            (mcf["TrueAzimuth"][()],   'true_az',       '<f8'),
            (mcf["RecoZenith"][()],    'reco_zen',      '<f8'),
            (mcf["RecoAzimuth"][()],   'reco_az',       '<f8'),
            (mcf["eff_oneweight"][()], 'oneweight',     '<f8'),
            (mcf["eff_oneweight"][()], 'eff_oneweight', '<f8'),
            (mcf['PrimaryType'][()],   'ptype',         '<i8'),
            (mcf['QTot'][()],          'qtot',          '<f8'),
            (mcf['RLogL'][()],         'rlogl',         '<f8'),
            (mcf['ZTravel'][()],       'ztravel',       '<f8'),
            (mcf['COGZ'][()],          'cogz',          '<f8'),
            (mcf['COGZSigma'][()],     'cogzsigma',     '<f8'),
           ]
    mcf.close()
    return data

def core_ps_data(path):
    import numpy as np
    mcf  = np.load(path)
    # TODO find actual particle type information
    np.random.seed(1)
    ptype = np.where(np.random.rand(len(mcf['trueE']))<0.4511734444723442, 14,-14)
    data = [(mcf['trueE'],              'true_e',    '<f8'),
            (mcf['trueDec']+np.pi/2,    'true_zen',  '<f8'),
            (mcf['trueAzi'],            'true_az',   '<f8'),
            (np.power(10, mcf['logE']), 'reco_e',    '<f8'),
            (mcf['dec']+np.pi/2,        'reco_zen',  '<f8'),
            (mcf['azi'],                'reco_az',   '<f8'),
            (mcf['ow'],                 'oneweight', '<f8'),
            (ptype,                     'ptype',     '<i8'),
           ]
    return data

def core_oscNext_data(path):
    import sys
    sys.path.append('../')
    from controls import oscNext_nfiles
    import h5py as h5
    import numpy as np
    mcf  = h5.File(path, 'r')
    true_e       = []
    true_az      = []
    true_zen     = []
    reco_e       = []
    reco_az      = []
    reco_zen     = []
    ptype        = []
    trackprob    = []
    oneweight    = []
    rweight      = []
    passed_muon  = []
    passed_lowup = []
    for key in mcf.keys():
        true_e    = np.append(true_e, mcf[key]['MCInIcePrimary.energy'][()])
        true_az   = np.append(true_az, mcf[key]['MCInIcePrimary.dir.azimuth'][()])
        true_zen  = np.append(true_zen, np.arccos(mcf[key]['MCInIcePrimary.dir.coszen'][()]))
        reco_e    = np.append(reco_e, mcf[key]['L7_reconstructed_total_energy'][()])
        reco_az   = np.append(reco_az, mcf[key]['L7_reconstructed_azimuth'][()])
        reco_zen  = np.append(reco_zen, np.arccos(mcf[key]['L7_reconstructed_coszen'][()]))
        ptype     = np.append(ptype, mcf[key]['MCInIcePrimary.pdg_encoding'][()])
        trackprob = np.append(trackprob, mcf[key]['L7_PIDClassifier_FullSky_ProbTrack'][()])
        oneweight = np.append(oneweight, mcf[key]['I3MCWeightDict.OneWeight'][()] / (mcf[key]['I3MCWeightDict.NEvents'][()] * mcf[key]['I3MCWeightDict.gen_ratio'][()] * oscNext_nfiles[key]))
        rweight   = np.append(rweight, mcf[key]['ReferenceWeight'][()])
        passed_lowup = np.append(passed_muon, 
                                      mcf[key]['FilterMask.LowUp_13.prescale_passed'][()] * mcf[key]['FilterMask.LowUp_13.condition_passed'][()]
                                     ) 
        passed_muon  = np.append(passed_muon, 
                                      mcf[key]['FilterMask.MuonFilter_13.prescale_passed'][()] * mcf[key]['FilterMask.MuonFilter_13.condition_passed'][()]
                                     )
    data = [
            (true_e,       'true_e',      '<f8'),
            (true_zen,     'true_zen',    '<f8'),
            (true_az,      'true_az',     '<f8'),
            (reco_e,       'reco_e',      '<f8'),
            (reco_zen,     'reco_zen',    '<f8'),
            (reco_az,      'reco_az',     '<f8'),
            (oneweight,    'oneweight',   '<f8'),
            (ptype,        'ptype',       '<i8'),
            (trackprob,    'trackprob',   '<f8'),
            (rweight,      'rweight',     '<f8'),
            (passed_muon,  'passed_muon', '<i8'),
            (passed_lowup, 'pass_lowup',  '<i8'),
           ]
    mcf.close()
    return data

core_data_loaders = {
                     'genie':core_lowup_data,
                     'nancy':core_lowup_data,
                     'oscNext':core_oscNext_data,
                     'intracks':core_ps_data,
                     'corsika':core_lowup_data_patch,
                    }
