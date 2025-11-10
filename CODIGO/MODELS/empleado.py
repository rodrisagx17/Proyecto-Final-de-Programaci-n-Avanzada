from datetime import datetime
from typing import Optional
from MODELS.persona import Persona
from MODELS.sede import Sede

class Empleado:
    def __init__(self, cod_emple: Optional[int] = None, persona: Optional[Persona] = None, 
                 sede: Optional[Sede] = None, fecha_contrat: datetime = None, 
                 salario: float = 0.0, rol: str = ""):
        self.cod_emple = cod_emple
        self.persona = persona or Persona()
        self.sede = sede
        self.fecha_contrat = fecha_contrat
        self.salario = salario
        self.rol = rol
