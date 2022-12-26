from solar_common.sensitivity.poisson_nllh import poisson_nllh
from scipy.optimize import minimize
import numpy as np
from scipy.optimize import minimize
import pickle, json

# seed around sens
scl_dict = {}
scl_dict[(5,300)]    = 10**0.2
scl_dict[(5,500)]    = 10**(-0.8)
scl_dict[(5,800)]    = 10**(-1.2)
scl_dict[(5,1000)]   = 10**(-1.2)
scl_dict[(5,3000)]   = 10**(-1.5)
scl_dict[(5,5000)]   = 10**(-1.6)
scl_dict[(5,8000)]   = 10**(-1.3)
scl_dict[(5,10000)]  = 10**(-1.3)
scl_dict[(8,300)]    = 10**(-2.5)
scl_dict[(8,500)]    = 10**(-3.)
scl_dict[(8,800)]    = 10**(-3.)
scl_dict[(8,1000)]   = 10**(-3)
scl_dict[(8,3000)]   = 10**(-2.5)
scl_dict[(8,5000)]   = 10**(-1.9)
scl_dict[(8,8000)]   = 10**(-1.5)
scl_dict[(8,10000)]  = 10**(-1.4)
scl_dict[(11,300)]   = 10**(-2.5)
scl_dict[(11,500)]   = 10**(-2.8)
scl_dict[(11,800)]   = 10**(-3.1)
scl_dict[(11,1000)]  = 10**(-3.1)
scl_dict[(11,3000)]  = 10**(-2.9)
scl_dict[(11,5000)]  = 10**(-2.5)
scl_dict[(11,8000)]  = 10**(-2.)
scl_dict[(11,10000)] = 10**(-1.9)
print(scl_dict)

CHH = [5,8,11]
MM  = [300, 500, 800, 1000, 3000, 5000, 8000, 10000]
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


data = load_data()
bg   = load_bg()


rand = np.random.RandomState(92594)
best_fits = {}
p_vals    = {}
for ch in CHH:
    with open('/data/user/jlazar/solar/data/cumulative_TS_pkl/ch%d_cumsum.pkl' % ch, 'rb') as f:
        spl = pickle.load(f)
    r = []
    pvall = []
    for m in MM:
        sig_temp = livetime*np.load('/data/user/jlazar/solar/data/distributions/ch%d-m%d_1AU_BRW_IC86_pass2_MC_00.npy' % (ch, m))
        bg_func = lambda x: nllh((x[0], -np.inf), data, sig_temp, bg)
        fit_bg  = minimize(bg_func, (0., -5.2), method='L-BFGS-B')
        print(fit_bg.x)
        if not fit_bg.success:
            raise Exception('Background fit did not pass')
        sig_func = lambda x: nllh(x, data, sig_temp, bg)
        fit_sig  = minimize(sig_func, (0.1, np.log((0.5*rand.rand()+1)*scl_dict[(ch,m)])), method='L-BFGS-B', tol=1e-6)
        if not fit_sig.success:
            print(ch, m)
            print(fit_sig)
        r.append((2*(fit_bg.fun-fit_sig.fun), fit_sig.x, m))
        #pvall.append(2*(fit_bg.fun-fit_sig.fun))
    best_fits[ch] = r
    #p_vals[ch] = pvall
#print(p_vals)
for ch in CHH:
    with open('/data/user/jlazar/solar/data/cumulative_TS_pkl/ch%d_cumsum.pkl' % ch, 'rb') as f:
        spl = pickle.load(f)
    print(ch)
    a = best_fits[ch]
    for _ in a:
        print(_[2])
        print(np.log10(np.exp(_[1])))
        print(_[0])
        print(1-spl(_[0]))
for key, val in best_fits.items():
    x = []
    for z in val:
        x.append((z[0], list(z[1]), z[2]))
    best_fits[key] = x
with open('./best_fits.json', 'w') as jsf:
    json.dump(best_fits, jsf)
