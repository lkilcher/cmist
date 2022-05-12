import os
from pathlib import Path
import json
import numpy as np
import pkg_resources
from configparser import ConfigParser

if os.path.isfile(os.path.expanduser('~/.cmist-lib/config')):
    config = ConfigParser()
    config.read('~/.cmist-lib/config')
    if 'cache_dir' in config:
        cache_dir = config['cache_dir']
else:
    cache_dir = os.path.expanduser('~/.cmist-lib/cache')

try:
    pkg_root = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../') + '/'
except:
    pkg_root = '../'

data_root = pkg_root + 'data/'

Path(cache_dir).mkdir(parents=True, exist_ok=True)

print("The cmist-cache folder is: {}".format(cache_dir))

def _load_station_index():
    stream = pkg_resources.resource_stream(__name__, 'data/coops_stations.json')
    return json.load(stream)

station_index = _load_station_index()
