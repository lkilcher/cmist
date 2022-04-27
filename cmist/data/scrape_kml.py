import fastkml
import zipfile
import numpy as np
import cPickle as pkl


def parse_noaa_kmz(fname):

    with zipfile.ZipFile(fname) as zfl:
        with zfl.open('doc.kml') as fl:
            outfile = fl.read()

    kml = fastkml.KML()

    kml.from_string(outfile)

    # There is a 'doc' and a 'folder'
    features = list(list(list(kml.features())[0].features())[0].features())

    outdat = {varnm: np.empty(len(features), dtype=dtype)
              for varnm, dtype in [('num', 'S10'),
                                   ('name', 'S50'),
                                   ('lon', np.float32),
                                   ('lat', np.float32),
                                   ('DEPLOY', np.int8),
                                   ('RECOVER', np.int8),
                                   ('Duration', np.float32),
                                   ('Depth', np.float32),
                                   ('Inst', 'S10'),
                                   ('Platform', 'S30'),
              ]}

    for idx, feat in enumerate(features):
        tmp = feat.extended_data.elements[0]
        outdat['num'][idx] = feat.name
        outdat['name'][idx] = tmp.data[1]['value']
        outdat['lat'][idx] = tmp.data[2]['value']
        outdat['lon'][idx] = tmp.data[3]['value']
        outdat['DEPLOY'][idx] = tmp.data[4]['value']
        outdat['RECOVER'][idx] = tmp.data[5]['value']
        outdat['Duration'][idx] = tmp.data[6]['value']
        outdat['Depth'][idx] = tmp.data[7]['value']
        outdat['Inst'][idx] = tmp.data[8]['value']
        outdat['Platform'][idx] = tmp.data[9]['value']

    return outdat
        
dat2016 = parse_noaa_kmz('Puget2016-2dep.kmz')
dat2016['year'] = np.ones_like(dat2016['num'], dtype=np.int16) * 2016
dat2017 = parse_noaa_kmz('Puget2017-3dep.kmz')
dat2017['year'] = np.ones_like(dat2017['num'], dtype=np.int16) * 2017

dat = {}
for fld in dat2016:
    dat[fld] = np.hstack((dat2016[fld], dat2017[fld]))

with file('coops_planned.pkl', 'w') as fl:
    pkl.dump(dat, fl)
