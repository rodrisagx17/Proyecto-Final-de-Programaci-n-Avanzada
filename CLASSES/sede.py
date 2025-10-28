"""_summary_"""

from datetime import time
from zona import Zona


class Sede:
    # Constructor
    def __init__(
        self,
        id_sede: int,
        nombre: str,
        hora_abre: time,
        hora_cierra: time,
        calle: str,
        numero: str,
        ciudad: str,
        estado_p: str,
        cp: str,
    ):
        # Atributos
        self.idsede = id_sede
        self.nombre = nombre
        self.hora_abre = hora_abre
        self.hora_cierra = hora_cierra
        self.calle = calle
        self.numero = numero
        self.ciudad = ciudad
        self.estado_p = estado_p
        self.cp = cp
