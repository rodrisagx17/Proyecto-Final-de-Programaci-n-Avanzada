"""_summary_"""

from datetime import time
from datetime import date
from usuarioxclase import UsuarioxClase
from empleadoxclase import EmpleadoxClase


class Clase:
    # Constructor
    def __init__(
        self,
        id_clase: int,
        nombre: str,
        descripcion: str,
        num_partic: int,
        fecha: date,
        hora_inicio: time,
        hora_fin: time,
    ):
        # Atributos
        self.idclase = id_clase
        self.nombre = nombre
        self.descripcion = descripcion
        self.num_partic = num_partic
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
