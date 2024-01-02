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

    #     elif check_params_set(["TDryBulb", "TDewPoint"]):
    #         self.HumRatio = ps.GetHumRatioFromTDewPoint(self.TDewPoint, self.Pressure),
    #         self.TWetBulb = ps.GetTWetBulbFromHumRatio(
    #             self.TDryBulb, self.HumRatio, self.Pressure,
    #         )
    #         self.RelHum = ps.GetRelHumFromHumRatio(
    #             self.TDryBulb, self.HumRatio, self.Pressure,
    #         )
    #         self.VapPres = ps.GetVapPresFromHumRatio(self.HumRatio, self.Pressure)
    #         self.MoistAirEnthalpy = ps.GetMoistAirEnthalpy(self.TDryBulb, self.HumRatio),
    #         self.MoistAirVolume = ps.GetMoistAirVolume(
    #             self.TDryBulb, self.HumRatio, self.Pressure,
    #         )
    #         self.DegreeOfSaturation = ps.GetDegreeOfSaturation(
    #             self.TDryBulb, self.HumRatio, self.Pressure,
    #         )
    #     elif check_params_set(["TDryBulb", "RelHum"]):
    #         self.HumRatio = ps.GetHumRatioFromRelHum(
    #             self.TDryBulb, self.RelHum, self.Pressure,
    #         )
    #         self.TWetBulb = ps.GetTWetBulbFromHumRatio(
    #             self.TDryBulb, self.HumRatio, self.Pressure,
    #         )
    #         self.TDewPoint = ps.GetTDewPointFromHumRatio(
    #             self.TDryBulb, self.HumRatio, self.Pressure,
    #         )
    #         self.VapPres = ps.GetVapPresFromHumRatio(self.HumRatio, self.Pressure)
    #         self.MoistAirEnthalpy = ps.GetMoistAirEnthalpy(self.TDryBulb, self.HumRatio),
    #         self.MoistAirVolume = ps.GetMoistAirVolume(
    #             self.TDryBulb, self.HumRatio, self.Pressure,
    #         )
    #         self.DegreeOfSaturation = ps.GetDegreeOfSaturation(
    #             self.TDryBulb, self.HumRatio, self.Pressure,
    #         )
    #     else:
    #         raise ArgumentError("Invalid input Arguments for HumidAirState")


@dataclass
class AirWaterFlow:
    """class that describes a combined flow of air and water"""

    mass_flow: float
    humid_air_state: HumidAirState
    mass_flow_air: float = field(init=False)
    mass_flow_water: float = field(init=False)
    enthalpie_flow: float = field(init=False)

    def __post_init__(self):
        # self.id = f'{self.phrase}_{self.word_type.name.lower()}'
        self.mass_flow_air = 0.0  # TODO
        self.mass_flow_water = 0.0  # TODO
        self.enthalpy_flow = 0.0  # TODO


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
        enthalpy_liquid = IAPWS95(T=ps.GetTKelvinFromTCelsius(TDryBulb), x=0).h * 1000
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

has1 = HumidAirState.from_TDryBulb_RelHum(TDryBulb=35, RelHum=1.)

print(has1)

print(has1 == has)

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
