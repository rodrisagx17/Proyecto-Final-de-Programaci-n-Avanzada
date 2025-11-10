from typing import Optional

class Persona:
    def __init__(self, nombre: str = "", apellido_pa: str = "", apellido_ma: str = "",
                 email: str = "", telefono: str = "", activo: bool = True, 
                 id: Optional[int] = None):
        self.id = id
        self.nombre = nombre
        self.apellido_pa = apellido_pa
        self.apellido_ma = apellido_ma
        self.email = email
        self.telefono = telefono
        self.activo = activo

    @property
    def edad(self) -> int:
        return self._edad

    @edad.setter
    def edad(self, valor: int) -> None:
        if valor > 0:
            self._edad = valor
        else:
            raise ValueError("La edad debe ser positiva")

    @activo.setter
    def activo(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise TypeError("El valor de activo debe ser booleano")
        self._activo = valor