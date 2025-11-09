"""Clase base Persona para gestionar información personal"""


class Persona:
    def __init__(
        self,
        nombre: str,
        apellido_pa: str,
        apellido_ma: str,
        edad: int,
        email: str,
        telefono: str,
        ID: int = None,
    ):
        self._id = ID
        self._nombre = nombre
        self._apellidopa = apellido_pa
        self._apellidoma = apellido_ma
        self._edad = edad
        self._email = email
        self._telefono = telefono
        self._activo = True
        self._nombre_completo = f"{self._nombre} {self._apellidopa} {self._apellidoma}"

    # GETTERS
    @property
    def id(self) -> int:
        return self._id

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def nombre_completo(self):
        return self._nombre_completo

    @property
    def edad(self) -> int:
        return self._edad

    @property
    def email(self) -> str:
        return self._email

    @property
    def telefono(self) -> str:
        return self._telefono

    @property
    def activo(self) -> bool:
        return self._activo

    # SETTERS (como para validaciones simples)
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
