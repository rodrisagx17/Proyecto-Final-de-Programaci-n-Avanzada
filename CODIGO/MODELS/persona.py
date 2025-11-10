from typing import Optional

class Persona:
    def __init__(self, id: Optional[int] = None, nombre: str = "", apellido_pa: str = "", 
                 apellido_ma: str = "", edad: int = 0, email: str = "", telefono: str = "", 
                 activo: bool = True):
        self.id = id
        self.nombre = nombre
        self.apellido_pa = apellido_pa
        self.apellido_ma = apellido_ma
        self.edad = edad
        self.email = email
        self.telefono = telefono
        self.activo = activo

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido_pa} {self.apellido_ma}"
