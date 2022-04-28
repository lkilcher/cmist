import os
#import cPickle as pkl
import json
import numpy as np
import pkg_resources

cache_dir = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../') + '/' + '.cmist-cache/'

try:
    os.mkdir(cache_dir)
except OSError:
    pass

print("The cmist-cache folder is: {}".format(cache_dir))


def _load_station_index():
    stream = pkg_resources.resource_stream(__name__, 'data/coops_stations.json')
    return json.load(stream)

station_index = _load_station_index()
