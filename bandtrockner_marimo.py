import marimo

__generated_with = "0.7.9"
app = marimo.App()


@app.cell
def __(haf_mix, haf_pri, haf_sec, mo):
    mo.md(
        f"""
        # Entstaubung Bandtrockner
        ## Luftströme

        - Abluft Trockner: {haf_pri.str_short()}    
        - Falschluf: {haf_sec.str_short()}
        - Mischung: {haf_mix.str_short()}
        """
    )
    return


@app.cell
def __(inputs):
    inputs
    return


@app.cell
def __(inputs, psf):
    has_pri = psf.HumidAirState.from_t_dry_bulb_rel_hum(
        inputs.value["has_pri_t_dry"], inputs.value["has_pri_rel_hum"] / 100
    )
    haf_pri = psf.HumidAirFlow(inputs.value["haf_pri_q"] / 3600, has_pri)

    has0 = psf.HumidAirState.from_t_dry_bulb_rel_hum(
        inputs.value["has_0_t_dry"], inputs.value["has_0_rel_hum"] / 100
    )
    has0_heated = has0.at_t_dry_bulb(inputs.value["falschluft_t_dry"])
    haf_sec = psf.HumidAirFlow(
        inputs.value["haf_pri_q"]/3600 * inputs.value["percent_falschluft"] / 100, has0_heated
    )


    haf_mix = psf.mix_humid_air_flows([haf_pri, haf_sec])
    return haf_mix, haf_pri, haf_sec, has0, has0_heated, has_pri


@app.cell
def __(mo):
    markdown = mo.md(
        """
        ### Abluft Trockner
        - Luftmenge [m³/h]: {haf_pri_q}
        - Temperatur [°C]: {has_pri_t_dry}
        - rel Feuchtigkeit [%]: {has_pri_rel_hum}
        ### Umgebung
        - Temperatur [°C]: {has_0_t_dry}
        - rel Feuchtigkeit [%]: {has_0_rel_hum}
        ### Falschluft
        - Anteil Falschluft [%]: {percent_falschluft}
        - Temperatur Falschluft [°C]: {falschluft_t_dry}
        """
    )

    inputs = mo.ui.batch(
        markdown,
        {
            "haf_pri_q": mo.ui.slider(
                100,
                50000,
                value=23000,
                show_value=True,
                step=100,
                full_width=True,
            ),
            "has_pri_t_dry": mo.ui.slider(
                0, 100, value=35, show_value=True, full_width=True
            ),
            "has_pri_rel_hum": mo.ui.slider(
                0, 100, value=85, show_value=True, full_width=True
            ),
            "has_0_t_dry": mo.ui.slider(
                -20, 60, value=35, show_value=True, full_width=True
            ),
            "has_0_rel_hum": mo.ui.slider(
                0, 100, value=85, show_value=True, full_width=True
            ),
            "percent_falschluft": mo.ui.slider(
                0, 200, value=20, show_value=True, full_width=True
            ),
            "falschluft_t_dry": mo.ui.slider(
                -20, 100, value=60, show_value=True, full_width=True
            ),
        },
    )
    return inputs, markdown


@app.cell
def __():
    import marimo as mo
    import psychroflow as psf
    return mo, psf


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
