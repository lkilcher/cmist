import os
#import cPickle as pkl
import json
import numpy as np

try:
    pkg_root = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../') + '/'
except:
    pkg_root = '../'
data_root = pkg_root + 'data/'
cache_dir = pkg_root + '.cache/'


try:
    os.mkdir(cache_dir)
except OSError:
    pass


with open(data_root + 'coops_stations.json', 'r') as fl:
    station_index = json.load(fl)
