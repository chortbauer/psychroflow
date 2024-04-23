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
from scipy import optimize

from psychrostate import (
    HumidAirState,
    get_t_dry_bulb_from_tot_enthalpy_air_water_mix,
    get_sat_hum_ratio,
    STANDARD_PRESSURE,
)
from waterstate import WaterState


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

    @classmethod
    def from_volume_flow_temperature(
        cls, volume_flow: float, temperature: float
    ) -> Self:
        """init with volume_flow and temperature"""
        return cls(volume_flow, WaterState(temperature))

    @classmethod
    def from_mass_flow_temperature(cls, mass_flow: float, temperature: float) -> Self:
        """init with mass_flow and temperature"""
        ws = WaterState(temperature)
        return cls(mass_flow / ws.density, ws)


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

    @classmethod
    def from_m_air_HumidAirState(
        cls, mass_flow_air: float, humid_air_state: HumidAirState
    ) -> Self:
        """create humid air flow from mass_flow_air and humid_air_state"""
        volume_flow = mass_flow_air * humid_air_state.moist_air_volume
        return cls(volume_flow, humid_air_state)

    @classmethod
    def from_m_air_m_water_enthalpy_flow(
        cls, m_air: float, m_water: float, enthalpy_flow: float, pressure: float
    ) -> Self:
        """create humid air flow from m_air, m_water and enthalpy"""
        hum_ratio = m_water / m_air
        t_dry_bulb = get_t_dry_bulb_from_tot_enthalpy_air_water_mix(
            hum_ratio, enthalpy_flow / (m_air + m_water), pressure
        )
        # sat_hum_ratio = ps.GetSatHumRatio(t_dry_bulb, pressure)
        sat_hum_ratio = get_sat_hum_ratio(t_dry_bulb, pressure)

        if hum_ratio <= sat_hum_ratio:
            # gas phase only
            has = HumidAirState.from_t_dry_bulb_hum_ratio(
                t_dry_bulb, hum_ratio, pressure
            )
            volume_flow = m_air * has.moist_air_volume
            return cls(volume_flow, has)

        raise ValueError("Condensation")

    def str_short(self) -> str:
        """returns a short strin repr"""
        vol = f"V={self.volume_flow*3600:.1f}m³/h"
        t = f"T={self.humid_air_state.t_dry_bulb:.1f}°C"
        t_dew = f"T_dew={self.humid_air_state.t_dew_point:.1f}°C"
        f = f"Feuchte={self.humid_air_state.rel_hum*100:.1f}%"
        return "; ".join([vol, t, t_dew, f])

    def add_water_flow(
        self, wf: WaterFlow, *, ignore_valid_range=False
    ) -> "HumidAirFlow":
        """add water flow"""
        m_air = self.mass_flow_air
        m_water = self.mass_flow_water + wf.mass_flow

        hum_ratio = m_water / m_air

        enthalpy_flow = self.enthalpy_flow + wf.enthalpy_flow
        enthalpy = enthalpy_flow / m_air

        has_out = HumidAirState.from_hum_ratio_enthalpy(hum_ratio, enthalpy)

        if not ignore_valid_range:
            if has_out.rel_hum > 1:
                raise ValueError("Condensation")

        return HumidAirFlow(m_air * has_out.moist_air_volume, has_out)

    def how_much_water_to_rel_hum(
        self, t_water: float, rel_hum_target: float
    ) -> WaterFlow:
        """returns the water flow needed to reach the target relative humidity"""

        if rel_hum_target < self.humid_air_state.rel_hum:
            raise ValueError("rel_hum_target must be higher than current rel_hum")

        def fun(v_f):
            rel_hum_mix = self.add_water_flow(
                WaterFlow(v_f, WaterState(t_water)), ignore_valid_range=True
            ).humid_air_state.rel_hum

            if rel_hum_mix > 1:
                return 1 - rel_hum_target
            return rel_hum_mix - rel_hum_target

        sol = optimize.root_scalar(
            fun, method="brentq", bracket=[0, self.volume_flow / 1e0], xtol=1e-24
        )

        if sol.converged:
            return WaterFlow(sol.root, WaterState(t_water))

        raise ValueError("Root not converged: " + sol.flag)

    def add_water_to_rel_hum(
        self, t_water: float, rel_hum_target: float
    ) -> "HumidAirFlow":
        """add water with specified temperature to air flow to reach specified relative humidity"""
        wf = self.how_much_water_to_rel_hum(t_water, rel_hum_target)

        return self.add_water_flow(wf)

    def add_enthalpy(self, enthalpy_added_flow: float) -> "HumidAirFlow":
        """add enthalpy_flow [W] to humid air flow"""
        enthalpy_flow = self.enthalpy_flow + enthalpy_added_flow
        pressure = self.humid_air_state.pressure

        return HumidAirFlow.from_m_air_m_water_enthalpy_flow(
            self.mass_flow_air, self.mass_flow_water, enthalpy_flow, pressure
        )

    def get_enthalpy_to_rel_hum(self, rel_hum_target: float) -> float:
        """get the enthalpy_flow [W] needed to reach a target relative humidity"""

        if 1 < rel_hum_target:
            raise ValueError("Relative humidity target cannot be > 1")

        if (not isclose(0, self.humid_air_state.hum_ratio)) and isclose(
            0, rel_hum_target
        ):
            raise ValueError("Relative humidity target cannot be 0")

        def fun(h_f):
            rel_hum = self.add_enthalpy(h_f).humid_air_state.rel_hum

            return rel_hum - rel_hum_target

        has_lower_bound = HumidAirState.from_t_dry_bulb_hum_ratio(
            self.humid_air_state.t_dew_point,
            self.humid_air_state.hum_ratio,
            pressure=self.humid_air_state.pressure,
        )
        h_f_lower_bound = (
            has_lower_bound.moist_air_enthalpy - self.humid_air_state.moist_air_enthalpy
        ) * self.mass_flow_air

        has_upper_bound = HumidAirState.from_t_dry_bulb_hum_ratio(
            150,
            self.humid_air_state.hum_ratio,
            pressure=self.humid_air_state.pressure,
        )

        h_f_upper_bound = (
            has_upper_bound.moist_air_enthalpy - self.humid_air_state.moist_air_enthalpy
        ) * self.mass_flow_air

        sol = optimize.root_scalar(
            fun, method="brentq", bracket=[h_f_lower_bound, h_f_upper_bound]
        )

        if sol.converged:
            return sol.root

        raise ValueError("Root not converged: " + sol.flag)

    # TODO test
    # TODO is the gas ratio valid after combustion?
    # def heat_with_gas(self, m_gas_flow: float) -> "HumidAirFlow":
    #     """heat the humid air flow by burning gas (CH4) [kg/s]"""
    #     mol_mass_ch4 = 16  # g/mol
    #     mol_mass_h2o = 18  # g/mol

    #     # TODO enthalpy gas flow

    #     m_water_flow_combustion = m_gas_flow / mol_mass_ch4 * 2 * mol_mass_h2o

    #     calorific_value_gas_gross = 12 * 1000 * 3600  # kWh/kg to J/kg

    #     enthalpy_flow_combustion = m_gas_flow * calorific_value_gas_gross

    #     m_water = self.mass_flow_water + m_water_flow_combustion
    #     m_air = 1 # TODO calculate air mass after combustion
    #     enthalpy_flow = self.enthalpy_flow + enthalpy_flow_combustion

    #     return HumidAirFlow.from_m_air_m_water_enthalpy_flow(
    #         m_air, m_water, enthalpy_flow, self.humid_air_state.pressure
    #     )

    def at_reference_point_DIN1334(self, dry: bool = True) -> "HumidAirFlow":
        if dry:
            has_din1343_dry = HumidAirState.from_t_dry_bulb_rel_hum(
                t_dry_bulb=0,
                rel_hum=0,
                pressure=101325,
            )
            return HumidAirFlow.from_m_air_HumidAirState(
                self.mass_flow_air, has_din1343_dry
            )
        else:
            # has_din1343_wet = HumidAirState.from_t_dry_bulb_hum_ratio(
            #     t_dry_bulb=0,
            #     hum_ratio=self.humid_air_state.hum_ratio,
            #     pressure=101325,
            # )
            # return HumidAirFlow.from_m_air_HumidAirState(
            #     self.mass_flow_air, has_din1343_wet
            # )
            raise ValueError("only dry reference state implemented")


@dataclass
class AirWaterFlow:
    """A Flow of air and water"""

    humid_air_flow: HumidAirFlow
    water_flow: WaterFlow
    dry: bool = field(default=True, init=False)
    mass_flow_air: float = field(init=False)
    mass_flow_water: float = field(init=False)
    mass_flow: float = field(init=False)
    enthalpy_flow: float = field(init=False)

    def __post_init__(self):
        # TODO allow no air
        # check if temperatures match
        if not isclose(
            self.humid_air_flow.humid_air_state.t_dry_bulb,
            self.water_flow.water_state.temperature,
        ):
            raise ValueError("Temperature of air- and waterflow must be equal!")

        # if liquid water
        if not isclose(self.water_flow.mass_flow, 0):
            self.dry = False
            # if there is liquid water the air has to be saturated
            if not isclose(self.humid_air_flow.humid_air_state.rel_hum, 1):
                raise ValueError("Air over liquid water has to be saturated")

        self.mass_flow_air = self.humid_air_flow.mass_flow_air
        self.mass_flow_water = (
            self.humid_air_flow.mass_flow_water + self.water_flow.mass_flow
        )
        self.mass_flow = self.mass_flow_air + self.mass_flow_water
        self.enthalpy_flow = (
            self.humid_air_flow.enthalpy_flow + self.water_flow.enthalpy_flow
        )

    @classmethod
    def from_humid_air_flow(cls, haf: HumidAirFlow) -> Self:
        """air water flow with humid air only"""
        return cls(
            haf,
            WaterFlow(
                0,
                WaterState(haf.humid_air_state.t_dry_bulb),
            ),
        )

    @classmethod
    def from_water_flow(
        cls, wf: WaterFlow, pressure: float = STANDARD_PRESSURE
    ) -> Self:
        """air water flow with liquid water only"""
        return cls(
            HumidAirFlow(
                0,
                HumidAirState.from_t_dry_bulb_rel_hum(
                    wf.water_state.temperature, 1, pressure
                ),
            ),
            wf,
        )

    @classmethod
    def from_m_air_m_water_enthalpy_flow(
        cls, m_air: float, m_water: float, enthalpy_flow: float, pressure: float
    ) -> Self:
        """create air- waterflow by mixing a HumidAirFlow and a WaterFlow"""
        hum_ratio = m_water / m_air
        t_dry_bulb = get_t_dry_bulb_from_tot_enthalpy_air_water_mix(
            hum_ratio, enthalpy_flow / (m_air + m_water), pressure
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
        ws = WaterState(t_dry_bulb)
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
        enthalpy_flow = haf_in_1.enthalpy_flow + haf_in_2.enthalpy_flow
        if isclose(
            haf_in_1.humid_air_state.pressure, haf_in_2.humid_air_state.pressure
        ):
            pressure = haf_in_1.humid_air_state.pressure
            return cls.from_m_air_m_water_enthalpy_flow(
                m_air, m_water, enthalpy_flow, pressure
            )
        raise ValueError("The pressure of the mixing air streams must be equal")

    @classmethod
    def from_mixing_air_water(cls, haf_in: HumidAirFlow, wf_in: WaterFlow) -> Self:
        """create air- waterflow by mixing a HumidAirFlow and a WaterFlow"""
        m_air = haf_in.mass_flow_air
        m_water = haf_in.mass_flow_water + wf_in.mass_flow
        enthalpy_flow = haf_in.enthalpy_flow + wf_in.enthalpy_flow
        pressure = haf_in.humid_air_state.pressure
        return cls.from_m_air_m_water_enthalpy_flow(
            m_air, m_water, enthalpy_flow, pressure
        )

    def add_enthalpy(self, enthalpy_flow: float) -> "AirWaterFlow":
        """add enthalpy_flow [W] to AirWaterFlow"""
        m_air = self.mass_flow_air
        m_water = self.mass_flow_water
        enthalpy_flow = self.enthalpy_flow + enthalpy_flow
        pressure = self.humid_air_flow.humid_air_state.pressure
        return AirWaterFlow.from_m_air_m_water_enthalpy_flow(
            m_air, m_water, enthalpy_flow, pressure
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

    # haf_out = hafs_in[0]
    # for haf in hafs_in[1:]:
    #     haf_out = mix_two_humid_air_flows(haf_out, haf)

    pressures = [haf.humid_air_state.pressure for haf in hafs_in]
    if not all(
        isclose(pressures[i], pressures[i + 1]) for i in range(len(pressures) - 1)
    ):
        raise ValueError("Pressure of mixing air flows must be equal")

    awf = AirWaterFlow.from_m_air_m_water_enthalpy_flow(
        m_air=sum([haf.mass_flow_air for haf in hafs_in]),
        m_water=sum([haf.mass_flow_water for haf in hafs_in]),
        enthalpy_flow=sum([haf.enthalpy_flow for haf in hafs_in]),
        pressure=pressures[0],
    )

    if awf.dry:
        return awf.humid_air_flow

    raise ValueError("Condensation")


def add_water_to_air_stream(haf: HumidAirFlow, wf: WaterFlow) -> HumidAirFlow:
    """add water stream to air stream"""
    return haf.add_water_flow(wf)
