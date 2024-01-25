import marimo

__generated_with = "0.1.81"
app = marimo.App()


@app.cell
def __(mo):
    number_air_flows = mo.ui.number(1,10,label="Anzahl Luftströme")
    number_air_flows
    return number_air_flows,


@app.cell
def __(interface_md, ui):
    interface_md(ui)
    return


@app.cell
def __(psf, pss, ui):
    hafs = []
    for v, t, rh in ui.value:
        _haf = psf.HumidAirFlow(
            v / 3600,
            pss.HumidAirState.from_t_dry_bulb_rel_hum(
                t, rh / 100
            ),
        )
        hafs.append(_haf)

    haf = psf.mix_humid_air_flows(hafs)
    haf.str_short()
    return haf, hafs, rh, t, v


@app.cell
def __(mo, number_air_flows):
    def interface_constructor(i):
        sl_vol = mo.ui.slider(0,100000,value=0, label="V [m³/h]")
        sl_t_dry_bulb = mo.ui.slider(-20,80, value=20, label="T [°C]")
        sl_rel_hum = mo.ui.slider(0,100,step=1, value=30, label="rel Hum. [%]")
        # ui = mo.md(f"{sl_vol} {sl_t_dry_bulb} {sl_rel_hum}")
        ui = mo.ui.array([sl_vol, sl_t_dry_bulb, sl_rel_hum])
        return ui

    def interface_multiplier(number):
        ui = mo.ui.array([interface_constructor(i) for i in range(number)])
        return ui

    ui = interface_multiplier(number_air_flows.value)

    def interface_md(ui):
        ui_str_lines = []
        for ui_flow in ui.elements:
            ui_str_elems = []
            for elem in ui_flow.elements:
                ui_str_elems.append(f"{elem}")
            ui_str_lines.append(" ".join(ui_str_elems))

        return mo.md(" ".join(ui_str_lines))

    ui
    return interface_constructor, interface_md, interface_multiplier, ui


@app.cell
def __():
    import psychroflow as psf
    import psychrostate as pss
    return psf, pss


@app.cell
def __():
    import marimo as mo
    return mo,


if __name__ == "__main__":
    app.run()
