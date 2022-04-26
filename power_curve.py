import numpy as np
import matplotlib.pyplot as plt
plt.ion()

class PowerCurve(object):
    _rho = 1020

    def __init__(self, v_cutin, v_rated, rated_power=None, cp=None, capture_area=None):
        self.v_cutin = v_cutin
        self.v_rated = v_rated

        pow_flux_rated = 0.5 * self._rho * v_rated ** 3.0

        if ((rated_power is None and cp is None) or
            (rated_power is None and capture_area is None) or
            (cp is None and capture_area is None)):
            raise TypeError("You must specify at least two of the three following inputs: rated_power, cp, capture_area.")
        
        elif rated_power is None:
            rated_power = pow_flux_rated * cp * capture_area
        elif cp is None:
            cp = rated_power / (pow_flux_rated * capture_area)
        elif capture_area is None:
            capture_area = rated_power / (pow_flux_rated * cp)
            
        self.capture_area = capture_area
        self.cp = cp
        self.rated_power = rated_power

    @property
    def rotor_diameter(self, ):
        return 2 * np.sqrt(self.capture_area / np.pi)
        
    def __call__(self, vel):
        vel = np.abs(vel)
        out = 0.5 * self._rho * vel ** 3 * self.cp * self.capture_area
        out[vel < self.v_cutin] = 0
        out[vel > self.v_rated] = self.rated_power
        return out


def show_curve(pc, vel=np.arange(0, 4, 0.1), scale='MW', ax=None, color=None):

    scale_factor = dict(MW=1e6, kW=1e3, W=1)

    if scale not in scale_factor:
        raise Exception("Scale must be one of: 'MW', 'kW', 'W'.")

    if ax is None or isinstance(ax, int):
        fig = plt.figure(ax)
        fig.clf()
        fig, ax = plt.subplots(1, 1, num=fig.number)

    ax.plot(vel, pc(vel) / scale_factor[scale], color=color)
    ax.set_ylabel('Power ({})'.format(scale))
    ax.set_xlabel('Speed (m/s)')
    
    ax.set_title('Power Curve ($C_p={}, d_{{rotor}}={:.1f}m$)'.format(pc.cp, pc.rotor_diameter))

    return ax
