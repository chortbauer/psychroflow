# -*- coding: utf-8 -*-
"""
just for testing
Created on 2024-01-22 07:30:30
@author: orc
"""

import pprint

import numpy as np

import psychroflow as psf # pylint: disable=unused-import
import psychrostate as pss # pylint: disable=unused-import
import waterstate as ws


PrettyPrinter = pprint.PrettyPrinter(underscore_numbers=True)
pp = PrettyPrinter.pprint

# t_range = np.linspace(1,100,20)
# for t in t_range:
#     print(t , psf.get_density_water(t))

hafs = []

has1 = psf.HumidAirState.from_t_dry_bulb_rel_hum(50, 0.4)
haf1 = psf.HumidAirFlow(1 / 3600, has1)
hafs.append(haf1)
pp(haf1)

# has2 = psf.HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=-10, rel_hum=0.5)
# haf2 = psf.HumidAirFlow(1 / 3600, has2)
# hafs.append(haf2)
# pp(haf2)



# for i, haf in enumerate(hafs):
    # print(f"haf{i}: {haf.str_short()}")

# mix = psf.mix_humid_air_flows([haf1, haf2])
# print("mix: " + mix.str_short())

# pp(mix)

wf = psf.WaterFlow(1, ws.WaterState(10))

wf_s = haf1.how_much_water_to_rel_hum(wf,0.7)
# haf = haf1.add_water_flow_to_rel_hum(wf,0.7)

pp(wf_s)
# pp(haf)

# pp(haf1.add_water_flow(wf_s))
