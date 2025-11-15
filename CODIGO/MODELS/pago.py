from datetime import datetime
from typing import Optional
from MODELS.cliente import Cliente
from MODELS.empleado import Empleado
from MODELS.membresia import Membresia

class Pago:
    def __init__(self, folio: Optional[int] = None, cliente: Optional[Cliente] = None, 
                 empleado: Optional[Empleado] = None, membresia: Optional[Membresia] = None, 
                 monto: float = 0.0, monto_pagado: float = 0.0, 
                 metodo: str = "Efectivo", fecha_pago: datetime = None, 
                 concepto: str = "", estado: str = "Completado", referencia: str = ""):
        self.folio = folio
        self.cliente = cliente or Cliente()
        self.empleado = empleado or Empleado()
        self.membresia = membresia or Membresia()
        self.monto = monto
        self.monto_pagado = monto_pagado
        self.metodo = metodo
        self.fecha_pago = fecha_pago
        self.concepto = concepto
        self.estado = estado
        self.referencia = referencia

    @property
    def cambio(self):
        return self.monto_pagado - self.monto
        
    def __str__(self):
        return f"Pago {self.folio} - ${self.monto} - {self.estado}"