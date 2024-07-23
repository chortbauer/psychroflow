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


psf.HumidAirFlow.from_m_air_m_water_enthalpy_flow(
    m_air=0.6790955478428202,
    m_water=3.823321578469525e-06,
    enthalpy_flow=-34108.586030716404,
    pressure=435000.0,
)
