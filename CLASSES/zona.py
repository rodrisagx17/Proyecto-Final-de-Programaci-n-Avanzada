"""_summary_"""

from datetime import time
from datetime import date
from clase import Clase


class Zona:
    # Constructor
    def __init__(
        self,
        id_zona: int,
        nombre: str,
        categoria: str,
        condicion: str,
        hora_apertura: time,
        hora_cierre: time,
        fecha: date,
    ):
        # Atributos
        self.idzona = id_zona
        self.nombre = nombre
        self.categoria = categoria
        self.condicion = condicion
        self.hora_apertura = hora_apertura
        self.hora_cierre = hora_cierre
        self.fecha = fecha
