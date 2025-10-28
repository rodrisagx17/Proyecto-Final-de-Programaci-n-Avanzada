"""_summary_"""

from datetime import date


class Membresia:
    # Constructor
    def __init__(
        self,
        cod_memb: int,
        nombre: str,
        descripcion: str,
        precio: float,
        fecha_ini: date,
        fecha_venc: date,
        estado_plan: str,
    ):
        # Atributos
        self.codmemb = cod_memb
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.fecha_ini = fecha_ini
        self.fecha_venc = fecha_venc
        self.estado_plan = estado_plan
