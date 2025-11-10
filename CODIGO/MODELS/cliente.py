from datetime import datetime
from typing import Optional
from MODELS.sede import Sede

class Cliente:
    def __init__(self, id: Optional[int] = None, identificacion: str = "", 
                 nombre: str = "", apellido_paterno: str = "", apellido_materno: str = "",
                 telefono: str = "", genero: str = "", fecha_nacimiento: datetime = None,
                 fecha_inscripcion: datetime = None, sede_inscrito: Optional[Sede] = None,
                 activo: bool = True):
        self.id = id
        self.identificacion = identificacion
        self.nombre = nombre
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.telefono = telefono
        self.genero = genero
        self.fecha_nacimiento = fecha_nacimiento
        self.fecha_inscripcion = fecha_inscripcion
        self.sede_inscrito = sede_inscrito
        self.activo = activo

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"

    @property
    def edad(self) -> int:
        if self.fecha_nacimiento is None:
            return 0
        hoy = datetime.now()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )