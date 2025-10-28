"""_summary_"""

from datetime import date
from empleadoxclase import EmpleadoxClase
from persona import Persona


class Empleado:
    # Constructor
    def __init__(
        self,
        cod_empl: int,
        fecha_contrata: date,
        salario: float,
        dias_trabajo: str,
        activo_emple: bool,
        rol: str,
        especialidad: str,
    ):
        # Atributos
        self.idempleado = cod_empl
        self.fecha_contrata = fecha_contrata
        self.salario = salario
        self.dias_trabajo = dias_trabajo
        self.activo_emple = activo_emple
        self.rol = rol
        self.especialidad = especialidad
