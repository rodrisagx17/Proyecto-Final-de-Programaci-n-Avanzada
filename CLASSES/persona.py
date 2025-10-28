"""_summary_"""

from datetime import date


class Persona:
    # Constructor
    def __init__(
        self,
        iden_of: str,
        nombre_P: str,
        nombre_S: str,
        ap: str,
        am: str,
        calle: str,
        numero: str,
        ciudad: str,
        estado_p: str,
        cp: str,
        email: str,
        activo: bool,
        fecha_desactiv: date,
        tipo_perona: str,
    ):
        # Atributos
        self.idpersona = iden_of
        self.nombre_P = nombre_P
        self.nombre_S = nombre_S
        self.ap = ap
        self.am = am
        self.calle = calle
        self.numero = numero
        self.ciudad = ciudad
        self.estado_p = estado_p
        self.cp = cp
        self.email = email
        self.activo = activo
        self.fecha_desactiv = fecha_desactiv
        self.tipo_perona = tipo_perona
