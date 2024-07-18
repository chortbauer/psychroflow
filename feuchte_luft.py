# -*- coding: utf-8 -*-
"""
Created on 2023-10-13 09:46:02
@author: orc
"""

import math
import warnings
from cmath import isclose
from datetime import datetime

from jinja2 import Environment, FileSystemLoader
from scipy import optimize
from weasyprint import CSS, HTML

# constants
R_L = 287.05  # [J/kgK]
R_W = 461.52  # [J/kgK]
WAERMEKAPAZITAET_LUFT = 1004.6  # [J/kgK]
WAERMEKAPAZITAET_WASSER_DAMPF = 1863.0  # [J/kgK]
WAERMEKAPAZITAET_WASSER_FL = 4191.0  # [J/kgK]
VERDAMPFUNGS_ENTHALPIE = 2500900.0  # [J/kg]
DICHTE_WASSER_FL = 997.0  # [kg/m3]

TRIPLE_POINT_TEMPERATUR_C = 0.01  # [°C]
TRIPLE_POINT_PRESSURE = 611.657  # [Pa]

STANDARD_DRUCK = 101300.0  # [Pa]
C2K = 273.15  # [K]


class humid_air_state:
    """describes the state of a air water(vapour) mix"""
    def __init__(
        self,
        temperatur_C=None,
        rel_feuchte=None,
        wasserbeladung=None,
        spez_enthalpie=None,
        druck=STANDARD_DRUCK,
    ) -> None:
        self.druck = druck

        if (
            (temperatur_C is not None)
            and (rel_feuchte is not None)
            and (wasserbeladung is None)
            and (spez_enthalpie is None)
        ):
            if not (-100 <= temperatur_C <= 100):
                raise AttributeError("-100 <= temperatur_C <= 100")
            self.temperatur_C = temperatur_C
            self.temperatur_K = temperatur_C + C2K
            self.rel_feuchte = rel_feuchte
            self.partial_druck_sat = self.get_partial_druck_sat()
            self.wasserbeladung_sat = self.get_wasserbeladung_sat()
            self.taupunkt = self.get_taupunkt()
            self.wasserbeladung = self.get_wasserbeladung_from_rel_feuchte()
            (
                self.wasserbeladung_g,
                self.wasserbeladung_fl,
            ) = self.get_wasserbeladungen_g_fl()
            self.dichte_g = self.get_dichte_g()
            self.dichte = self.get_dichte()
            self.spez_enthalpie = self.get_spez_enthalpie()
        elif (
            (temperatur_C is None)
            and (rel_feuchte is None)
            and (wasserbeladung is not None)
            and (spez_enthalpie is not None)
        ):
            self.wasserbeladung = wasserbeladung
            self.spez_enthalpie = spez_enthalpie
            self.temperatur_C = self.get_temp_from_enthalpie()
            self.temperatur_K = self.temperatur_C + C2K  # type: ignore
            self.partial_druck_sat = self.get_partial_druck_sat()
            self.wasserbeladung_sat = self.get_wasserbeladung_sat()
            (
                self.wasserbeladung_g,
                self.wasserbeladung_fl,
            ) = self.get_wasserbeladungen_g_fl()
            self.rel_feuchte = self.get_rel_feuchte_from_wasserbeladung()
            self.taupunkt = self.get_taupunkt()
            self.dichte_g = self.get_dichte_g()
            self.dichte = self.get_dichte()
        elif (
            (temperatur_C is not None)
            and (rel_feuchte is None)
            and (wasserbeladung is not None)
            and (spez_enthalpie is None)
        ):
            if not (-100 <= temperatur_C <= 100):
                raise AttributeError("-100 <= temperatur_C <= 100")
            self.temperatur_C = temperatur_C
            self.temperatur_K = temperatur_C + C2K
            self.wasserbeladung = wasserbeladung
            self.partial_druck_sat = self.get_partial_druck_sat()
            self.wasserbeladung_sat = self.get_wasserbeladung_sat()
            (
                self.wasserbeladung_g,
                self.wasserbeladung_fl,
            ) = self.get_wasserbeladungen_g_fl()
            self.rel_feuchte = self.get_rel_feuchte_from_wasserbeladung()
            self.taupunkt = self.get_taupunkt()
            self.dichte_g = self.get_dichte_g()
            self.dichte = self.get_dichte()
            self.spez_enthalpie = self.get_spez_enthalpie()
        else:
            raise AttributeError(
                "either Temp and rel_feuchte or wasserbeladung und spez_enthalpie or wasserbeladung and temperatur"
            )

    def __str__(self) -> str:
        printworthy_attributes = [
            f"Temperatur = {self.temperatur_C:.5g} °C",
            f"rel_Luftfeuchtigkeit = {self.rel_feuchte*100:.5g} %",
            f"Taupunkt = {self.taupunkt:.5g} °C",
            f"Druck = {self.druck:.5g} Pa",
            f"Dichte = {self.dichte:.5g} kg/m3",
            f"Wasserbeladung gesamt = {self.wasserbeladung:.5g}",
        ]

        if self.wasserbeladung > self.wasserbeladung_sat:
            printworthy_attributes.append(
                f"Wasserbeladung gasförmig = {self.wasserbeladung_sat:.5g}"
            )
            printworthy_attributes.append(
                f"Wasserbeladung flüssig = {self.wasserbeladung - self.wasserbeladung_sat:.5g}"
            )

        printworthy_attributes.append(
            f"spezifische Enthalpie = {self.spez_enthalpie:.5g} J/kg"
        )

        return "\n".join(printworthy_attributes)

    def get_partial_druck_sat(self) -> float:
        # source: https://doi.org/10.1175/JAMC-D-17-0334.1
        return (
            math.exp(34.494 - 4924.99 / (self.temperatur_C + 237.1))  # type: ignore
            / (self.temperatur_C + 105) ** 1.57  # type: ignore
        )

    def get_rel_feuchte_from_wasserbeladung(self) -> float:
        if self.wasserbeladung < self.wasserbeladung_sat:
            return (
                self.wasserbeladung
                / (R_L / R_W + self.wasserbeladung)
                * self.druck
                / self.partial_druck_sat
            )
        else:
            return 1.0

    def get_taupunkt(self) -> float:
        if isclose(self.partial_druck_sat, 0.0):
            return -(
                math.exp(34.494 - 4924.99 / (self.temperatur_C + 237.1))  # type: ignore
                / (self.temperatur_C + 105) ** 1.57  # type: ignore
            )
        else:

            def fun(temperatur):
                return (self.partial_druck_sat * self.rel_feuchte) - (
                    math.exp(34.494 - 4924.99 / (temperatur + 237.1))
                    / (temperatur + 105) ** 1.57
                )

            sol = optimize.root(fun, x0=20, method="hybr")

            return sol.x[0]

    def get_wasserbeladung_from_rel_feuchte(self) -> float:
        if math.isclose(self.rel_feuchte, 0):
            return 0
        else:
            return (
                0.62197
                * self.partial_druck_sat
                / (self.druck / self.rel_feuchte - self.partial_druck_sat)
            )

    def get_wasserbeladung_sat(self) -> float:
        return (
            R_L / R_W * self.partial_druck_sat / (self.druck - self.partial_druck_sat)
        )

    def get_wasserbeladungen_g_fl(self):
        if self.wasserbeladung <= self.wasserbeladung_sat:
            return [self.wasserbeladung, 0.0]
        else:
            return [
                self.wasserbeladung_sat,
                self.wasserbeladung - self.wasserbeladung_sat,
            ]

    def get_dichte_g(self) -> float:
        return 1 / (
            R_L * self.temperatur_K / self.druck * (1 + self.wasserbeladung / 0.62197)
        )

    def get_dichte(self) -> float:
        if self.wasserbeladung <= self.wasserbeladung_sat:
            return self.dichte_g
        else:
            return (1 + self.wasserbeladung) / (
                (1 + self.wasserbeladung_sat) / self.dichte_g
                + (self.wasserbeladung - self.wasserbeladung_sat) / DICHTE_WASSER_FL
            )

    def get_spez_enthalpie(self) -> float:
        temperatur_over_triple = self.temperatur_C - TRIPLE_POINT_TEMPERATUR_C  # type: ignore

        if self.wasserbeladung <= self.wasserbeladung_sat:
            return (
                WAERMEKAPAZITAET_LUFT * temperatur_over_triple
                + self.wasserbeladung
                * (
                    VERDAMPFUNGS_ENTHALPIE
                    + WAERMEKAPAZITAET_WASSER_DAMPF * temperatur_over_triple
                )
            )
        else:
            return (
                WAERMEKAPAZITAET_LUFT * temperatur_over_triple
                + self.wasserbeladung_sat
                * (
                    VERDAMPFUNGS_ENTHALPIE
                    + WAERMEKAPAZITAET_WASSER_DAMPF * temperatur_over_triple
                )
                + (self.wasserbeladung - self.wasserbeladung_sat)
                * WAERMEKAPAZITAET_WASSER_FL
                * temperatur_over_triple
            )

    def get_temp_from_enthalpie(self) -> None:
        def fun(temperatur_C):
            def get_wasserbeladung_sat(self, temperatur_C) -> float:
                partial_druck_sat = (
                    math.exp(34.494 - 4924.99 / (temperatur_C + 237.1))
                    / (temperatur_C + 105) ** 1.57
                )
                return R_L / R_W * partial_druck_sat / (self.druck - partial_druck_sat)

            wasserbeladung_sat = get_wasserbeladung_sat(self, temperatur_C)
            temperatur_over_triple = temperatur_C - TRIPLE_POINT_TEMPERATUR_C

            if self.wasserbeladung <= wasserbeladung_sat:
                return self.spez_enthalpie - (
                    WAERMEKAPAZITAET_LUFT * temperatur_over_triple
                    + self.wasserbeladung
                    * (
                        VERDAMPFUNGS_ENTHALPIE
                        + WAERMEKAPAZITAET_WASSER_DAMPF * temperatur_over_triple
                    )
                )
            else:
                return self.spez_enthalpie - (
                    WAERMEKAPAZITAET_LUFT * temperatur_over_triple
                    + wasserbeladung_sat
                    * (
                        VERDAMPFUNGS_ENTHALPIE
                        + WAERMEKAPAZITAET_WASSER_DAMPF * temperatur_over_triple
                    )
                    + (self.wasserbeladung - wasserbeladung_sat)
                    * WAERMEKAPAZITAET_WASSER_FL
                    * temperatur_over_triple
                )

        sol = optimize.root(fun, x0=50, method="hybr")
        # sol = optimize.minimize_scalar(fun, bounds=[-100,100], method="Bounded")

        if -100 <= sol.x[0] <= 100:
            return sol.x[0]
        else:
            raise AttributeError("-100<= Temperature <=100")

        # return sol.x[0]

    def ohne_fluessigkeit(self):
        return humid_air_state(
            temperatur_C=self.temperatur_C, rel_feuchte=self.rel_feuchte
        )


class steam_stream:
    def __init__(self, temperatur_C, massenstrom) -> None:
        self.temperatur_C = temperatur_C
        self.temperatur_K = temperatur_C + C2K
        self.massenstrom = massenstrom
        self.enthalpie_strom = (  # TODO druck berücksichtigen
            WAERMEKAPAZITAET_WASSER_FL
            * self.massenstrom
            * (100 - TRIPLE_POINT_TEMPERATUR_C)
            + VERDAMPFUNGS_ENTHALPIE * massenstrom
            + WAERMEKAPAZITAET_WASSER_DAMPF
            * self.massenstrom
            * (self.temperatur_C - 100)
        )


class water_stream:
    def __init__(self, temperatur_C, massenstrom=None, volumenstrom=None) -> None:
        self.temperatur_C = temperatur_C
        self.temperatur_K = temperatur_C + C2K
        if (massenstrom is None) and (volumenstrom is not None):
            self.volumenstrom = volumenstrom
            self.massenstrom = volumenstrom * DICHTE_WASSER_FL
        elif (massenstrom is not None) and (volumenstrom is None):
            self.massenstrom = massenstrom
            self.volumenstrom = massenstrom / DICHTE_WASSER_FL
        else:
            raise AttributeError("either volumenstrom or massenstrom")
        self.enthalpie_strom = (
            WAERMEKAPAZITAET_WASSER_FL
            * self.massenstrom
            * (temperatur_C - TRIPLE_POINT_TEMPERATUR_C)
        )

    def __str__(self) -> str:
        return "\n".join(
            [
                f"Temperatur = {self.temperatur_C:.5g} °C",
                f"Volumenstrom = {self.volumenstrom*3600*1000:.5g} l/h",
                f"Volumenstrom = {self.volumenstrom:.5g} m3/s",
                f"Massenstrom = {self.massenstrom:.5g} kg/s",
                f"Enthalpiestrom = {self.enthalpie_strom:.5g} J/s",
            ]
        )

    def with_massenstrom(self, massenstrom: float):
        return water_stream(temperatur_C=self.temperatur_C, massenstrom=massenstrom)


class humid_air_stream:
    def __init__(
        self, humid_air_state: humid_air_state, volumenstrom=None, massenstrom=None
    ) -> None:
        self.humid_air_state = humid_air_state
        if (volumenstrom is not None) and (massenstrom is None):
            self.volumenstrom = volumenstrom
            self.massenstrom = self.volumenstrom * self.humid_air_state.dichte
        elif (volumenstrom is None) and (massenstrom is not None):
            self.massenstrom = massenstrom
            self.volumenstrom = self.massenstrom / self.humid_air_state.dichte
        else:
            raise AttributeError("either massenstrom oder volumenstrom required")
        self.massenstrom_luft = self.massenstrom / (
            1 + self.humid_air_state.wasserbeladung
        )
        self.massenstrom_wasser = (
            self.massenstrom_luft * self.humid_air_state.wasserbeladung
        )
        self.massenstrom_wasser_g = (
            self.massenstrom_luft * self.humid_air_state.wasserbeladung_g
        )
        self.massenstrom_wasser_fl = (
            self.massenstrom_luft * self.humid_air_state.wasserbeladung_fl
        )
        self.enthalpie_strom = (
            self.massenstrom_luft * self.humid_air_state.spez_enthalpie
        )

    def __str__(self) -> str:
        return (
            "\n".join(
                [
                    f"Volumenstrom = {self.volumenstrom*3600:.5g} m3/h",
                    f"Volumenstrom = {self.volumenstrom:.5g} m3/s",
                    f"Massenstrom = {self.massenstrom:.5g} kg/s",
                    f"Massenstrom Luft = {self.massenstrom_luft:.5g} kg/s",
                    f"Massenstrom Wasser = {self.massenstrom_wasser:.5g} kg/s",
                    f"Enthalpiestrom = {self.enthalpie_strom:.5g} J/s",
                ]
            )
            + "\n"
            + self.humid_air_state.__str__()
        )

    def str_short(self) -> str:
        return f"V = {self.volumenstrom*3600:6.0f} m3/h; T = {self.humid_air_state.temperatur_C:4.1f} °C; rel_F = {self.humid_air_state.rel_feuchte*100:3.0f} %"

    def split_into_gas_and_fluessig(self):
        gas = humid_air_stream(
            self.humid_air_state.ohne_fluessigkeit(),
            massenstrom=(self.massenstrom - self.massenstrom_wasser_fl),
        )
        fluessigkeit = water_stream(
            self.humid_air_state.temperatur_C, massenstrom=self.massenstrom_wasser_fl
        )
        return [gas, fluessigkeit]

    def with_added_enthalpie(self, enthalpie_change: float):
        spez_enthalpie_change = enthalpie_change / self.massenstrom_luft
        return humid_air_stream(
            humid_air_state(
                wasserbeladung=self.humid_air_state.wasserbeladung,
                spez_enthalpie=(
                    self.humid_air_state.spez_enthalpie + spez_enthalpie_change
                ),
            ),
            massenstrom=self.massenstrom,
        )

    def with_temperatur_C(self, temperatur_C):
        return humid_air_stream(
            humid_air_state(
                temperatur_C=temperatur_C,
                wasserbeladung=self.humid_air_state.wasserbeladung,
            ),
            massenstrom=self.massenstrom,
        )


def combine_two_humid_air_streams(
    stream1: humid_air_stream, stream2: humid_air_stream
) -> humid_air_stream:
    if not math.isclose(stream1.humid_air_state.druck, stream2.humid_air_state.druck):
        raise AttributeError(
            "pressures not equal"
            + "\n"
            + f"p1 = {stream1.humid_air_state.druck} Pa"
            + "\n"
            + f"p2 = {stream2.humid_air_state.druck} Pa"
        )

    massenstrom_luft = stream1.massenstrom_luft + stream2.massenstrom_luft
    massenstrom_wasser = stream1.massenstrom_wasser + stream2.massenstrom_wasser
    massenstrom = massenstrom_luft + massenstrom_wasser

    wasserbeladung = massenstrom_wasser / massenstrom_luft

    enthalpie_strom = stream1.enthalpie_strom + stream2.enthalpie_strom
    spez_enthalpie = enthalpie_strom / massenstrom_luft

    combined_state = humid_air_state(
        wasserbeladung=wasserbeladung,
        spez_enthalpie=spez_enthalpie,
        druck=stream1.humid_air_state.druck,
    )
    return humid_air_stream(humid_air_state=combined_state, massenstrom=massenstrom)


def combine_air_streams(list_of_air_streams):
    if not all(
        math.isclose(
            stream.humid_air_state.druck, list_of_air_streams[0].humid_air_state.druck
        )
        for stream in list_of_air_streams
    ):
        raise AttributeError("pressures not equal")

    combined_stream = list_of_air_streams[0]
    for stream in list_of_air_streams[1:]:
        combined_stream = combine_two_humid_air_streams(combined_stream, stream)

    return combined_stream


def add_enthalpie_to_air_stream(
    stream: humid_air_stream, enthalpie_change: float
) -> humid_air_stream:
    spez_enthalpie_change = enthalpie_change / stream.massenstrom_luft
    return humid_air_stream(
        humid_air_state(
            wasserbeladung=stream.humid_air_state.wasserbeladung,
            spez_enthalpie=(
                stream.humid_air_state.spez_enthalpie + spez_enthalpie_change
            ),
        ),
        massenstrom=stream.massenstrom,
    )


def how_much_enthalpie_to_temp(stream: humid_air_stream, temperatur_C: float) -> float:
    def fun(enthalpie_strom):
        return (
            temperatur_C
            - add_enthalpie_to_air_stream(
                stream, enthalpie_strom
            ).humid_air_state.temperatur_C
        )  # type: ignore

    sol = optimize.root(fun, x0=-1.0, method="hybr")

    return sol.x[0]


def add_water_to_air_stream(
    air_stream: humid_air_stream, water_stream: water_stream
) -> humid_air_stream:
    massenstrom_luft = air_stream.massenstrom_luft
    massenstrom_wasser = air_stream.massenstrom_wasser + water_stream.massenstrom
    massenstrom = massenstrom_luft + massenstrom_wasser

    wasserbeladung = massenstrom_wasser / massenstrom_luft

    enthalpie_strom = air_stream.enthalpie_strom + water_stream.enthalpie_strom
    spez_enthalpie = enthalpie_strom / massenstrom_luft

    combined_state = humid_air_state(
        wasserbeladung=wasserbeladung,
        spez_enthalpie=spez_enthalpie,
        druck=air_stream.humid_air_state.druck,
    )
    return humid_air_stream(humid_air_state=combined_state, massenstrom=massenstrom)


def druck_meereshoehe(meereshoehe: float) -> float:
    return STANDARD_DRUCK * math.exp(-meereshoehe / 8435)


def how_much_water_into_air_till_rel_feuchte(
    air: humid_air_stream,
    water_temperatur_C: float,
    rel_feuchte: float = 0.9,
) -> water_stream:
    if air.humid_air_state.rel_feuchte > rel_feuchte:
        raise AttributeError(
            "rel_feuchte goal must be lower than rel_feuchte air_stream"
        )

    def fun(variable):
        water_stream_scaled = water_stream(
            temperatur_C=water_temperatur_C, massenstrom=variable
        )
        return (
            rel_feuchte
            - add_water_to_air_stream(
                air_stream=air, water_stream=water_stream_scaled
            ).humid_air_state.rel_feuchte
        )

    sol = optimize.brentq(fun, a=0, b=1e15)

    return water_stream(temperatur_C=water_temperatur_C, massenstrom=sol)


def rotationswaermetauscher(
    air_stream_1_1: humid_air_stream,
    air_stream_2_1: humid_air_stream,
    rueckwaermegrad: 0.65,
) -> list[humid_air_stream, humid_air_stream]:
    if not isclose(air_stream_1_1.massenstrom, air_stream_2_1.massenstrom, rel_tol=0.1):
        raise AttributeError("Massenströme nicht gleich")

    temperatur_air_stream_1_1 = air_stream_1_1.humid_air_state.temperatur_C
    temperatur_air_stream_2_1 = air_stream_2_1.humid_air_state.temperatur_C

    temperatur_air_stream_1_2 = temperatur_air_stream_1_1 + rueckwaermegrad * (
        temperatur_air_stream_2_1 - temperatur_air_stream_1_1
    )

    enth_21 = how_much_enthalpie_to_temp(air_stream_1_1, temperatur_air_stream_1_2)
    air_stream_1_2 = add_enthalpie_to_air_stream(air_stream_1_1, enth_21)
    air_stream_2_2 = add_enthalpie_to_air_stream(air_stream_2_1, -enth_21)

    if isclose(air_stream_1_2.humid_air_state.rel_feuchte, 1.0):
        warnings.warn(
            f"air_stream_1_2 rel Feuchte = {air_stream_1_2.humid_air_state.rel_feuchte*100:.1f} %"
        )

    if isclose(air_stream_2_2.humid_air_state.rel_feuchte, 1.0):
        warnings.warn(
            f"air_stream_2_2 rel Feuchte = {air_stream_2_2.humid_air_state.rel_feuchte*100:.1f} %"
        )

    return [air_stream_1_2, air_stream_2_2]


def create_report_combine_air_streams(
    list_of_air_streams,
    projekt_name="",
    projekt_number="",
    author="orc",
    filename="Mischung_feuchte_Luft",
    save_html=False,
    save_pdf=True,
):
    env = Environment(loader=FileSystemLoader("templates"))

    template = env.get_template("template.html")

    items_air_streams_to_mix = []
    for i, air_stream in enumerate(list_of_air_streams):
        an_item = dict(
            id=i + 1,
            v=f"{air_stream.volumenstrom*3600:,.1f}".replace(",", " ").replace(
                ".", ","
            ),
            t=f"{air_stream.humid_air_state.temperatur_C:.1f}".replace(".", ","),
            rh=f"{air_stream.humid_air_state.rel_feuchte*100:.1f}".replace(".", ","),
            ttp=f"{air_stream.humid_air_state.taupunkt:.1f}".replace(".", ","),
        )
        items_air_streams_to_mix.append(an_item)

    comb_air_stream = combine_air_streams(list_of_air_streams)
    state_mixed = dict(
        id="",
        v=f"{comb_air_stream.volumenstrom*3600:,.1f}".replace(",", " ").replace(
            ".", ","
        ),
        t=f"{comb_air_stream.humid_air_state.temperatur_C:.1f}".replace(".", ","),
        rh=f"{comb_air_stream.humid_air_state.rel_feuchte*100:.1f}".replace(".", ","),
        ttp=f"{comb_air_stream.humid_air_state.taupunkt:.1f}".replace(".", ","),
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
        druck=f"{comb_air_stream.humid_air_state.druck/1000:.3g}".replace(".", ","),
        delta_ttp_t=f"{comb_air_stream.humid_air_state.temperatur_C - comb_air_stream.humid_air_state.taupunkt:.1f}".replace(
            ".", ","
        ),
    )

    # save html to file
    if save_html:
        with open(filename + ".html", "w", encoding="utf-8") as f:
            f.write(html)

    # print html to pdf
    if save_pdf:
        css = CSS(
            string="""
            @page {size: A4; margin: 2.5cm;}
            """
        )
        HTML(string=html).write_pdf(filename + ".pdf", stylesheets=[css])
