import pprint

import numpy as np
import psychroflow as psf


PrettyPrinter = pprint.PrettyPrinter(underscore_numbers=True)
pp = PrettyPrinter.pprint

t_range = np.linspace(1,100,20)
for t in t_range:
    print(t , psf.get_density_water(t))




has1 = psf.HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=60, rel_hum=0.8)
haf1 = psf.HumidAirFlow(24000 / 3600, has1)
pp(haf1)

has2 = psf.umidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=20, rel_hum=0.6)
haf2 = psf.HumidAirFlow(6000 / 3600, has2)
pp(haf2)

awf = psf.AirWaterFlow.from_mixing_two_humid_air_flows(haf1, haf2)
pp(awf)