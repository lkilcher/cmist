import shutil
from . import base
import os
from scipy.io import loadmat
from .web_io import load_from_web


def load_from_cache(idx):
    fname = base.cache_dir + idx + '.mat'
    if os.path.isfile(fname):
        out = base.veldata(loadmat(fname, squeeze_me=True))
        out['time'] = out['time'].astype('datetime64[m]')
        return out
    return None


def get_station(idx, force_reload=False):
    if not force_reload:
        data = load_from_cache(idx)
        if data is not None:
            return data
    data = load_from_web(idx)
    data._to_cache()
    return data


def reset_cache():
    try:
        shutil.rmtree(base.cache_dir)
    except:
        pass
    os.mkdir(base.cache_dir)
