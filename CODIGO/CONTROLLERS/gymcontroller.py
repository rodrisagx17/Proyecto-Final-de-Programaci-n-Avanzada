from DATABASE.databasemanager import DatabaseManager
from MODELS.direccion import Direccion
from MODELS.persona import Persona
from MODELS.sede import Sede
from MODELS.cliente import Cliente
from datetime import datetime
from typing import List, Optional

class GymController:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    # ========== OPERACIONES DIRECCIÓN ==========
    def crear_direccion(self, direccion: Direccion) -> Optional[int]:
        query = "INSERT INTO Direccion (Calle, Ciudad, EstadoP, CP) VALUES (%s, %s, %s, %s)"
        if self.db.execute_query(query, (direccion.calle, direccion.ciudad, direccion.estado, direccion.cp)):
            return self.db.get_last_id()
        return None

    # ========== OPERACIONES PERSONA ==========
    def crear_persona(self, persona: Persona) -> Optional[int]:
        query = """
        INSERT INTO Persona (Nombre, ApellidoPA, ApellidoMA, Edad, Email, Telefono, Activo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        if self.db.execute_query(query, (
            persona.nombre, persona.apellido_pa, persona.apellido_ma, persona.edad,
            persona.email, persona.telefono, persona.activo
        )):
            return self.db.get_last_id()
        return None

    # ========== OPERACIONES SEDE ==========
    def crear_sede(self, sede: Sede) -> Optional[int]:
        # Primero crear dirección
        if not sede.direccion.id:
            dir_id = self.crear_direccion(sede.direccion)
            if not dir_id:
                return None
            sede.direccion.id = dir_id

        query = """
        INSERT INTO Sede (Nombre, HoraAbre, HoraCierra, IDDireccion, Telefono)
        VALUES (%s, %s, %s, %s, %s)
        """
        if self.db.execute_query(query, (
            sede.nombre, sede.hora_abre, sede.hora_cierra,
            sede.direccion.id, sede.telefono
        )):
            return self.db.get_last_id()
        return None

    def obtener_sedes(self) -> List[Sede]:
        query = """
        SELECT s.*, d.Calle, d.Ciudad, d.EstadoP, d.CP
        FROM Sede s
        JOIN Direccion d ON s.IDDireccion = d.ID
        """
        resultados = self.db.fetch_all(query)
        sedes = []
        
        for res in resultados:
            direccion = Direccion(
                id=res['IDDireccion'],
                calle=res['Calle'],
                ciudad=res['Ciudad'],
                estado=res['EstadoP'],
                cp=res['CP']
            )
            sede = Sede(
                id=res['ID'],
                nombre=res['Nombre'],
                hora_abre=str(res['HoraAbre']),
                hora_cierra=str(res['HoraCierra']),
                direccion=direccion,
                telefono=res['Telefono']
            )
            sedes.append(sede)
        
        return sedes

    # ========== OPERACIONES CLIENTE ==========
    def crear_cliente(self, cliente: Cliente) -> Optional[int]:
        # Primero crear persona
        if not cliente.persona.id:
            # Calcular edad a partir de fecha_nac
            if cliente.fecha_nac:
                hoy = datetime.now()
                cliente.persona.edad = hoy.year - cliente.fecha_nac.year - (
                    (hoy.month, hoy.day) < (cliente.fecha_nac.month, cliente.fecha_nac.day)
                )
            
            persona_id = self.crear_persona(cliente.persona)
            if not persona_id:
                return None
            cliente.persona.id = persona_id

        query = """
        INSERT INTO Cliente (IDPersona, IDSedeInscrito, Genero, FechaNac, FechaInscri)
        VALUES (%s, %s, %s, %s, %s)
        """
        if self.db.execute_query(query, (
            cliente.persona.id,
            cliente.sede_inscrito.id if cliente.sede_inscrito else None,
            cliente.genero,
            cliente.fecha_nac,
            cliente.fecha_inscri
        )):
            return self.db.get_last_id()
        return None

    def obtener_clientes(self) -> List[Cliente]:
        query = """
        SELECT c.*, p.Nombre, p.ApellidoPA, p.ApellidoMA, p.Edad, p.Email, p.Telefono,
               s.ID as SedeID, s.Nombre as SedeNombre, s.HoraAbre, s.HoraCierra,
               d.Calle, d.Ciudad, d.EstadoP, d.CP
        FROM Cliente c
        JOIN Persona p ON c.IDPersona = p.ID
        LEFT JOIN Sede s ON c.IDSedeInscrito = s.ID
        LEFT JOIN Direccion d ON s.IDDireccion = d.ID
        WHERE p.Activo = TRUE
        """
        resultados = self.db.fetch_all(query)
        clientes = []
        
        for res in resultados:
            # Construir dirección y sede
            direccion = Direccion(
                calle=res['Calle'],
                ciudad=res['Ciudad'],
                estado=res['EstadoP'],
                cp=res['CP']
            ) if res['Calle'] else None
            
            sede_inscrito = None
            if res['SedeID']:
                sede_inscrito = Sede(
                    id=res['SedeID'],
                    nombre=res['SedeNombre'],
                    hora_abre=str(res['HoraAbre']),
                    hora_cierra=str(res['HoraCierra']),
                    direccion=direccion
                )
            
            persona = Persona(
                id=res['IDPersona'],
                nombre=res['Nombre'],
                apellido_pa=res['ApellidoPA'],
                apellido_ma=res['ApellidoMA'],
                edad=res['Edad'],
                email=res['Email'],
                telefono=res['Telefono']
            )
            
            cliente = Cliente(
                cod_cli=res['CodCli'],
                persona=persona,
                sede_inscrito=sede_inscrito,
                genero=res['Genero'],
                fecha_nac=res['FechaNac'],
                fecha_inscri=res['FechaInscri']
            )
            clientes.append(cliente)
        
        return clientes