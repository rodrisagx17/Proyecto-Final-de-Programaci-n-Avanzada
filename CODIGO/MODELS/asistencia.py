from datetime import date, time
from typing import Optional
from MODELS.cliente import Cliente
from MODELS.sede import Sede

class Asistencia:
    def __init__(self, id: Optional[int] = None, cliente: Optional[Cliente] = None, 
                 sede: Optional[Sede] = None, fecha: date = None, 
                 hora_entrada: time = None, hora_salida: time = None):
        self.id = id
        self.cliente = cliente or Cliente()
        self.sede = sede or Sede()
        self.fecha = fecha
        self.hora_entrada = hora_entrada
        self.hora_salida = hora_salida
        
    def __str__(self):
        return f"Asistencia {self.id} - Cliente: {self.cliente.persona.nombre_completo}"