# -*- coding: utf-8 -*-
"""
Created on 2024-01-23 12:38:04
@author: orc
"""

import warnings
from typing import Self
from math import exp

from dataclasses import dataclass, field

from scipy import optimize


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

    @classmethod
    def from_t_dry_bulb_hum_ratio(
        cls, t_dry_bulb: float, hum_ratio: float, pressure: float = STANDARD_PRESSURE
    ) -> Self:
        """initiate HumidAirState with t_dry_bulb and hum_ratio"""

        if 0 > hum_ratio:
            raise ValueError("Humidity ratio cannot be negative")

        vap_pres = get_vap_press_from_hum_ratio(hum_ratio, pressure)
        rel_hum = get_rel_hum_from_vap_pressure(t_dry_bulb, vap_pres)
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
        t_dry_bulb = get_temp_from_tot_enthalpy_air_water_mix(
            hum_ratio, tot_enthalpy, pressure
        )
        t_dew_point = get_t_dew_point_from_vap_pressure(vap_pres)
        rel_hum = get_rel_hum_from_vap_pressure(t_dry_bulb, vap_pres)
        moist_air_volume = get_moist_air_volume(t_dry_bulb, hum_ratio, pressure)
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


def get_sat_vap_pressure(t_dry_bulb: float) -> float:
    """
    calculate the saturation vapor pressure of water

    [1] C. O. Popiel und J. Wojtkowiak,
    „Simple Formulas for Thermophysical Properties of Liquid Water
    for Heat Transfer Calculations (from 0°C to 150°C)“,
    Heat Transfer Engineering, Bd. 19, Nr. 3, S. 87-101, Jan. 1998,
    doi: 10.1080/01457639808939929.
    """

    if -50 > t_dry_bulb or 150 < t_dry_bulb:
        raise ValueError("Invalid temperature range -50<=t<=150 ([t]=°C)")

    pc = 220.64e5  # Pa
    t_c = 647.096  # K

    t = 1 - (273.15 + t_dry_bulb) / t_c
    a1 = -7.85951783
    a2 = 1.84408259
    a3 = -11.7866497
    a4 = 22.6807411
    a5 = -15.9618719
    a6 = 1.80122502

    return pc * exp(
        (t_c / (273.15 + t_dry_bulb))
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

    if vap_pres < get_sat_vap_pressure(-50):
        warnings.warn(
            "Dew point temperature < 50 °C are no calculated correctly. Other values not affected"
        )
        return -50

    def fun(t):
        return vap_pres - get_sat_vap_pressure(t)

    # sol = optimize.root_scalar(fun, bracket=[-50, 150])
    sol = optimize.root_scalar(fun, x0=20)

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
        raise ValueError("sat_vap_pressure > pressure; no saturation possible")

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


def get_temp_from_tot_enthalpy_air_water_mix(
    hum_ratio: float, enthalpy: float, pressure: float
) -> float:
    """
    calculate temperature of an air water mix at equilibrium
    WARNING: enthalpy is per the total mass, in J / kg(Air+Water)
    """

    def fun(t):
        return enthalpy - get_tot_enthalpy_air_water_mix(hum_ratio, t, pressure)

    # sol = optimize.root_scalar(fun, bracket=[-50, 99])
    sol = optimize.root_scalar(fun, x0=20)

    if sol.converged:
        return sol.root
    raise ArithmeticError("Root not found: " + sol.flag)


def get_density_water(t: float) -> float:
    """
    [1] C. O. Popiel und J. Wojtkowiak,
    Simple Formulas for Thermophysical Properties of Liquid Water
    for Heat Transfer Calculations (from 0°C to 150°C)“,
    Heat Transfer Engineering, Bd. 19, Nr. 3, S. 87-101, Jan. 1998, doi: 10.1080/01457639808939929.
    """
    if 0.01 > t or 150 < t:
        raise ValueError("Temperature range: 0.01 °C < T < 150 °C")

    tau = 1 - (t + 273.15) / 647.096

    rho_c = 322
    b1 = 1.99274064
    b2 = 1.09965342
    b3 = -0.510839303
    b4 = -1.75493479
    b5 = -45.5170352
    b6 = -6.74694450e5
    return rho_c * (
        1
        + b1 * tau ** (1 / 3)
        + b2 * tau ** (2 / 3)
        + b3 * tau ** (5 / 3)
        + b4 * tau ** (16 / 3)
        + b5 * tau ** (43 / 3)
        + b6 * tau ** (110 / 3)
    )


def get_enthalpy_water(t: float) -> float:
    """
    [1] C. O. Popiel und J. Wojtkowiak,
    Simple Formulas for Thermophysical Properties of Liquid Water
    for Heat Transfer Calculations (from 0°C to 150°C)“,
    Heat Transfer Engineering, Bd. 19, Nr. 3, S. 87-101, Jan. 1998, doi: 10.1080/01457639808939929.
    """
    if 0.01 > t or 150 < t:
        raise ValueError("Temperature range: 0.01 °C < T < 150 °C")

    d1 = -2.844699e-2
    d2 = 4.211925
    d3 = -1.017034e-3
    d4 = 1.311054e-5
    d5 = -6.756469e-8
    d6 = 1.724481e-10

    return (d1 + d2 * t + d3 * t**2 + d4 * t**3 + d5 * t**4 + d6 * t**5) * 1e3


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

    # saturated air over ice
    if t_dry_bulb <= 0:
        # raise ArgumentError("Enthalpy over ice not implemented!")
        enthalpy_ice = (-333.4 + 2.07 * (t_dry_bulb - 0.01)) * 1e3
        enthalpy = (
            enthalpy_gas * (1 + hum_ratio - sat_hum_ratio)
            + sat_hum_ratio * enthalpy_ice
        ) / (1 + hum_ratio)
        return enthalpy

    # saturated air over liquid water
    enthalpy_water = get_enthalpy_water(t_dry_bulb)
    enthalpy = (
        enthalpy_gas * (1 + hum_ratio - sat_hum_ratio) + sat_hum_ratio * enthalpy_water
    ) / (1 + hum_ratio)
    return enthalpy


@dataclass
class WaterState:
    """A state of liquid water"""

    temperature: float
    pressure: float = field(default=STANDARD_PRESSURE)
    density: float = field(init=False)
    enthalpy: float = field(init=False)

    def __post_init__(self):
        self.density = get_density_water(self.temperature)
        self.enthalpy = get_enthalpy_water(self.temperature)
