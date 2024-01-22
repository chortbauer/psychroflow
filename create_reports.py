# -*- coding: utf-8 -*-
"""
Created on 2024-01-19 09:56:57
@author: orc
"""

# from pathlib import Path
from datetime import datetime

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

# from weasyprint.text.fonts import FontConfiguration

import psychroflow as psf


def combine_humid_air_flows(
    humid_air_flows,
    projekt_name="",
    projekt_number="",
    author="orc",
    filename="report_mix_air_streams",
    save_html=False,
    save_pdf=True,
):
    """creates a report for the mixing of humid air flows"""
    env = Environment(loader=FileSystemLoader("templates"))

    template = env.get_template("combine_air_streams.html")

    items_air_streams_to_mix = []
    for i, haf in enumerate(humid_air_flows):
        an_item = dict(
            id=i + 1,
            v=f"{haf.volume_flow*3600:,.1f}".replace(",", " ").replace(".", ","),
            t=f"{haf.humid_air_state.t_dry_bulb:.1f}".replace(".", ","),
            rh=f"{haf.humid_air_state.rel_hum*100:.1f}".replace(".", ","),
            ttp=f"{haf.humid_air_state.t_dew_point:.1f}".replace(".", ","),
        )
        items_air_streams_to_mix.append(an_item)

    comb_air_stream = psf.mix_humid_air_flows(humid_air_flows)
    state_mixed = dict(
        id="",
        v=f"{comb_air_stream.volume_flow*3600:,.1f}".replace(",", " ").replace(
            ".", ","
        ),
        t=f"{comb_air_stream.humid_air_state.t_dry_bulb:.1f}".replace(".", ","),
        rh=f"{comb_air_stream.humid_air_state.rel_hum*100:.1f}".replace(".", ","),
        ttp=f"{comb_air_stream.humid_air_state.t_dew_point:.1f}".replace(".", ","),
    )

    # render the template with variables
    html = template.render(
        page_title_text="Mischung feuchte Luft",
        title_text="Mischung feuchte Luft",
        author=author,
        date=datetime.today().strftime("%d.%m.%Y"),
        projekt_name=projekt_name,
        projekt_nr=projekt_number,
        items_mix=items_air_streams_to_mix,
        state_mixed=state_mixed,
        druck=f"{comb_air_stream.humid_air_state.pressure/1000:.3g}".replace(".", ","),
        delta_ttp_t=f"{comb_air_stream.humid_air_state.t_dry_bulb - comb_air_stream.humid_air_state.t_dew_point:.1f}".replace(
            ".", ","
        ),
    )

    # save html to file
    if save_html:
        with open(filename + ".html", "w", encoding="utf-8") as f:
            f.write(html)

    # print html to pdf
    if save_pdf:
        # font_config = FontConfiguration()
        css = CSS(
            string="""@page {size: A4; margin: 2.5cm;}""",
            # font_config=font_config,
        )
        HTML(string=html).write_pdf(filename + ".pdf", stylesheets=[css])
