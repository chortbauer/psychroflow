from ctypes import ArgumentError
import logging

from numbers import Real
from typing import Optional
from dataclasses import dataclass, field

import psychrolib as ps


# set the psychrolib unit system
ps.SetUnitSystem(ps.SI)


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
        self.enthalpie_flow = 0.0  # TODO


# # logging.basicConfig(level=logging.DEBUG)
has = HumidAirState(TDryBulb=35, TWetBulb=31.024634459874047)

print(has)

has = HumidAirState(TDryBulb=35, TDewPoint=20)

print(has)

has = HumidAirState(TDryBulb=35, RelHum=0.8)

print(has)
