import matplotlib.pyplot as plt
import matplotlib as mpl
from .hist_scatter import scatter_hist_vel


def quickshow(dset, fignum=None, figsize=[8, 6]):
    fig = plt.figure(fignum, figsize=figsize)
    fig.clf()
    fig, axs = plt.subplots(3, 1,
                            sharex=True, sharey=True,
                            num=fig.number,
                            )
    pcol_args = dict(
        u=dict(
            cmap=plt.get_cmap('seismic'),
            vmin= -3, vmax=3, 
        ),
        v=dict(
            cmap=plt.get_cmap('seismic'),
            vmin= -3, vmax=3, 
        ), 
        w=dict(
            cmap=plt.get_cmap('seismic'),
            vmin= -0.3, vmax=0.3, 
        ), 
    )
    
    for iax, ax in enumerate(axs):
        pc_args = pcol_args[['u', 'v', 'w'][iax]]
        ax.pcolormesh(dset['time'].values, dset['z'], dset['vel'][iax],
                      **pc_args)

    return fig, axs
