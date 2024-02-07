# -*- coding: utf-8 -*-
"""
Created on 2024-02-07 14:25:22
@author: orc
"""

import numpy as np

from math import log

# Constants
M = 18.015268  # g/mol
R = 0.461526  # kJ/kg·K

# Table 1 from Release on the Values of Temperature, Pressure and Density of
# Ordinary and Heavy Water Substances at their Respective Critical Points
Tc = 647.096  # K
Pc = 22.064  # MPa
rhoc = 322.0  # kg/m³
Tc_D2O = 643.847  # K
Pc_D2O = 21.6618  # MPa
rhoc_D2O = 355.9999698294  # kg/m³

Tt = 273.16  # K
Pt = 611.657e-6  # MPa
Tb = 373.1243  # K
f_acent = 0.3443

# IAPWS, Guideline on the Use of Fundamental Physical Constants and Basic
# Constants of Water, http://www.iapws.org/relguide/fundam.pdf
Dipole = 1.85498  # Debye


def get_enthalpy_ice(T, P):
    """
    References
    ----------
    IAPWS, Revised Release on the Equation of State 2006 for H2O Ice Ih
    September 2009, http://iapws.org/relguide/Ice-2009.html
    """
    # Check input in range of validity
    if T > 273.16:
        # No Ice Ih stable
        warnings.warn("Metastable ice")
    elif P > 208.566:
        # Ice Ih limit upper pressure
        raise NotImplementedError("Incoming out of bound")
    elif P < Pt:
        Psub = _Sublimation_Pressure(T)
        if Psub > P:
            # Zone Gas
            warnings.warn("Metastable ice in vapor region")
    elif T > 251.165:
        Pmel = _Melting_Pressure(T)
        if Pmel < P:
            # Zone Liquid
            warnings.warn("Metastable ice in liquid region")

    Tr = T / Tt
    Pr = P / Pt
    P0 = 101325e-6 / Pt
    s0 = -0.332733756492168e4 * 1e-3  # Express in kJ/kgK

    gok = [
        -0.632020233335886e6,
        0.655022213658955,
        -0.189369929326131e-7,
        0.339746123271053e-14,
        -0.556464869058991e-21,
    ]
    r2k = [
        complex(-0.725974574329220e2, -0.781008427112870e2) * 1e-3,
        complex(-0.557107698030123e-4, 0.464578634580806e-4) * 1e-3,
        complex(0.234801409215913e-10, -0.285651142904972e-10) * 1e-3,
    ]
    t1 = complex(0.368017112855051e-1, 0.510878114959572e-1)
    t2 = complex(0.337315741065416, 0.335449415919309)
    r1 = complex(0.447050716285388e2, 0.656876847463481e2) * 1e-3

    go = gop = gopp = 0
    for k in range(5):
        go += gok[k] * 1e-3 * (Pr - P0) ** k
    for k in range(1, 5):
        gop += gok[k] * 1e-3 * k / Pt * (Pr - P0) ** (k - 1)
    for k in range(2, 5):
        gopp += gok[k] * 1e-3 * k * (k - 1) / Pt**2 * (Pr - P0) ** (k - 2)
    r2 = r2p = 0
    for k in range(3):
        r2 += r2k[k] * (Pr - P0) ** k
    for k in range(1, 3):
        r2p += r2k[k] * k / Pt * (Pr - P0) ** (k - 1)
    r2pp = r2k[2] * 2 / Pt**2

    c = r1 * (
        (t1 - Tr) * log(t1 - Tr)
        + (t1 + Tr) * log(t1 + Tr)
        - 2 * t1 * log(t1)
        - Tr**2 / t1
    ) + r2 * (
        (t2 - Tr) * log(t2 - Tr)
        + (t2 + Tr) * log(t2 + Tr)
        - 2 * t2 * log(t2)
        - Tr**2 / t2
    )
    ct = r1 * (-log(t1 - Tr) + log(t1 + Tr) - 2 * Tr / t1) + r2 * (
        -log(t2 - Tr) + log(t2 + Tr) - 2 * Tr / t2
    )
    ctt = r1 * (1 / (t1 - Tr) + 1 / (t1 + Tr) - 2 / t1) + r2 * (
        1 / (t2 - Tr) + 1 / (t2 + Tr) - 2 / t2
    )
    cp = r2p * (
        (t2 - Tr) * log(t2 - Tr)
        + (t2 + Tr) * log(t2 + Tr)
        - 2 * t2 * log(t2)
        - Tr**2 / t2
    )
    ctp = r2p * (-log(t2 - Tr) + log(t2 + Tr) - 2 * Tr / t2)
    cpp = r2pp * (
        (t2 - Tr) * log(t2 - Tr)
        + (t2 + Tr) * log(t2 + Tr)
        - 2 * t2 * log(t2)
        - Tr**2 / t2
    )

    g = go - s0 * Tt * Tr + Tt * c.real
    gt = -s0 + ct.real
    gp = gop + Tt * cp.real
    gtt = ctt.real / Tt
    gtp = ctp.real
    gpp = gopp + Tt * cpp.real

    h = g - T * gt

    return h
