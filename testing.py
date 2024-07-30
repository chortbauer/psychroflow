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
import psychrostate as ps
import waterstate as ws

PrettyPrinter = pprint.PrettyPrinter(underscore_numbers=True)
pp = PrettyPrinter.pprint

# t_range = np.linspace(1,100,20)
# for t in t_range:
#     print(t , psf.get_density_water(t))

hafs = []

# has0 = psf.HumidAirState.from_t_dry_bulb_rel_hum(100, 0.999)
# sat_vap = ps.get_vap_press_from_hum_ratio(0.00000001, 1e5)
# rel_hum = get_rel_hum_from_vap_pressure(70, sat_vap)


# has0 = psf.HumidAirState.from_t_dry_bulb_hum_ratio(
#     t_dry_bulb=-30.0,
#     hum_ratio=9.715396778867134e-05,
#     pressure=243333.33333333334,
# )
# has0_heated = has0.at_t_dry_bulb(60)
# haf0 = psf.HumidAirFlow(0.2, has0)

# t_wet_bulb = ps.get_t_wet_bulb(has0.t_dry_bulb, has0.hum_ratio, has0.pressure)

# print(f"{has0}")

# t_dry_bulb, rh, pressure, hum_ratio, h, t_wet_bulb = [-50.0, 0.0, 891428.5714285715, 0.0, -50240.045999999995, -50.0077504573249]

# # t_wet = ps.get_t_wet_bulb_from_t_dry_bulb_hum_ratio(40,0.002,1.002e5)
# # print(t_wet)

# hum_ratio = 0
# hum_ratio =  ps.get_sat_hum_ratio(t_dry_bulb, pressure)

# h = ps.get_moist_air_enthalpy(t_dry_bulb, hum_ratio)
# hum_ratio_s = ps.get_sat_hum_ratio(t_wet_bulb, pressure)
# hum_ratio = hum_ratio
# h_water  = ps.get_enthalpy_water(t_wet_bulb)
# h_s = ps.get_sat_air_enthalpy(t_wet_bulb, pressure)

# print(f"{h=}")
# print(f"{hum_ratio_s=}")
# print(f"{hum_ratio=}")
# print(f"{h_water=}")
# print(f"{h_s=}")


# hum_ratio = ps.get_hum_ratio_from_t_dry_bulb_t_wet_bulb(t_dry_bulb,t_wet_bulb,pressure)
# print(hum_ratio)

has = ps.HumidAirState.from_t_dry_bulb_rel_hum(-50, 1, 8e4)
