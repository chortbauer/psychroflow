# -*- coding: utf-8 -*-
"""
Created on 2024-01-23 14:59:00
@author: orc
"""

from dataclasses import dataclass, field

STANDARD_PRESSURE = 101_325  # Pa

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