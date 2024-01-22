import psychroflow as psf
from create_reports import combine_humid_air_flows


hafs = []

has = psf.HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=44, rel_hum=0.5)
hafs.append(psf.HumidAirFlow(24000 / 3600, has))

has = psf.HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=10, rel_hum=0.2)
hafs.append(psf.HumidAirFlow(6000 / 3600, has))

has = psf.HumidAirState.from_t_dry_bulb_rel_hum(t_dry_bulb=12, rel_hum=0.3)
hafs.append(psf.HumidAirFlow(6000 / 3600, has))


combine_humid_air_flows(hafs)
