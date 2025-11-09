"""Clase Empleado que hereda de Persona"""

from datetime import datetime
from persona import Persona
from sede import Sede


class Empleado(Persona):
    def __init__(
        self,
        # Parámetros de Persona (clase padre)
        nombre: str,
        apellido_pa: str,
        apellido_ma: str,
        edad: int,
        email: str,
        telefono: str,
        # Parámetros específicos de Empleado
        sede: Sede,
        fechacontrat: datetime,
        salario: float,
        rol: str,
        ID: int = None,  # id de Persona (opcional)
        cod_emple: int = None,  # código de Empleado (opcional)
    ):

        # Inicializar la clase padre (Persona)
        super().__init__(nombre, apellido_pa, apellido_ma, edad, email, telefono, ID)

        self._cod_emple = cod_emple
        self._fechacontrat = fechacontrat
        self._salario = salario
        self._rol = rol
        self.sede = sede

    # GETTERS
    @property
    def cod_emple(self) -> int:
        return self._cod_emple

    @property
    def fechacontrat(self) -> datetime:
        return self._fechacontrat

    @property
    def salario(self) -> float:
        return self._salario

    @property
    def rol(self) -> str:
        return self._rol

    # SETTERS (con validaciones opcionales)
    @salario.setter
    def salario(self, valor: float) -> None:
        if valor < 0:
            raise ValueError("El salario no puede ser negativo")
        self._salario = valor

    @rol.setter
    def rol(self, valor: str) -> None:
        if not valor.strip():
            raise ValueError("El rol no puede estar vacío")
        self._rol = valor
