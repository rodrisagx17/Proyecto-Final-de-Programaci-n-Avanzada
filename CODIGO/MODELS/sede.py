from typing import Optional
from MODELS.direccion import Direccion

class Sede:
    def __init__(self, id: Optional[int] = None, nombre: str = "", hora_abre: str = "", 
                 hora_cierra: str = "", direccion: Optional[Direccion] = None, 
                 telefono: str = ""):
        self.id = id
        self.nombre = nombre
        self.hora_abre = hora_abre
        self.hora_cierra = hora_cierra
        self.direccion = direccion or Direccion()
        self.telefono = telefono

    def __str__(self):
        return f"{self.nombre} - {self.direccion}"