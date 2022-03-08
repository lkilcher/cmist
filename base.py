import os
#import cPickle as pkl
import json
import numpy as np
from scipy.io import savemat

try:
    pkg_root = os.path.dirname(os.path.realpath(__file__)) + '/'
except:
    pkg_root = './'
data_root = pkg_root + 'data/'
cache_dir = pkg_root + '.cache/'


try:
    os.mkdir(cache_dir)
except OSError:
    pass


with open(data_root + 'coops_stations.json', 'r') as fl:
    station_index = json.load(fl)


class veldata(dict):

    def savemat(self, fname):
        savemat(fname, self)

    def _to_cache(self, ):
        self.savemat(cache_dir + self.index + '.mat')

    def __getattr__(self, name):
        return self[name]

    @property
    def index(self, ):
        return self['Station ID']

    @property
    def u(self, ):
        return self['vel'][0]

    @property
    def v(self, ):
        return self['vel'][1]

    @property
    def w(self, ):
        return self['vel'][2]

    @property
    def U(self, ):
        return np.abs(self.u + 1j * self.v)

    @property
    def speed(self, ):
        return self.U
