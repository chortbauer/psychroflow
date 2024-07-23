import marimo

__generated_with = "0.7.9"
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
    import pprint

    import marimo as mo
    from pathvalidate import sanitize_filepath

    import psychrostate as pss
    import psychroflow as psf
    from create_reports import create_report_mix_humid_air_flows

    PrettyPrinter = pprint.PrettyPrinter(underscore_numbers=True)
    pp = PrettyPrinter.pprint
    return (
        PrettyPrinter,
        create_report_mix_humid_air_flows,
        mo,
        pp,
        pprint,
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
def __(hafs, mo, psf):
    # create output text

    md_hafs = mo.md("\n\n".join([haf.str_short() + haf.t_dew for haf in hafs]))

    if 1 <= len(hafs):
        haf_mix = psf.mix_humid_air_flows(hafs)

    md_mix = (
        mo.md("## Output Stream \n\n **" + haf_mix.str_short() + "**")
        if 1 <= len(hafs)
        else mo.md("")
    )

    md_output = (
        mo.vstack([mo.md("## Input Streams"), md_hafs, md_mix])
        if 1 <= len(hafs)
        else mo.md("### No active input streams!")
    )
    return haf_mix, md_hafs, md_mix, md_output


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
    n_hafs_n = n_hafs.value if n_hafs.value else n_hafs_default

    enabled_ticks = mo.ui.array(
        [mo.ui.checkbox(value=False) for _ in range(n_hafs_n)]
    )
    enabled_ticks_stack = mo.vstack(enabled_ticks)

    sliders_volume_flow = mo.ui.array(
        [
            mo.ui.slider(
                0,
                200_000,
                value=10000,
                step=100,
                show_value=True,
            )
            for i in range(n_hafs_n)
        ],
    )
    sliders_volume_flow_stack = mo.vstack(sliders_volume_flow)

    sliders_t_dry = mo.ui.array(
        [
            mo.ui.slider(-40, 100, value=20, show_value=True)
            for _ in range(n_hafs_n)
        ],
    )
    sliders_t_dry_stack = mo.vstack(sliders_t_dry)

    sliders_rel_hum = mo.ui.array(
        [mo.ui.slider(0, 100, value=40, show_value=True) for _ in range(n_hafs_n)]
    )
    sliders_rel_hum_stack = mo.vstack(sliders_rel_hum)

    sliders_stack = mo.hstack(
        [
            enabled_ticks_stack,
            sliders_volume_flow_stack,
            sliders_t_dry_stack,
            sliders_rel_hum_stack,
        ],
        align="center",
        justify="space-around",
    )

    headings_stack = mo.hstack(
        ["", "Volumenstrom [m³/h]", "Temperatur [°C]", "rel Feuchte [%]"],
        align="center",
        justify="space-around",
    )

    ui_hafs = mo.vstack(
        [
            headings_stack,
            sliders_stack,
        ]
    )
    return (
        enabled_ticks,
        enabled_ticks_stack,
        headings_stack,
        n_hafs_n,
        sliders_rel_hum,
        sliders_rel_hum_stack,
        sliders_stack,
        sliders_t_dry,
        sliders_t_dry_stack,
        sliders_volume_flow,
        sliders_volume_flow_stack,
        ui_hafs,
    )


@app.cell
def __(
    enabled_ticks,
    n_hafs_n,
    psf,
    sliders_rel_hum,
    sliders_t_dry,
    sliders_volume_flow,
):
    # mix air flows

    hafs = []

    for i in range(int(n_hafs_n)):
        if enabled_ticks.value[i]:
            hafs.append(
                psf.HumidAirFlow(
                    sliders_volume_flow.value[i]/3600,
                    psf.HumidAirState.from_t_dry_bulb_rel_hum(
                        t_dry_bulb=sliders_t_dry.value[i],
                        rel_hum=sliders_rel_hum.value[i] / 100,
                    ),
                )
            )
    return hafs, i


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
