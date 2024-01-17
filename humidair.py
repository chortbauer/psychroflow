# -*- coding: utf-8 -*-
"""
Created on 2024-01-02 07:09:48
@author: orc

Unit conventions:
SI units are used for all physical values except temperatur for which °C is used.
"""

from functools import total_ordering
import pprint
from math import exp

from typing import Self
from dataclasses import dataclass

from scipy import optimize

from psychroflow import get_temp_from_tot_enthalpy_air_water_mix

PrettyPrinter = pprint.PrettyPrinter(underscore_numbers=True)
pp = PrettyPrinter.pprint





# t=-1
# print(get_sat_vap_pressure(t))
# print(get_sat_vap_pressure_0_150(t))
# print(get_sat_hum_ratio(t, 101325))
