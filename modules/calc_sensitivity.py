import numpy as np
from scipy.special import gamma
from scipy.optimize import broyden1, ridder


from DM import DMAnnihilationJungmanSD

def initialize_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-m',
                        type=int,
                        help='path to mcfile to be used'
                       )
    parser.add_argument('--ch',
                        type=int,
                        help='fluxtype to be used, e.g. conv-numu or ch5-m1000'
                       )
    parser.add_argument('--options',
                        type=str,
                        default='00'
                       )
    parser.add_argument('--syst_type',
                        default='Nominal'
                       )
    
    args = parser.parse_args()
    return args

def factorial(x):
    x = np.asarray(x)
    return gamma(x+1)

def neg_log_likelihood(mu_s, n_s, mu_b, n_b):
    """
    mu_s float: mean number of signal events
    n_s  int  : observed number of signal events
    mu_b float: mean number of background events
    n_b  int  : observed number of bacground events
    """
    mu_s = np.asarray(mu_s)
    mu_b = np.asarray(mu_b)
    n_b  = np.asarray(n_b)
    n_s  = np.asarray(n_s)
    mu   = mu_s*n_s + mu_b*n_b
    #lh   = -np.log(np.exp(-mu) * np.power(mu, mu_b) / factorial(mu_b))
    lh   = -np.log(np.exp(-mu_b) * np.power(mu_b, mu) / factorial(mu))
    lh   = lh[np.where(~np.isnan(lh))]
    lh   = lh[np.where(~np.isinf(lh))]
    return np.sum(lh)

def calc_sens(mu_b, mu_s, yint=2.71, n_b=1.0):
        
    neg_llh0 = neg_log_likelihood(mu_s, 0, mu_b, n_b)
    func     = lambda x: 2*(neg_log_likelihood(mu_s, x, mu_b, n_b) - neg_llh0) - yint
    sens     = ridder(func, 1e-5, 1e3) * 1e-39 # cm^{2}
    #sens = broyden1(func, 0.0) * 1e-39 # cm^{2}
    return sens

class SensitivityCalculator():

    def __init__(self, ch, m, syst_type, options):
        
        self.ch = ch
        self.m  = m
        self.syst_type = syst_type
        self.options = options

    def calc_sens(self, include_solar=True):
        mu_s = self.load_signal()
        mu_b = self.load_background(include_solar=include_solar)
        sens = calc_sens(mu_b, mu_s)
        return sens
        
    def load_signal(self):
        factor = 1.e-3/self.m*self.ann_rate()
        if self.syst_type in ['Nominal', 'PSTracks', 'Hans']:
            mu_s = factor*np.load('/data/user/jlazar/solar_WIMP/data/e_d_theta_hist/ch%d-m%d_%s_e_d_theta_%s.npy' % (self.ch, self.m, self.syst_type, self.options))
        else:
            mu_s = factor*np.load('/data/user/jlazar/solar_WIMP/data/e_d_theta_hist/ch%d-m%d_%s_e_d_theta_%s.npy' % (self.ch, self.m, self.syst_type, self.options))
            mu_s += factor*np.load('/data/user/jlazar/solar_WIMP/data/e_d_theta_hist/ch%d-m%d_LE_%s_e_d_theta_%s.npy' % (self.ch, self.m, self.syst_type, self.options))
        
        return mu_s

    def load_background(self, include_solar=True):
        if self.syst_type in ['Nominal', 'PSTracks', 'Hans']:
            mu_b = np.load('/data/user/jlazar/solar_WIMP/data/e_d_theta_hist/conv-numu_%s_e_d_theta_%s.npy' % (self.syst_type, self.options))
            if include_solar:
                mu_b += np.load('/data/user/jlazar/solar_WIMP/data/e_d_theta_hist/solar-atm_%s_e_d_theta_%s.npy' % (self.syst_type, self.options))
        else:
            mu_b = np.load('/data/user/jlazar/solar_WIMP/data/e_d_theta_hist/conv-numu_%s_e_d_theta_%s.npy' % (self.syst_type, self.options))
            mu_b += np.load('/data/user/jlazar/solar_WIMP/data/e_d_theta_hist/conv-numu_LE_%s_e_d_theta_%s.npy' % (self.syst_type, self.options))
            if include_solar:
                mu_b += np.load('/data/user/jlazar/solar_WIMP/data/e_d_theta_hist/solar-atm_%s_e_d_theta_%s.npy' % (self.syst_type, self.options))
                mu_b += np.load('/data/user/jlazar/solar_WIMP/data/e_d_theta_hist/solar-atm_LE_%s_e_d_theta_%s.npy' % (self.syst_type, self.options))
        return mu_b

    def ann_rate(self):
        '''
        Capture rate for benchmark case of 1pb
        '''
        return DMAnnihilationJungmanSD(self.m, 1e-36)

if __name__=='__main__':
    args = initialize_args()
    sc = SensitivityCalculator(args.ch, args.m, args.syst_type, args.options)
    print(sc.calc_sens())
