import cmist
import cmist.plot as cplt
import matplotlib.pyplot as plt
import matplotlib as mpl
import power_curve as pclib
import utide
mpl.use('TkAgg')
plt.ion()
from importlib import reload
reload(cplt)
import numpy as np
import tools
import pandas as pd

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
    'COI1205', # Kalgin Island (east of)
    # 'COI0507',
    # 'COI0509',
    # 'COI0510',
    # 'COI0511',
    'COI1203',
    # 'COI0419',
    # 'COI0420',
    # 'COI0512', Iliamna Bay
    # 'COI0514',
    # 'COI0515',
    # 'COI0516',
    # 'COI1202',
    # 'COI0513',
    # 'COI0421',
    # 'COI1201', Homer spit
    # 'COI0422',
    # 'COI0515',
    # 'COI0523',
    # 'COI0524',
    # 'COI0521',
    # 'COI0418',
    # 'COI0520',
]

# Define your output time range here
t_out = np.arange(np.datetime64('2013-01-01T00'),
                  np.datetime64('2023-01-01T00'),
                  np.timedelta64(1, 'h'))

figA = plt.figure(101)

pc = pclib.PowerCurve(v_cutin=0.3, v_rated=2.5, rated_power=1e6, cp=0.42)

for st in stations:
    dset = cmist.get_station(st)

    qs_fig, qs_axs = cplt.quickshow(dset, 101)

    zinds = slice(None) # This averages over the entire depth
    # Take the depth average
    VEL = dset['vel'].values[:2, zinds].mean(1)

    # What is the heading (in Degrees Clockwise from True North) of
    # the ebb-flood velocity
    THETA0 = tools.calc_principal_heading(VEL)

    # Rotate the velocity into the 'streamwise'/'crossflow' directions
    tmp = VEL[0] + 1j * VEL[1]
    tmp *= np.exp(-1j*np.pi/180*(90-THETA0)) # "(90-THETA0)" corrects for "CW from North" def of THETA0
    VEL_S, VEL_X = tmp.real, tmp.imag
    
    
    coefs = utide.solve(dset.time, VEL_S, lat=49, trend=False)

    outvel = utide.reconstruct(t_out, coefs)

    pow = pc(outvel['h'])

    data = pd.DataFrame({'vel': outvel['h'], 'power kW': pow / 1000}, index=t_out)
    data.to_csv('PowerData_CMIST-station-{}.csv'.format(st))
    
    figA.clf()
    ax = plt.axes()
    ax.plot(t_out, outvel['h'], 'r-', lw=1, label='UTide')
    ax.plot(dset.time, VEL_S, 'k-', lw=2, label='Data')

    figA.savefig('fig/FitFigure-{}.png'.format(st))
    
    hist_fig, hist_ax = cplt.scatter_hist_vel(VEL, principal_heading=THETA0)
    hist_fig.text(0.5, 0.03,
                  '{} ({})\nat z={:.1f} m'.format(dset.attrs['Station Name'],
                                                  dset.attrs['Station ID'],
                                                  dset['z'].values[zinds].mean()),
                  ha='center'
                  )

    hist_fig.savefig('fig/{}-VelHist01.png'.format(st))

    break
    
