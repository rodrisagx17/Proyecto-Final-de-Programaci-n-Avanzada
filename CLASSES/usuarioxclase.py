"""_summary_"""

from datetime import date


class UsuarioxClase:
    # Constructor
    def __init__(
        self,
        cod_user_us: int,
        ids: int,
        idz: int,
        idc: int,
        estado: str,
        fecha_ins: date,
    ):
        # Atributos
        self.cod_user_us = cod_user_us
        self.ids = ids
        self.idz = idz
        self.idc = idc
        self.estado = estado
        self.fecha_ins = fecha_ins
