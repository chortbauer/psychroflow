from ctypes import ArgumentError
import logging

from typing import Optional, Self
from dataclasses import dataclass, field

from scipy import optimize
import psychrolib as ps
from iapws import IAPWS95


# set the psychrolib unit system
ps.SetUnitSystem(ps.SI)

STANDARD_PRESSURE = 101325  # Pa


# TODO create classmethods for differrent ways to initiate
@dataclass
class HumidAirState:
    """class that describes a humid air state"""

    Pressure: float
    HumRatio: float
    TDryBulb: float
    TWetBulb: float
    TDewPoint: float
    RelHum: float
    VapPres: float
    MoistAirEnthalpy: float
    MoistAirVolume: float
    DegreeOfSaturation: float

    @classmethod
    def from_TDryBulb_RelHum(
        cls, TDryBulb: float, RelHum: float, Pressure: float = STANDARD_PRESSURE
    ) -> Self:
        """initiate HumidAirState with TDryBulb and RelHum"""

        if 0 > RelHum > 1:
            raise ValueError("Wet bulb temperature is above dry bulb temperature")

        HumRatio = ps.GetHumRatioFromRelHum(TDryBulb, RelHum, Pressure)
        TWetBulb = ps.GetTWetBulbFromHumRatio(
            TDryBulb,
            HumRatio,
            Pressure,
        )
        TDewPoint = ps.GetTDewPointFromHumRatio(
            TDryBulb,
            HumRatio,
            Pressure,
        )
        VapPres = ps.GetVapPresFromHumRatio(HumRatio, Pressure)
        MoistAirEnthalpy = ps.GetMoistAirEnthalpy(TDryBulb, HumRatio)
        MoistAirVolume = ps.GetMoistAirVolume(
            TDryBulb,
            HumRatio,
            Pressure,
        )
        DegreeOfSaturation = ps.GetDegreeOfSaturation(TDryBulb, HumRatio, Pressure)
        return cls(
            Pressure,
            HumRatio,
            TDryBulb,
            TWetBulb,
            TDewPoint,
            RelHum,
            VapPres,
            MoistAirEnthalpy,
            MoistAirVolume,
            DegreeOfSaturation,
        )

    @classmethod
    def from_TDryBul_TWetBulb(
        cls, TDryBulb: float, TWetBulb: float, Pressure: float = STANDARD_PRESSURE
    ) -> Self:
        """initiate HumidAirState with TDryBulb and TWetBulb"""

        if TWetBulb > TDryBulb:
            raise ValueError("Wet bulb temperature is above dry bulb temperature")

        HumRatio = ps.GetHumRatioFromTWetBulb(
            TDryBulb,
            TWetBulb,
            Pressure,
        )
        TDewPoint = ps.GetTDewPointFromHumRatio(
            TDryBulb,
            HumRatio,
            Pressure,
        )
        RelHum = ps.GetRelHumFromHumRatio(
            TDryBulb,
            HumRatio,
            Pressure,
        )
        VapPres = ps.GetVapPresFromHumRatio(HumRatio, Pressure)
        MoistAirEnthalpy = ps.GetMoistAirEnthalpy(TDryBulb, HumRatio)
        MoistAirVolume = ps.GetMoistAirVolume(
            TDryBulb,
            HumRatio,
            Pressure,
        )
        DegreeOfSaturation = ps.GetDegreeOfSaturation(
            TDryBulb,
            HumRatio,
            Pressure,
        )
        return cls(
            Pressure,
            HumRatio,
            TDryBulb,
            TWetBulb,
            TDewPoint,
            RelHum,
            VapPres,
            MoistAirEnthalpy,
            MoistAirVolume,
            DegreeOfSaturation,
        )

    @classmethod
    def from_TDryBul_TDewPoint(
        cls, TDryBulb: float, TDewPoint: float, Pressure: float = STANDARD_PRESSURE
    ) -> Self:
        """initiate HumidAirState with TDryBulb and TDewPoint"""

        if TDewPoint > TDryBulb:
            raise ValueError("Dry bulb temperature is above dew point temperature")

        HumRatio = ps.GetHumRatioFromTDewPoint(TDewPoint, Pressure)
        TWetBulb = ps.GetTWetBulbFromHumRatio(
            TDryBulb,
            HumRatio,
            Pressure,
        )
        RelHum = ps.GetRelHumFromHumRatio(
            TDryBulb,
            HumRatio,
            Pressure,
        )
        VapPres = ps.GetVapPresFromHumRatio(HumRatio, Pressure)
        MoistAirEnthalpy = ps.GetMoistAirEnthalpy(TDryBulb, HumRatio)
        MoistAirVolume = ps.GetMoistAirVolume(
            TDryBulb,
            HumRatio,
            Pressure,
        )
        DegreeOfSaturation = ps.GetDegreeOfSaturation(
            TDryBulb,
            HumRatio,
            Pressure,
        )
        return cls(
            Pressure,
            HumRatio,
            TDryBulb,
            TWetBulb,
            TDewPoint,
            RelHum,
            VapPres,
            MoistAirEnthalpy,
            MoistAirVolume,
            DegreeOfSaturation,
        )


@dataclass
class HumidAirFlow:
    volume_flow: float
    humid_air_state: HumidAirState
    mass_flow_air: float = field(init=False)
    mass_flow_water: float = field(init=False)
    mass_flow: float = field(init=False)
    enthalpy_flow: float = field(init=False)

    def __post_init__(self):
        self.mass_flow_air = self.volume_flow / self.humid_air_state.MoistAirVolume
        self.mass_flow_water = self.humid_air_state.HumRatio * self.mass_flow_air
        self.mass_flow = self.mass_flow_air + self.mass_flow_water
        self.enthalpy_flow = self.humid_air_state.MoistAirEnthalpy * self.mass_flow_air


@dataclass
class WaterState:
    temperature: float
    pressure: float = field(default=STANDARD_PRESSURE)
    iapws95: IAPWS95 = field(init=False)
    density: float = field(init=False)
    enthalpy: float = field(init=False)

    def __post_init__(self):
        self.iapws95 = IAPWS95(
            T=ps.GetTKelvinFromTCelsius(self.temperature), P=self.pressure / 1e6
        )

        self.density = self.iapws95.rho
        self.enthalpy = self.iapws95.h * 1e3

    @classmethod
    def from_iapws95(cls, iapws95: IAPWS95) -> Self:
        return cls(iapws95.T, iapws95.P)


@dataclass
class WaterFlow:
    volume_flow: float
    water_state: WaterState
    mass_flow: float = field(init=False)
    enthalpy_flow: float = field(init=False)

    def __post_init__(self):
        self.mass_flow = self.volume_flow * self.water_state.density
        self.enthalpy_flow = self.water_state.enthalpy * self.mass_flow


def get_enthalpie_air_water_mix(
    HumRatio: float, TDryBulb: float, Pressure: float
) -> float:
    """specific enthalpy of an air water mixture at equilibrium"""

    sat_hum_ratio = ps.GetSatHumRatio(TDryBulb=TDryBulb, Pressure=Pressure)

    if HumRatio <= sat_hum_ratio:
        # only gas phase
        return ps.GetMoistAirEnthalpy(TDryBulb=TDryBulb, HumRatio=HumRatio)

    if TDryBulb > ps.FREEZING_POINT_WATER_SI:
        # gas over liquid water
        enthalpy_gas = ps.GetSatAirEnthalpy(TDryBulb=TDryBulb, Pressure=Pressure)
        enthalpy_liquid = IAPWS95(T=ps.GetTKelvinFromTCelsius(TDryBulb), x=0).h * 1e3
        return enthalpy_gas + (HumRatio - sat_hum_ratio) * enthalpy_liquid
    else:
        raise ArgumentError("Enthalpy over ice not implemented!")


def get_temp_from_enthalpie_air_water_mix(
    HumRatio: float, Enthalpy: float, Pressure: float
) -> float:
    """calculate temperature of an air water mix at equilibrium"""

    def fun(t):
        return Enthalpy - get_enthalpie_air_water_mix(HumRatio, t, Pressure)

    sol = optimize.root(fun, x0=20)

    if sol.success:
        return sol.x[0]
    raise ArithmeticError("Root not found: " + sol.message)


# # logging.basicConfig(level=logging.DEBUG)


# has = HumidAirState.from_TDryBul_TDewPoint(TDryBulb=35, TDewPoint=40)
has = HumidAirState.from_TDryBul_TWetBulb(TDryBulb=35, TWetBulb=35)

print(has)

# has1 = HumidAirState.from_TDryBulb_RelHum(TDryBulb=35, RelHum=1.0)

af = HumidAirFlow(1, has)

print(af)

ws = WaterState(10)

print(ws)

# t = 25
# p = 101325

# xs = ps.GetSatHumRatio(TDryBulb=t, Pressure=p)
# print(f"{xs=}")

# # es = air_water_enthalpie(xs, t, p)
# # print(f"{es=}")

# # es = air_water_enthalpie(xs*1.1, t, p)
# # print(f"{es=}")

# hs = ps.GetSatAirEnthalpy(t, p)
# print(f"{hs=} J/kg")

# h = get_enthalpie_air_water_mix(0.0203, t, p)
# print(f"{h=} J/kg")

# h_iap = IAPWS95(T=ps.GetTKelvinFromTCelsius(t), x=0).h * 1000

# print(f"{h_iap=} J/kg")

# x = 0.0034
# h = 10000

# t = get_temp_from_enthalpie_air_water_mix(x, h, p)
# print(f"{t=} °C")

# print(f"{ps.GetRelHumFromHumRatio(t,x,p)*100} %")
# h = get_enthalpie_air_water_mix(x, t, p)
# print(f"{h=} J/kg")
