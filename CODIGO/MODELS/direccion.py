from typing import Optional

class Direccion:
    def __init__(self, id: Optional[int] = None, calle: str = "", ciudad: str = "", 
                 estado: str = "", cp: int = 0):
        self.id = id
        self.calle = calle
        self.ciudad = ciudad
        self.estado = estado
        self.cp = cp

    def __str__(self):
        return f"{self.calle}, {self.ciudad}, {self.estado} {self.cp}"
