# -*- coding: utf-8 -*-
"""
create reports for mixing air streams
Created on 2024-01-23 12:52:16
@author: orc
"""

import psychrostate as pss
import psychroflow as psf
from create_reports import combine_humid_air_flows

p = pss.get_pressure_from_height(300)

hafs = []

has = psf.HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=44, rel_hum=0.5, pressure=p)
hafs.append(psf.HumidAirFlow(24000 / 3600, has))

has = psf.HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=10, rel_hum=0.2, pressure=p)
hafs.append(psf.HumidAirFlow(6000 / 3600, has))

has = psf.HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=12, rel_hum=0.3, pressure=p)
hafs.append(psf.HumidAirFlow(6000 / 3600, has))


combine_humid_air_flows(
    humid_air_flows=hafs,
    projekt_name="",
    projekt_number="",
    author="orc",
    file_name="output/report_mix_air_streams",
    save_html=False
)
