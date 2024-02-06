# -*- coding: utf-8 -*-
"""
just for testing
Created on 2024-01-22 07:30:30
@author: orc
"""

# pylint: disable=unused-import

import pprint

import numpy as np

import psychroflow as psf
import psychrostate as pss
import waterstate as ws


PrettyPrinter = pprint.PrettyPrinter(underscore_numbers=True)
pp = PrettyPrinter.pprint

# t_range = np.linspace(1,100,20)
# for t in t_range:
#     print(t , psf.get_density_water(t))

hafs = []

# has1 = psf.HumidAirState.from_t_dry_bulb_rel_hum(20, 0.3)
# haf1 = psf.HumidAirFlow(1, has1)
# hafs.append(haf1)
# pp(haf1)

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


ts = [-100, -80, -60 - 40, -20, 0, 0.01, 20, 40, 60, 80, 100]


import matplotlib.pyplot as plt

# fig, ax = plt.subplots(1)

# ax.plot(ts, np.vectorize(pss.get_sat_vap_pressure)(ts,ignore_valid_range=True))

# fig.savefig("output/test.png")

for t in ts:
    print(f"{t}°C, {pss.get_sat_vap_pressure(t, ignore_valid_range=True)}")
