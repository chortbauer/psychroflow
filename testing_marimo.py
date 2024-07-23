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
def __(has, ps):
    hum_ratio=has.hum_ratio
    t_dry_bulb=has.t_dry_bulb
    pressure=has.pressure
    def fun_(t):
        return (
            ps.get_moist_air_enthalpy(t_dry_bulb, hum_ratio)
            + (ps.get_sat_hum_ratio(t, pressure) - hum_ratio) * ps.get_enthalpy_water(t)
            - ps.get_sat_air_enthalpy(t, pressure)
        )
    return fun_, hum_ratio, pressure, t_dry_bulb


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
def __(mo):
    sl_t = mo.ui.slider(-100,100, value=20,show_value=True, label="T_dry_bulb [°C]", full_width=True)
    sl_rel_hum = mo.ui.slider(0,100, value=50, show_value=True, label="rel Hum [%]", full_width=True)

    mo.vstack([sl_t, sl_rel_hum])
    return sl_rel_hum, sl_t


@app.cell
def __(ps, sl_rel_hum, sl_t):
    has = ps.HumidAirState.from_t_dry_bulb_rel_hum(sl_t.value,sl_rel_hum.value/100)
    has
    return has,


@app.cell
def __(get_t_wet_bulb, has):
    get_t_wet_bulb(has.t_dry_bulb, has.hum_ratio, has.pressure)
    return


@app.cell
def __(fun_, np, plt):
    t_ = np.linspace(-1, 1, 500)

    fig, ax = plt.subplots(1, figsize=(10,6))

    ax.grid()

    ax.plot(t_, [fun_(t) for t in t_])
    return ax, fig, t_


@app.cell
def __():
    return


@app.cell
def __(ps):
    ps.get_sat_vap_pressure(373.9)
    return


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
