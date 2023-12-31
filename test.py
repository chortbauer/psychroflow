import psychroflow as pf

pf.logging.basicConfig(level=pf.logging.DEBUG)

pf.add(1.,2)

pf.HumidAirState(t_dry_bulb=12, rel_hum=34)