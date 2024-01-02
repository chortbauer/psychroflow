from ctypes import ArgumentError
import logging

from typing import Optional
from dataclasses import dataclass, field

from scipy import optimize
import psychrolib as ps
from iapws import IAPWS95


# set the psychrolib unit system
ps.SetUnitSystem(ps.SI)

SPECIFIC_HEAT_CAPACITY_LIQUID_WATER = 4191.0  # [J/kgK]


# HACK test function
def add(x: float, y: float) -> float:
    logging.debug(f"{x=}")
    return x + y


@dataclass(kw_only=True)
class HumidAirState:
    """class that describes a humid air state"""

    Pressure: float = 101325
    HumRatio: Optional[float] = None
    TDryBulb: Optional[float] = None
    TWetBulb: Optional[float] = None
    TDewPoint: Optional[float] = None
    RelHum: Optional[float] = None
    VapPres: Optional[float] = None
    MoistAirEnthalpy: Optional[float] = None
    MoistAirVolume: Optional[float] = None
    DegreeOfSaturation: Optional[float] = None

    def __post_init__(self):
        # list of all possible parameters
        PARAMS_ALL = (
            "HumRatio",
            "TDryBulb",
            "TWetBulb",
            "TDewPoint",
            "RelHum",
            "VapPres",
            "MoistAirEnthalpy",
            "MoistAirVolume",
            "DegreeOfSaturation",
        )

        # list of booleans of which parameters have been set
        set_params = [self.__dict__[p] is not None for p in PARAMS_ALL]

        def check_params_set(params: list[str]) -> bool:
            check_params = [p in params for p in PARAMS_ALL]
            return set_params == check_params

        if check_params_set(["TDryBulb", "TWetBulb"]):
            self.HumRatio = ps.GetHumRatioFromTWetBulb(
                self.TDryBulb, self.TWetBulb, self.Pressure  # type: ignore
            )
            self.TDewPoint = ps.GetTDewPointFromHumRatio(
                self.TDryBulb, self.HumRatio, self.Pressure  # type: ignore
            )
            self.RelHum = ps.GetRelHumFromHumRatio(
                self.TDryBulb, self.HumRatio, self.Pressure  # type: ignore
            )
            self.VapPres = ps.GetVapPresFromHumRatio(self.HumRatio, self.Pressure)
            self.MoistAirEnthalpy = ps.GetMoistAirEnthalpy(self.TDryBulb, self.HumRatio)  # type: ignore
            self.MoistAirVolume = ps.GetMoistAirVolume(
                self.TDryBulb, self.HumRatio, self.Pressure  # type: ignore
            )
            self.DegreeOfSaturation = ps.GetDegreeOfSaturation(
                self.TDryBulb, self.HumRatio, self.Pressure  # type: ignore
            )
        elif check_params_set(["TDryBulb", "TDewPoint"]):
            self.HumRatio = ps.GetHumRatioFromTDewPoint(self.TDewPoint, self.Pressure)  # type: ignore
            self.TWetBulb = ps.GetTWetBulbFromHumRatio(
                self.TDryBulb, self.HumRatio, self.Pressure  # type: ignore
            )
            self.RelHum = ps.GetRelHumFromHumRatio(
                self.TDryBulb, self.HumRatio, self.Pressure  # type: ignore
            )
            self.VapPres = ps.GetVapPresFromHumRatio(self.HumRatio, self.Pressure)
            self.MoistAirEnthalpy = ps.GetMoistAirEnthalpy(self.TDryBulb, self.HumRatio)  # type: ignore
            self.MoistAirVolume = ps.GetMoistAirVolume(
                self.TDryBulb, self.HumRatio, self.Pressure  # type: ignore
            )
            self.DegreeOfSaturation = ps.GetDegreeOfSaturation(
                self.TDryBulb, self.HumRatio, self.Pressure  # type: ignore
            )
        elif check_params_set(["TDryBulb", "RelHum"]):
            self.HumRatio = ps.GetHumRatioFromRelHum(
                self.TDryBulb, self.RelHum, self.Pressure  # type: ignore
            )
            self.TWetBulb = ps.GetTWetBulbFromHumRatio(
                self.TDryBulb, self.HumRatio, self.Pressure  # type: ignore
            )
            self.TDewPoint = ps.GetTDewPointFromHumRatio(
                self.TDryBulb, self.HumRatio, self.Pressure  # type: ignore
            )
            self.VapPres = ps.GetVapPresFromHumRatio(self.HumRatio, self.Pressure)
            self.MoistAirEnthalpy = ps.GetMoistAirEnthalpy(self.TDryBulb, self.HumRatio)  # type: ignore
            self.MoistAirVolume = ps.GetMoistAirVolume(
                self.TDryBulb, self.HumRatio, self.Pressure  # type: ignore
            )
            self.DegreeOfSaturation = ps.GetDegreeOfSaturation(
                self.TDryBulb, self.HumRatio, self.Pressure  # type: ignore
            )
        else:
            raise ArgumentError("Invalid input Arguments for HumidAirState")


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


def get_enthalpie_air_water_mix(HumRatio: float, TDryBulb: float, Pressure: float) -> float:
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


# has = HumidAirState(TDryBulb=35, TDewPoint=20)

# print(has)

# has = HumidAirState(TDryBulb=35, RelHum=0.8)

# print(has)

t = 25
p = 101325

xs = ps.GetSatHumRatio(TDryBulb=t, Pressure=p)
print(f"{xs=}")

# es = air_water_enthalpie(xs, t, p)
# print(f"{es=}")

# es = air_water_enthalpie(xs*1.1, t, p)
# print(f"{es=}")

hs = ps.GetSatAirEnthalpy(t, p)
print(f"{hs=} J/kg")

h = get_enthalpie_air_water_mix(0.0203, t, p)
print(f"{h=} J/kg")

h_iap = IAPWS95(T=ps.GetTKelvinFromTCelsius(t), x=0).h * 1000

print(f"{h_iap=} J/kg")

x = 0.0034
h= 10000

t = get_temp_from_enthalpie_air_water_mix(x, h, p)
print(f"{t=} °C")

print(f"{ps.GetRelHumFromHumRatio(t,x,p)*100} %")
h = get_enthalpie_air_water_mix(x, t, p)
print(f"{h=} J/kg")
