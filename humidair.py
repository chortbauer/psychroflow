# -*- coding: utf-8 -*-
"""
Created on 2024-01-02 07:09:48
@author: orc

Unit conventions:
SI units are used for all physical values except temperatur for which °C is used.
"""

import pprint
from math import isclose, exp

from typing import Self
from dataclasses import dataclass, field

from scipy import optimize

import psychrolib as ps

ps.SetUnitSystem(ps.SI)

PrettyPrinter = pprint.PrettyPrinter(underscore_numbers=True)
pp = PrettyPrinter.pprint


STANDARD_PRESSURE = 101_325  # Pa


@dataclass
class HumidAirState:
    """a humid air state"""

    pressure: float
    hum_ratio: float
    t_dry_bulb: float
    t_wet_bulb: float
    t_dew_point: float
    rel_hum: float
    vap_pres: float
    moist_air_enthalpy: float
    moist_air_volume: float
    degree_of_saturation: float

    @classmethod
    def from_t_dry_bulb_rel_hum(
        cls, t_dry_bulb: float, rel_hum: float, pressure: float = STANDARD_PRESSURE
    ) -> Self:
        """initiate HumidAirState with t_dry_bulb and rel_hum"""

        if 0 > rel_hum > 1:
            raise ValueError("Wet bulb temperature is above dry bulb temperature")

        hum_ratio = ps.GetHumRatioFromRelHum(t_dry_bulb, rel_hum, pressure)
        t_wet_bulb = ps.GetTWetBulbFromHumRatio(
            t_dry_bulb,
            hum_ratio,
            pressure,
        )
        t_dew_point = ps.GetTDewPointFromHumRatio(
            t_dry_bulb,
            hum_ratio,
            pressure,
        )
        vap_pres = ps.GetVapPresFromHumRatio(hum_ratio, pressure)
        moist_air_enthalpy = ps.GetMoistAirEnthalpy(t_dry_bulb, hum_ratio)
        moist_air_volume = ps.GetMoistAirVolume(
            t_dry_bulb,
            hum_ratio,
            pressure,
        )
        degree_of_saturation = ps.GetDegreeOfSaturation(t_dry_bulb, hum_ratio, pressure)
        return cls(
            pressure,
            hum_ratio,
            t_dry_bulb,
            t_wet_bulb,
            t_dew_point,
            rel_hum,
            vap_pres,
            moist_air_enthalpy,
            moist_air_volume,
            degree_of_saturation,
        )




def get_sat_vap_pressure(t:float)->float:
    """calculate the saturation vapor pressure of water / ice"""
    if -100 > t or 100 < t:
        raise ValueError("Invalid temperature range -100<=t<=100 ([t]=°C)")
    
    def get_sat_vap_pressure_water(t: float) -> float:
        """calculate the saturation vapor pressure of liquid water"""
        if 0.01 > t or 100 < t:
            raise ValueError("Invalid temperature range 0<=t<=100 ([t]=°C)")
        return exp(34.494 - 4924.99 / (t + 237.1)) / (t + 105) ** 1.57

    def get_sat_vap_pressure_ice(t: float) -> float:
        """calculate the saturation vapor pressure of water ice"""
        if -100 > t or 0.01 < t:
            raise ValueError("Invalid temperature range 0<=t<=100 ([t]=°C)")
        return exp(43.494 - 6545.8 / (t + 278)) / (t + 868) ** 2
        
    try: 
        return get_sat_vap_pressure_water(t)
    except ValueError:
        return get_sat_vap_pressure_ice(t)
    

def get_t_dew_point_from_vap_pressure(vap_pres:float)->float:
    """calculate the dew point tempreture from the water vapor pressure"""
    if vap_pres < 0:
        raise ValueError("Partial pressure of water vapor in moist air cannot be negative")

    def fun(t):
        return vap_pres - get_sat_vap_pressure(t)
    
    sol = optimize.root_scalar(fun, bracket=[-100, 100])

    if sol.converged:
        return sol.root
    else:
        raise ValueError("Root not converged: " + sol.flag)
    
def get_vap_pres_from_rel_hum(t_dry_bulb: float, rel_hum: float) -> float:
    """Return partial pressure of water vapor as a function of relative humidity and temperature."""
    
    if rel_hum < 0 or rel_hum > 1:
        raise ValueError("Relative humidity is outside range [0, 1]")

    return rel_hum * get_sat_vap_pressure(t_dry_bulb)


def get_hum_ratio_from_vap_press(vap_pres: float, pressure: float) -> float:
    """Return humidity ratio given water vapor pressure and atmospheric pressure."""

    if vap_pres < 0:
        raise ValueError("Partial pressure of water vapor in moist air cannot be negative")

    hum_ratio = 0.621945 * vap_pres / (pressure - vap_pres)

    return hum_ratio


def get_hum_ratio_from_rel_hum(t_dry_bulb:float,rel_hum:float, pressure:float=STANDARD_PRESSURE)->float:
    """Return humidity ratio given dry-bulb temperature, relative humidity, and pressure."""

    if rel_hum < 0 or rel_hum > 1:
        raise ValueError("Relative humidity is outside range [0, 1]")
    
    vap_pres = get_vap_pres_from_rel_hum(t_dry_bulb, rel_hum)

    return get_hum_ratio_from_vap_press(vap_pres, pressure)
    