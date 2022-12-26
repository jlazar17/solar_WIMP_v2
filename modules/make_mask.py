import numpy as np

def make_mask(recarray, cuts):
    if len(cuts)==0:
        return np.full(len(recarray), True)
    mask = np.full((len(cuts), len(recarray)), True)
    for i, cut in enumerate(cuts):
        if hasattr(cut, '__call__'):
            mask[i] = cut(recarray)
        else:
            if cut[0]=='lt':
                mask[i] = recarray[cut[1]]<cut[2]
            elif cut[0]=='gt':
                mask[i] = recarray[cut[1]]>cut[2]
            elif cut[0]=='lte':
                mask[i] = recarray[cut[1]]<=cut[2]
            elif cut[0]=='gte':
                mask[i] = recarray[cut[1]]>=cut[2]
            else:
                raise ValueError
    return np.logical_and.reduce(mask, axis=0)
