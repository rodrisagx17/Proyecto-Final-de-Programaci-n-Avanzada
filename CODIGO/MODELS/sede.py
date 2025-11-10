from typing import Optional

class Sede:
    def __init__(self, id: Optional[int] = None, nombre: str = "", hora_abre: str = "", 
                 hora_cierra: str = "", direccion: str = "", telefono: str = "", 
                 ciudad: str = "", estado: str = "", cp: int = 0):
        self.id = id
        self.nombre = nombre
        self.hora_abre = hora_abre
        self.hora_cierra = hora_cierra
        self.direccion = direccion
        self.telefono = telefono
        self.ciudad = ciudad
        self.estado = estado
        self.cp = cp

    def __str__(self):
        return f"{self.nombre} - {self.direccion}, {self.ciudad}"