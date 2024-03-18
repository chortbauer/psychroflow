# -*- coding: utf-8 -*-
"""
just for testing
Created on 2024-01-22 07:30:30
@author: orc
"""

# pylint: disable=unused-import

import pprint
import importlib

import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt

import psychroflow as psf

PrettyPrinter = pprint.PrettyPrinter(underscore_numbers=True)
pp = PrettyPrinter.pprint

# t_range = np.linspace(1,100,20)
# for t in t_range:
#     print(t , psf.get_density_water(t))

hafs = []

has1 = psf.HumidAirState.from_t_dry_bulb_rel_hum(32, 0.18)
pp(has1)

pp(psf.HumidAirState.from_t_dry_bulb_hum_ratio(6, has1.hum_ratio))

# has2 = psf.HumidAirState.from_t_dry_bulb_hum_ratio(22, hum_ratio=has1.hum_ratio)
# pp(has2)

# has = psf.HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=10, rel_hum=0.9)
# hafs.append(psf.HumidAirFlow(1, has))

# has = psf.HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=-10, rel_hum=0.0, pressure=p)
# hafs.append(psf.HumidAirFlow(10000 / 3600, has))

# has = psf.HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=20, rel_hum=0.0, pressure=p)
# hafs.append(psf.HumidAirFlow(4000 / 3600, has))


# mix = psf.mix_humid_air_flows(hafs)
# print(mix.str_short())

# wf = psf.WaterFlow.from_volume_flow_temperature(0, temp)

# awf = psf.AirWaterFlow.from_humid_air_flow(haf1)
# pp(awf)

# pp(awf.add_enthalpy(-5e4))

# def fun(h_f):
#     rel_hum = haf1.add_enthalpy(h_f).humid_air_state.rel_hum
#     print(rel_hum)

#     # if rel_hum > 1:
#     #     return 1 - rel_hum_target
#     return rel_hum - rel_hum_target

# has_lower_bound = psf.HumidAirState.from_t_dry_bulb_rel_hum(
#     haf1.humid_air_state.t_dew_point, 1
# )

# pp(has_lower_bound)

# h_f_lower_bound = (
#     has_lower_bound.moist_air_enthalpy - haf1.humid_air_state.moist_air_enthalpy
# ) * haf1.mass_flow_air

# sol = optimize.root_scalar(fun, method="brentq", bracket=[h_f_lower_bound, 0])









# has2 = psf.HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=-10, rel_hum=0.5)
# haf2 = psf.HumidAirFlow(1 / 3600, has2)
# hafs.append(haf2)
# pp(haf2)


# for i, haf in enumerate(hafs):
# print(f"haf{i}: {haf.str_short()}")

# mix = psf.mix_humid_air_flows([haf1, haf2])

# print("haf1: " + haf1.str_short())
# mix = haf1.heat_with_gas(1.5e-3)
# print("mix: " + mix.str_short())

# pp(mix)

# pp(mix)

# wf = psf.WaterFlow(1, ws.WaterState(10))

# wf_s = haf1.how_much_water_to_rel_hum(80,1)
# haf = haf1.add_water_to_rel_hum(10,0.99999)
# haf = haf1.add_water_to_rel_hum(80, 0.999)

# # pp(wf)
# pp(haf)

# pp(haf1.add_water_flow(wf_s))
