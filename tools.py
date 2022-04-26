import numpy as np

def calc_principal_heading(vel, tidal_mode=True):
    """Compute the principal angle of the horizontal velocity.

    Parameters
    ----------
    vel : np.ndarray (2,...,Nt), or (3,...,Nt)
      The 2D or 3D velocity array (3rd-dim is ignored in this calculation)
    tidal_mode : bool (default: True)

    Returns
    -------
    p_heading : float or ndarray
      The principal heading in degrees clockwise from North.

    Notes
    -----
    When tidal_mode=True, this tool calculates the heading that is
    aligned with the bidirectional flow. It does so following these
    steps:
      1. rotates vectors with negative velocity by 180 degrees
      2. then doubles those angles to make a complete circle again
      3. computes a mean direction from this, and halves that angle
         (to undo the doubled-angles in step 2)
      4. The returned angle is forced to be between 0 and 180. So, you
         may need to add 180 to this if you want your positive
         direction to be in the western-half of the plane.

    Otherwise, this function simply computes the average direction
    using a vector method.

    """
    dt = vel[0] + vel[1] * 1j
    if tidal_mode:
        # Flip all vectors that are below the x-axis
        dt[dt.imag <= 0] *= -1
        # Now double the angle, so that angles near pi and 0 get averaged
        # together correctly:
        dt *= np.exp(1j * np.angle(dt))
        dt = np.ma.masked_invalid(dt)
        # Divide the angle by 2 to remove the doubling done on the previous
        # line.
        pang = np.angle(
            np.nanmean(dt, -1, dtype=np.complex128)) / 2
    else:
        pang = np.angle(np.nanmean(dt, -1))

    return np.round((90 - np.rad2deg(pang)), decimals=4)
