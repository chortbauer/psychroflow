# -*- coding: utf-8 -*-
"""
Created on 2024-01-23 12:38:04
@author: orc
"""

from typing import Self
from math import exp, isclose
from dataclasses import dataclass
from scipy import optimize

from waterstate import (
    get_enthalpy_water,
    get_enthalpy_water_liquid,
    get_enthalpy_water_ice,
)


STANDARD_PRESSURE = 101_325  # Pa


def get_pressure_from_height(height_above_sea_level: float) -> float:
    """return mean atmospheric pressure at height above mean sea level"""
    return STANDARD_PRESSURE * exp(-height_above_sea_level / 8435)


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

    @classmethod
    def from_t_dry_bulb_rel_hum(
        cls, t_dry_bulb: float, rel_hum: float, pressure: float = STANDARD_PRESSURE
    ) -> Self:
        """initiate HumidAirState with t_dry_bulb and rel_hum"""

        if 0 > rel_hum > 1:
            raise ValueError("Wet bulb temperature is above dry bulb temperature")

        hum_ratio = get_hum_ratio_from_rel_hum(t_dry_bulb, rel_hum, pressure)
        vap_pres = get_vap_press_from_hum_ratio(hum_ratio, pressure)
        t_wet_bulb = get_t_wet_bulb(t_dry_bulb, hum_ratio, pressure)
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
            t_wet_bulb,
            t_dew_point,
            rel_hum,
            vap_pres,
            moist_air_enthalpy,
            moist_air_volume,
        )

    @classmethod
    def from_t_dry_bulb_hum_ratio(
        cls, t_dry_bulb: float, hum_ratio: float, pressure: float = STANDARD_PRESSURE
    ) -> Self:
        """initiate HumidAirState with t_dry_bulb and hum_ratio"""

        if 0 > hum_ratio:
            if isclose(hum_ratio, 0):
                hum_ratio = 0
            else:
                raise ValueError("Humidity ratio cannot be negative")

        vap_pres = get_vap_press_from_hum_ratio(hum_ratio, pressure)
        rel_hum = get_rel_hum_from_vap_pressure(t_dry_bulb, vap_pres)

        if 1 < rel_hum:
            if isclose(rel_hum, 1):
                rel_hum = 1
            else:
                raise ValueError("relative Humidity > 1; Condensation!")

        t_wet_bulb = get_t_wet_bulb(t_dry_bulb, hum_ratio, pressure)
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
            t_wet_bulb,
            t_dew_point,
            rel_hum,
            vap_pres,
            moist_air_enthalpy,
            moist_air_volume,
        )

    @classmethod
    def from_hum_ratio_enthalpy(
        cls,
        hum_ratio: float,
        moist_air_enthalpy: float,
        pressure: float = STANDARD_PRESSURE,
    ) -> Self:
        """init humid air state from hum_ratio [kg(Water)/kg(Air)] and enthalpy [J/kg(Air)]"""
        vap_pres = get_vap_press_from_hum_ratio(hum_ratio, pressure)
        tot_enthalpy = moist_air_enthalpy / (1 + hum_ratio)
        t_dry_bulb = get_t_dry_bulb_from_tot_enthalpy_air_water_mix(
            hum_ratio, tot_enthalpy, pressure
        )
        t_wet_bulb = get_t_wet_bulb(t_dry_bulb, hum_ratio, pressure)
        t_dew_point = get_t_dew_point_from_vap_pressure(vap_pres)
        rel_hum = get_rel_hum_from_vap_pressure(t_dry_bulb, vap_pres)
        moist_air_volume = get_moist_air_volume(t_dry_bulb, hum_ratio, pressure)
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
        )

    def at_t_dry_bulb(self, t_dry_bulb: float) -> "HumidAirState":
        """return the humid air state with same humidity ratio at a different temperature"""
        return HumidAirState.from_t_dry_bulb_hum_ratio(
            t_dry_bulb=t_dry_bulb, hum_ratio=self.hum_ratio, pressure=self.pressure
        )


def get_sat_vap_pressure(t_dry_bulb: float) -> float:
    """
    calculate the saturation vapor pressure of water / ice
    """
    if -223.15 > t_dry_bulb or 373.9 < t_dry_bulb:
        raise ValueError(
            f"Invalid temperature range -223.15°C<=t<=373.9°C; {t_dry_bulb:=.2f}"
        )

    if 0.01 <= t_dry_bulb:
        return get_sat_vap_pressure_liquid_water(t_dry_bulb=t_dry_bulb)

    return get_sat_vap_pressure_water_ice(t_dry_bulb=t_dry_bulb)


def get_sat_vap_pressure_liquid_water(t_dry_bulb: float) -> float:
    """
    calculate the saturation vapor pressure of water

    [1] J. Huang,
    „A Simple Accurate Formula for Calculating Saturation Vapor Pressure of Water and Ice“,
    Journal of Applied Meteorology and Climatology, Bd. 57, Nr. 6, S. 1265-1272, Juni 2018,
    doi: 10.1175/JAMC-D-17-0334.1.
    """
    if 0.01 > t_dry_bulb or 373.9 < t_dry_bulb:
        raise ValueError(
            f"Invalid temperature range 0.01°C<=t<=373.9°C; {t_dry_bulb:=.2f}"
        )

    p_c = 22.064e6  # Pa
    t_c = 647.096  # K

    t_ = 1 - (273.15 + t_dry_bulb) / t_c
    a1 = -7.85951783
    a2 = 1.84408259
    a3 = -11.7866497
    a4 = 22.6807411
    a5 = -15.9618719
    a6 = 1.80122502

    p_s = p_c * exp(
        (t_c / (273.15 + t_dry_bulb))
        * (
            a1 * t_
            + a2 * t_**1.5
            + a3 * t_**3
            + a4 * t_**3.5
            + a5 * t_**4
            + a6 * t_**7.5
        )
    )
    return p_s


def get_sat_vap_pressure_water_ice(
    t_dry_bulb: float, *, ignore_valid_range: bool = False
) -> float:
    """
    calculate the saturation vapor pressure of water

    [1] W. Wagner, T. Riethmann, R. Feistel, und A. H. Harvey,
    „New Equations for the Sublimation Pressure and Melting Pressure of H2O Ice Ih“,
    Journal of Physical and Chemical Reference Data, Bd. 40, Nr. 4, S. 043103, Dez. 2011,
    doi: 10.1063/1.3657937.
    """
    if not ignore_valid_range:
        if -223.15 > t_dry_bulb or 0.01 < t_dry_bulb:
            raise ValueError(
                f"Invalid temperature range -223.15°C<=t<=0.01°C; {t_dry_bulb:=.2f}"
            )

    p_t = 611.657
    t_t = 273.16

    t = 273.15 + t_dry_bulb
    t_ = t / t_t

    b1 = -0.212144006e2
    b2 = 0.273203819e2
    b3 = -0.610598130e1

    p_s = p_t * exp(
        (t_t / t)
        * (b1 * t_**0.333333333e-2 + b2 * t_**0.120666667e1 + b3 * t_**0.170333333e1)
    )
    return p_s


def get_vap_pres_from_rel_hum(t_dry_bulb: float, rel_hum: float) -> float:
    """Return partial pressure of water vapor as a function of relative humidity and temperature."""

    if isclose(0, rel_hum):
        rel_hum = 0
    elif isclose(1, rel_hum):
        rel_hum = 1
    elif 0 > rel_hum or 1 < rel_hum:
        raise ValueError("Relative humidity is outside range [0, 1]")

    return rel_hum * get_sat_vap_pressure(t_dry_bulb)


def get_t_dew_point_from_vap_pressure(vap_pres: float) -> float:
    """calculate the dew point tempreture from the water vapor pressure"""
    if vap_pres < 0:
        raise ValueError(
            "Partial pressure of water vapor in moist air cannot be negative"
        )

    # if vapour pressure == 0, return -196°C
    if isclose(0, vap_pres):
        return -196

    def fun(t):
        return vap_pres - get_sat_vap_pressure(t)

    sol = optimize.root_scalar(fun, method="brentq", bracket=[-223.1, 373.9])

    if sol.converged:
        return sol.root

    raise ValueError("Root not converged: " + sol.flag)


def get_hum_ratio_from_vap_press(vap_pres: float, pressure: float) -> float:
    """Return humidity ratio given water vapor pressure and atmospheric pressure."""

    if 0 > vap_pres:
        raise ValueError(
            "Partial pressure of water vapor in moist air cannot be negative"
        )

    hum_ratio = 0.621945 * vap_pres / (pressure - vap_pres)

    if 0 > hum_ratio:
        raise ValueError("Vapour pressure water > pressure")

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
        + hum_ratio * (2500.9 + 1.863 * (t_dry_bulb - t_tr))
    ) * 1e3


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


def get_sat_hum_ratio(t_dry_bulb: float, pressure: float) -> float:
    """
    Return humidity ratio of saturated air given dry-bulb temperature and pressure.
    """
    sat_vap_pressure = get_sat_vap_pressure(t_dry_bulb)

    if sat_vap_pressure > pressure:
        return float("inf")  # TODO is this ok?
        # raise ValueError("sat_vap_pressure > pressure; Pure steam is not implemented")

    return 0.621945 * sat_vap_pressure / (pressure - sat_vap_pressure)


def get_sat_air_enthalpy(t_dry_bulb: float, pressure: float) -> float:
    """
    Return saturated air enthalpy given dry-bulb temperature and pressure.
    """
    sat_hum_ratio = get_sat_hum_ratio(t_dry_bulb, pressure)
    return get_moist_air_enthalpy(t_dry_bulb, sat_hum_ratio)


def get_rel_hum_from_vap_pressure(t_dry_bulb: float, vap_pres: float) -> float:
    """
    Return relative humidity given dry-bulb temperature and vapor pressure.
    """
    if vap_pres < 0:
        raise ValueError(
            "Partial pressure of water vapor in moist air cannot be negative"
        )

    return vap_pres / get_sat_vap_pressure(t_dry_bulb)


def get_t_dry_bulb_from_tot_enthalpy_air_water_mix(
    hum_ratio: float, tot_enthalpy: float, pressure: float
) -> float:
    """
    calculate temperature of an air water mix at equilibrium
    WARNING: enthalpy is per the total mass, in J / kg(Air+Water)
    """

    def fun(t):
        return tot_enthalpy - get_tot_enthalpy_air_water_mix(hum_ratio, t, pressure)

    sol = optimize.root_scalar(fun, method="brentq", bracket=[-223.1, 373.9])

    if sol.converged:
        return sol.root
    raise ArithmeticError("Root not found: " + sol.flag)


def get_tot_enthalpy_air_water_mix(
    hum_ratio: float, t_dry_bulb: float, pressure: float
) -> float:
    """specific enthalpy of an air water mixture at equilibrium in J / kg(Air + Water)"""

    # sat_hum_ratio = ps.GetSatHumRatio(t_dry_bulb, pressure)
    sat_hum_ratio = get_sat_hum_ratio(t_dry_bulb, pressure)

    # unsaturated air
    if hum_ratio <= sat_hum_ratio:
        # recalculate with hum_ratio as the specific enthalpy per total mass
        return get_moist_air_enthalpy(t_dry_bulb, hum_ratio) / (1 + hum_ratio)

    enthalpy_gas = get_sat_air_enthalpy(t_dry_bulb, pressure)

    # saturated air over liquid water
    if t_dry_bulb >= 0.01:
        enthalpy_water = get_enthalpy_water_liquid(t_dry_bulb)
        tot_enthalpy = (enthalpy_gas + enthalpy_water * (hum_ratio - sat_hum_ratio)) / (
            1 + hum_ratio
        )
        return tot_enthalpy

    # saturated air over ice
    enthalpy_ice = get_enthalpy_water_ice(t_dry_bulb)
    tot_enthalpy = (enthalpy_gas + enthalpy_ice * (hum_ratio - sat_hum_ratio)) / (
        1 + hum_ratio
    )
    return tot_enthalpy


def get_t_dry_bulb_from_sat_vap_pressure(sat_vap_pressure: float) -> float:
    """get the dry bulb temperature from a given saturation vapour pressure"""
    sol = optimize.root_scalar(
        lambda t: get_sat_vap_pressure(t) - sat_vap_pressure,
        method="brentq",
        bracket=[-223.15, 373.9],
    )

    if sol.converged:
        return sol.root
    raise ArithmeticError("Root not found: " + sol.flag)


def get_t_wet_bulb(t_dry_bulb: float, hum_ratio: float, pressure: float) -> float:
    t_dry_bulb_lim_up = min(150, get_t_dry_bulb_from_sat_vap_pressure(pressure) - 1e-3)

    def fun(t):
        return (
            get_moist_air_enthalpy(t_dry_bulb, hum_ratio)
            + (get_sat_hum_ratio(t, pressure) - hum_ratio) * get_enthalpy_water(t)
            - get_sat_air_enthalpy(t, pressure)
        )

    sol = optimize.root_scalar(
        fun, method="brentq", bracket=[-223.15, t_dry_bulb_lim_up]
    )

    if sol.converged:
        return sol.root
    raise ArithmeticError("Root not found: " + sol.flag)
