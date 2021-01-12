import numpy as np

from physicsconstants import PhysicsConstants

units = PhysicsConstants()

datadir = '/data/user/jlazar/solar_WIMP_v2/data/'

conv_czz = np.linspace(-1, 1, 150)
conv_ee  = np.logspace(0, 6, 525)

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

