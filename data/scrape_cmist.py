import time
import pickle as pkl
import json
from collections import defaultdict
import numpy as np
from datetime import datetime
import copy


def load_station_index():
    with open('coops_stations-full.pkl', 'rb') as fl:
        data = pkl.load(fl)
    return data


flag = defaultdict(lambda: False, {})
#flag['scrape data'] = True
#flag['process data'] = True
#flag['make kmz'] = True


def most_common(lst):
    return max(set(lst), key=lst.count)


if flag['scrape data']:

    from selenium import webdriver
    import selenium.webdriver.remote.errorhandler as err

    ####
    # Start the chrome webdriver
    if 'drv' not in vars():
        drv = webdriver.Firefox()
        drv.get('https://cmist.noaa.gov/cmist/login.do')
        drv.get('https://cmist.noaa.gov/cmist/ssl/public.do')

    ####
    # navigate to the home page
    drv.get('https://cmist.noaa.gov/cmist/requests/GetPortsStations.do?requests')
    time.sleep(1)

    ####
    # Get the station numbers
    station_codes = []
    while True:
        tmp = drv.find_element_by_id('stationTable')
        station_codes += [line.split(' ', 1)[0] for line in tmp.text.split('\n')[1:]]
        try:
            el = drv.find_element_by_link_text('Next 100')
        except err.NoSuchElementException:
            try:
                el = drv.find_element_by_link_text('Last 63')
            except err.NoSuchElementException:
                break
        el.click()
        time.sleep(0.1)

    ####
    # Now iterate over the stations and grab the data for each.
    fulldat = {}
    for idx, code in enumerate(station_codes):
        drv.get('https://cmist.noaa.gov/cmist/requests/selectdata.do?stationid={}'.format(code))
        try:
            head = drv.find_element_by_id('stationTable').find_elements_by_tag_name('td')
        except err.NoSuchElementException:
            continue
        rows = drv.find_element_by_id('deploymentTable').find_elements_by_tag_name('tr')
        fulldat[code] = dict(station_name=head[1].text.lstrip().rstrip(),
                             project=head[2].text.lstrip().rstrip(),
                             sensor=[],
                             time_range=[],
                             lonlat=[],
        )
        for rw in rows[2:]:
            vals = rw.find_elements_by_tag_name('td')
            fulldat[code]['sensor'] += [vals[1].text]
            fulldat[code]['time_range'] += [(vals[2].text,
                                            vals[3].text)]
            fulldat[code]['lonlat'] += [(float(vals[5].text),
                                        float(vals[4].text))]
        time.sleep(0.1)
        # if idx == 3:
        #     break

    ####
    # Save the data
    with open('coops_stations-full.pkl', 'wb') as fl:
        pkl.dump(fulldat, fl)
    with open('coops_stations-full.json', 'w') as fl:
        json.dump(fulldat, fl, indent=4, sort_keys=True)

else:

    ####
    # Load the data
    fulldat = load_station_index()


if flag['process data']:

    # This is a reprocessing step.
    procdat = copy.deepcopy(fulldat)
    for tag, site in procdat.items():
        site['link'] = 'https://cmist.noaa.gov/cmist/requests/selectdata.do?stationid={}'.format(tag)
        # There are some typos in the source data:
        if tag == 'cb0801':
            site['lonlat'][20] = site['lonlat'][19]
            site['lonlat'][21] = site['lonlat'][19]
            site['lonlat'][22] = site['lonlat'][19]
        elif tag == 'cb0402':
            site['lonlat'][0] = site['lonlat'][2]
            site['lonlat'][1] = site['lonlat'][2]
        elif tag == 'nb0201':
            site['lonlat'][3] = site['lonlat'][0]
        elif tag == 'mg0101':
            site['lonlat'][0] = site['lonlat'][1]

        lonlat = np.array(site['lonlat']).T
        lonlat_ = lonlat.mean(1)
        if (np.abs((lonlat - lonlat_[:, None])) > 0.1).any():
            raise Exception("This is not one site!")
        site['deployments'] = dict(lonlat=site['lonlat'],
                                   sensor=site['sensor'],
                                   time_range=site['time_range'], )
        site['sensor'] = most_common(site['sensor'])
        site['lonlat'] = lonlat_.tolist()
        tmp = [0]
        for tr in site['time_range']:
            if tr[1] == 'n/a':
                continue
            dt = (datetime.strptime(tr[1],
                                    '%Y-%m-%d %H:%M:%S') -
                  datetime.strptime(tr[0],
                                    '%Y-%m-%d %H:%M:%S'))
            tmp.append(dt.total_seconds() / 3600. / 24)
        site.pop('time_range')
        site['total_days'] = np.sum(tmp)
        site['longest_record_days'] = max(tmp)
        site['nrecords'] = len(tmp) - 1

    with open('coops_stations.json', 'w') as fl:
        json.dump(procdat, fl, indent=4, sort_keys=True)

else:
    with open('coops_stations.json', 'rb') as fl:
        procdat = json.load(fl)


if flag['make kmz']:
    import simplekml as kml

    k = kml.Kml(name='NOAA C-MIST stations')

    fldr = k

    for tag in np.sort(procdat.keys()):
        site = procdat[tag]
        lon = site['lonlat'][0]
        lat = site['lonlat'][1]
        pt = fldr.newpoint(name=tag, coords=[(lon, lat)])
        # pt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png'
        # pt.iconstyle.hotspot = kml.HotSpot(x=0.5, y=0,
        #                                    xunits='fraction',
        #                                    yunits='fraction')
        # cl = 'FF' + cl[5:] + cl[3:5] + cl[1:3]
        # pt.style.iconstyle.color = cl
        ed = kml.ExtendedData()
        nm = site['station_name']
        nm = nm.replace('&', '+')
        ed.newdata('name', str(nm), 'Station Name')
        ed.newdata('sensor', str(site['sensor']), 'Sensor (most common)')
        ed.newdata('time', str(site['total_days']), 'Total Time (days)')
        ed.newdata('longest', str(site['longest_record_days']), 'Longest Record (days)')
        ed.newdata('nrecords', str(site['nrecords']), 'Number of records')
        ed.newdata('link', site['link'], 'link')
        pt.extendeddata = ed

    # k.document.lookat = kml.LookAt(
    #     gxaltitudemode=kml.GxAltitudeMode.relativetoseafloor,
    #     latitude=44., longitude=-126, range=2.4E6,
    #     heading=0, tilt=0)

    k.savekmz('NOAA_CMIST_Sites.kmz')
