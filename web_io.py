from __future__ import print_function
from selenium import webdriver
import selenium.webdriver.remote.errorhandler as err
from selenium.webdriver.support.ui import Select
import zipfile
import numpy as np
import time
import base
import os


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
        chromeOptions = webdriver.ChromeOptions()
        prefs = {"download.default_directory": base.cache_dir}
        chromeOptions.add_experimental_option("prefs", prefs)
        drv = webdriver.Chrome(chrome_options=chromeOptions)
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
    ncols = len(dtmp[0])
    out = base.veldata()
    out['time'] = hdr['DATE_TIME']
    for nm in ['HEADING', 'PITCH', 'ROLL', 'TEMPERATURE', 'PRESSURE', 'DEPTH']:
        out[nm.lower()] = hdr[nm]
    out['vel'] = np.empty((3, nrows, ncols), dtype=np.float32)
    out.update(**meta)
    for idx in range(nrows):
        out['vel'][0, idx, :] = dtmp[idx]['VEL_EAST']
        out['vel'][1, idx, :] = dtmp[idx]['VEL_NORTH']
        out['vel'][2, idx, :] = dtmp[idx]['VEL_VERT']
    return out


def download(idx, ):
    drv = get_driver()
    drv.get(base.station_index[idx]['link'])
    # Set the datatype to get all data
    slct = Select(drv.find_element_by_name('datatype'))
    slct.select_by_visible_text('Speed/Direction/Ancillary Data')
    # Set the format to CSV:
    slct = Select(drv.find_element_by_name('format'))
    slct.select_by_visible_text('CSV')
    # Now get the data:
    elm = drv.find_element_by_id('submitBtn')
    elm.click()
    while True:
        try:
            btn = drv.find_element_by_class_name('btn-primary')
            break
        except err.NoSuchElementException:
            # The button isn't here, so keep waiting...
            time.sleep(1)
    # Click the download button!
    btn.click()
    return base.cache_dir + btn.text


def load_from_web(idx):
    fname = download(idx)
    while True:
        if os.path.isfile(fname):
            break
        time.sleep(0.1)
    data = read_cmist_zip(fname)
    os.remove(fname)
    return data
