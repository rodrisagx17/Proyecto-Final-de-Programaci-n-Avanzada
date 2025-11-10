from datetime import datetime
from typing import Optional
from MODELS.sede import Sede

class Empleado:
    def __init__(self, id: Optional[int] = None, nombre: str = "", 
                 apellido_paterno: str = "", apellido_materno: str = "",
                 email: str = "", telefono: str = "", fecha_contratacion: datetime = None,
                 salario: float = 0.0, rol: str = "", sede: Optional[Sede] = None,
                 activo: bool = True):
        self.id = id
        self.nombre = nombre
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.email = email
        self.telefono = telefono
        self.fecha_contratacion = fecha_contratacion
        self.salario = salario
        self.rol = rol
        self.sede = sede
        self.activo = activo

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"