import numpy as np

from typing import Any

import pytest

from psychrostate import HumidAirState
import psychrostate as psf

pressure = psf.STANDARD_PRESSURE


def approx(o1: Any, o2: Any) -> None:
    assert type(o1) == type(o2)

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
def test_has():
    has_test_data = []
    for t in np.linspace(-30, 80, 12):
        for rh in np.linspace(0, 1, 12):
            for p in np.linspace(50000, 1500000, 12):
                has = HumidAirState.from_t_dry_bulb_rel_hum(t, rh, p)
                has_test_data.append([t, rh, p, has.hum_ratio, has.moist_air_enthalpy])

    for t, rh, p, hr, h in has_test_data:
        approx(
            HumidAirState.from_t_dry_bulb_rel_hum(t, rh, p),
            HumidAirState.from_t_dry_bulb_hum_ratio(t, hr, p),
        )

    for t, rh, p, hr, h in has_test_data:
        approx(
            HumidAirState.from_t_dry_bulb_rel_hum(t, rh, p),
            HumidAirState.from_hum_ratio_enthalpy(hr, h, p),
        )
