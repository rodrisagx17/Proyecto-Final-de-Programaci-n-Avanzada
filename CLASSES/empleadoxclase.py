"""_summary_"""

from datetime import date


class EmpleadoxClase:
    # Constructor
    def __init__(
        self,
        cod_empl_em: int,
        ids: int,
        idz: int,
        idc: int,
        fecha_asig: date,
        tarifaxclase: float,
    ):
        # Atributos
        self.cod_empl_em = cod_empl_em
        self.ids = ids
        self.idz = idz
        self.idc = idc
        self.fecha_asig = fecha_asig
        self.tarifaxclase = tarifaxclase
