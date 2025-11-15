from datetime import datetime
from typing import Optional
from MODELS.cliente import Cliente
from MODELS.inventario import Inventario
from MODELS.empleado import Empleado

class PrestamoEquipo:
    def __init__(self, id: Optional[int] = None, cliente: Optional[Cliente] = None, 
                 equipo: Optional[Inventario] = None, empleado: Optional[Empleado] = None, 
                 fecha_prestamo: datetime = None, fecha_devolucion: datetime = None, 
                 estado: str = "Prestado", observaciones: str = ""):
        self.id = id
        self.cliente = cliente or Cliente()
        self.equipo = equipo or Inventario()
        self.empleado = empleado or Empleado()
        self.fecha_prestamo = fecha_prestamo
        self.fecha_devolucion = fecha_devolucion
        self.estado = estado
        self.observaciones = observaciones
        
    @property
    def esta_atrasado(self):
        if self.estado == "Prestado" and self.fecha_devolucion:
            from datetime import datetime
            return datetime.now() > self.fecha_devolucion
        return False
        
    def __str__(self):
        return f"Préstamo {self.id} - {self.equipo.nombre} - {self.estado}"