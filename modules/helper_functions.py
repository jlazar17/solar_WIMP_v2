import numpy as np

def opening_angle(zen1, az1, zen2, az2):
    return np.arccos(np.sin(zen1)*np.sin(zen2)*np.cos(az1-az2)+np.cos(zen1)*np.cos(zen2))

def mc_fname(path):
    return '.'.join(path.split('/')[-1].split('.')[:-1])
