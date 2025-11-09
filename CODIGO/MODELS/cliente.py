"""Clase Cliente que hereda de Persona"""

from datetime import date, datetime
from persona import Persona
from sede import Sede


class Cliente(Persona):
    def __init__(
        self,
        # Parámetros de Persona (clase padre)
        nombre: str,
        apellido_pa: str,
        apellido_ma: str,
        edad: int,
        email: str,
        telefono: str,
        # Parámetros específicos de Cliente
        sede_inscrito: Sede,
        genero: str,
        fecha_nac: date,
        fecha_inscri: datetime,
        ID: int = None,  # id de Persona (opcional)
        cod_cli: int = None,  # código de Cliente (opcional)
    ):

        # Inicializar la clase padre (Persona)
        super().__init__(nombre, apellido_pa, apellido_ma, edad, email, telefono, ID)

        self._cod_cli = cod_cli
        self._genero = genero
        self._fecha_nac = fecha_nac
        self._fecha_inscri = fecha_inscri
        self.sede_inscrito = sede_inscrito

    # GETTERS
    @property
    def cod_cli(self) -> int:
        return self._cod_cli

    @property
    def genero(self) -> str:
        return self._genero

    @property
    def fecha_nac(self) -> date:
        return self._fecha_nac

    @property
    def fecha_inscri(self) -> datetime:
        return self._fecha_inscri

    # SETTERS (con validaciones opcionales)
    @genero.setter
    def genero(self, valor: str) -> None:
        opciones_validas = ["M", "F", "MASCULINO", "FEMENINO"]
        if valor.upper() in opciones_validas:
            self._genero = valor
        else:
            raise ValueError(f"Género debe ser uno de: {opciones_validas}")
