# -*- coding: utf-8 -*-
"""
create reports for mixing air streams
Created on 2024-01-23 12:52:16
@author: orc
"""

import psychrostate as pss
import psychroflow as psf

p = pss.get_pressure_from_height(300)

hafs = []

has = psf.HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=42.17, rel_hum=0.1, pressure=p)
hafs.append(psf.HumidAirFlow(12900 / 3600, has))

has = psf.HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=-20, rel_hum=0.2, pressure=p)
hafs.append(psf.HumidAirFlow((17100) / 3600, has))

# has = psf.HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=-10, rel_hum=0.0, pressure=p)
# hafs.append(psf.HumidAirFlow(10000 / 3600, has))

# has = psf.HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=20, rel_hum=0.0, pressure=p)
# hafs.append(psf.HumidAirFlow(4000 / 3600, has))


mix = psf.mix_humid_air_flows(hafs)
print(mix.str_short())


from create_reports import create_report_mix_humid_air_flows
create_report_mix_humid_air_flows(
    humid_air_flows=hafs,
    projekt_name="IFK Komm. Fixkraft",
    projekt_number="",
    author="orc",
    file_name="output/report_mix_air_streams",
    save_html=False
)
