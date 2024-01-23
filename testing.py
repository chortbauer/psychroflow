# -*- coding: utf-8 -*-
"""
just for testing
Created on 2024-01-22 07:30:30
@author: orc
"""

import pprint

import psychroflow as psf
from psychrostate import get_t_dry_bulb_from_tot_enthalpy_air_water_mix, get_tot_enthalpy_air_water_mix


PrettyPrinter = pprint.PrettyPrinter(underscore_numbers=True)
pp = PrettyPrinter.pprint

# t_range = np.linspace(1,100,20)
# for t in t_range:
#     print(t , psf.get_density_water(t))


# has1 = psf.HumidAirState.from_t_dry_bulb_rel_hum(44, 0.5)
# haf1 = psf.HumidAirFlow(24000 / 3600, has1)
# pp(haf1)

# has2 = psf.HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=10, rel_hum=0.7)
# haf2 = psf.HumidAirFlow(6000 / 3600, has2)
# pp(haf2)

# has3 = HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=15, rel_hum=0.1)
# haf3 = HumidAirFlow(6000 / 3600, has2)
# pp(haf2)

# print("haf1: " + haf1.str_short())

# print("mix: " + psf.mix_humid_air_flows([haf1, haf2]).str_short())


get_t_dry_bulb_from_tot_enthalpy_air_water_mix(hum_ratio = 0.00012285469664445817, tot_enthalpy = -15108.320983684625, pressure = 942857.142857143)
