import cmist
import cmist.plot as cplt
import matplotlib.pyplot as plt
plt.ion()
from importlib import reload
reload(cplt)

stations = [
    # 'COI0301',
    # 'COI0302',
    # 'COI0303',
    # 'COI0206',
#    'COI0207',
    # 'COI0213',
    # 'COI1209',
    # 'COI1208',
    # 'COI1207',
    # 'COI0307',
    # 'COI0306',
    # 'COI1204', # North Foreland
    # 'COI1210',
    # 'COI0503', # East Foreland
    # 'COI0502', # Between forelands
    # 'COI0501', # West Foreland
    # 'COI0801', 
    # 'COI0802', 
    # 'COI0504', 
    # 'COI0506', # Kenai River
    # 'COI0505',
    # 'COI0508',
    # 'COI1205', # Kalgin Island (east of)
    # 'COI0507',
    # 'COI0509',
    # 'COI0510',
#    'COI0511',
    # 'COI1203',
    # 'COI0419',
    # 'COI0420',
    # 'COI0512', # Iliamna Bay
    # 'COI0514',
    # 'COI0515',
    # 'COI0516',
    # 'COI1202',
    # 'COI0513',
    # 'COI0421',
     'COI1201', # Homer spit
    # 'COI0422',
    # 'COI0515',
    # 'COI0523',
    # 'COI0524',
    # 'COI0521',
    # 'COI0418',
    # 'COI0520',
]

for st in stations:
    dset = cmist.get_station(st)

    qs_fig, qs_axs = cplt.quickshow(dset, 101)

    zinds = slice(-5, None)
    hist_fig, hist_ax = cplt.scatter_hist_vel(dset['vel'].values[:2, zinds].mean(1))
    hist_fig.text(0.5, 0.03,
                  '{} ({})\nat z={:.1f} m'.format(dset.attrs['Station Name'],
                                                  dset.attrs['Station ID'],
                                                  dset['z'].values[zinds].mean()),
                  ha='center'
                  )

    hist_fig.savefig('fig/{}-VelHist01.png'.format(st))
    qs_fig.savefig('fig/{}-qsFig01.png'.format(st))

    break
