import numpy as np

def MaskMuonFilter(mc):
    mask = np.where(mc.muon_prescale*mc.muon_condition==1)[0]
    return mask
