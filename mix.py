# -*- coding: utf-8 -*-
"""
create reports for mixing air streams
Created on 2024-01-23 12:52:16
@author: orc
"""
import pprint

import psychrostate as pss
import psychroflow as psf

PrettyPrinter = pprint.PrettyPrinter(underscore_numbers=True)
pp = PrettyPrinter.pprint

p = pss.get_pressure_from_height(300)

hafs = []

has = psf.HumidAirState.from_t_dry_bulb_hum_ratio(
    t_dry_bulb=110, hum_ratio=0.07, pressure=p
)
hafs.append(psf.HumidAirFlow(20000 / 3600, has))
pp(has)

# has = psf.HumidAirState.from_t_dry_bulb_hum_ratio(t_dry_bulb=55, hum_ratio=0.01, pressure=p)
has = psf.HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=15, rel_hum=0.8, pressure=p)
hafs.append(psf.HumidAirFlow(25000 / 3600, has))
pp(has)


mix = psf.mix_humid_air_flows(hafs)
pp(mix.humid_air_state)
print(mix.str_short())


from create_reports import create_report_mix_humid_air_flows

create_report_mix_humid_air_flows(
    humid_air_flows=hafs,
    projekt_name="",
    projekt_number="",
    author="orc",
    file_name="output/report_mix_air_streams",
    save_html=False,
)
