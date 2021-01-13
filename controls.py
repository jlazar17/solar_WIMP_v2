import numpy as np

from physicsconstants import PhysicsConstants
units = PhysicsConstants()

datadir = '/data/user/jlazar/solar_WIMP_v2/data/'

conv_numu_params = dict(czz=np.linspace(-1, 1, 150),
                        ee=np.logspace(0, 6, 525),
                       )

############################### PARAMETERS FOR DISTRIBUTION CALCS #################################
start = 2455349.5
stop  = 2456810.5 # 4 years
n     = 35000
dist_calc_params = dict(cdtheta=np.linspace(-1, 1, 300),
                        ee=np.logspace(0,6,61),
                        ptrackk=np.linspace(0,1,101),
                        jds=np.linspace(start, stop, n), # roughly every hour
                        azimuths=np.random.rand(n)*np.pi*2,
                        r_sun=6.9e10, # cm
                       )

######################## PARAMETERS FOR GENERATING THE SIGNAL FROM CHARON #########################
# osc params from http://www.nu-fit.org/?q=node/228
charon_params = dict(theta_13=33.44,
                     theta_12=49.0,
                     theta_23=8.57,
                     delta_m_12=7.42e-5,
                     delta_m_13=2.514e-3,
                     delta=195.0,
                     process='ann',
                     nodes=200,
                     bins=200,
                     Emin=1.0,
                     interactions=True,
                    )

