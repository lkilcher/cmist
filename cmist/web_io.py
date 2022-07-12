from selenium import webdriver
import selenium.webdriver.remote.errorhandler as err
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import zipfile
import numpy as np
import time
from . import base
import os, shutil
from xarray import Dataset


# This is just a pointer (holds a slot in memory)
_driver = [None, ]


def get_driver():
    """Load/reload the selenium webdriver, and login to the cmist webpage."""
    drv = _driver[0]
    try:
        drv.get_window_size()
        old_driver = True
    except:
        print('Reloading webdriver...', end=' ')
        # Start the webdriver
        try:
            chromeOptions = webdriver.ChromeOptions()
            prefs = {"download.default_directory": base.cache_dir}
            chromeOptions.add_experimental_option("prefs", prefs)
            drv = webdriver.Chrome(chrome_options=chromeOptions)
            drv.get('https://cmist.noaa.gov/cmist/login.do')
            drv.get('https://cmist.noaa.gov/cmist/ssl/public.do')
        except err.WebDriverException:
            profile = webdriver.FirefoxProfile()
            profile.set_preference("browser.download.dir", base.cache_dir)
            profile.set_preference('browser.download.folderList', 2)
            profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/octet-stream')
            profile.set_preference("browser.download.manager.showWhenStarting", False)
            profile.set_preference("browser.helperApps.alwaysAsk.force", False)
            profile.set_preference("browser.download.manager.useWindow", False)
            profile.set_preference("browser.download.manager.focusWhenStarting", False)
            profile.set_preference("browser.download.manager.showAlertOnComplete", False)
            profile.set_preference("browser.download.manager.closeWhenDone", True)
            drv = webdriver.Firefox(profile)
            drv.get('https://cmist.noaa.gov/cmist/login.do')
            drv.get('https://cmist.noaa.gov/cmist/ssl/public.do')
        old_driver = False
        print('done.')
    if old_driver:
        drv.get('https://cmist.noaa.gov/cmist/ssl/welcome.do')
        if 'Welcome, Public' not in drv.page_source:
            print('Logging in again...', end=' ')
            drv.get('https://cmist.noaa.gov/cmist/login.do')
            drv.get('https://cmist.noaa.gov/cmist/ssl/public.do')
            print('done.')
    _driver[0] = drv
    return drv


def read_bin(file):
    dtype = ['datetime64[m]', ] + ['float'] * 6
    return np.genfromtxt(file, dtype=dtype, delimiter=',', names=True)


def read_header(file):
    dtype = ['datetime64[m]', ] + ['float'] * 7
    return np.genfromtxt(file, dtype=dtype, delimiter=',', names=True)


def read_metadata(fl):
    out = {}
    out['z'] = []
    for ln in fl:
        ln = ln.decode('utf8')
        if len(ln) <= 2 or \
           ln.startswith('#') or \
           ln.startswith('Metadata'):
            continue
        nm, val = ln.split(':', 1)
        nm = nm.rstrip()
        val = val.lstrip(' ').rstrip('\r\n')
        try:
            val = float(val)
        except:
            pass
        if nm.startswith('Bin') and nm.endswith('Est. Depth'):
            out['z'].append(float(val.rstrip('m')))
        else:
            out[nm] = val
    out['z'] = -np.array(out['z'])
    return out


def align_time(time0, time1):
    """
    Make sure the two time vectors align. If they don't, step through
    and find the matches.

    This function assumes that `time0` is correct, and that `time1` may
    have gaps.

    This function returns an 'indexing object' (either a `slice`, or a
    boolean array).
    """
    # First we check if the two times are the same.
    if np.array_equal(time0, time1):
        # If they are, we just return a "slice-all" object.
        return slice(None)
    # Otherwise, we need to find the ones that match...
    # Here I create a 'boolean array' (see: http://tinyurl.com/hx3f49n)
    out = np.zeros(len(time0), dtype=bool)
    # idx1 and idx0 are index (a.k.a. 'counting') variables that keep
    # track of position in each array
    idx1 = 0
    for idx0 in range(len(time0)):
        # `idx0` is always stepped forward 1
        if time0[idx0] == time1[idx1]:
            # Match! So, we can set this index to 'good'
            out[idx0] = True
            idx1 += 1  # advance the 'count' for time1
            # Otherwise, we DO NOT advance this count.
            # I don't need an 'else' statement here
    return out


def read_cmist_zip(fname):
    fnm = fname.split('/')[-1].split('.')[0]
    dtmp = {}
    with zipfile.ZipFile(fname) as zfl:
        for nm in zfl.namelist():
            if nm.startswith(fnm + '/' + fnm + '-bin') and nm.endswith('.csv'):
                idx = int(nm.split('bin')[-1].split('.')[0]) - 1
                with zfl.open(nm) as fl:
                    dtmp[idx] = read_bin(fl)
            if nm.endswith('metadata.dat'):
                with zfl.open(nm) as fl:
                    meta = read_metadata(fl)
            if nm.endswith('-hdr.csv'):
                with zfl.open(nm) as fl:
                    hdr = read_header(fl)
    nrows = len(dtmp)
    out = dict()
    out['time'] = hdr['DATE_TIME']
    ncols = len(out['time'])
    for nm in ['HEADING', 'PITCH', 'ROLL', 'TEMPERATURE', 'PRESSURE', 'DEPTH']:
        out[nm.lower()] = hdr[nm]
    # We default the 'vel' array to be np.NaN (not-a-number), so that
    # values we don't assign below, have this value.
    out['vel'] = np.empty((3, nrows, ncols), dtype=np.float32) * np.NaN
    out.update(**meta)
    for idx in range(nrows):
        inds = align_time(out['time'], dtmp[idx]['DATE_TIME'])
        # inds is either the `slice-all` (equivalent to a ":"), or the boolean array
        # If the latter, only the values that are 'True' get assigned from the right to left
        out['vel'][0, idx, inds] = dtmp[idx]['VEL_EAST'] / 100.
        out['vel'][1, idx, inds] = dtmp[idx]['VEL_NORTH'] / 100.
        out['vel'][2, idx, inds] = dtmp[idx]['VEL_VERT'] / 100.
    dset = Dataset(
        data_vars=dict(
            vel=(['ENU', 'z', 'time',], out.pop('vel')),
            pressure=(['time'], out.pop('pressure')),
            temperature=(['time'], out.pop('temperature')),
            depth=(['time'], out.pop('depth')),
            heading=(['time'], out.pop('heading')),
            pitch=(['time'], out.pop('pitch')),
            roll=(['time'], out.pop('roll')),
        ), 
        coords=dict(
            ENU=(['ENU'], ['East', 'North', 'Up']),
            time=(['time'], out.pop('time')),
            z=(['z'], out.pop('z'))
        ),
    )
    dset['vel'].attrs['units'] = 'm/s'
    dset['temperature'].attrs['units'] = 'Celsius'
    dset['heading'].attrs['units'] = 'degrees'
    dset['pitch'].attrs['units'] = 'degrees'
    dset['roll'].attrs['units'] = 'degrees'
    dset['pressure'].attrs['units'] = 'dBar'
    dset['depth'].attrs['units'] = 'm'
    dset['z'].attrs['units'] = 'm (relative to sea level)'
    dset['time'].attrs['timezone'] = 'UTC'
    for ky in out:
        if '/' in ky:
            nky = ky.replace('/', '-')
        else:
            nky = ky
        dset.attrs[nky] = out[ky]
    return dset


def download(idx, deployment):
    info = base.station_index[idx]
    t_range = info['deployments']['time_range'][deployment - 1]
    drv = get_driver()
    drv.get(base.station_index[idx]['link'])
    # Set the start time:
    if t_range[0].upper() != 'N/A':
        inp = drv.find_element(By.ID,"startDateTime")
        inp.clear()
        inp.send_keys(t_range[0])
    if t_range[1].upper() != 'N/A':
        inp = drv.find_element(By.ID,"endDateTime")
        inp.clear()
        inp.send_keys(t_range[1])
    # Set the datatype to get all data
    slct = Select(drv.find_element(By.NAME,'datatype'))
    slct.select_by_visible_text('Speed/Direction/Ancillary Data')
    # Set the format to CSV:
    slct = Select(drv.find_element(By.NAME,'format'))
    slct.select_by_visible_text('CSV')
    # Now get the data:
    elm = drv.find_element(By.ID,'submitBtn')
    elm.click()
    while True:
        try:
            btn = drv.find_element(By.CLASS_NAME,'btn-primary')
            break
        except err.NoSuchElementException:
            # The button isn't here, so keep waiting...
            time.sleep(1)
    # Click the download button!
    btn.click()
    return base.cache_dir + btn.text


def load_from_web(idx, deployment):
    fname = download(idx, deployment)
    #print(fname)
    path, fname2 = os.path.split(fname)
    fname2 = os.path.expanduser('~/Downloads/' + fname2)
    print(fname2)
    n = 0
    while n < 600:
        # Wait for one minute 600 * 0.1 = 60 seconds
        # check if the file was actually downloaded to <user>/Downloads/
        # This happens on MSWin, even though I don't think it should.
        if os.path.isfile(fname2):
            print("Moving file {}".format(fname2))
            shutil.move(fname2, fname)
        if os.path.isfile(fname):
            break
        #print(n)    
        n = n + 1
        time.sleep(0.1)
        
    data = read_cmist_zip(fname)
    data.attrs['deployment'] = deployment
    data.attrs['_zipfilename_'] = fname
    return data
