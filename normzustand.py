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
import psychrostate as pss

PrettyPrinter = pprint.PrettyPrinter(underscore_numbers=True)
pp = PrettyPrinter.pprint

# t_range = np.linspace(1,100,20)
# for t in t_range:
#     print(t , psf.get_density_water(t))

hafs = []

has1 = psf.HumidAirState.from_t_dry_bulb_rel_hum(
    20, 0.7, pressure=pss.get_pressure_from_height(210)
)
haf1 = psf.HumidAirFlow(150_000, has1)
pp(haf1)

pp(haf1.at_reference_point_DIN1334())


has2 = psf.HumidAirState.from_t_dry_bulb_hum_ratio(
    30, hum_ratio=has1.hum_ratio, pressure=has1.pressure
)
haf2 = psf.HumidAirFlow(5_000, has2)
pp(haf2)

pp(haf2.at_reference_point_DIN1334())



haf_mix = psf.mix_humid_air_flows([haf1,haf2])
pp(haf_mix)

pp(haf_mix.at_reference_point_DIN1334())