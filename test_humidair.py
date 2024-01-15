from pytest import approx

from humidair import *


def test_get_sat_vap_pressure():
    assert get_sat_vap_pressure(0.01) == approx(611.689, rel=1e-6)
    assert get_sat_vap_pressure(20) == approx(2339.32, rel=1e-6)
    assert get_sat_vap_pressure(40) == approx(7384.93, rel=1e-6)
    assert get_sat_vap_pressure(60) == approx(19_946.1, rel=1e-6)
    assert get_sat_vap_pressure(80) == approx(47_415.0, rel=1e-6)
    assert get_sat_vap_pressure(100) == approx(101_417, rel=1e-6)

    assert get_sat_vap_pressure(0) == approx(611.29, rel=1e-5)
    assert get_sat_vap_pressure(-20) == approx(103.23, rel=1e-4)
    assert get_sat_vap_pressure(-40) == approx(12.841, rel=1e-4)
    assert get_sat_vap_pressure(-60) == approx(1.0814, rel=1e-4)
    assert get_sat_vap_pressure(-80) == approx(0.054_77, rel=1e-4)
    assert get_sat_vap_pressure(-100) == approx(0.001_405_0, rel=1e-4)


def test_get_t_dew_point_from_vap_pressure():
    assert get_t_dew_point_from_vap_pressure(611.689) == approx(0.01, abs=1e-2)
    assert get_t_dew_point_from_vap_pressure(2339.32) == approx(20, rel=1e-6)
    assert get_t_dew_point_from_vap_pressure(7384.93) == approx(40, rel=1e-6)
    assert get_t_dew_point_from_vap_pressure(19_946.1) == approx(60, rel=1e-6)
    assert get_t_dew_point_from_vap_pressure(47_415.0) == approx(80, rel=1e-6)
    # assert get_t_dew_point_from_vap_pressure(101_417) == approx(100, rel=1e-6)

    assert get_t_dew_point_from_vap_pressure(611.29) == approx(0, abs=1e-4)
    assert get_t_dew_point_from_vap_pressure(103.23) == approx(-20, rel=1e-4)
    assert get_t_dew_point_from_vap_pressure(12.841) == approx(-40, rel=1e-4)
    assert get_t_dew_point_from_vap_pressure(1.0814) == approx(-60, rel=1e-4)
    assert get_t_dew_point_from_vap_pressure(0.054_77) == approx(-80, rel=1e-4)
    # assert get_t_dew_point_from_vap_pressure(0.001_405_0) == approx(-100, rel=1e-4)


def test_get_hum_ratio_from_rel_hum():
    assert get_hum_ratio_from_rel_hum(20,0) == approx(0, abs=1e-6)
    assert get_hum_ratio_from_rel_hum(20,1) == approx(0, abs=1e-6)
