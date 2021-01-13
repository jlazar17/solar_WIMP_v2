import numpy as np
from numpy import cos as c
from numpy import sin as s
import h5py
from scipy.interpolate import splrep, splev
from helper_functions import opening_angle

#np.random.seed(69420)
#
#mcfile = '/data/ana/SterileNeutrino/IC86/HighEnergy/SPE_Templates/Nominal/Ares/IC86.AVG/Merged/Ares_IC86.AVG_0.97_lite_platinum_98000.h5'
#mc       = h5py.File(mcfile, 'r')
#nu_e     = mc["NuEnergy"]['value']
#nu_zen   = mc["NuZenith"]['value']
#nu_az    = mc["NuAzimuth"]['value']
#reco_zen = mc["MuExZenith"]['value']
#reco_az  = mc["MuExAzimuth"]['value']

def meows_error(e):
    tck    = np.load("/data/user/jlazar/solar_WIMP/data/MEOWS_median_error_splrep.npy", allow_pickle=True, encoding='bytes')
    log10e = np.log10(e)
    return np.power(10, splev(log10e, tck))

def thry_error(e):
    tck = np.load('/data/user/jlazar/solar_WIMP/data/3y_ang_error_spline.npy', allow_pickle=True, encoding='bytes')
    return splev(np.log(e), tck)


def rot1(nu_az, nu_zen, gen_az, gen_zen):
    new_x =  c(nu_zen)*c(gen_az)*s(gen_zen) + s(nu_zen)*c(gen_zen)
    new_y =  s(gen_az)*s(gen_zen)
    new_z = -s(nu_zen)*c(gen_az)*s(gen_zen) + c(nu_zen)*c(gen_zen)
    new_az  = np.zeros(len(new_x))
    for i in range(len(new_x)):
        if new_x[i] > 0:
            new_az[i] = np.arctan(new_y[i] / new_x[i]) % (2*np.pi)
        else:
            new_az[i] = np.arctan(new_y[i] / new_x[i]) + np.pi
    new_zen = np.arccos(new_z)
    return new_az, new_zen

def rot2(nu_az, nu_zen, gen_az, gen_zen):
    new_x = c(nu_az)*c(gen_az)*s(gen_zen) - s(nu_az)*s(gen_az)*s(gen_zen)
    new_y = s(nu_az)*c(gen_az)*s(gen_zen) + c(nu_az)*s(gen_az)*s(gen_zen)
    new_z = c(gen_zen)
    new_az  = np.zeros(len(new_x))
    for i in range(len(new_x)):
        if new_x[i] > 0:
            new_az[i] = np.arctan(new_y[i] / new_x[i]) % (2*np.pi)
        else:
            new_az[i] = np.arctan(new_y[i] / new_x[i]) + np.pi
    new_zen = np.arccos(new_z)
    return new_az, new_zen

def rotate_coords(nu_az, nu_zen, gen_az, gen_zen):
    return rot2(nu_az, nu_zen, *rot1(nu_az,nu_zen, gen_az, gen_zen))

def gen_new_zen_az(e):
    scale           = thry_error(nu_e)/meows_error(nu_e)
    opening_angles  = opening_angle(nu_zen, nu_az, reco_zen, reco_az)
    gen_zen         = opening_angles * scale
    gen_az          = np.random.rand(len(opening_angles))*2*np.pi
    new_az, new_zen = rotate_coords(nu_az, nu_zen, gen_az, gen_zen)
    return new_az, new_zen
