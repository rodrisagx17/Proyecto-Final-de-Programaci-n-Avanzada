from DATABASE.databasemanager import DatabaseManager
from MODELS.direccion import Direccion
from MODELS.persona import Persona
from MODELS.sede import Sede
from MODELS.cliente import Cliente
from MODELS.empleado import Empleado
from MODELS.asistencia import Asistencia
from MODELS.membresia import Membresia
from MODELS.pago import Pago
from MODELS.inventario import Inventario
from MODELS.prestamo_equipo import PrestamoEquipo
from datetime import datetime, date
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
        if not cliente.persona.id:
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

    # ========== OPERACIONES EMPLEADO ==========
    def crear_empleado(self, empleado: Empleado) -> Optional[int]:
        if not empleado.persona.id:
            persona_id = self.crear_persona(empleado.persona)
            if not persona_id:
                return None
            empleado.persona.id = persona_id

        query = """
        INSERT INTO Empleado (IDPersona, IDSede, FechaContrat, Salario, Rol)
        VALUES (%s, %s, %s, %s, %s)
        """
        if self.db.execute_query(query, (
            empleado.persona.id,
            empleado.sede.id if empleado.sede else None,
            empleado.fecha_contratacion,
            empleado.salario,
            empleado.rol
        )):
            return self.db.get_last_id()
        return None

    # ========== OPERACIONES ASISTENCIA ==========
    def registrar_entrada(self, asistencia: Asistencia) -> Optional[int]:
        query = """
        INSERT INTO Asistencia (IDCliente, IDSede, Fecha, HoraEntrada)
        VALUES (%s, %s, %s, %s)
        """
        if self.db.execute_query(query, (
            asistencia.cliente.cod_cli,
            asistencia.sede.id,
            date.today(),
            datetime.now().time()
        )):
            return self.db.get_last_id()
        return None

    def registrar_salida(self, asistencia_id: int) -> bool:
        query = "UPDATE Asistencia SET HoraSalida = %s WHERE ID = %s"
        return self.db.execute_query(query, (datetime.now().time(), asistencia_id))

    def obtener_asistencias_dia(self, fecha: date = None) -> List[Asistencia]:
        if fecha is None:
            fecha = date.today()
            
        query = """
        SELECT a.*, c.CodCli, p.Nombre, p.ApellidoPA, p.ApellidoMA,
               s.ID as SedeID, s.Nombre as SedeNombre
        FROM Asistencia a
        JOIN Cliente c ON a.IDCliente = c.CodCli
        JOIN Persona p ON c.IDPersona = p.ID
        JOIN Sede s ON a.IDSede = s.ID
        WHERE a.Fecha = %s
        ORDER BY a.HoraEntrada DESC
        """
        resultados = self.db.fetch_all(query, (fecha,))
        asistencias = []
        
        for res in resultados:
            cliente = Cliente(
                cod_cli=res['CodCli'],
                persona=Persona(
                    nombre=res['Nombre'],
                    apellido_pa=res['ApellidoPA'],
                    apellido_ma=res['ApellidoMA']
                )
            )
            sede = Sede(
                id=res['SedeID'],
                nombre=res['SedeNombre']
            )
            asistencia = Asistencia(
                id=res['ID'],
                cliente=cliente,
                sede=sede,
                fecha=res['Fecha'],
                hora_entrada=res['HoraEntrada'],
                hora_salida=res['HoraSalida']
            )
            asistencias.append(asistencia)
        
        return asistencias

    # ========== OPERACIONES MEMBRESIA ==========
    def crear_membresia(self, membresia: Membresia) -> Optional[int]:
        query = """
        INSERT INTO Membresia (IDCliente, Tipo, Precio, FechaInicio, FechaVenc, Estado)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        if self.db.execute_query(query, (
            membresia.cliente.cod_cli,
            membresia.tipo,
            membresia.precio,
            membresia.fecha_inicio,
            membresia.fecha_venc,
            membresia.estado
        )):
            return self.db.get_last_id()
        return None

    def obtener_membresias_cliente(self, cliente_id: int) -> List[Membresia]:
        query = """
        SELECT m.*, c.CodCli, p.Nombre, p.ApellidoPA, p.ApellidoMA
        FROM Membresia m
        JOIN Cliente c ON m.IDCliente = c.CodCli
        JOIN Persona p ON c.IDPersona = p.ID
        WHERE m.IDCliente = %s
        ORDER BY m.FechaInicio DESC
        """
        resultados = self.db.fetch_all(query, (cliente_id,))
        membresias = []
        
        for res in resultados:
            cliente = Cliente(
                cod_cli=res['CodCli'],
                persona=Persona(
                    nombre=res['Nombre'],
                    apellido_pa=res['ApellidoPA'],
                    apellido_ma=res['ApellidoMA']
                )
            )
            membresia = Membresia(
                cod_mem=res['CodMem'],
                cliente=cliente,
                tipo=res['Tipo'],
                precio=res['Precio'],
                fecha_inicio=res['FechaInicio'],
                fecha_venc=res['FechaVenc'],
                estado=res['Estado']
            )
            membresias.append(membresia)
        
        return membresias

    # ========== OPERACIONES PAGO ==========
    def registrar_pago(self, pago: Pago) -> Optional[int]:
        query = """
        INSERT INTO Pago (IDCliente, IDEmpleado, IDMembresia, Monto, MontoPagado, 
                         Metodo, FechaPago, Concepto, Estado, Referencia)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        if self.db.execute_query(query, (
            pago.cliente.cod_cli,
            pago.empleado.cod_emple if pago.empleado else None,
            pago.membresia.cod_mem if pago.membresia else None,
            pago.monto,
            pago.monto_pagado,
            pago.metodo,
            pago.fecha_pago or datetime.now(),
            pago.concepto,
            pago.estado,
            pago.referencia
        )):
            return self.db.get_last_id()
        return None

    def obtener_pagos_cliente(self, cliente_id: int) -> List[Pago]:
        query = """
        SELECT p.*, c.CodCli, p2.Nombre as ClienteNombre, p2.ApellidoPA as ClienteApellidoPA,
               e.CodEmple, p3.Nombre as EmpleadoNombre, m.CodMem, m.Tipo as MembresiaTipo
        FROM Pago p
        JOIN Cliente c ON p.IDCliente = c.CodCli
        JOIN Persona p2 ON c.IDPersona = p2.ID
        LEFT JOIN Empleado e ON p.IDEmpleado = e.CodEmple
        LEFT JOIN Persona p3 ON e.IDPersona = p3.ID
        LEFT JOIN Membresia m ON p.IDMembresia = m.CodMem
        WHERE p.IDCliente = %s
        ORDER BY p.FechaPago DESC
        """
        resultados = self.db.fetch_all(query, (cliente_id,))
        pagos = []
        
        for res in resultados:
            cliente = Cliente(
                cod_cli=res['CodCli'],
                persona=Persona(
                    nombre=res['ClienteNombre'],
                    apellido_pa=res['ClienteApellidoPA']
                )
            )
            empleado = None
            if res['CodEmple']:
                empleado = Empleado(
                    cod_emple=res['CodEmple'],
                    persona=Persona(
                        nombre=res['EmpleadoNombre']
                    )
                )
            membresia = None
            if res['CodMem']:
                membresia = Membresia(
                    cod_mem=res['CodMem'],
                    tipo=res['MembresiaTipo']
                )
            pago = Pago(
                folio=res['Folio'],
                cliente=cliente,
                empleado=empleado,
                membresia=membresia,
                monto=res['Monto'],
                monto_pagado=res['MontoPagado'],
                metodo=res['Metodo'],
                fecha_pago=res['FechaPago'],
                concepto=res['Concepto'],
                estado=res['Estado'],
                referencia=res['Referencia']
            )
            pagos.append(pago)
        
        return pagos

    # ========== OPERACIONES INVENTARIO ==========
    def agregar_inventario(self, inventario: Inventario) -> Optional[int]:
        query = """
        INSERT INTO Inventario (IDSede, Nombre, Categoria, Tipo, Descripcion, 
                               PrecioVenta, PrecioCompra, Cantidad, StockMinimo, FechaCaducidad, Activo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        if self.db.execute_query(query, (
            inventario.sede.id if inventario.sede else None,
            inventario.nombre,
            inventario.categoria,
            inventario.tipo,
            inventario.descripcion,
            inventario.precio_venta,
            inventario.precio_compra,
            inventario.cantidad,
            inventario.stock_minimo,
            inventario.fecha_caducidad,
            inventario.activo
        )):
            return self.db.get_last_id()
        return None

    def obtener_inventario_sede(self, sede_id: int) -> List[Inventario]:
        query = """
        SELECT i.*, s.Nombre as SedeNombre
        FROM Inventario i
        LEFT JOIN Sede s ON i.IDSede = s.ID
        WHERE i.IDSede = %s AND i.Activo = TRUE
        ORDER BY i.Nombre
        """
        resultados = self.db.fetch_all(query, (sede_id,))
        inventarios = []
        
        for res in resultados:
            sede = None
            if res['IDSede']:
                sede = Sede(
                    id=res['IDSede'],
                    nombre=res['SedeNombre']
                )
            inventario = Inventario(
                codigo_barras=res['CodigoBarras'],
                sede=sede,
                nombre=res['Nombre'],
                categoria=res['Categoria'],
                tipo=res['Tipo'],
                descripcion=res['Descripcion'],
                precio_venta=res['PrecioVenta'],
                precio_compra=res['PrecioCompra'],
                cantidad=res['Cantidad'],
                stock_minimo=res['StockMinimo'],
                fecha_caducidad=res['FechaCaducidad'],
                activo=res['Activo']
            )
            inventarios.append(inventario)
        
        return inventarios

    def actualizar_stock(self, codigo_barras: int, nueva_cantidad: int) -> bool:
        query = "UPDATE Inventario SET Cantidad = %s WHERE CodigoBarras = %s"
        return self.db.execute_query(query, (nueva_cantidad, codigo_barras))

    # ========== OPERACIONES PRÉSTAMO EQUIPO ==========
    def registrar_prestamo(self, prestamo: PrestamoEquipo) -> Optional[int]:
        query = """
        INSERT INTO Prestamo_Equipo (IDCliente, IDEquipo, IDEmpleado, FechaPrestamo, Estado, Observaciones)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        if self.db.execute_query(query, (
            prestamo.cliente.cod_cli,
            prestamo.equipo.codigo_barras,
            prestamo.empleado.cod_emple,
            prestamo.fecha_prestamo or datetime.now(),
            prestamo.estado,
            prestamo.observaciones
        )):
            return self.db.get_last_id()
        return None

    def devolver_prestamo(self, prestamo_id: int) -> bool:
        query = """
        UPDATE Prestamo_Equipo 
        SET FechaDevolucion = %s, Estado = 'Devuelto' 
        WHERE ID = %s
        """
        return self.db.execute_query(query, (datetime.now(), prestamo_id))

    def obtener_prestamos_activos(self) -> List[PrestamoEquipo]:
        query = """
        SELECT pe.*, c.CodCli, p.Nombre as ClienteNombre, p.ApellidoPA as ClienteApellidoPA,
               i.CodigoBarras, i.Nombre as EquipoNombre,
               e.CodEmple, p2.Nombre as EmpleadoNombre
        FROM Prestamo_Equipo pe
        JOIN Cliente c ON pe.IDCliente = c.CodCli
        JOIN Persona p ON c.IDPersona = p.ID
        JOIN Inventario i ON pe.IDEquipo = i.CodigoBarras
        JOIN Empleado e ON pe.IDEmpleado = e.CodEmple
        JOIN Persona p2 ON e.IDPersona = p2.ID
        WHERE pe.Estado = 'Prestado'
        ORDER BY pe.FechaPrestamo DESC
        """
        resultados = self.db.fetch_all(query)
        prestamos = []
        
        for res in resultados:
            cliente = Cliente(
                cod_cli=res['CodCli'],
                persona=Persona(
                    nombre=res['ClienteNombre'],
                    apellido_pa=res['ClienteApellidoPA']
                )
            )
            equipo = Inventario(
                codigo_barras=res['CodigoBarras'],
                nombre=res['EquipoNombre']
            )
            empleado = Empleado(
                cod_emple=res['CodEmple'],
                persona=Persona(
                    nombre=res['EmpleadoNombre']
                )
            )
            prestamo = PrestamoEquipo(
                id=res['ID'],
                cliente=cliente,
                equipo=equipo,
                empleado=empleado,
                fecha_prestamo=res['FechaPrestamo'],
                fecha_devolucion=res['FechaDevolucion'],
                estado=res['Estado'],
                observaciones=res['Observaciones']
            )
            prestamos.append(prestamo)
        
        return prestamos
    
        # ========== MÉTODOS PARA REGISTRO DE ASISTENCIA ==========
    def buscar_cliente_por_codigo(self, codigo: int) -> Optional[Cliente]:
        query = """
        SELECT c.*, p.Nombre, p.ApellidoPA, p.ApellidoMA, p.Edad, p.Email, p.Telefono,
               s.ID as SedeID, s.Nombre as SedeNombre, s.HoraAbre, s.HoraCierra,
               d.Calle, d.Ciudad, d.EstadoP, d.CP
        FROM Cliente c
        JOIN Persona p ON c.IDPersona = p.ID
        LEFT JOIN Sede s ON c.IDSedeInscrito = s.ID
        LEFT JOIN Direccion d ON s.IDDireccion = d.ID
        WHERE c.CodCli = %s AND p.Activo = TRUE
        """
        resultado = self.db.fetch_one(query, (codigo,))
        
        if resultado:
            direccion = Direccion(
                calle=resultado['Calle'],
                ciudad=resultado['Ciudad'],
                estado=resultado['EstadoP'],
                cp=resultado['CP']
            ) if resultado['Calle'] else None
            
            sede_inscrito = None
            if resultado['SedeID']:
                sede_inscrito = Sede(
                    id=resultado['SedeID'],
                    nombre=resultado['SedeNombre'],
                    hora_abre=str(resultado['HoraAbre']),
                    hora_cierra=str(resultado['HoraCierra']),
                    direccion=direccion
                )
            
            persona = Persona(
                id=resultado['IDPersona'],
                nombre=resultado['Nombre'],
                apellido_pa=resultado['ApellidoPA'],
                apellido_ma=resultado['ApellidoMA'],
                edad=resultado['Edad'],
                email=resultado['Email'],
                telefono=resultado['Telefono']
            )
            
            cliente = Cliente(
                cod_cli=resultado['CodCli'],
                persona=persona,
                sede_inscrito=sede_inscrito,
                genero=resultado['Genero'],
                fecha_nac=resultado['FechaNac'],
                fecha_inscri=resultado['FechaInscri']
            )
            return cliente
        
        return None

    def obtener_membresia_activa_cliente(self, cliente_id: int) -> Optional[Membresia]:
        query = """
        SELECT m.* 
        FROM Membresia m
        WHERE m.IDCliente = %s AND m.Estado = 'Activa'
        ORDER BY m.FechaVenc DESC
        LIMIT 1
        """
        resultado = self.db.fetch_one(query, (cliente_id,))
        
        if resultado:
            cliente = Cliente(cod_cli=cliente_id)
            membresia = Membresia(
                cod_mem=resultado['CodMem'],
                cliente=cliente,
                tipo=resultado['Tipo'],
                precio=resultado['Precio'],
                fecha_inicio=resultado['FechaInicio'],
                fecha_venc=resultado['FechaVenc'],
                estado=resultado['Estado']
            )
            return membresia
        return None

    def registrar_asistencia_cliente(self, cliente_id: int, sede_id: int) -> dict:
        try:
            hoy = date.today()
            
            query_pendientes = """
            SELECT ID, Fecha FROM Asistencia 
            WHERE IDCliente = %s AND HoraSalida IS NULL AND Fecha < %s
            """
            pendientes = self.db.fetch_all(query_pendientes, (cliente_id, hoy))
            
            for pendiente in pendientes:
                query_cerrar = "UPDATE Asistencia SET HoraSalida = '23:59:59' WHERE ID = %s"
                self.db.execute_query(query_cerrar, (pendiente['ID'],))
                print(f"CERRADA asistencia pendiente del {pendiente['Fecha']} para cliente {cliente_id}")
            
            query_check = """
            SELECT ID, HoraEntrada FROM Asistencia 
            WHERE IDCliente = %s AND Fecha = %s AND HoraSalida IS NULL
            """
            asistencia_hoy = self.db.fetch_one(query_check, (cliente_id, hoy))
            
            if asistencia_hoy:
                hora_salida = datetime.now().time()
                query_salida = "UPDATE Asistencia SET HoraSalida = %s WHERE ID = %s"
                if self.db.execute_query(query_salida, (hora_salida, asistencia_hoy['ID'])):
                    return {
                        'success': True,
                        'tipo': 'salida',
                        'asistencia_id': asistencia_hoy['ID'],
                        'mensaje': f'Salida registrada (Entrada: {asistencia_hoy["HoraEntrada"]})'
                    }
            else:
                hora_entrada = datetime.now().time()
                query_entrada = """
                INSERT INTO Asistencia (IDCliente, IDSede, Fecha, HoraEntrada)
                VALUES (%s, %s, %s, %s)
                """
                if self.db.execute_query(query_entrada, (cliente_id, sede_id, hoy, hora_entrada)):
                    nueva_id = self.db.get_last_id()
                    return {
                        'success': True,
                        'tipo': 'entrada',
                        'asistencia_id': nueva_id,
                        'mensaje': 'Entrada registrada correctamente'
                    }
            
            return {'success': False, 'mensaje': 'No se pudo registrar la asistencia'}
            
        except Exception as e:
            return {'success': False, 'mensaje': f'Error: {str(e)}'}