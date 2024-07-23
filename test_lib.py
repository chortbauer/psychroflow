# -*- coding: utf-8 -*-
"""
test psychrostate

Created on 2024-01-24 08:17:15
@author: orc
"""

from typing import Any

import pytest
import numpy as np

from psychrostate import HumidAirState
import psychrostate as ps
import psychroflow as pf

P = ps.STANDARD_PRESSURE


def approx(o1: Any, o2: Any) -> None:
    """custom approx functioin that handles dataclasses"""
    assert isinstance(o1, type(o2))

    o1_keys = [v for v in dir(o1) if not v.startswith("__")]
    o2_keys = [v for v in dir(o2) if not v.startswith("__")]

    assert sorted(o1_keys) == sorted(o2_keys)

    for k in o1_keys:
        v1 = getattr(o1, k)
        v2 = getattr(o2, k)
        if isinstance(v1, int) or isinstance(v1, float):
            assert v1 == pytest.approx(v2)
            continue

        if isinstance(v1, bool) or isinstance(v1, str):
            assert v1 == v2
            continue

        approx(v1, v2)


# test different methods to initialize HumidAirState
def test_has_init_methods():
    """tests if all classmethods for initiating a HumidAirState agree with each other"""

    # generate test data using from_t_dry_bulb_rel_hum
    has_test_data = []
    for t in np.linspace(-50, 80, 16):
        for rh in np.linspace(0, 1, 8):
            for p in np.linspace(80000, 1500000, 8):
                has = HumidAirState.from_t_dry_bulb_rel_hum(t, rh, p)
                has_test_data.append([t, rh, p, has.hum_ratio, has.moist_air_enthalpy])

    # compare with from_t_dry_bulb_hum_ratio
    for t, rh, p, hr, h in has_test_data:
        approx(
            HumidAirState.from_t_dry_bulb_rel_hum(t, rh, p),
            HumidAirState.from_t_dry_bulb_hum_ratio(t, hr, p),
        )

    # compare with from_hum_ratio_enthalpy
    for t, rh, p, hr, h in has_test_data:
        approx(
            HumidAirState.from_t_dry_bulb_rel_hum(t, rh, p),
            HumidAirState.from_hum_ratio_enthalpy(hr, h, p),
        )


# test different methods to initialize HumidAirFlow
def test_haf_init_methods():
    """tests if all classmethods for initiating a HumidAirFlow agree with each other"""

    # generate test data for comparisons
    haf_test_data = []
    for q in np.linspace(0.1, 1e5/3600, 16):
        for t in np.linspace(-50, 80, 4):
            for rh in np.linspace(0, 1, 4):
                for p in np.linspace(80000, 1500000, 4):
                    has = HumidAirState.from_t_dry_bulb_rel_hum(t, rh, p)
                    haf = pf.HumidAirFlow(q, has)
                    haf_test_data.append(
                        [
                            haf,
                            q,
                            p,
                            has,
                            haf.mass_flow_air,
                            haf.mass_flow_water,
                            haf.enthalpy_flow,
                        ]
                    )

    # compare with from_m_air_HumidAirState
    for haf, q, p, has, mass_flow_air, mass_flow_water, enthalpy_flow in haf_test_data:
        approx(haf, pf.HumidAirFlow.from_m_air_HumidAirState(mass_flow_air, has))

    # compare with from_m_air_m_water_enthalpy_flow
    for haf, q, p, has, mass_flow_air, mass_flow_water, enthalpy_flow in haf_test_data:
        approx(
            haf,
            pf.HumidAirFlow.from_m_air_m_water_enthalpy_flow(
                mass_flow_air, mass_flow_water, enthalpy_flow, p
            ),
        )
