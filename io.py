import shutil
from . import base
import os
from scipy.io import loadmat
from .web_io import load_from_web
from .base import station_index


def load_from_cache(idx, deployment):
    fname = base.cache_dir + idx + '.{:04d}.mat'.format(deployment)
    if os.path.isfile(fname):
        out = base.veldata(loadmat(fname, squeeze_me=True))
        out['time'] = out['time'].astype('datetime64[m]')
        return out
    return None


def get_station(idx, deployment='latest', force_reload=False):
    """
    Get the ADCP data for a CMIST/COOPS station.

    Parameters
    ----------
    idx : string
          The case-sensitive 'Station ID' defined on the CMIST website
          (e.g., 'COI1207', 'jx0302', 'SFB1332')
    deployment : (int, or one of the strings: {'latest', 'longest'})
        Either an integer indicating the deployment #, or 'latest'
        (default) or 'longest'. NOTE: this is one-based (not zero-based).
    force_reload : bool
        Whether to force re-downloading the data, or to allow using
        cached data.
        
    """
    if isinstance(deployment, int):
        pass
    elif deployment == 'latest':
        # The last one is the latest
        deployment = station_index[idx]['nrecords']
    elif deployment == 'longest':
        deployment = station_index[idx]['longest_deployment']
    else:
        raise ValueError("Invalid value for 'deployment'.")
    if not force_reload:
        data = load_from_cache(idx, deployment)
        if data is not None:
            return data
    data = load_from_web(idx, deployment)
    data._to_cache()
    return data


def reset_cache():
    try:
        shutil.rmtree(base.cache_dir)
    except:
        pass
    os.mkdir(base.cache_dir)

