import numpy as np
import warnings
from solar_common.sensitivity.poisson_nllh import poisson_nllh
from scipy.optimize import minimize
from scipy.stats import poisson
import pickle

import matplotlib.pyplot as plt

pull_edges  = np.linspace(-5, 5, 101)
pull_cents  = (pull_edges[:-1]+pull_edges[1:])/2
pull_widths = pull_edges[1:]-pull_edges[:-1]

# All masses for which distributions have been computed
MM = [300, 500, 800, 1000, 3000, 5000, 8000, 10000]
CHH = [5,8,11]
# livetime for the INT sample is 3186.1 days
livetime = 3186.1*24*3600 # Livetime in seconds

def load_data():
    from glob import glob
    yrr = [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
    dist = None
    for yr in yrr:
        fs = glob('/data/user/jlazar/solar/data//distributions/unblinded_data/IC86_%d_exp_*.npy' % yr)

        for f in fs:
            if dist is None:
                dist = np.divide(np.load(f), len(fs))
            else:
                dist += np.divide(np.load(f), len(fs))
    return dist

# This function loads the background template from oversampled data
def load_bg():
    from glob import glob
    yrr = [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
    dist = None
    for yr in yrr:
        fs = glob('/data/user/jlazar/solar/data//distributions/oversample/IC86_%d_exp_*.npy' % yr)

        for f in fs:
            if dist is None:
                dist = np.divide(np.load(f), len(fs))
            else:
                dist += np.divide(np.load(f), len(fs))
    return dist

def nllh(x, data, mus, mub):
    return poisson_nllh(data, np.exp(x[0])*mub+np.exp(x[1])*mus)


def unblind(data, bg, stage=0):
    best_fits = {}
    
    # Carry out the fit
    for ch in CHH:
        r = []
        for m in MM:
            sig_temp = livetime*np.load('/data/user/jlazar/solar/data/distributions/ch%d-m%d_1AU_BRW_IC86_pass2_MC_00.npy' % (ch, m))
            bg_func = lambda x: nllh((x[0], -np.inf), data, sig_temp, bg)
            fit_bg  = minimize(bg_func, (0., -5.2), method='L-BFGS-B')
            if not fit_bg.success:
                raise Exception('Background fit did not pass')
            sig_func = lambda x: nllh(x, data, sig_temp, bg)
            fit_sig  = minimize(sig_func, (0.1, np.log10(np.random.rand())), method='L-BFGS-B')
            r.append((fit_sig.fun, fit_sig.x, m))
        r  = sorted(r, key)
        best_r = r[0]
        bf_TS  = 2*(fit_bg.fun - best_r[0])
        bf_x   = best_r[1]
        bf_m   = best_r[2]
        best_fits[ch] = (bf_TS, bf_x, bf_m)
    if stage >= 0:
        data_away = data[:180,]
        bg_away = bg[:180,]
        for ch in CHH:
            bf_sig = livetime * np.load('/data/user/jlazar/solar/data/distributions/ch%d-m%d_1AU_BRW_IC86_pass2_MC_00.npy' % (ch, best_fits[ch][2]))
            bf_x   = best_fits[ch][1]
            bf_model =10**bf_x[0]*bg+10**bf_x[1]*bf_sig
            bf_model_away = bf_model[:180,]

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")            
                pull_away = (bf_model_away-data_away)/np.sqrt(bf_model_away)
            pull_away = np.where(np.isfinite(pull_away), pull_away, 0)
            
            h_away,_ = np.histogram(pull_away, bins=pull_edges)
            h_away = h_away/np.sum(h_away)
            plt.step(pull_cents, h_away/np.sum(h_away))
            plt.step(pull_cents, np.cumsum(h_away))
            plt.axvline(3)
            plt.axhline(0.997)
            plt.savefig('/data/user/jlazar/solar/solar_WIMP_v2/analysis/unblinding/ch%d_pull_dist_away.pdf' % ch, dpi=400)
            plt.close()

    if stage>=1:
        data_near = data[180:,]
        bg_near   = bg[180:,]
        for ch in CHH:
            bf_sig        = livetime * np.load('/data/user/jlazar/solar/data/distributions/ch%d-m%d_1AU_BRW_IC86_pass2_MC_00.npy' % (ch, best_fits[ch][2]))
            bf_x          = best_fits[ch][1]
            bf_model      = 10**bf_x[0]*bg+10**bf_x[1]*bf_sig
            bf_model_near = bf_model[180:,]
            
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                pull_near = (bf_model_near-data_near)/np.sqrt(bf_model_near)
            pull_near = np.where(np.isfinite(pull_near), pull_near, 0)
            
            h,_ = np.histogram(pull_near, bins=pull_edges)
            h = h/np.sum(h)
            plt.step(pull_cents, h)
            plt.step(pull_cents, np.cumsum(h))
            plt.axvline(3)
            plt.axhline(0.997)
            plt.savefig('/data/user/jlazar/solar/solar_WIMP_v2/analysis/unblinding/ch%d_pull_dist_near.pdf' % ch, dpi=400)
            plt.close()
    if stage>=2:
        pp = []
        for ch in CHH:
            bf_TS = best_fits[ch][0]
            with open('/data/user/jlazar/solar/data/cumulative_TS_pkl/ch%d_cumsum.pkl' % ch, 'rb') as f:
                spl = pickle.load(f)
            if bf_TS>12:
                p = 0
            else:
                p = 1 - spl(bf_TS)
            if p<1e-3:
                raise Exception('Best fit p-value less than 1e-3')
            pp.append(p)
    if stage>=3:
        for ch in CHH:
            bf_TS = best_fits[ch][0]
            with open('/data/user/jlazar/solar/data/cumulative_TS_pkl/ch%d_cumsum.pkl' % ch, 'rb') as f:
                spl = pickle.load(f)
            if bf_TS>12:
                p = 0
            else:
                p = 1 - spl(bf_TS)
            if p<1e-2:
                raise Exception('Best fit p-value less than 1e-2')
    if stage>3:
        print(best_fits)
        print(pp)
        
        
####################################
