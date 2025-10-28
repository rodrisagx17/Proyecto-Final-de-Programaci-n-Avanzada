"""_summary_"""

from datetime import time
from datetime import date
from membresia import Membresia
from usuarioxclase import UsuarioxClase
from persona import Persona


class Usuario:
    # Constructor
    def __init__(
        self,
        cod_user: int,
        genero: str,
        fecha_nac: date,
        fecha_inscrip: date,
        hora_inscrip: time,
    ):
        # Atributos
        self.coduser = cod_user
        self.genero = genero
        self.fecha_nac = fecha_nac
        self.fecha_inscrip = fecha_inscrip
        self.hora_inscrip = hora_inscrip
