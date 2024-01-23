# -*- coding: utf-8 -*-
"""
Created on 2024-01-02 07:09:48
@author: orc

Unit conventions:
SI units are used for all physical values except temperatur for which °C is used.
"""

# from logging import warning
from math import isclose

from typing import Self
from dataclasses import dataclass, field

# from scipy import optimize

from psychrostate import (
    HumidAirState,
    WaterState,
    get_temp_from_tot_enthalpy_air_water_mix,
    get_sat_hum_ratio,
)


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
        t_dew = f"T_dew={self.humid_air_state.t_dew_point:.1f}°C"
        f = f"Feuchte={self.humid_air_state.rel_hum*100:.1f}%"
        return "; ".join([vol, t, t_dew, f])


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
        sat_hum_ratio = get_sat_hum_ratio(t_dry_bulb, pressure)

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
