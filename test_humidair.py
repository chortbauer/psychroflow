from pytest import approx

from humidair import *


def test_get_sat_vap_pressure():
    assert get_sat_vap_pressure(5) == approx(872.6, rel=0.0003)
    assert get_sat_vap_pressure(25) == approx(3169.7, rel=0.0003)
    assert get_sat_vap_pressure(50) == approx(12351.3, rel=0.0003)
    assert get_sat_vap_pressure(100) == approx(101418.0, rel=0.0003)
    assert get_sat_vap_pressure(150) == approx(476101.4, rel=0.0003)


def test_get_t_dew_point_from_vap_pressure():
    assert get_t_dew_point_from_vap_pressure(611.689) == approx(0.01, abs=1e-3)
    assert get_t_dew_point_from_vap_pressure(2339.32) == approx(20, rel=1e-4)
    assert get_t_dew_point_from_vap_pressure(7384.93) == approx(40, rel=1e-4)
    assert get_t_dew_point_from_vap_pressure(19_946.1) == approx(60, rel=1e-4)
    assert get_t_dew_point_from_vap_pressure(47_415.0) == approx(80, rel=1e-4)
    assert get_t_dew_point_from_vap_pressure(101_417) == approx(100, rel=1e-4)


def test_get_hum_ratio_from_rel_hum():
    assert get_hum_ratio_from_rel_hum(20,0) == approx(0, abs=1e-6)
    assert get_hum_ratio_from_rel_hum(20,1) == approx(0, abs=1e-6)
