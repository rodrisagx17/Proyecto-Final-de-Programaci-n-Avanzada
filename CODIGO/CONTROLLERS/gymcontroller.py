from DATABASE.databasemanager import DatabaseManager
from MODELS.sede import Sede
from MODELS.cliente import Cliente
from MODELS.empleado import Empleado
from typing import List, Optional
import json

class GymController:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    # ========== OPERACIONES SEDE ==========
    def crear_sede(self, sede: Sede) -> Optional[int]:
        query = """
        INSERT INTO Sede (Nombre, HoraAbre, HoraCierra, Direccion, Telefonos, Ciudad, Estado, CP)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Convertir teléfono a JSON array
        telefonos_json = json.dumps([sede.telefono]) if sede.telefono else '[]'
        
        if self.db.execute_query(query, (
            sede.nombre, sede.hora_abre, sede.hora_cierra, sede.direccion,
            telefonos_json, sede.ciudad, sede.estado, sede.cp
        )):
            return self.db.get_last_id()
        return None

    def obtener_sedes(self) -> List[Sede]:
        query = "SELECT * FROM Sede"
        resultados = self.db.fetch_all(query)
        sedes = []
        
        for res in resultados:
            # Procesar el campo JSON de teléfonos
            telefonos = []
            if res['Telefonos']:
                try:
                    telefonos = json.loads(res['Telefonos'])
                except:
                    telefonos = []
            
            telefono_principal = telefonos[0] if telefonos else ""
            
            sede = Sede(
                id=res['ID'],
                nombre=res['Nombre'],
                hora_abre=str(res['HoraAbre']),
                hora_cierra=str(res['HoraCierra']),
                direccion=res['Direccion'],
                telefono=telefono_principal,
                ciudad=res['Ciudad'],
                estado=res['Estado'],
                cp=res['CP']
            )
            sedes.append(sede)
        
        return sedes

    # ========== OPERACIONES CLIENTE ==========
    def crear_cliente(self, cliente: Cliente) -> Optional[int]:
        query = """
        INSERT INTO Cliente (Identificacion, Nombre, ApellidoPaterno, ApellidoMaterno, Telefono, 
                            Genero, FechaNacimiento, FechaInscripcion, IDSedeInscrito, Activo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        if self.db.execute_query(query, (
            cliente.identificacion,
            cliente.nombre,
            cliente.apellido_paterno,
            cliente.apellido_materno,
            cliente.telefono,
            cliente.genero,
            cliente.fecha_nacimiento,
            cliente.fecha_inscripcion,
            cliente.sede_inscrito.id if cliente.sede_inscrito else None,
            cliente.activo
        )):
            return self.db.get_last_id()
        return None

    def obtener_clientes(self) -> List[Cliente]:
        query = """
        SELECT c.*, s.Nombre as SedeNombre, s.HoraAbre, s.HoraCierra, s.Direccion as SedeDireccion,
               s.Ciudad as SedeCiudad, s.Estado as SedeEstado, s.CP as SedeCP
        FROM Cliente c
        LEFT JOIN Sede s ON c.IDSedeInscrito = s.ID
        WHERE c.Activo = TRUE
        """
        resultados = self.db.fetch_all(query)
        clientes = []
        
        for res in resultados:
            sede_inscrito = None
            if res['IDSedeInscrito']:
                sede_inscrito = Sede(
                    id=res['IDSedeInscrito'],
                    nombre=res['SedeNombre'],
                    hora_abre=str(res['HoraAbre']),
                    hora_cierra=str(res['HoraCierra']),
                    direccion=res['SedeDireccion'],
                    ciudad=res['SedeCiudad'],
                    estado=res['SedeEstado'],
                    cp=res['SedeCP']
                )
            
            cliente = Cliente(
                id=res['ID'],
                identificacion=res['Identificacion'],
                nombre=res['Nombre'],
                apellido_paterno=res['ApellidoPaterno'],
                apellido_materno=res['ApellidoMaterno'],
                telefono=res['Telefono'],
                genero=res['Genero'],
                fecha_nacimiento=res['FechaNacimiento'],
                fecha_inscripcion=res['FechaInscripcion'],
                sede_inscrito=sede_inscrito,
                activo=res['Activo']
            )
            clientes.append(cliente)
        
        return clientes

    def actualizar_cliente(self, cliente: Cliente) -> bool:
        query = """
        UPDATE Cliente 
        SET Identificacion=%s, Nombre=%s, ApellidoPaterno=%s, ApellidoMaterno=%s, 
            Telefono=%s, Genero=%s, FechaNacimiento=%s, IDSedeInscrito=%s
        WHERE ID=%s
        """
        return self.db.execute_query(query, (
            cliente.identificacion,
            cliente.nombre,
            cliente.apellido_paterno,
            cliente.apellido_materno,
            cliente.telefono,
            cliente.genero,
            cliente.fecha_nacimiento,
            cliente.sede_inscrito.id if cliente.sede_inscrito else None,
            cliente.id
        ))

    def eliminar_cliente(self, cliente_id: int) -> bool:
        query = "UPDATE Cliente SET Activo=FALSE WHERE ID=%s"
        return self.db.execute_query(query, (cliente_id,))

    # ========== OPERACIONES EMPLEADO ==========
    def crear_empleado(self, empleado: Empleado) -> Optional[int]:
        query = """
        INSERT INTO Empleado (Nombre, ApellidoPaterno, ApellidoMaterno, Email, Telefono,
                             FechaContratacion, Salario, Rol, IDSede, Activo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        if self.db.execute_query(query, (
            empleado.nombre,
            empleado.apellido_paterno,
            empleado.apellido_materno,
            empleado.email,
            empleado.telefono,
            empleado.fecha_contratacion,
            empleado.salario,
            empleado.rol,
            empleado.sede.id if empleado.sede else None,
            empleado.activo
        )):
            return self.db.get_last_id()
        return None

    # ========== OPERACIONES ASISTENCIA ==========
    def registrar_asistencia(self, cliente_id: int, sede_id: int) -> bool:
        query = """
        INSERT INTO Asistencia (IDCliente, IDSede, Fecha, HoraEntrada)
        VALUES (%s, %s, CURDATE(), CURTIME())
        """
        return self.db.execute_query(query, (cliente_id, sede_id))

    def registrar_salida(self, cliente_id: int) -> bool:
        query = """
        UPDATE Asistencia 
        SET HoraSalida = CURTIME() 
        WHERE IDCliente = %s AND Fecha = CURDATE() AND HoraSalida IS NULL
        """
        return self.db.execute_query(query, (cliente_id,))
