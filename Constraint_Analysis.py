import math as m
import matplotlib.pyplot as plt
import numpy as np

p_sl = 0.002377  # slug/ft^3
pressure_sl = 2116.2  # lbf/ft^2

BETA = 1
Q = 222.93
ALPHA = 0.2905
CDO = 0.02060
K = 0.03745
ROC = 0
g = 32.1740  # ft/s^2
ACC = 0
V = 762.45

service_ceiling = 41000  # ft
cruise_speed = 793.84  # ft/s


def temperature_ratio(alt):
    if alt < 36089:
        return 1 - (alt / 145454)
    else:
        return 0.7519


def pressure_ratio(alt):
    if alt <= 36089:
        return temperature_ratio(alt) ** 5.2621
    else:
        return 0.233 * m.exp(-((alt - 36089) / 20790))


def density_ratio(alt):
    if alt <= 36089:
        return temperature_ratio(alt) ** 4.2621
    else:
        return 0.297 * m.exp(-((alt - 36089) / 20790))


def pressure(alt=0):
    return pressure_ratio(alt) * pressure_sl


def density(alt=0):
    return density_ratio(alt) * p_sl


def sound_speed(alt=0):
    if alt <= 36089:
        return m.sqrt(temperature_ratio(alt)) * 1116
    else:
        return 968  # ft/ sec


# V in ft/s
def get_q(alt, V):
    return 0.5 * density(alt) * V ** 2


def alpha(p, prop_eff, V):
    return (p / p_sl) * (prop_eff / V)


def get_K(e, AR):
    return 1 / (m.pi * e * AR)


def Cdo(LDmax, K):
    return 1 / (4 * LDmax ** 2 * K)


def TWratio(beta, alpha, q, WoSratio, Cdo, K, n, V, ROC, g, acc):
    return (beta / alpha) * (
            ((q / beta) * (WoSratio) ** -1) * (
            Cdo + K * ((n * beta * WoSratio) / (q)) ** 2) + ROC * V ** -1 + acc * g ** -1)


def TWratioTakeoff(fobs, fms, fv, clmaxto, stofl, WSRatio, Cdo, rolling_coef):
    return fobs * fms * ((fv) / (density() * 32.1740 * clmaxto * stofl)) * WSRatio + (
            (0.7 * Cdo) / (clmaxto)) + rolling_coef


def WSratioLanding(fms, slfl, hobs, angle, rolling_coef, clmaxl, fv, cdol):
    a = (slfl - (hobs / (fms * m.tan(m.radians(angle)))))
    b = density() * g
    c = rolling_coef * clmaxl
    d = (0.7 * fv) ** 2 * cdol
    e = fms / fv ** 2
    return a * b * (c + d) * e


x_cruise = []
y_cruise = []

x_ceiling = []
y_ceiling = []

x_takeoff = []
y_takeoff = []

x_landing = []
y_landing = np.arange(0, 2, 0.02)


def plot():
    for i in range(100):
        WoS_inc = 0.1 + i * 0.1
        # Getting cruise constraint
        # ToWo_inc_cruise = TWratio(BETA, ALPHA, Q, WoS_inc, CDO, K, 1, V, 0, g, ACC)
        ToWo_inc_cruise = TWratio(0.9654, 0.62856, 76.88, WoS_inc, 0.01864, 0.0464, 1, 286.928, 0, g, 0)
        x_cruise.append(WoS_inc)
        y_cruise.append(ToWo_inc_cruise)

        # Getting service ceiling constraint
        # ToWo_inc_cruise = TWratio(BETA, ALPHA, Q, WoS_inc, CDO, K, 1, V, ROC, g, ACC)
        ToWo_inc_ceiling = TWratio(0.956, 0.4258, 51.75, WoS_inc, 0.01864, 0.0464, 1,
                                   286.928,
                                   8.33, g, ACC)
        x_ceiling.append(WoS_inc)
        y_ceiling.append(ToWo_inc_ceiling)

        # Getting takeoff field length constraint
        # TWratioTakeoff(fobs, fms, fv, clmaxto, stofl, WSRatio, Cdo, rolling_coef)
        ToWo_inc_takeoff = TWratioTakeoff(1.17, 1.15, 1.21, 2, 2000, WoS_inc, 0.05864, 0.025)
        x_takeoff.append(WoS_inc)
        y_takeoff.append(ToWo_inc_takeoff)

        # Getting landing field length constraint
        # WSratioLanding(fms, slfl, hobs, angle, rolling_coef, clmaxl, fv, cdol)
        landing_WS = WSratioLanding(1.15, 1800, 50, 3, 0.025, 2.5, 1.3, 0.05864)
        x_landing.append(landing_WS)

    plt.plot(x_cruise, y_cruise, label="cruise constraint", color="black", linestyle="dotted")
    plt.plot(x_ceiling, y_ceiling, label="service ceiling constraint", color="black", linestyle="solid")
    plt.plot(x_takeoff, y_takeoff, label="takeoff field length constraint", color="black", linestyle="dashed")
    plt.plot(x_landing, y_landing, label="landing field length constraint", color="black", linestyle="dashdot")
    plt.xlim(0, 6)
    plt.ylim(0, 1)
    plt.legend()
    plt.xlabel(r"$\frac{W}{S}$")
    plt.ylabel(r"$\frac{T}{W}$")
    plt.fill_between(np.arange(0.1, 5.7, 0.1), y_ceiling[:56], 1, color='black', alpha=0.25)
    plt.show()


# print(service_ceiling)
# print(cruise_speed)
# print(get_q(service_ceiling, cruise_speed))

plot()
