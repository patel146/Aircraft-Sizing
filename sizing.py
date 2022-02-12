import math
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# input travel range in nmi, c_shp as lb/hr*hp
'''FUNCTION VERIFIED ACCURATE'''


def ff_cruise(travel_range, c_shp, prop_eff, LoD):
    travel_range = travel_range * 6076  # converts nmi to ft
    c_shp = c_shp / 3600  # converts lb/hr*hp to lb/hp*sec
    return math.exp((-travel_range * c_shp) / (550 * prop_eff * LoD))


# input time_req in minutes, speed in knots, c_shp in lb/hr*hp
'''FUNCTION VERIFIED ACCURATE'''


def ff_loiter(time_req, speed, c_shp, LoD, prop_eff):
    time_req = time_req * 60  # minutes => seconds
    speed = speed * (6076 / 3600)  # knots => ft/s
    c_shp = c_shp / 3600  # => lb/hp*sec
    LoD = LoD * 0.866
    return math.exp((-time_req * speed * c_shp) / (550 * prop_eff * LoD))


class Aircraft:
    ffs = []

    def __init__(self, LoD_max, ff_warmup, ff_taxi, ff_takeoff, ff_climb, ff_descent, ff_landing, cruise_leg):
        self.LoD_max = LoD_max
        self.ff_warmup = ff_warmup
        self.ff_taxi = ff_taxi
        self.ff_takeoff = ff_takeoff
        self.ff_climb = ff_climb
        self.ff_Cruise = ff_cruise(cruise_leg, 0.4, 0.8, self.LoD_max)
        self.ff_descent = ff_descent
        self.ff_landing = ff_landing
        self.ff_Loiter = ff_loiter(45, 100, 0.5, self.LoD_max, 0.7)
        self.ffs = list(self.__dict__.values())
        self.ffs.remove(self.LoD_max)


class Mission:
    # ff stands for fuel fraction of various mission phases

    mission_sequence = []

    def __init__(self, leg_range, warmup=1, taxi=1, takeoff=1, climb=1, cruise=1, descent=1, landing=1,
                 loiter=1, stops=0):
        self.warmup = warmup
        self.taxi = taxi * 2
        self.takeoff = takeoff
        self.climb = climb
        self.Cruise = cruise
        self.descent = descent
        self.landing = landing
        self.mission_sequence = list(self.__dict__.values())
        self.stops = stops
        if self.stops >= 1:
            for i, segment in enumerate(self.mission_sequence):
                self.mission_sequence[i] = segment * (self.stops + 1)
        self.loiter = loiter
        self.mission_sequence.append(self.loiter)
        self.leg_range = leg_range
        print(f"{self.stops} stop mission sequence: {self.mission_sequence}")


# set up aircraft
concept_aircraft_ferry = Aircraft(17, 0.990, 0.995, 0.995, 0.985, 0.985, 0.995, 1200)
concept_aircraft_cargo = Aircraft(17, 0.990, 0.995, 0.995, 0.985, 0.985, 0.995, 750)
concept_aircraft_multistop = Aircraft(17, 0.990, 0.995, 0.995, 0.985, 0.985, 0.995, 75)

# use ff)_cruise function for ff_Cruise attribute
ferry_mission = Mission(1200)
cargo_mission = Mission(750)
multistop_mission = Mission(75, stops=2)


def sizing(Wo_guess, mission, W_payload, W_crew, LoD, leg_range):
    A = 1.04
    power = 0.94

    aircraft = Aircraft(LoD, 0.990, 0.995, 0.995, 0.985, 0.985, 0.995, leg_range)

    def combined_ff():
        ff_list = aircraft.ffs
        Combined_ff_temp = 1

        for i, ff in enumerate(ff_list):
            # print(f"{mission.mission_sequence[i]} : {ff}")
            if mission.mission_sequence[i] >= 1:
                for e in range(mission.mission_sequence[i]):
                    Combined_ff_temp *= ff
        return Combined_ff_temp

    Combined_ff = combined_ff()
    print(f"total_fuel_fraction {Combined_ff}")

    fuel_weight = 1.06 * (Wo_guess - (Combined_ff * Wo_guess))
    FUEL_WEIGHT_FRACTION = fuel_weight / Wo_guess

    EMPTY_WEIGHT_FRACTION = A * Wo_guess ** (power - 1)

    W_fixed = W_payload + W_crew
    FIXED_WEIGHT_FRACTION = W_fixed / Wo_guess

    Wo_actual = W_fixed / (1 - (FUEL_WEIGHT_FRACTION + EMPTY_WEIGHT_FRACTION))
    diff = Wo_actual - Wo_guess

    GROWTH_FACTOR = 1 / (FUEL_WEIGHT_FRACTION + EMPTY_WEIGHT_FRACTION)

    # print(f"overall fuel fraction: {Combined_ff}")
    # print(f"starting weight: {Wo_guess}")
    # print(f"weight after mission: {Combined_ff * Wo_guess}")
    # print(f"weight of fuel required for mission: {fuel_weight}")
    # print(f"FUEL WEIGHT FRACTION: {FUEL_WEIGHT_FRACTION}")
    # print(f"EMPTY_WEIGHT_FRACTION: {EMPTY_WEIGHT_FRACTION}")
    print(f"Actual MTOW: {Wo_actual}")
    print(f"difference between actual and guess {diff}")

    def pieChart():
        labels = 'fuel', 'empty', 'fixed'
        sizes = [FUEL_WEIGHT_FRACTION, EMPTY_WEIGHT_FRACTION, FIXED_WEIGHT_FRACTION]

        plt.pie(sizes, labels=labels)
        plt.show()

    return Wo_actual, diff, GROWTH_FACTOR


def recursion(initial_guess, W_fixed, LoD, mission):
    print(mission.leg_range)
    while True:
        actual, diff, growth_fac = sizing(initial_guess, mission, W_fixed / 2, W_fixed / 2, LoD, mission.leg_range)
        initial_guess += 0.1
        if abs(diff) < 0.1:
            return actual, diff, growth_fac


'''MISSION SIZING'''
# print(recursion(2200, 410 + 0, 17, ferry_mission))
# print(recursion(7500, 410 + 1700, 17, cargo_mission))
# print(recursion(9500, 410 + 1640, 17, multistop_mission))

x = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]  # LOD
y = [10544.327620937562, 10370.387033873107, 10228.817500440407, 10111.389766296217, 10012.39486210787,
     9927.802512940885, 9854.707467944701, 9790.905320599728, 9734.735942301702, 9684.893539493783]


# for i in range(10):
#     input_LoD = 10 + i
#     x.append(input_LoD)
#     y.append(recursion(9600, 2050, input_LoD, multistop_mission)[0])

def trade_study():
    plt.figure(facecolor='white')
    ax = plt.axes()

    ax.plot(x, y, ms=4, ls='-.', markevery=[1], linewidth=2.0, color='black', label='Takeoff weight')

    plt.text(2, 8, 'testing')
    plt.xlabel(r"$\frac{L}{D}_{max}$ $[-]$", fontname='serif', fontsize=12)
    plt.xlim(9, 20)
    plt.ylabel(r"$W_o$ $[lb_f]$", fontname='serif', fontsize=12)

    # plt.xticks(fontsize=10, fontname='serif')
    # plt.yticks(fontsize=10, fontname='serif')
    # plt.tick_params(
    #     axis='both',
    #     which='both',
    #     bottom=True,
    #     top=False,
    #     left=True,
    #     right=False
    # )
    ax.grid(linestyle=':', color='black', alpha=0.5, linewidth=0.5)
    plt.show()


w_o_actuals = []
w_pay_inputs = []
Lods = []

for e in range(5):
    for i in range(10):
        pay_values = 1000 + i * 100
        Lod_values = 15 + e
        w_o_actuals.append(recursion(4000, pay_values, Lod_values, ferry_mission)[0])
        w_pay_inputs.append(pay_values)
        Lods.append(Lod_values)

print(w_o_actuals)

fig = go.Figure(go.Carpet(
    a=Lods,
    b=w_pay_inputs,
    y=w_o_actuals,
    aaxis=dict(
        tickprefix='LoD = ',
        smoothing=1,
        minorgridcount=1, ),
    baxis=dict(
        tickprefix='W_pay = ',
        ticksuffix='lbm',
        smoothing=1,
        minorgridcount=1,
    )))

fig.show()

print(w_o_actuals)
print(w_pay_inputs)
print(Lods)
