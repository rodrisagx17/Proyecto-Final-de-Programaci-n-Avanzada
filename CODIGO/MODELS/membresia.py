from datetime import datetime
from MODELS.cliente import Cliente
from typing import Optional

class Membresia:
    def __init__(self, cliente: Cliente, tipo: str, precio: float,
                 fecha_inicio: datetime, fecha_venc: datetime, estado: str = "Activa",
                 cod_mem: Optional[int] = None):
        self.cod_mem = cod_mem
        self.cliente = cliente
        self.tipo = tipo
        self.precio = precio
        self.fecha_inicio = fecha_inicio
        self.fecha_venc = fecha_venc
        self.estado = estado

    @property
    def dias_restantes(self) -> int:
        return (self.fecha_venc - datetime.now()).days