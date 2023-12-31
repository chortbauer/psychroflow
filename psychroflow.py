from ctypes import ArgumentError
import logging

import numbers
from typing import Optional
from dataclasses import dataclass, field

import psychrolib as ps


# set the psychrolib unit system
ps.SetUnitSystem(ps.SI)


# HACK test function
def add(x: float, y: float) -> float:
    logging.debug(f"{x=}")
    return x + y


@dataclass(init=False)
class HumidAirState:
    """class that describes a humid air state"""

    pressure: float
    hum_ratio: float
    t_dry_bulb: float
    t_wet_bulb: float
    t_dew_point: float
    rel_hum: float
    vap_pres: float
    moist_air_enthalpie: float
    moist_air_volume: float
    degree_of_saturation: float

    def __init__(
        self,
        pressure: float = 101325,
        t_dry_bulb: Optional[float] = None,
        t_wet_bulb: Optional[float] = None,
        t_dew_point: Optional[float] = None,
        rel_hum: Optional[float] = None,
        vap_pres: Optional[float] = None,
        moist_air_enthalpie: Optional[float] = None,
        moist_air_volume: Optional[float] = None,
        degree_of_saturation: Optional[float] = None,
    ):
        self.pressure = pressure

        def check_params(params_pos: list[str]) -> bool:
            """function that checks if the given arguments match a pattern of parameters"""

            logging.debug("Checking parameters: " + str(params_pos))

            params_all = [
                "t_dry_bulb",
                "t_wet_bulb",
                "t_dew_point",
                "rel_hum",
                "vap_pres",
                "moist_air_enthalpie",
                "moist_air_volume",
                "degree_of_saturation",
            ]

            args_all = [
                t_dry_bulb,
                t_wet_bulb,
                t_dew_point,
                rel_hum,
                vap_pres,
                moist_air_enthalpie,
                moist_air_volume,
                degree_of_saturation,
            ]

            # list of arguments that should be numbers
            args_pos = [args_all[params_all.index(param)] for param in params_pos]

            # list of arguments that should be None
            args_neg = [
                args_all[params_all.index(param)]
                for param in params_all
                if param not in params_pos
            ]

            if all(isinstance(arg, numbers.Real) for arg in args_pos):
                logging.debug("The given parameters match the pattern")
                if all(arg is None for arg in args_neg):
                    return True
                else:
                    raise ArgumentError("Invalid combination of parameters given!")
            else:
                logging.debug("The given parameters do not match the pattern")
                return False

        if check_params(["t_dry_bulb", "t_wet_bulb"]):
            if isinstance(t_dry_bulb, numbers.Real):
                self.t_dry_bulb = float(t_dry_bulb)
            if isinstance(t_wet_bulb, numbers.Real):
                self.t_wet_bulb = float(t_wet_bulb)

            # self.hum_ratio = ps.GetHumRatioFromTWetBulb(self.t_dry_bulb, self.t_wet_bulb, self.pressure)
            # self.t_dew_point = ps.GetTDewPointFromHumRatio(self.t_dry_bulb, self.hum_ratio, self.pressure)
            # self.rel_hum = ps.GetRelHumFromHumRatio(self.t_dry_bulb, self.hum_ratio, self.pressure)
            # self. = ps.GetVapPresFromHumRatio(self.hum_ratio, self.pressure)
            # MoistAirEnthalpy = ps.GetMoistAirEnthalpy(self.t_dry_bulb, self.hum_ratio)
            # MoistAirVolume = ps.GetMoistAirVolume(self.t_dry_bulb, self.hum_ratio, self.pressure)
            # DegreeOfSaturation = ps.GetDegreeOfSaturation(self.t_dry_bulb, self.hum_ratio, self.pressure)

            (
                self.hum_ratio,
                self.t_dew_point,
                self.rel_hum,
                self.vap_pres,
                self.moist_air_enthalpie,
                self.moist_air_volume,
                self.degree_of_saturation,
            ) = ps.CalcPsychrometricsFromTWetBulb(
                TDryBulb=self.t_dry_bulb, TWetBulb=self.t_wet_bulb, Pressure=pressure
            )
            # HumRatio, TDewPoint, RelHum, VapPres, MoistAirEnthalpy, MoistAirVolume, DegreeOfSaturation

        if check_params(["t_dry_bulb", "rel_hum"]):
            if isinstance(t_dry_bulb, numbers.Real):
                self.t_dry_bulb = float(t_dry_bulb)
            if isinstance(rel_hum, numbers.Real):
                self.rel_hum = float(rel_hum)

            (
                self.hum_ratio,
                self.t_wet_bulb,
                self.t_dew_point,
                self.vap_pres,
                self.moist_air_enthalpie,
                self.moist_air_volume,
                self.degree_of_saturation,
            ) = ps.CalcPsychrometricsFromRelHum(
                TDryBulb=self.t_dry_bulb, RelHum=self.rel_hum, Pressure=pressure
            )
            # HumRatio, TWetBulb, TDewPoint, VapPres, MoistAirEnthalpy, MoistAirVolume, DegreeOfSaturation

        
        if check_params(["t_dry_bulb", "t_dew_point"]):
            if isinstance(t_dry_bulb, numbers.Real):
                self.t_dry_bulb = float(t_dry_bulb)
            if isinstance(t_dew_point, numbers.Real):
                self.t_dew_point = float(t_dew_point)

            (
                self.hum_ratio,
                self.t_wet_bulb,
                self.rel_hum,
                self.vap_pres,
                self.moist_air_enthalpie,
                self.moist_air_volume,
                self.degree_of_saturation,
            ) = ps.CalcPsychrometricsFromTDewPoint(
                TDryBulb=self.t_dry_bulb, TDewPoint=self.t_dew_point, Pressure=pressure
            )
            # HumRatio, TWetBulb, RelHum, VapPres, MoistAirEnthalpy, MoistAirVolume, DegreeOfSaturation




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


# logging.basicConfig(level=logging.DEBUG)
has = HumidAirState(t_dry_bulb=35, t_wet_bulb=31.814175443002092)

print(has)

has = HumidAirState(t_dry_bulb=35, t_dew_point=31.024634459874047)

print(has)

has = HumidAirState(t_dry_bulb=35, rel_hum=0.8)

print(has)
