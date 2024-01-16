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
    t_dew_point: float
    rel_hum: float
    vap_pres: float
    moist_air_enthalpy: float
    moist_air_volume: float

    @classmethod
    def from_t_dry_bulb_rel_hum(
        cls, t_dry_bulb: float, rel_hum: float, pressure: float = STANDARD_PRESSURE
    ) -> Self:
        """initiate HumidAirState with t_dry_bulb and rel_hum"""

        if 0 > rel_hum > 1:
            raise ValueError("Wet bulb temperature is above dry bulb temperature")

        hum_ratio = get_hum_ratio_from_rel_hum(t_dry_bulb, rel_hum, pressure)
        vap_pres = get_vap_press_from_hum_ratio(hum_ratio, pressure)
        t_dew_point = get_t_dew_point_from_vap_pressure(vap_pres)
        moist_air_enthalpy = get_moist_air_enthalpy(t_dry_bulb, hum_ratio)
        moist_air_volume = get_moist_air_volume(
            t_dry_bulb,
            hum_ratio,
            pressure,
        )
        return cls(
            pressure,
            hum_ratio,
            t_dry_bulb,
            t_dew_point,
            rel_hum,
            vap_pres,
            moist_air_enthalpy,
            moist_air_volume,
        )


def get_sat_vap_pressure(T: float) -> float:
    """
    calculate the saturation vapor pressure of water

    [1] C. O. Popiel und J. Wojtkowiak,
    „Simple Formulas for Thermophysical Properties of Liquid Water
    for Heat Transfer Calculations (from 0°C to 150°C)“,
    Heat Transfer Engineering, Bd. 19, Nr. 3, S. 87-101, Jan. 1998,
    doi: 10.1080/01457639808939929.
    """

    if 0 > T or 150 < T:
        raise ValueError("Invalid temperature range 0<=t<=150 ([t]=°C)")

    pc = 220.64e5  # Pa
    Tc = 647.096  # K

    t = 1 - (273.15 + T) / Tc
    a1 = -7.85951783
    a2 = 1.84408259
    a3 = -11.7866497
    a4 = 22.6807411
    a5 = -15.9618719
    a6 = 1.80122502

    return pc * exp(
        (Tc / (273.15 + T))
        * (
            a1 * t
            + a2 * t**1.5
            + a3 * t**3
            + a4 * t**3.5
            + a5 * t**4
            + a6 * t**7.5
        )
    )


def get_t_dew_point_from_vap_pressure(vap_pres: float) -> float:
    """calculate the dew point tempreture from the water vapor pressure"""
    if vap_pres < 0:
        raise ValueError(
            "Partial pressure of water vapor in moist air cannot be negative"
        )

    def fun(t):
        return vap_pres - get_sat_vap_pressure(t)

    sol = optimize.root_scalar(fun, bracket=[0, 150])

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

    if 0 > vap_pres:
        raise ValueError(
            "Partial pressure of water vapor in moist air cannot be negative"
        )

    hum_ratio = 0.621945 * vap_pres / (pressure - vap_pres)

    return hum_ratio


def get_vap_press_from_hum_ratio(hum_ratio: float, pressure: float) -> float:
    """
    Return vapor pressure given humidity ratio and pressure.

    """
    if hum_ratio < 0:
        raise ValueError("Humidity ratio can not be negative")

    return pressure * hum_ratio / (0.621945 + hum_ratio)


def get_hum_ratio_from_rel_hum(
    t_dry_bulb: float, rel_hum: float, pressure: float = STANDARD_PRESSURE
) -> float:
    """Return humidity ratio given dry-bulb temperature, relative humidity, and pressure."""

    if rel_hum < 0 or rel_hum > 1:
        raise ValueError("Relative humidity is outside range [0, 1]")

    vap_pres = get_vap_pres_from_rel_hum(t_dry_bulb, rel_hum)

    return get_hum_ratio_from_vap_press(vap_pres, pressure)


def get_moist_air_enthalpy(t_dry_bulb: float, hum_ratio: float) -> float:
    """
    Return moist air enthalpy given dry-bulb temperature and humidity ratio.
    J/kg(dry_Air)

    [1] H. D. Baehr und S. Kabelac, Thermodynamik.
    Berlin, Heidelberg: Springer Berlin Heidelberg, 2016.
    doi: 10.1007/978-3-662-49568-1.
    eqn (5.70)
    """
    if hum_ratio < 0:
        raise ValueError("Humidity ratio cannot be negative")

    t_tr = 0.01

    return (
        1.0046 * (t_dry_bulb - t_tr)
        + hum_ratio * (2500.9 + 1.863 * (t_dry_bulb - t_tr)) * 1e3
    )


def get_moist_air_volume(t_dry_bulb: float, hum_ratio: float, pressure: float) -> float:
    """
    Return the specific volume of moist air given dry-bulb temperature, humidity ratio an pressure.
    m³/kg(dry_Air)

    [1] H. D. Baehr und S. Kabelac, Thermodynamik.
    Berlin, Heidelberg: Springer Berlin Heidelberg, 2016.
    doi: 10.1007/978-3-662-49568-1.
    eqn (5.68)
    """
    if hum_ratio < 0:
        raise ValueError("Humidity ratio cannot be negative")

    return 287.05 * (t_dry_bulb + 273.15) / pressure * (1 + hum_ratio / 0.621945)
