from datetime import datetime
from typing import Optional
from MODELS.persona import Persona
from MODELS.sede import Sede

class Cliente:
    def __init__(self, cod_cli: Optional[int] = None, persona: Optional[Persona] = None, 
                 sede_inscrito: Optional[Sede] = None, genero: str = "", 
                 fecha_nac: datetime = None, fecha_inscri: datetime = None):
        self.cod_cli = cod_cli
        self.persona = persona or Persona()
        self.sede_inscrito = sede_inscrito
        self.genero = genero
        self.fecha_nac = fecha_nac
        self.fecha_inscri = fecha_inscri
