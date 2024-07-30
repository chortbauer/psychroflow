import marimo

__generated_with = "0.7.9"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np

    import psychrostate as ps

    from typing import Self
    from math import exp, isclose
    from dataclasses import dataclass
    from scipy import optimize

    from waterstate import (
        get_enthalpy_water,
        get_enthalpy_water_liquid,
        get_enthalpy_water_ice,
    )
    return (
        Self,
        dataclass,
        exp,
        get_enthalpy_water,
        get_enthalpy_water_ice,
        get_enthalpy_water_liquid,
        isclose,
        mo,
        np,
        optimize,
        plt,
        ps,
    )


@app.cell
def __(hum_ratio, pressure, ps, t_dry_bulb):
    def fun_t(t):
        return (
            ps.get_moist_air_enthalpy(t_dry_bulb, hum_ratio)
            + (ps.get_sat_hum_ratio(t, pressure) - hum_ratio) * ps.get_enthalpy_water(t)
            - ps.get_sat_air_enthalpy(t, pressure)
        )
    return fun_t,


@app.cell
def __(optimize, ps):
    def get_t_wet_bulb(t_dry_bulb: float, hum_ratio: float, pressure: float) -> float:
        def fun(t):
            return (
                ps.get_moist_air_enthalpy(t_dry_bulb, hum_ratio)
                + (ps.get_sat_hum_ratio(t, pressure) - hum_ratio) * ps.get_enthalpy_water(t)
                - ps.get_sat_air_enthalpy(t, pressure)
            )

        sol = optimize.root_scalar(fun, method="brentq", bracket=[-223.1, 99.9])

        if sol.converged:
            return sol.root
        raise ArithmeticError("Root not found: " + sol.flag)
    return get_t_wet_bulb,


@app.cell
def __(ps, sl_rel_hum, sl_t):
    has = ps.HumidAirState.from_t_dry_bulb_rel_hum(sl_t.value,sl_rel_hum.value/100)
    has
    return has,


@app.cell
def __(mo):
    sl_t = mo.ui.slider(-100,100, value=20,show_value=True, label="T_dry_bulb [°C]", full_width=True)
    sl_rel_hum = mo.ui.slider(0,100, value=50, show_value=True, label="rel Hum [%]", full_width=True)
    sl_pressure = mo.ui.slider(8e4,1.2e5, value=1e5, show_value=True, label="Pressure [Pa]", full_width=True)

    mo.vstack([sl_t, sl_pressure])
    return sl_pressure, sl_rel_hum, sl_t


@app.cell
def __(np, plt, ps, sl_pressure, sl_t):


    t_dry_bulb = sl_t.value
    pressure = sl_pressure.value

    # t_ = np.linspace(t_dry_bulb-t_int, t_dry_bulb+t_int, 500)
    # hum_ratio_ = np.linspace(0, hum_ratio_s, 500)
    phi_ = np.linspace(0,1,500)

    fun_t_wet_phi = lambda phi: ps.get_t_wet_bulb_from_t_dry_bulb_hum_ratio(t_dry_bulb, ps.get_hum_ratio_from_rel_hum(t_dry_bulb, phi,pressure), pressure)

    fig, ax = plt.subplots(1, figsize=(10,6))

    ax.grid()

    # ax.plot(hum_ratio_, [fun_(h) for h in hum_ratio_])
    # ax.plot(t_, [fun_t(t) for t in t_])
    ax.plot(phi_, [fun_t_wet_phi(phi) for phi in phi_])
    return ax, fig, fun_t_wet_phi, phi_, pressure, t_dry_bulb


@app.cell
def __():
    return


@app.cell
def __(ps):
    ps.get_sat_vap_pressure(373.9)
    return


@app.cell
def __(ps, test):
    ps.isclose(0,test)
    return


@app.cell
def __():
    test = 0/1
    return test,


@app.cell
def __(ps):
    ps.HumidAirState.from_t_dry_bulb_rel_hum(-50, 1, 8e4)
    return


@app.cell
def __(ps):
    ps.HumidAirState.from_t_dry_bulb_rel_hum(-50,1)
    return


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
