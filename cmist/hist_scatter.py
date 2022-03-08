import numpy as np
import matplotlib.pyplot as plt


def map_hist(x, y, h, bins):
    xi = np.digitize(x, bins[0]) - 1
    yi = np.digitize(y, bins[1]) - 1
    inds = np.ravel_multi_index((xi, yi),
                                (len(bins[0]) - 1, len(bins[1]) - 1),
                                mode='clip')
    vals = h.flatten()[inds]
    bads = ((x < bins[0][0]) | (x > bins[0][-1]) |
            (y < bins[1][0]) | (y > bins[1][-1]))
    vals[bads] = np.NaN
    return vals


def scat_hist2d(x, y,
                s=20, marker=u'o',
                mode='mountain',
                bins=10, range=None,
                normed=False, weights=None,  # np.histogram2d args
                edgecolors='none',
                ax=None, dens_func=None,
                **kwargs):
    """
    Make a scattered-histogram plot.

    Parameters
    ----------
    x, y : array_like, shape (n, )
        Input data

    s : scalar or array_like, shape (n, ), optional, default: 20
        size in points^2.

    marker : `~matplotlib.markers.MarkerStyle`, optional, default: 'o'
        See `~matplotlib.markers` for more information on the different
        styles of markers scatter supports. `marker` can be either
        an instance of the class or the text shorthand for a particular
        marker.

    mode: [None | 'mountain' | 'valley' | 'clip']
       Possible values are:

       - None : The points are plotted as one scatter object, in the
         order in-which they are specified at input.

       - 'mountain' : The points are sorted/plotted in the order of
         the number of points in their 'bin'. This means that points
         in the highest density will be plotted on-top of others. This
         cleans-up the edges a bit, the points near the edges will
         overlap.

       - 'valley' : The reverse order of 'mountain'. The low density
         bins are plotted on top of the high ones.

       - 'clip' : This returns a ?LINE COLLECTION? where points are
         clipped at the edges of their boxes. Thus, there is no
         overlap, but individual (outlier) points will also be
         clipped.

    bins : int or array_like or [int, int] or [array, array], optional
        The bin specification:

          * If int, the number of bins for the two dimensions (nx=ny=bins).
          * If array_like, the bin edges for the two dimensions
            (x_edges=y_edges=bins).
          * If [int, int], the number of bins in each dimension
            (nx, ny = bins).
          * If [array, array], the bin edges in each dimension
            (x_edges, y_edges = bins).
          * A combination [int, array] or [array, int], where int
            is the number of bins and array is the bin edges.

    range : array_like, shape(2,2), optional
        The leftmost and rightmost edges of the bins along each dimension
        (if not specified explicitly in the `bins` parameters):
        ``[[xmin, xmax], [ymin, ymax]]``. All values outside of this range
        will be considered outliers and not tallied in the histogram.

    normed : bool, optional
        If False, returns the number of samples in each bin. If True,
        returns the bin density ``bin_count / sample_count / bin_area``.

    weights : array_like, shape(N,), optional
        An array of values ``w_i`` weighing each sample ``(x_i, y_i)``.
        Weights are normalized to 1 if `normed` is True. If `normed` is
        False, the values of the returned histogram are equal to the sum of
        the weights belonging to the samples falling into each bin.

    edgecolors : color or sequence of color, optional, default: 'none'
        If None, defaults to (patch.edgecolor).
        If 'face', the edge color will always be the same as
        the face color.  If it is 'none', the patch boundary will not
        be drawn.  For non-filled markers, the `edgecolors` kwarg
        is ignored; color is determined by `c`.

    ax : an axes instance to plot into.

    dens_func : function or callable (default: None)
        A function that modifies (inputs and returns) the dens
        values (e.g., np.log10). The default is to not modify the
        values, which will modify their coloring.

    kwargs : these are all passed on to scatter.

    Returns
    -------
    paths : `~matplotlib.collections.PathCollection`
        The scatter instance.
    """
    if ax is None:
        ax = plt.gca()

    h, xe, ye = np.histogram2d(x, y, bins=bins,
                               range=range, normed=normed,
                               weights=weights)
    # bins = (xe, ye)
    dens = map_hist(x, y, h, bins=(xe, ye))
    if dens_func is not None:
        dens = dens_func(dens)
    iorder = slice(None)  # No ordering by default
    if mode == 'mountain':
        iorder = np.argsort(dens)
    elif mode == 'valley':
        iorder = np.argsort(dens)[::-1]
    x = x[iorder]
    y = y[iorder]
    dens = dens[iorder]
    if hasattr(ax, 'PolarAffine'):
        x2 = np.arctan2(y, x)
        y2 = np.sqrt(x ** 2 + y ** 2)
        x, y = x2, y2
    return ax.scatter(x, y,
                      s=s, c=dens,
                      edgecolors=edgecolors,
                      marker=marker,
                      **kwargs)


def scatter_hist_vel(vel, principal_heading=None, fignum=26):

    fig = plt.figure(fignum, figsize=[5, 5])
    fig.clf()
    ax = fig.add_axes([.12, .1, .7, .85], polar=True)
    # ax.set_theta_zero_location("N")
    # ax.set_theta_direction(-1)
    scat = scat_hist2d(vel[0], vel[1],
                       bins=np.arange(-3, 3, 0.1), normed=True, vmin=0)
    theta_ticks = np.arange(0, 360, 30)
    ax.xaxis.set_ticks(theta_ticks * np.pi / 180)
    ax.xaxis.set_ticklabels(['{}°'.format((90 - tk) % 360) for tk in theta_ticks])

    th = np.arange(np.pi / 2, 0, -0.01)
    #th = np.arange(0, np.pi / 2, 0.01)
    r = np.ones_like(th) * 3.9
    x = r * np.cos(th)
    y = r * np.sin(th)
    #ax.plot(x, y, clip_on=False)
    
    r_ticks = np.arange(1, 4, 1)
    ax.yaxis.set_ticks(r_ticks)
    ax.yaxis.set_ticklabels(['{} m/s'.format(tk) for tk in r_ticks])
    # for val in r_ticks:
    #     ax.text(80 * np.pi / 180, val, '{} m/s'.format(val), )
    cbax = fig.add_axes([.9, .2, .02, .6])
    cb = plt.colorbar(scat, cax=cbax)
    ax.set_rlabel_position(87)
    ax.text(np.deg2rad(65), 3.7, 'Degrees True', rotation=-25,
            ha='center', va='bottom')
    if principal_heading is not None:
        principal_heading = (90 - principal_heading) * np.pi / 180
        ax.plot(principal_heading * np.ones(2), [0, 10], 'r--', lw=2)
        ax.plot(principal_heading * np.ones(2) + np.pi / 2, [0, 10], 'r:', lw=1)
        ax.plot(principal_heading * np.ones(2) - np.pi / 2, [0, 10], 'r:', lw=1)
        ax.plot(principal_heading * np.ones(2) + np.pi, [0, 10], 'r--', lw=1)
    # ax.set_title('Degrees True')
    # ax.set_title('Velocity {:0.0f} meters above bottom'
    #              .format(hab), pad=10,
    #              size='large')
    ax.set_rlim([0, 3.5])
    #ax.set_xlabel("Mean Velocity Probability Density (15 meters above bottom)")

    # ct = CurvedText(th, r, 'Degrees True', axes=ax, va='bottom')
    # plt.draw()
    # ct.draw()

    # pax = dict(x=np.arange(0, 10))
    # pax['y'] = pax['x'] * np.exp(1j * (principal_heading +
    #                                    np.pi / 2))
    # pax['x'] = pax['x'] * np.exp(1j * principal_heading)
    # ax.plot(pax['x'].real, pax['x'].imag, 'r--', lw=2)
    # ax.plot(pax['y'].real, pax['y'].imag, 'r:', lw=1.5)
    # ax.plot(-pax['x'].real, -pax['x'].imag, 'r:', lw=1)
    # ax.plot(-pax['y'].real, -pax['y'].imag, 'r:', lw=1)
    # ax.set_xlim([-3, 2])
    # ax.set_ylim([-2, 3])
    # ax.set_aspect('equal')

    if principal_heading is not None:
        ax.text(principal_heading, 2.8, 'u', color='r',
                ha='right', va='top',
                weight='bold',
                size='xx-large')
        ax.text(principal_heading + np.pi / 2, 2, 'v', color='r',
                ha='right', va='bottom',
                weight='bold',
                size='xx-large')
    ax.yaxis.grid(True, linestyle='--')
    ax.xaxis.grid(True, linestyle=':')
    return fig, ax
