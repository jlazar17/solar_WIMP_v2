import numpy as np
from helper_functions import mc_fname
from make_mask import make_mask

def mc_name(path):
    if 'hmniederhausen/' in path:
        name = 'intracks'
    elif ('oscNext' in path):
        name = 'oscNext'
    elif 'JLevel' in path:
        if 'nancy' in path:
            name = 'nancy'
        elif 'genie' in path:
            name = 'genie'
        elif 'corsika' in path:
            name = 'corsika'
    else:
        raise RuntimeError('Event selection not recognized')
    return name

def load_core_data(selection, path):
    from core_data_loaders import core_data_loaders
    if selection in core_data_loaders.keys():
        data = core_data_loaders[selection](path)
    else:
        raise RuntimeError('Do not know how to load %s' % path)
    return data

def check_same_len(mc_data):
    lst = [len(t[0]) for t in mc_data]
    return len(set(lst))==1

class MCReader(object):

    def __init__(self, path=None, name=None, options='00', additional_data=None, thin=None):

        self.options       = options
        self.path          = path
        self._current_mask = None 
        self._thin         = thin

        # Make sure there is some way to make data
        if path is None and additional_data is None:
            raise RuntimeError('Must specify either a path or data')
        # Load data from path if specified
        elif path is not None:
            self.fname = mc_fname(path)
            self.name  = mc_name(path)
            mc_descs   = load_core_data(self.name, path)
        else:
            self.name = name
            mc_descs = []
        if additional_data is not None:
            if type(additional_data)==tuple:
                mc_descs.append(additional_data)
            else:
                for data_desc in additional_data:
                    mc_descs.append(data_desc)
        if not check_same_len(mc_descs):
            raise RuntimeError('All data must be the same length')
        self._mc_descs = mc_descs
        self._set_mc_data(mc_descs)
        if thin is not None:
            slc = slice(None, None, thin)
            self._mc_data = self._mc_data[slc]
        self.mc_data = self._mc_data

    def _set_mc_data(self, mc_descs):
        
        arr = np.array(
                       [tup for tup in zip(*tuple([t[0] for t in mc_descs]))],
                       dtype=[(t[1], t[2]) for t in mc_descs]
                      )
        self._mc_data = arr.view(np.recarray)

    def __len__(self):
        return len(self.mc_data)

    def __getitem__(self, key):
        return self.mc_data[key]

    def __add__(self, other):
        shared_dnames = list(set(self._mc_data.dtype.names) & set(other._mc_data.dtype.names))
        data          = [(np.append(self.mc_data[name], other.mc_data[name]), name, dtype)
                         for name, dtype in self._mc_data.dtype.descr
                         if name in shared_dnames
                        ]
        name = '%s-%s' % (self.name, other.name)
        return MCReader(additional_data=data, name=name)
    
    def add_data(self, new_data_desc):
        if len(new_data_desc[0])!=len(self._mc_data):
            raise ValueError('New data must have same length of whole MC set')
        elif(new_data_desc[1] in [desc[1] for desc in self._mc_descs]):
            raise ValueError('There is already a field with name %s' % new_data_desc[1])
        self._mc_descs.append(new_data_desc)
        self._set_mc_data(self._mc_descs)
        self.mc_data = self._mc_data
        if self._current_mask is not None:
            self.mc_data = self._mc_data[self._current_mask]
            

    def unmask(self):
        self.mc_data = self._mc_data
        self._current_mask = None 

    def make_mask(self, cuts):
        return make_mask(self._mc_data, cuts)

    def apply_mask(self, mask):
        self.mc_data       = self._mc_data[mask]
        self._current_mask = mask
