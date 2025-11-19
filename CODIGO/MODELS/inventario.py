from datetime import date
from typing import Optional
from MODELS.sede import Sede

class Inventario:
    def __init__(self, codigo_barras: Optional[int] = None, sede: Optional[Sede] = None, 
                 nombre: str = "", categoria: str = "", tipo: str = "", 
                 descripcion: str = "", precio_venta: float = 0.0, 
                 precio_compra: float = 0.0, cantidad: int = 0, 
                 stock_minimo: int = 5, fecha_caducidad: date = None, 
                 activo: bool = True):
        self.codigo_barras = codigo_barras
        self.sede = sede or Sede()
        self.nombre = nombre
        self.categoria = categoria
        self.tipo = tipo
        self.descripcion = descripcion
        self.precio_venta = precio_venta
        self.precio_compra = precio_compra
        self.cantidad = cantidad
        self.stock_minimo = stock_minimo
        self.fecha_caducidad = fecha_caducidad
        self.activo = activo

    @property
    def necesita_reabastecer(self):
        return self.cantidad <= self.stock_minimo
        
    def __str__(self):
        return f"{self.nombre} - Stock: {self.cantidad}"