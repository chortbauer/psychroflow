import marimo

__generated_with = "0.7.12"
app = marimo.App()


@app.cell
def __(md_output):
    md_output
    return


@app.cell
def __(inputs):
    inputs
    return


@app.cell
def __():
    import marimo as mo

    import psychrostate as pss
    import psychroflow as psf

    import locale
    locale.setlocale(locale.LC_NUMERIC, 'de-AT.UTF-8')

    pass
    return locale, mo, psf, pss


@app.cell
def __(mo):
    # create inputs

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
        - Falschluft aufheizen: {heat_sec_airflow}
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
                -20, 100, value=35, show_value=True, full_width=True
            ),
            "has_pri_rel_hum": mo.ui.slider(
                0, 100, value=85, show_value=True, full_width=True
            ),
            "has_0_t_dry": mo.ui.slider(
                -20, 100, value=35, show_value=True, full_width=True
            ),
            "has_0_rel_hum": mo.ui.slider(
                0, 100, value=85, show_value=True, full_width=True
            ),
            "percent_falschluft": mo.ui.slider(
                0, 200, value=20, show_value=True, full_width=True
            ),
            "heat_sec_airflow": mo.ui.checkbox(True),
            "falschluft_t_dry": mo.ui.slider(
                -20, 100, value=60, show_value=True, full_width=True
            ),
        },
    )
    return inputs, markdown


@app.cell
def __(haf_mix, haf_pri, haf_sec, haf_sec_0, inputs, locale, mo):
    # create output text


    def haf_string_mo_md(haf):
        return mo.md(
            """
            $V = {} \, m^3/h$ &emsp; $T = {} \,°C$ &emsp; $\phi = {} \, \%$ &emsp; $T_d = {} \, °C$
            """.format(
                locale.format_string(
                    "%.0f", haf.volume_flow * 3600, grouping=True
                ),
                locale.format_string(
                    "%.0f", haf.humid_air_state.t_dry_bulb, grouping=True
                ),
                locale.format_string(
                    "%.0f", haf.humid_air_state.rel_hum * 100, grouping=True
                ),
                locale.format_string(
                    "%.0f", haf.humid_air_state.t_dew_point, grouping=True
                ),
            )
        )


    hafs = [haf_pri, haf_sec_0, haf_sec]
    names = ["Abluft Trockner", "Falschluft", "Falschluft geheizt"]

    if not inputs.value["heat_sec_airflow"]:
        hafs.pop()
        names.pop()

    names_hafs = zip(names, hafs)

    md_hafs = mo.vstack(
        [
            mo.hstack(
                [name, haf_string_mo_md(haf)],
            )
            for name, haf in names_hafs
        ]
    )

    md_mix = (
        mo.vstack(
            [
                mo.md("## Mischungs Luftstrom"),
                mo.hstack(["Luftstrom Filter", haf_string_mo_md(haf_mix)]),
            ]
        )
        if 0 < len(hafs)
        else mo.md("")
    )

    md_output = (
        mo.vstack([mo.md("## Eingangs Luftströme"), md_hafs, md_mix])
        if 0 < len(hafs)
        else mo.md(
            """
            ### Keine Eingänge aktiv

            Select Checkbox!
            """
        )
    )
    return (
        haf_string_mo_md,
        hafs,
        md_hafs,
        md_mix,
        md_output,
        names,
        names_hafs,
    )


@app.cell
def __(inputs, psf):

    has_pri = psf.HumidAirState.from_t_dry_bulb_rel_hum(
        inputs.value["has_pri_t_dry"], inputs.value["has_pri_rel_hum"] / 100
    )

    haf_pri = psf.HumidAirFlow(inputs.value["haf_pri_q"] / 3600, has_pri)


    has_0 = psf.HumidAirState.from_t_dry_bulb_rel_hum(
        inputs.value["has_0_t_dry"], inputs.value["has_0_rel_hum"] / 100
    )
    haf_sec_0 = psf.HumidAirFlow(
        inputs.value["haf_pri_q"]
        / 3600
        * inputs.value["percent_falschluft"]
        / 100,
        has_0,
    )

    if inputs.value["heat_sec_airflow"]:
        haf_sec = haf_sec_0.at_t_dry_bulb(inputs.value["falschluft_t_dry"])
    else: haf_sec = haf_sec_0


    haf_mix = psf.mix_humid_air_flows([haf_pri, haf_sec])
    return haf_mix, haf_pri, haf_sec, haf_sec_0, has_0, has_pri


@app.cell
def __():
    # mo.md(
    #     f"""
    #     # Entstaubung Bandtrockner
    #     ## Luftströme

    #     - Abluft Trockner: {haf_pri.str_short()}    
    #     - Falschluf: {haf_sec.str_short()}
    #     - Mischung: {haf_mix.str_short()}
    #     """
    # )
    return


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
