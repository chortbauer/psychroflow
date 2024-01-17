# -*- coding: utf-8 -*-
"""
Created on 2024-01-02 07:09:48
@author: orc

Unit conventions:
SI units are used for all physical values except temperatur for which °C is used.
"""

from math import isclose

from typing import Self
from dataclasses import dataclass, field

from scipy import optimize

import humidair as ha
from humidair import HumidAirState


STANDARD_PRESSURE = 101_325  # Pa


@dataclass
class HumidAirFlow:
    """A flow of air and water vapour"""

    volume_flow: float
    humid_air_state: HumidAirState
    mass_flow_air: float = field(init=False)
    mass_flow_water: float = field(init=False)
    mass_flow: float = field(init=False)
    tot_enthalpy_flow: float = field(init=False)

    def __post_init__(self):
        self.mass_flow_air = self.volume_flow / self.humid_air_state.moist_air_volume
        self.mass_flow_water = self.humid_air_state.hum_ratio * self.mass_flow_air
        self.mass_flow = self.mass_flow_air + self.mass_flow_water
        self.tot_enthalpy_flow = (
            self.humid_air_state.moist_air_enthalpy * self.mass_flow_air
        )

    def str_short(self) -> str:
        """returns a short strin repr"""
        vol = f"V={self.volume_flow*3600:.1f}m³/h"
        t = f"T={self.humid_air_state.t_dry_bulb:.1f}°C"
        t_tau = f"T_tau={self.humid_air_state.t_dew_point:.1f}°C"
        f = f"Feuchte={self.humid_air_state.rel_hum*100:.1f}%"
        return "; ".join([vol, t, t_tau, f])


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
    tot_enthalpy_flow: float = field(init=False)

    def __post_init__(self):
        self.mass_flow = self.volume_flow * self.water_state.density
        self.tot_enthalpy_flow = self.water_state.enthalpy * self.mass_flow


@dataclass
class AirWaterFlow:
    """A Flow of air and water"""

    humid_air_flow: HumidAirFlow
    water_flow: WaterFlow
    dry: bool = field(default=True, init=False)

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
            self.dry = False
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
    def from_m_air_m_water_tot_enthalpy_flow(
        cls, m_air: float, m_water: float, tot_enthalpy_flow: float, pressure: float
    ) -> Self:
        """create air- waterflow by mixing a HumidAirFlow and a WaterFlow"""
        hum_ratio = m_water / m_air
        t_dry_bulb = get_temp_from_tot_enthalpy_air_water_mix(
            hum_ratio, tot_enthalpy_flow / (m_air + m_water), pressure
        )
        # sat_hum_ratio = ps.GetSatHumRatio(t_dry_bulb, pressure)
        sat_hum_ratio = ha.get_sat_hum_ratio(t_dry_bulb, pressure)

        if hum_ratio <= sat_hum_ratio:
            # gas phase only
            has = HumidAirState.from_t_dry_bulb_hum_ratio(
                t_dry_bulb, hum_ratio, pressure
            )
            volume_flow = m_air * has.moist_air_volume
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
        tot_enthalpy_flow = haf_in_1.tot_enthalpy_flow + haf_in_2.tot_enthalpy_flow
        if isclose(
            haf_in_1.humid_air_state.pressure, haf_in_2.humid_air_state.pressure
        ):
            pressure = haf_in_1.humid_air_state.pressure
            return cls.from_m_air_m_water_tot_enthalpy_flow(
                m_air, m_water, tot_enthalpy_flow, pressure
            )
        raise ValueError("The pressure of the mixing air streams must be equal")

    @classmethod
    def from_mixing_air_water(cls, haf_in: HumidAirFlow, wf_in: WaterFlow) -> Self:
        """create air- waterflow by mixing a HumidAirFlow and a WaterFlow"""
        m_air = haf_in.mass_flow_air
        m_water = haf_in.mass_flow_water + wf_in.mass_flow
        tot_enthalpy_flow = haf_in.tot_enthalpy_flow + wf_in.tot_enthalpy_flow
        pressure = haf_in.humid_air_state.pressure
        return cls.from_m_air_m_water_tot_enthalpy_flow(
            m_air, m_water, tot_enthalpy_flow, pressure
        )


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
    sat_hum_ratio = ha.get_sat_hum_ratio(t_dry_bulb, pressure)

    # unsaturated air
    if hum_ratio <= sat_hum_ratio:
        # recalculate with hum_ratio as the specific enthalpy per total mass
        return ha.get_moist_air_enthalpy(t_dry_bulb, hum_ratio) / (1 + hum_ratio)

    enthalpy_gas = ha.get_sat_air_enthalpy(t_dry_bulb, pressure)

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


def get_temp_from_tot_enthalpy_air_water_mix(
    hum_ratio: float, enthalpy: float, pressure: float
) -> float:
    """
    calculate temperature of an air water mix at equilibrium
    WARNING: enthalpy is per the total mass, in J / kg(Air+Water)
    """

    def fun(t):
        return enthalpy - get_tot_enthalpy_air_water_mix(hum_ratio, t, pressure)

    sol = optimize.root_scalar(fun, bracket=[-50, 99])

    if sol.converged:
        return sol.root
    raise ArithmeticError("Root not found: " + sol.flag)


def mix_two_humid_air_flows(
    haf_in_1: HumidAirFlow, haf_in_2: HumidAirFlow
) -> HumidAirFlow:
    """mix two humid air flows, raises error if there is condensation"""
    awf = AirWaterFlow.from_mixing_two_humid_air_flows(haf_in_1, haf_in_2)
    if awf.dry:
        return awf.humid_air_flow

    raise ValueError("Condensation")


def mix_humid_air_flows(hafs_in: list[HumidAirFlow]) -> HumidAirFlow:
    """mix two humid air flows, raises error if there is condensation"""

    haf_out = hafs_in[0]
    for haf in hafs_in[1:]:
        haf_out = mix_two_humid_air_flows(haf_out, haf)

    return haf_out

# should it be a method of HAF
def add_water_to_air_stream(haf: HumidAirFlow, wf: WaterFlow) -> HumidAirFlow:
    """add water stream to air stream"""
    m_air = haf.mass_flow_air
    m_water = haf.mass_flow_water + wf.mass_flow

    hum_ratio = m_water / m_air

    tot_enthalpy_flow = haf.tot_enthalpy_flow + wf.tot_enthalpy_flow
    enthalpy = tot_enthalpy_flow / m_air

    has_out = HumidAirState.from_hum_ratio_enthalpy(hum_ratio, enthalpy)

    return HumidAirFlow(m_air * has_out.moist_air_volume, has_out)
