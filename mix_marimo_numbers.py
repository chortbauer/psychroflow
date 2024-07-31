import marimo

__generated_with = "0.7.12"
app = marimo.App()


@app.cell
def __(ui_n_hafs):
    ui_n_hafs
    return


@app.cell
def __(ui_hafs):
    ui_hafs
    return


@app.cell
def __(md_output):
    md_output
    return


@app.cell
def __(mo):
    form = (
        mo.md("""
        ### Create Report

        {project_name}

        {project_number}

        {filename}

    """)
        .batch(
            project_name=mo.ui.text(label="Projekt Name", value=""),
            project_number=mo.ui.text(label="Projekt Nummer", value=""),
            filename=mo.ui.text(label="Dateiname"),
            # author=mo.ui.text(label="Author"),
            # date=mo.ui.date(label="Datum"),
        )
        .form(
            clear_on_submit = True,
            show_clear_button=True,
        )
    )
    form
    return form,


@app.cell
def __():
    import marimo as mo
    from pathvalidate import sanitize_filepath

    import psychrostate as pss
    import psychroflow as psf
    from create_reports import create_report_mix_humid_air_flows

    import locale
    locale.setlocale(locale.LC_NUMERIC, 'de-AT.UTF-8')

    pass
    return (
        create_report_mix_humid_air_flows,
        locale,
        mo,
        psf,
        pss,
        sanitize_filepath,
    )


@app.cell
def __(create_report_mix_humid_air_flows, form, hafs, sanitize_filepath):
    if form.value and form.value["filename"] and 1 <= len(hafs):
        create_report_mix_humid_air_flows(
            humid_air_flows=hafs,
            projekt_name=form.value["project_name"],
            projekt_number=form.value["project_number"],
            author="orc",
            file_name=sanitize_filepath(f"output/{form.value["filename"]}"),
            save_html=False,
        )
    return


@app.cell
def __(hafs, locale, mo, psf):
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


    md_hafs = mo.vstack([haf_string_mo_md(haf) for haf in hafs])

    if 0 < len(hafs):
        haf_mix = psf.mix_humid_air_flows(hafs)

    md_mix = (
        mo.vstack([mo.md("## Mischungs Luftstrom"), haf_string_mo_md(haf_mix)])
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
    return haf_mix, haf_string_mo_md, md_hafs, md_mix, md_output


@app.cell
def __(mo):
    # create ui n_hafs
    n_hafs_default = 5
    n_hafs = mo.ui.number(start=1, stop=100, step=1, value=n_hafs_default, label="Anzahl Luftströme").form()

    ui_n_hafs = mo.vstack([mo.md("## Anzahl Luftströme"),n_hafs,mo.md("Warning: Changing this number resets all other values!")])
    return n_hafs, n_hafs_default, ui_n_hafs


@app.cell
def __(mo, n_hafs, n_hafs_default):
    # create ui
    n_hafs_n = n_hafs.value+1 if n_hafs.value else n_hafs_default+1

    checks = [True] * n_hafs_n
    checks[-1] = False

    enabled_ticks = mo.ui.array([mo.ui.checkbox(value=i) for i in checks])

    inputs_volume_flow = mo.ui.array(
        [
            mo.ui.number(
                0,
                200_000,
                value=10000,
                # step=100,
            )
            for i in range(n_hafs_n)
        ],
    )

    inputs_t_dry = mo.ui.array(
        [mo.ui.number(-40, 100, value=20) for _ in range(n_hafs_n)],
    )

    inputs_rel_hum = mo.ui.array(
        [mo.ui.number(0, 100, value=40) for _ in range(n_hafs_n)]
    )

    headings = ["", "Volumenstrom [m³/h]", "Temperatur [°C]", "rel Feuchte [%]"]
    element_width = 10
    widths = [1] + [element_width] * 3
    headings_stack = mo.hstack(
        headings,
        widths=widths,
        align="center",
    )

    ui_sliders = mo.vstack(
        [
            mo.hstack(
                i,
                widths=widths,
                align="center",
            )
            for i in zip(
                enabled_ticks, inputs_volume_flow, inputs_t_dry, inputs_rel_hum
            )
        ]
    )

    ui_hafs = mo.vstack([headings_stack, ui_sliders])
    return (
        checks,
        element_width,
        enabled_ticks,
        headings,
        headings_stack,
        inputs_rel_hum,
        inputs_t_dry,
        inputs_volume_flow,
        n_hafs_n,
        ui_hafs,
        ui_sliders,
        widths,
    )


@app.cell
def __(
    enabled_ticks,
    inputs_rel_hum,
    inputs_t_dry,
    inputs_volume_flow,
    n_hafs_n,
    psf,
):
    # mix air flows

    hafs = []

    for i in range(int(n_hafs_n)):
        if enabled_ticks.value[i]:
            hafs.append(
                psf.HumidAirFlow(
                    inputs_volume_flow.value[i]/3600,
                    psf.HumidAirState.from_t_dry_bulb_rel_hum(
                        t_dry_bulb=inputs_t_dry.value[i],
                        rel_hum=inputs_rel_hum.value[i] / 100,
                    ),
                )
            )
    return hafs, i


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
