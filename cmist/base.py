import os
#import cPickle as pkl
import json
import numpy as np
import pkg_resources

cache_dir = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../') + '/' + '.cache/'

try:
    os.mkdir(cache_dir)
except OSError:
    pass


def _load_station_index():

    print(__name__)
    stream = pkg_resources.resource_stream(__name__, 'data/coops_stations.json')
    return json.load(stream)
    
    # with open(data_root + 'coops_stations.json', 'r') as fl:
    #     station_index = json.load(fl)

station_index = _load_station_index()
