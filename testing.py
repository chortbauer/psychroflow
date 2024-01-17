import pprint

import numpy as np
from psychroflow import *


PrettyPrinter = pprint.PrettyPrinter(underscore_numbers=True)
pp = PrettyPrinter.pprint

# t_range = np.linspace(1,100,20)
# for t in t_range:
#     print(t , psf.get_density_water(t))


has1 = HumidAirState.from_hum_ratio_enthalpy(0.034, 143000)
haf1 = HumidAirFlow(24000 / 3600, has1)
# pp(haf1)

has2 = HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=10, rel_hum=0.1)
haf2 = HumidAirFlow(6000 / 3600, has2)
# pp(haf2)

has3 = HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=15, rel_hum=0.1)
haf3 = HumidAirFlow(6000 / 3600, has2)
# pp(haf2)

print("haf1: " + haf1.str_short())

print("mix: " + mix_humid_air_flows([haf1, haf2, haf3]).str_short())

