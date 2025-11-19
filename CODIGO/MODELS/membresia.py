from datetime import datetime
from typing import Optional
from MODELS.cliente import Cliente

class Membresia:
    def __init__(self, cod_mem: Optional[int] = None, cliente: Optional[Cliente] = None, 
                 tipo: str = "Mensual", precio: float = 0.0, fecha_inicio: datetime = None, 
                 fecha_venc: datetime = None, estado: str = "Activa"):
        self.cod_mem = cod_mem
        self.cliente = cliente or Cliente()
        self.tipo = tipo
        self.precio = precio
        self.fecha_inicio = fecha_inicio
        self.fecha_venc = fecha_venc
        self.estado = estado
        
    @property
    def dias_restantes(self):
        if self.fecha_venc:
            from datetime import datetime
            return (self.fecha_venc - datetime.now().date()).days
        return 0
        
    def __str__(self):
        return f"Membresía {self.tipo} - {self.estado}"