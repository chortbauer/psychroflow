# -*- coding: utf-8 -*-
"""
Created on 2024-01-02 07:09:48
@author: orc

Unit conventions:
SI units are used for all physical values except temperatur for which °C is used.
"""
from ctypes import ArgumentError

# import logging
import pprint
from math import isclose

from typing import Self
from dataclasses import dataclass, field

from scipy import optimize
import psychrolib as ps

PrettyPrinter = pprint.PrettyPrinter(underscore_numbers=True)
pp = PrettyPrinter.pprint

# set the psychrolib unit system
ps.SetUnitSystem(ps.SI)

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

    @classmethod
    def from_t_dry_bulb_t_wet_bulb(
        cls, t_dry_bulb: float, t_wet_bulb: float, pressure: float = STANDARD_PRESSURE
    ) -> Self:
        """initiate HumidAirState with t_dry_bulb and t_wet_bulb"""

        if t_wet_bulb > t_dry_bulb:
            raise ValueError("Wet bulb temperature is above dry bulb temperature")

        hum_ratio = ps.GetHumRatioFromTWetBulb(
            t_dry_bulb,
            t_wet_bulb,
            pressure,
        )
        t_dew_point = ps.GetTDewPointFromHumRatio(
            t_dry_bulb,
            hum_ratio,
            pressure,
        )
        rel_hum = ps.GetRelHumFromHumRatio(
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
        degree_of_saturation = ps.GetDegreeOfSaturation(
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
            degree_of_saturation,
        )

    @classmethod
    def from_t_dry_bulb_t_dew_point(
        cls, t_dry_bulb: float, t_dew_point: float, pressure: float = STANDARD_PRESSURE
    ) -> Self:
        """initiate HumidAirState with t_dry_bulb and t_dew_point"""

        if t_dew_point > t_dry_bulb:
            raise ValueError("Dry bulb temperature is above dew point temperature")

        hum_ratio = ps.GetHumRatioFromTDewPoint(t_dew_point, pressure)
        t_wet_bulb = ps.GetTWetBulbFromHumRatio(
            t_dry_bulb,
            hum_ratio,
            pressure,
        )
        rel_hum = ps.GetRelHumFromHumRatio(
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
        degree_of_saturation = ps.GetDegreeOfSaturation(
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
            degree_of_saturation,
        )


@dataclass
class HumidAirFlow:
    """A flow of air and water vapour"""

    volume_flow: float
    humid_air_state: HumidAirState
    mass_flow_air: float = field(init=False)
    mass_flow_water: float = field(init=False)
    mass_flow: float = field(init=False)
    enthalpy_flow: float = field(init=False)

    def __post_init__(self):
        self.mass_flow_air = self.volume_flow / self.humid_air_state.moist_air_volume
        self.mass_flow_water = self.humid_air_state.hum_ratio * self.mass_flow_air
        self.mass_flow = self.mass_flow_air + self.mass_flow_water
        self.enthalpy_flow = (
            self.humid_air_state.moist_air_enthalpy * self.mass_flow_air
        )


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


@dataclass
class WaterFlow:
    """A flow of liquid water"""

    volume_flow: float
    water_state: WaterState
    mass_flow: float = field(init=False)
    enthalpy_flow: float = field(init=False)

    def __post_init__(self):
        self.mass_flow = self.volume_flow * self.water_state.density
        self.enthalpy_flow = self.water_state.enthalpy * self.mass_flow


@dataclass
class AirWaterFlow:
    """A Flow of air and water"""

    humid_air_flow: HumidAirFlow
    water_flow: WaterFlow
    dry: bool = field(init=False)

    def __post_init__(self):
        # TODO allow no air
        # check if temperatures match
        if not isclose(
            self.humid_air_flow.humid_air_state.t_dry_bulb,
            self.water_flow.water_state.temperature,
        ):
            raise ValueError("Temperature of air- and waterflow must be equal!")

        # check pressure match
        if not isclose(
            self.humid_air_flow.humid_air_state.pressure,
            self.water_flow.water_state.pressure,
        ):
            raise ValueError("Pressure of air- and waterflow must be equal!")

        # if liquid water
        if not isclose(self.water_flow.mass_flow, 0):
            self.dry = True
            # if there is liquid water the air has to be saturated
            if not isclose(self.humid_air_flow.humid_air_state.rel_hum, 1):
                raise ValueError("Air over liquid water has to be saturated")

    @classmethod
    def from_humid_air_flow(cls, haf: HumidAirFlow) -> Self:
        """air water flow with humid air only"""
        return cls(
            haf,
            WaterFlow(
                0,
                WaterState(
                    haf.humid_air_state.t_dry_bulb, haf.humid_air_state.pressure
                ),
            ),
        )

    @classmethod
    def from_water_flow(cls, wf: WaterFlow) -> Self:
        """air water flow with liquid water only"""
        return cls(
            HumidAirFlow(
                0,
                HumidAirState.from_t_dry_bulb_rel_hum(
                    wf.water_state.temperature, 1, wf.water_state.pressure
                ),
            ),
            wf,
        )

    @classmethod
    def from_m_air_m_water_total_enthalpy(
        cls, m_air: float, m_water: float, total_enthalpy: float, pressure: float
    ) -> Self:
        """create air- waterflow by mixing a HumidAirFlow and a WaterFlow"""
        hum_ratio = m_water / m_air
        t_dry_bulb = get_temp_from_enthalpy_air_water_mix(
            hum_ratio, total_enthalpy / (m_air + m_water), pressure
        )
        sat_hum_ratio = ps.GetSatHumRatio(t_dry_bulb, pressure)

        if hum_ratio <= sat_hum_ratio:
            # gas phase only
            has = HumidAirState.from_t_dry_bulb_rel_hum(
                t_dry_bulb, hum_ratio / sat_hum_ratio, pressure
            )
            volume_flow = m_air / has.moist_air_volume
            return cls.from_humid_air_flow(
                HumidAirFlow(
                    volume_flow,
                    has,
                )
            )
        # gas phase and liquid phase
        has = HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb, 1, pressure)
        volume_flow_gas = m_air * has.moist_air_volume
        haf = HumidAirFlow(volume_flow_gas, has)
        ws = WaterState(t_dry_bulb, pressure)
        volume_flow_liquid = (hum_ratio - sat_hum_ratio) * m_air / ws.density
        wf = WaterFlow(volume_flow_liquid, ws)
        return cls(haf, wf)

    @classmethod
    def from_mixing_two_humid_air_flows(
        cls, haf_in_1: HumidAirFlow, haf_in_2: HumidAirFlow
    ) -> Self:
        """create air- waterflow by mixing a HumidAirFlow and a WaterFlow"""
        m_air = haf_in_1.mass_flow_air + haf_in_2.mass_flow_air
        m_water = haf_in_1.mass_flow_water + haf_in_2.mass_flow_water
        total_enthalpy = haf_in_1.enthalpy_flow + haf_in_2.enthalpy_flow
        if isclose(
            haf_in_1.humid_air_state.pressure, haf_in_2.humid_air_state.pressure
        ):
            pressure = haf_in_1.humid_air_state.pressure
            return cls.from_m_air_m_water_total_enthalpy(
                m_air, m_water, total_enthalpy, pressure
            )
        raise ValueError("The pressure of the mixing air streams must be equal")

    @classmethod
    def from_mixing_air_water(cls, haf_in: HumidAirFlow, wf_in: WaterFlow) -> Self:
        """create air- waterflow by mixing a HumidAirFlow and a WaterFlow"""
        m_air = haf_in.mass_flow_air
        m_water = haf_in.mass_flow_water + wf_in.mass_flow
        total_enthalpy = haf_in.enthalpy_flow + wf_in.enthalpy_flow
        pressure = haf_in.humid_air_state.pressure
        return cls.from_m_air_m_water_total_enthalpy(
            m_air, m_water, total_enthalpy, pressure
        )


def get_density_water(t: float) -> float:
    """
    [1] C. O. Popiel und J. Wojtkowiak,
    Simple Formulas for Thermophysical Properties of Liquid Water
    for Heat Transfer Calculations (from 0°C to 150°C)“,
    Heat Transfer Engineering, Bd. 19, Nr. 3, S. 87–101, Jan. 1998, doi: 10.1080/01457639808939929.
    """
    if 0.01 > t or 150 < t:
        raise ValueError("Temperature range: 0.01 °C < T < 150 °C")

    rho_c = 322
    b1 = 1.99274064
    b2 = 1.09965342
    b3 = -0.510839303
    b4 = -1.75493479
    b5 = -45.5170352
    b6 = -6.74694450e5
    return rho_c * (
        1
        + b1 * t ** (1 / 3)
        + b2 * t ** (2 / 3)
        + b3 * t ** (5 / 3)
        + b4 * t ** (16 / 3)
        + b5 * t ** (43 / 3)
        + b6 * t ** (110 / 3)
    )


def get_enthalpy_water(t: float) -> float:
    """
    [1] C. O. Popiel und J. Wojtkowiak,
    Simple Formulas for Thermophysical Properties of Liquid Water
    for Heat Transfer Calculations (from 0°C to 150°C)“,
    Heat Transfer Engineering, Bd. 19, Nr. 3, S. 87–101, Jan. 1998, doi: 10.1080/01457639808939929.
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


def get_total_enthalpy_air_water_mix(
    hum_ratio: float, t_dry_bulb: float, pressure: float
) -> float:
    """specific enthalpy of an air water mixture at equilibrium in J / kg(total)"""

    sat_hum_ratio = ps.GetSatHumRatio(t_dry_bulb, pressure)

    if hum_ratio <= sat_hum_ratio:
        # only gas phase
        # recalculate with hum_ratio as the specific enthalpy per total mass
        return ps.GetMoistAirEnthalpy(t_dry_bulb, hum_ratio) / (1 + hum_ratio)

    if t_dry_bulb > ps.FREEZING_POINT_WATER_SI:
        # gas over liquid water
        enthalpy_gas = ps.GetSatAirEnthalpy(t_dry_bulb, pressure) / (1 + sat_hum_ratio)
        enthalpy_liquid = get_enthalpy_water(t_dry_bulb)
        return (
            enthalpy_gas
            + (1 + sat_hum_ratio)
            + (hum_ratio - sat_hum_ratio) * enthalpy_liquid
        ) / (1 + hum_ratio)
    else:
        raise ArgumentError("Enthalpy over ice not implemented!")


def get_temp_from_enthalpy_air_water_mix(
    hum_ratio: float, total_enthalpy: float, pressure: float
) -> float:
    """
    calculate temperature of an air water mix at equilibrium
    WARNING: enthalpy is per the total mass, in J / kg(Air+Water)
    """

    def fun(t):
        return total_enthalpy - get_total_enthalpy_air_water_mix(hum_ratio, t, pressure)

    sol = optimize.root_scalar(fun, bracket=[0.01, 150], method="brentq")

    if sol.converged:
        return sol.root
    raise ArithmeticError("Root not found: " + sol.message)


# # has = HumidAirState.from_TDryBul_TDewPoint(t_dry_bulb=35, t_dew_point=40)
has1 = HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=40, rel_hum=0.5)
haf1 = HumidAirFlow(1, has1)
pp(haf1)

has2 = HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=-10, rel_hum=0.5)
haf2 = HumidAirFlow(2, has2)
pp(haf2)

awf = AirWaterFlow.from_mixing_two_humid_air_flows(haf1, haf2)
pp(awf)
